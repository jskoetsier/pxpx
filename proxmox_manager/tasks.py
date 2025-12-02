import logging

from celery import shared_task
from django.utils import timezone
from proxmoxer import ProxmoxAPI

from .models import AuditLog, Node, ProxmoxCluster, VirtualMachine

logger = logging.getLogger(__name__)


def get_proxmox_connection(cluster):
    return ProxmoxAPI(
        cluster.api_url.replace("https://", "").replace("http://", "").split(":")[0],
        user=cluster.username,
        password=cluster.password,
        verify_ssl=cluster.verify_ssl,
    )


@shared_task
def sync_cluster_data(cluster_id):
    try:
        cluster = ProxmoxCluster.objects.get(id=cluster_id)
        prox = get_proxmox_connection(cluster)

        nodes_data = prox.nodes.get()

        for node_data in nodes_data:
            node_name = node_data["node"]
            node_status_data = prox.nodes(node_name).status.get()

            cpu_usage = node_status_data.get("cpu", 0) * 100
            ram_total = node_status_data.get("memory", {}).get("total", 0)
            ram_used = node_status_data.get("memory", {}).get("used", 0)
            ram_usage = (ram_used / ram_total * 100) if ram_total > 0 else 0

            disk_total = node_status_data.get("rootfs", {}).get("total", 0)
            disk_used = node_status_data.get("rootfs", {}).get("used", 0)
            disk_usage = (disk_used / disk_total * 100) if disk_total > 0 else 0

            node, created = Node.objects.update_or_create(
                cluster=cluster,
                name=node_name,
                defaults={
                    "status": (
                        "online" if node_data.get("status") == "online" else "offline"
                    ),
                    "cpu_usage": round(cpu_usage, 2),
                    "ram_usage": round(ram_usage, 2),
                    "ram_total": ram_total,
                    "ram_used": ram_used,
                    "disk_usage": round(disk_usage, 2),
                    "disk_total": disk_total,
                    "disk_used": disk_used,
                    "uptime": node_status_data.get("uptime", 0),
                    "last_synced": timezone.now(),
                },
            )

            sync_vms_for_node.delay(node.id)

        return f"Successfully synced cluster {cluster.name}"

    except Exception as e:
        logger.error(f"Error syncing cluster {cluster_id}: {str(e)}")
        return f"Error syncing cluster: {str(e)}"


@shared_task
def sync_vms_for_node(node_id):
    try:
        node = Node.objects.get(id=node_id)
        cluster = node.cluster
        prox = get_proxmox_connection(cluster)

        vms_data = prox.nodes(node.name).qemu.get()

        for vm_data in vms_data:
            vmid = vm_data["vmid"]

            try:
                vm_config = prox.nodes(node.name).qemu(vmid).config.get()
                vm_status = prox.nodes(node.name).qemu(vmid).status.current.get()

                # Calculate disk size from config
                disk_gb = 0
                # Check for virtio disks (virtio0, virtio1, etc.)
                for key, value in vm_config.items():
                    if key.startswith(('virtio', 'scsi', 'sata', 'ide')):
                        # Parse disk size from string like "local:100/vm-100-disk-0.qcow2,size=32G"
                        if isinstance(value, str) and 'size=' in value:
                            size_part = value.split('size=')[1].split(',')[0]
                            if 'G' in size_part:
                                disk_gb += float(size_part.replace('G', ''))
                            elif 'T' in size_part:
                                disk_gb += float(size_part.replace('T', '')) * 1024
                            elif 'M' in size_part:
                                disk_gb += float(size_part.replace('M', '')) / 1024

                VirtualMachine.objects.update_or_create(
                    node=node,
                    vmid=vmid,
                    defaults={
                        "name": vm_data.get("name", f"VM-{vmid}"),
                        "vm_type": "qemu",
                        "status": vm_data.get("status", "unknown"),
                        "cpu_cores": vm_config.get("cores", 1),
                        "ram_mb": vm_config.get("memory", 512),
                        "disk_gb": round(disk_gb, 2),
                        "cpu_usage": round(vm_status.get("cpu", 0) * 100, 2),
                        "uptime": vm_status.get("uptime", 0),
                        "last_synced": timezone.now(),
                    },
                )
            except Exception as e:
                logger.warning(f"Error syncing VM {vmid} on node {node.name}: {str(e)}")
                continue

        lxc_data = prox.nodes(node.name).lxc.get()

        for container_data in lxc_data:
            vmid = container_data["vmid"]

            try:
                container_config = prox.nodes(node.name).lxc(vmid).config.get()
                container_status = prox.nodes(node.name).lxc(vmid).status.current.get()

                # Calculate disk size from config
                disk_gb = 0
                # LXC containers use rootfs
                rootfs = container_config.get('rootfs', '')
                if isinstance(rootfs, str) and 'size=' in rootfs:
                    size_part = rootfs.split('size=')[1].split(',')[0]
                    if 'G' in size_part:
                        disk_gb = float(size_part.replace('G', ''))
                    elif 'T' in size_part:
                        disk_gb = float(size_part.replace('T', '')) * 1024
                    elif 'M' in size_part:
                        disk_gb = float(size_part.replace('M', '')) / 1024

                VirtualMachine.objects.update_or_create(
                    node=node,
                    vmid=vmid,
                    defaults={
                        "name": container_data.get("name", f"CT-{vmid}"),
                        "vm_type": "lxc",
                        "status": container_data.get("status", "unknown"),
                        "cpu_cores": container_config.get("cores", 1),
                        "ram_mb": container_config.get("memory", 512),
                        "disk_gb": round(disk_gb, 2),
                        "cpu_usage": round(container_status.get("cpu", 0) * 100, 2),
                        "uptime": container_status.get("uptime", 0),
                        "last_synced": timezone.now(),
                    },
                )
            except Exception as e:
                logger.warning(
                    f"Error syncing container {vmid} on node {node.name}: {str(e)}"
                )
                continue

        return f"Successfully synced VMs for node {node.name}"

    except Exception as e:
        logger.error(f"Error syncing VMs for node {node_id}: {str(e)}")
        return f"Error syncing VMs: {str(e)}"


