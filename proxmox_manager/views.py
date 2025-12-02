from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MigrationForm, SnapshotForm, VMSearchForm
from .models import AuditLog, Node, ProxmoxCluster, VirtualMachine
from .tasks import (
    create_snapshot,
    get_proxmox_connection,
    migrate_vm_task,
    sync_cluster_data,
    vm_power_action,
)


@login_required
def dashboard(request):
    clusters = ProxmoxCluster.objects.filter(is_active=True)
    nodes = Node.objects.all()
    vms = VirtualMachine.objects.all()
    recent_logs = AuditLog.objects.select_related("user", "vm", "cluster")[:10]

    total_vms = vms.count()
    running_vms = vms.filter(status="running").count()
    stopped_vms = vms.filter(status="stopped").count()

    total_nodes = nodes.count()
    online_nodes = nodes.filter(status="online").count()

    avg_cpu = nodes.aggregate(Avg("cpu_usage"))["cpu_usage__avg"] or 0
    avg_ram = nodes.aggregate(Avg("ram_usage"))["ram_usage__avg"] or 0

    context = {
        "clusters": clusters,
        "nodes": nodes,
        "vms": vms,
        "total_vms": total_vms,
        "running_vms": running_vms,
        "stopped_vms": stopped_vms,
        "total_nodes": total_nodes,
        "online_nodes": online_nodes,
        "avg_cpu": round(avg_cpu, 2),
        "avg_ram": round(avg_ram, 2),
        "recent_logs": recent_logs,
    }

    return render(request, "proxmox_manager/dashboard.html", context)


@login_required
def vm_list(request):
    vms = VirtualMachine.objects.select_related("node", "node__cluster").all()

    form = VMSearchForm(request.GET or None)

    if form.is_valid():
        search = form.cleaned_data.get("search")
        cluster = form.cleaned_data.get("cluster")
        status = form.cleaned_data.get("status")
        vm_type = form.cleaned_data.get("vm_type")

        if search:
            vms = vms.filter(Q(name__icontains=search) | Q(vmid__icontains=search))

        if cluster:
            vms = vms.filter(node__cluster=cluster)

        if status:
            vms = vms.filter(status=status)

        if vm_type:
            vms = vms.filter(vm_type=vm_type)

    # Add stats for right sidebar
    clusters = ProxmoxCluster.objects.filter(is_active=True)
    nodes = Node.objects.all()
    all_vms = VirtualMachine.objects.all()

    context = {
        "vms": vms,
        "form": form,
        # Stats for right sidebar
        "clusters": clusters,
        "nodes": nodes,
        "total_vms": all_vms.count(),
        "running_vms": all_vms.filter(status="running").count(),
        "total_nodes": nodes.count(),
        "online_nodes": nodes.filter(status="online").count(),
        "avg_cpu": round(nodes.aggregate(Avg("cpu_usage"))["cpu_usage__avg"] or 0, 2),
        "avg_ram": round(nodes.aggregate(Avg("ram_usage"))["ram_usage__avg"] or 0, 2),
    }

    return render(request, "proxmox_manager/vm_list.html", context)


@login_required
def vm_detail(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)

    available_nodes = Node.objects.filter(
        cluster=vm.node.cluster, status="online"
    ).exclude(id=vm.node.id)

    # Add stats for right sidebar
    clusters = ProxmoxCluster.objects.filter(is_active=True)
    nodes = Node.objects.all()
    vms = VirtualMachine.objects.all()

    context = {
        "vm": vm,
        "available_nodes": available_nodes,
        # Stats for right sidebar
        "clusters": clusters,
        "nodes": nodes,
        "vms": vms,
        "total_vms": vms.count(),
        "running_vms": vms.filter(status="running").count(),
        "total_nodes": nodes.count(),
        "online_nodes": nodes.filter(status="online").count(),
        "avg_cpu": round(nodes.aggregate(Avg("cpu_usage"))["cpu_usage__avg"] or 0, 2),
        "avg_ram": round(nodes.aggregate(Avg("ram_usage"))["ram_usage__avg"] or 0, 2),
    }

    return render(request, "proxmox_manager/vm_detail.html", context)


