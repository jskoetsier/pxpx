from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("vms/", views.vm_list, name="vm_list"),
    path("vms/<int:vm_id>/", views.vm_detail, name="vm_detail"),
    path("vms/<int:vm_id>/console/", views.vm_console, name="vm_console"),
    path(
        "vms/<int:vm_id>/console/proxy/",
        views.vm_console_proxy,
        name="vm_console_proxy",
    ),
    path(
        "vms/<int:vm_id>/power/<str:action>/",
        views.vm_power_control,
        name="vm_power_control",
    ),
    path("vms/<int:vm_id>/migrate/", views.migrate_vm, name="migrate_vm"),
    path(
        "vms/<int:vm_id>/snapshot/", views.create_vm_snapshot, name="create_vm_snapshot"
    ),
    path("clusters/", views.cluster_list, name="cluster_list"),
    path("clusters/<int:cluster_id>/", views.cluster_detail, name="cluster_detail"),
    path("clusters/<int:cluster_id>/sync/", views.sync_cluster, name="sync_cluster"),
    path("clusters/sync-all/", views.sync_all_clusters, name="sync_all_clusters"),
    path("nodes/<int:node_id>/", views.node_detail, name="node_detail"),
    path("audit-log/", views.audit_log, name="audit_log"),
    # API endpoints for real-time updates
    path("api/dashboard/stats/", views.get_dashboard_stats, name="api_dashboard_stats"),
    path(
        "api/cluster/<int:cluster_id>/stats/",
        views.get_cluster_stats,
        name="api_cluster_stats",
    ),
]
