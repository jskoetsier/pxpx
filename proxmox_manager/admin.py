from django.contrib import admin

from .models import AuditLog, Node, ProxmoxCluster, VirtualMachine


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