@shared_task
def migrate_vm_task(vm_id, target_node_id, user_id, online=True):
    log_entry = None
    try:
        vm = VirtualMachine.objects.get(id=vm_id)
        target_node = Node.objects.get(id=target_node_id)
        source_node = vm.node
        cluster = vm.node.cluster

        if source_node.cluster != target_node.cluster:
            raise ValueError("Cannot migrate VM to a node in a different cluster")

        log_entry = AuditLog.objects.create(
            user_id=user_id,
            action="migrate",
            vm=vm,
            cluster=cluster,
            status="pending",
            details=f"Migrating VM {vm.vmid} from {source_node.name} to {target_node.name}",
        )

        prox = get_proxmox_connection(cluster)

        if vm.vm_type == "qemu":
            task_id = (
                prox.nodes(source_node.name)
                .qemu(vm.vmid)
                .migrate.post(target=target_node.name, online=1 if online else 0)
            )
        else:
            task_id = (
                prox.nodes(source_node.name)
                .lxc(vm.vmid)
                .migrate.post(target=target_node.name, online=1 if online else 0)
            )

        log_entry.task_id = task_id
        log_entry.save()

        vm.node = target_node
        vm.save()

        log_entry.status = "success"
        log_entry.completed_at = timezone.now()
        log_entry.details += f"\nMigration completed successfully. Task ID: {task_id}"
        log_entry.save()

        return f"Migration of VM {vm.vmid} to {target_node.name} initiated. Task: {task_id}"

    except Exception as e:
        logger.error(f"Error migrating VM {vm_id}: {str(e)}")
        if log_entry:
            log_entry.status = "failed"
            log_entry.completed_at = timezone.now()
            log_entry.details += f"\nMigration failed: {str(e)}"
            log_entry.save()
        return f"Migration Failed: {str(e)}"


@shared_task
def vm_power_action(vm_id, action, user_id):
    log_entry = None
    try:
        vm = VirtualMachine.objects.get(id=vm_id)
        cluster = vm.node.cluster

        log_entry = AuditLog.objects.create(
            user_id=user_id,
            action=action,
            vm=vm,
            cluster=cluster,
            status="pending",
            details=f"Executing {action} on VM {vm.vmid}",
        )

        prox = get_proxmox_connection(cluster)

        if vm.vm_type == "qemu":
            vm_handler = prox.nodes(vm.node.name).qemu(vm.vmid).status
        else:
            vm_handler = prox.nodes(vm.node.name).lxc(vm.vmid).status

        if action == "start":
            task_id = vm_handler.start.post()
            vm.status = "running"
        elif action == "stop":
            task_id = vm_handler.stop.post()
            vm.status = "stopped"
        elif action == "reboot":
            task_id = vm_handler.reboot.post()
        elif action == "shutdown":
            task_id = vm_handler.shutdown.post()
            vm.status = "stopped"
        else:
            raise ValueError(f"Unknown action: {action}")

        vm.save()

        log_entry.task_id = task_id
        log_entry.status = "success"
        log_entry.completed_at = timezone.now()
        log_entry.details += (
            f"\n{action.capitalize()} completed successfully. Task ID: {task_id}"
        )
        log_entry.save()

        return (
            f"{action.capitalize()} action on VM {vm.vmid} completed. Task: {task_id}"
        )

    except Exception as e:
        logger.error(f"Error executing {action} on VM {vm_id}: {str(e)}")
        if log_entry:
            log_entry.status = "failed"
            log_entry.completed_at = timezone.now()
            log_entry.details += f"\n{action.capitalize()} failed: {str(e)}"
            log_entry.save()
        return f"{action.capitalize()} Failed: {str(e)}"


@shared_task
def create_snapshot(vm_id, snapshot_name, user_id):
    log_entry = None
    try:
        vm = VirtualMachine.objects.get(id=vm_id)
        cluster = vm.node.cluster

        log_entry = AuditLog.objects.create(
            user_id=user_id,
            action="snapshot",
            vm=vm,
            cluster=cluster,
            status="pending",
            details=f"Creating snapshot '{snapshot_name}' for VM {vm.vmid}",
        )

        prox = get_proxmox_connection(cluster)

        if vm.vm_type == "qemu":
            task_id = (
                prox.nodes(vm.node.name)
                .qemu(vm.vmid)
                .snapshot.post(snapname=snapshot_name)
            )
        else:
            task_id = (
                prox.nodes(vm.node.name)
                .lxc(vm.vmid)
                .snapshot.post(snapname=snapshot_name)
            )

        log_entry.task_id = task_id
        log_entry.status = "success"
        log_entry.completed_at = timezone.now()
        log_entry.details += f"\nSnapshot created successfully. Task ID: {task_id}"
        log_entry.save()

        return f"Snapshot '{snapshot_name}' created for VM {vm.vmid}. Task: {task_id}"

    except Exception as e:
        logger.error(f"Error creating snapshot for VM {vm_id}: {str(e)}")
        if log_entry:
            log_entry.status = "failed"
            log_entry.completed_at = timezone.now()
            log_entry.details += f"\nSnapshot creation failed: {str(e)}"
            log_entry.save()
        return f"Snapshot creation failed: {str(e)}"