@login_required
def vm_power_control(request, vm_id, action):
    vm = get_object_or_404(VirtualMachine, id=vm_id)

    if action not in ["start", "stop", "reboot", "shutdown"]:
        messages.error(request, "Invalid action")
        return redirect("vm_list")

    vm_power_action.delay(vm.id, action, request.user.id)
    messages.success(request, f"{action.capitalize()} action initiated for {vm.name}")

    return redirect("vm_detail", vm_id=vm_id)


@login_required
def migrate_vm(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)

    if request.method == "POST":
        form = MigrationForm(request.POST, vm=vm)
        if form.is_valid():
            target_node = form.cleaned_data["target_node"]
            online = form.cleaned_data["online"]

            migrate_vm_task.delay(vm.id, target_node.id, request.user.id, online)
            messages.success(
                request,
                f"Migration of {vm.name} to {target_node.name} has been initiated",
            )
            return redirect("vm_detail", vm_id=vm_id)
    else:
        form = MigrationForm(vm=vm)

    context = {
        "vm": vm,
        "form": form,
    }

    return render(request, "proxmox_manager/migrate_vm.html", context)


@login_required
def create_vm_snapshot(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)

    if request.method == "POST":
        form = SnapshotForm(request.POST)
        if form.is_valid():
            snapshot_name = form.cleaned_data["snapshot_name"]
            create_snapshot.delay(vm.id, snapshot_name, request.user.id)
            messages.success(request, f"Snapshot creation initiated for {vm.name}")
            return redirect("vm_detail", vm_id=vm_id)
    else:
        form = SnapshotForm()

    context = {
        "vm": vm,
        "form": form,
    }

    return render(request, "proxmox_manager/create_snapshot.html", context)


@login_required
def cluster_list(request):
    clusters = ProxmoxCluster.objects.prefetch_related("nodes").all()

    cluster_stats = []
    for cluster in clusters:
        nodes = cluster.nodes.all()
        vms = VirtualMachine.objects.filter(node__cluster=cluster)

        cluster_stats.append(
            {
                "cluster": cluster,
                "node_count": nodes.count(),
                "vm_count": vms.count(),
                "running_vms": vms.filter(status="running").count(),
                "online_nodes": nodes.filter(status="online").count(),
            }
        )

    # Add stats for right sidebar
    all_clusters = ProxmoxCluster.objects.filter(is_active=True)
    nodes = Node.objects.all()
    vms = VirtualMachine.objects.all()

    context = {
        "cluster_stats": cluster_stats,
        # Stats for right sidebar
        "clusters": all_clusters,
        "nodes": nodes,
        "vms": vms,
        "total_vms": vms.count(),
        "running_vms": vms.filter(status="running").count(),
        "total_nodes": nodes.count(),
        "online_nodes": nodes.filter(status="online").count(),
        "avg_cpu": round(nodes.aggregate(Avg("cpu_usage"))["cpu_usage__avg"] or 0, 2),
        "avg_ram": round(nodes.aggregate(Avg("ram_usage"))["ram_usage__avg"] or 0, 2),
    }

    return render(request, "proxmox_manager/cluster_list.html", context)


@login_required
def cluster_detail(request, cluster_id):
    cluster = get_object_or_404(ProxmoxCluster, id=cluster_id)
    nodes = cluster.nodes.all()
    vms = VirtualMachine.objects.filter(node__cluster=cluster)

    context = {
        "cluster": cluster,
        "nodes": nodes,
        "vms": vms,
    }

    return render(request, "proxmox_manager/cluster_detail.html", context)


@login_required
def sync_cluster(request, cluster_id):
    cluster = get_object_or_404(ProxmoxCluster, id=cluster_id)

    # If AJAX request, return JSON
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        task = sync_cluster_data.delay(cluster.id)
        return JsonResponse(
            {
                "status": "started",
                "message": f"Sync initiated for cluster {cluster.name}",
                "task_id": task.id,
                "cluster_id": cluster.id,
            }
        )

    # Regular request - redirect with message
    sync_cluster_data.delay(cluster.id)
    messages.success(request, f"Sync initiated for cluster {cluster.name}")
    return redirect("dashboard")


