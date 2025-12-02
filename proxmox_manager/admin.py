from django.contrib import admin

from .models import AuditLog, CeleryTask, Node, ProxmoxCluster, VirtualMachine


@admin.register(ProxmoxCluster)
class ProxmoxClusterAdmin(admin.ModelAdmin):
    list_display = ["name", "api_url", "username", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "api_url"]


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "cluster",
        "status",
        "cpu_usage",
        "ram_usage",
        "disk_usage",
        "last_synced",
    ]
    list_filter = ["cluster", "status"]
    search_fields = ["name", "cluster__name"]


@admin.register(VirtualMachine)
class VirtualMachineAdmin(admin.ModelAdmin):
    list_display = [
        "vmid",
        "name",
        "node",
        "vm_type",
        "status",
        "cpu_cores",
        "ram_mb",
        "last_synced",
    ]
    list_filter = ["vm_type", "status", "node__cluster"]
    search_fields = ["name", "vmid", "node__name"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["action", "user", "vm", "cluster", "status", "created_at"]
    list_filter = ["action", "status", "created_at"]
    search_fields = ["user__username", "vm__name", "details"]
    readonly_fields = ["created_at", "completed_at"]


@admin.register(CeleryTask)
class CeleryTaskAdmin(admin.ModelAdmin):
    list_display = [
        "task_name",
        "state",
        "progress",
        "user",
        "vm",
        "cluster",
        "created_at",
        "execution_time",
    ]
    list_filter = ["state", "task_name", "created_at"]
    search_fields = ["task_id", "task_name", "user__username", "vm__name"]
    readonly_fields = [
        "task_id",
        "created_at",
        "started_at",
        "completed_at",
        "execution_time",
    ]

    def execution_time(self, obj):
        time = obj.execution_time
        return f"{time}s" if time else "N/A"

    execution_time.short_description = "Execution Time"