@login_required
def sync_all_clusters(request):
    clusters = ProxmoxCluster.objects.filter(is_active=True)

    # If AJAX request, return JSON
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        task_ids = []
        for cluster in clusters:
            task = sync_cluster_data.delay(cluster.id)
            task_ids.append(
                {"cluster_id": cluster.id, "task_id": task.id, "name": cluster.name}
            )

        return JsonResponse(
            {
                "status": "started",
                "message": f"Sync initiated for {len(clusters)} cluster(s)",
                "tasks": task_ids,
            }
        )

    # Regular request - redirect with message
    for cluster in clusters:
        sync_cluster_data.delay(cluster.id)
    messages.success(request, "Sync initiated for all clusters")
    return redirect("dashboard")


@login_required
def get_cluster_stats(request, cluster_id):
    """API endpoint to get cluster stats without page reload"""
    cluster = get_object_or_404(ProxmoxCluster, id=cluster_id)
    nodes = cluster.nodes.all()
    vms = VirtualMachine.objects.filter(node__cluster=cluster)

    nodes_data = []
    for node in nodes:
        nodes_data.append(
            {
                "id": node.id,
                "name": node.name,
                "status": node.status,
                "cpu_usage": float(node.cpu_usage),
                "ram_usage": float(node.ram_usage),
                "disk_usage": float(node.disk_usage),
                "vm_count": node.virtual_machines.count(),
            }
        )

    vms_data = []
    for vm in vms[:20]:  # Limit to 20 VMs for performance
        vms_data.append(
            {
                "id": vm.id,
                "name": vm.name,
                "vmid": vm.vmid,
                "status": vm.status,
                "cpu_usage": float(vm.cpu_usage) if vm.cpu_usage else 0,
                "ram_mb": vm.ram_mb,
                "node_name": vm.node.name,
            }
        )

    return JsonResponse(
        {
            "cluster": {
                "id": cluster.id,
                "name": cluster.name,
                "is_active": cluster.is_active,
            },
            "stats": {
                "node_count": nodes.count(),
                "vm_count": vms.count(),
                "running_vms": vms.filter(status="running").count(),
                "online_nodes": nodes.filter(status="online").count(),
            },
            "nodes": nodes_data,
            "vms": vms_data,
        }
    )


@login_required
def get_dashboard_stats(request):
    """API endpoint to get dashboard stats without page reload"""
    clusters = ProxmoxCluster.objects.filter(is_active=True)
    nodes = Node.objects.all()
    vms = VirtualMachine.objects.all()

    return JsonResponse(
        {
            "stats": {
                "total_vms": vms.count(),
                "running_vms": vms.filter(status="running").count(),
                "stopped_vms": vms.filter(status="stopped").count(),
                "total_nodes": nodes.count(),
                "online_nodes": nodes.filter(status="online").count(),
                "avg_cpu": round(
                    nodes.aggregate(Avg("cpu_usage"))["cpu_usage__avg"] or 0, 2
                ),
                "avg_ram": round(
                    nodes.aggregate(Avg("ram_usage"))["ram_usage__avg"] or 0, 2
                ),
            },
            "clusters": [
                {
                    "id": c.id,
                    "name": c.name,
                    "node_count": c.nodes.count(),
                    "vm_count": VirtualMachine.objects.filter(node__cluster=c).count(),
                }
                for c in clusters
            ],
        }
    )


@login_required
def audit_log(request):
    logs = AuditLog.objects.select_related("user", "vm", "cluster").all()[:100]

    # Add stats for right sidebar
    clusters = ProxmoxCluster.objects.filter(is_active=True)
    nodes = Node.objects.all()
    vms = VirtualMachine.objects.all()

    context = {
        "logs": logs,
        # Stats for right sidebar
        "clusters": clusters,
        "nodes": nodes,
        "vms": vms,
        "total_vms": vms.count(),
        "running_vms": vms.filter(status="running").count(),
        "total_nodes": nodes.count(),
        "online_nodes": nodes.filter(status="online").count(),
        "avg_cpu": round(nodes.aggregate(Avg("cpu_usage"))["cpu_usage__avg"] or 0, 2),
        "avg_ram": round(nodes.aggregate(Avg("ram_usage"))["ram_usage__avg"] or 0, 2),
    }

    return render(request, "proxmox_manager/audit_log.html", context)


@login_required
def node_detail(request, node_id):
    node = get_object_or_404(Node, id=node_id)
    vms = node.virtual_machines.all()

    # Add stats for right sidebar
    clusters = ProxmoxCluster.objects.filter(is_active=True)
    nodes = Node.objects.all()
    all_vms = VirtualMachine.objects.all()

    context = {
        "node": node,
        "vms": vms,
        # Stats for right sidebar
        "clusters": clusters,
        "nodes": nodes,
        "total_vms": all_vms.count(),
        "running_vms": all_vms.filter(status="running").count(),
        "total_nodes": nodes.count(),
        "online_nodes": nodes.filter(status="online").count(),
        "avg_cpu": round(nodes.aggregate(Avg("cpu_usage"))["cpu_usage__avg"] or 0, 2),
        "avg_ram": round(nodes.aggregate(Avg("ram_usage"))["ram_usage__avg"] or 0, 2),
    }

    return render(request, "proxmox_manager/node_detail.html", context)


@login_required
def vm_console(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)

    # Get console connection details from Proxmox
    try:
        proxmox = get_proxmox_connection(vm.node.cluster)
        node_name = vm.node.name

        # Create console ticket
        if vm.vm_type == "qemu":
            console_data = proxmox.nodes(node_name).qemu(vm.vmid).vncproxy.post()
        else:  # lxc
            console_data = proxmox.nodes(node_name).lxc(vm.vmid).vncproxy.post()

        # Get ticket and port for authentication
        vnc_ticket = console_data["ticket"]
        vnc_port = console_data["port"]

        # Get Proxmox host IP/hostname
        proxmox_host = (
            vm.node.cluster.api_url.replace("https://", "")
            .replace(":8006", "")
            .split(":")[0]
        )

        # Create websockify token: vmid_proxmoxhost_vncport
        # This will be used by our custom websockify plugin to create SSH tunnel
        ws_token = f"{vm.vmid}_{proxmox_host}_{vnc_port}"

        context = {
            "vm": vm,
            "vnc_ticket": vnc_ticket,
            "vnc_port": vnc_port,
            "proxmox_host": proxmox_host,
            "ws_token": ws_token,
            "node_name": node_name,
            "vmid": vm.vmid,
            "vm_type": vm.vm_type,
        }

        return render(request, "proxmox_manager/vm_console.html", context)

    except Exception as e:
        messages.error(request, f"Failed to open console: {str(e)}")
        return redirect("vm_detail", vm_id=vm_id)


@login_required
def vm_console_proxy(request, vm_id):
    """Proxy endpoint for noVNC websocket connection"""
    vm = get_object_or_404(VirtualMachine, id=vm_id)

    try:
        proxmox = get_proxmox_connection(vm.node.cluster)
        node_name = vm.node.name

        # Create VNC websocket
        if vm.vm_type == "qemu":
            vncwebsocket = (
                proxmox.nodes(node_name)
                .qemu(vm.vmid)
                .vncwebsocket.get(
                    port=request.GET.get("port"), vncticket=request.GET.get("vncticket")
                )
            )
        else:  # lxc
            vncwebsocket = (
                proxmox.nodes(node_name)
                .lxc(vm.vmid)
                .vncwebsocket.get(
                    port=request.GET.get("port"), vncticket=request.GET.get("vncticket")
                )
            )

        return JsonResponse(vncwebsocket)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
