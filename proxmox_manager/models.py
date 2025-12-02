from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models
from django.utils import timezone


class ProxmoxCluster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    api_url = models.URLField(
        help_text="Proxmox API URL (e.g., https://192.168.1.100:8006)"
    )
    username = models.CharField(
        max_length=100, help_text="API username (e.g., root@pam)"
    )
    password = models.CharField(max_length=255)
    verify_ssl = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proxmox Cluster"
        verbose_name_plural = "Proxmox Clusters"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Node(models.Model):
    STATUS_CHOICES = [
        ("online", "Online"),
        ("offline", "Offline"),
        ("unknown", "Unknown"),
    ]

    cluster = models.ForeignKey(
        ProxmoxCluster, on_delete=models.CASCADE, related_name="nodes"
    )
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unknown")
    cpu_usage = models.FloatField(default=0.0, help_text="CPU usage percentage (0-100)")
    ram_usage = models.FloatField(default=0.0, help_text="RAM usage percentage (0-100)")
    ram_total = models.BigIntegerField(default=0, help_text="Total RAM in bytes")
    ram_used = models.BigIntegerField(default=0, help_text="Used RAM in bytes")
    disk_usage = models.FloatField(
        default=0.0, help_text="Disk usage percentage (0-100)"
    )
    disk_total = models.BigIntegerField(default=0, help_text="Total disk in bytes")
    disk_used = models.BigIntegerField(default=0, help_text="Used disk in bytes")
    uptime = models.BigIntegerField(default=0, help_text="Uptime in seconds")
    last_synced = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Node"
        verbose_name_plural = "Nodes"
        unique_together = ["cluster", "name"]
        ordering = ["cluster", "name"]

    def __str__(self):
        return f"{self.cluster.name} - {self.name}"

    @property
    def ram_usage_gb(self):
        return round(self.ram_used / (1024**3), 2)

    @property
    def ram_total_gb(self):
        return round(self.ram_total / (1024**3), 2)

    @property
    def disk_usage_gb(self):
        return round(self.disk_used / (1024**3), 2)

    @property
    def disk_total_gb(self):
        return round(self.disk_total / (1024**3), 2)


class VirtualMachine(models.Model):
    TYPE_CHOICES = [
        ("qemu", "VM"),
        ("lxc", "Container"),
    ]

    STATUS_CHOICES = [
        ("running", "Running"),
        ("stopped", "Stopped"),
        ("paused", "Paused"),
        ("unknown", "Unknown"),
    ]

    node = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name="virtual_machines"
    )
    vmid = models.IntegerField()
    name = models.CharField(max_length=100)
    vm_type = models.CharField(choices=TYPE_CHOICES, max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unknown")
    cpu_cores = models.IntegerField(default=1)
    ram_mb = models.IntegerField(default=512, help_text="RAM in MB")
    disk_gb = models.FloatField(default=0.0, help_text="Disk size in GB")
    cpu_usage = models.FloatField(default=0.0, help_text="CPU usage percentage")
    ram_usage = models.FloatField(default=0.0, help_text="RAM usage percentage")
    uptime = models.BigIntegerField(default=0, help_text="Uptime in seconds")
    last_synced = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Virtual Machine"
        verbose_name_plural = "Virtual Machines"
        unique_together = ["node", "vmid"]
        ordering = ["node", "vmid"]

    def __str__(self):
        return f"{self.name} (ID: {self.vmid})"

    @property
    def cluster(self):
        return self.node.cluster


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("start", "Start VM"),
        ("stop", "Stop VM"),
        ("reboot", "Reboot VM"),
        ("shutdown", "Shutdown VM"),
        ("migrate", "Migrate VM"),
        ("snapshot", "Create Snapshot"),
        ("rollback", "Rollback Snapshot"),
        ("sync", "Sync Data"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    vm = models.ForeignKey(
        VirtualMachine, on_delete=models.SET_NULL, null=True, blank=True
    )
    cluster = models.ForeignKey(
        ProxmoxCluster, on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    details = models.TextField(blank=True)
    task_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} - {self.status} ({self.created_at})"


class CeleryTask(models.Model):
    TASK_STATE_CHOICES = [
        ("PENDING", "Pending"),
        ("STARTED", "Started"),
        ("SUCCESS", "Success"),
        ("FAILURE", "Failure"),
        ("RETRY", "Retry"),
        ("REVOKED", "Revoked"),
    ]

    task_id = models.CharField(max_length=255, unique=True, db_index=True)
    task_name = models.CharField(max_length=255, db_index=True)
    state = models.CharField(
        max_length=50, choices=TASK_STATE_CHOICES, default="PENDING", db_index=True
    )
    result = models.TextField(blank=True, null=True)
    traceback = models.TextField(blank=True, null=True)
    progress = models.IntegerField(default=0, help_text="Progress percentage (0-100)")
    progress_message = models.CharField(max_length=255, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    vm = models.ForeignKey(
        VirtualMachine, on_delete=models.SET_NULL, null=True, blank=True
    )
    cluster = models.ForeignKey(
        ProxmoxCluster, on_delete=models.SET_NULL, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Celery Task"
        verbose_name_plural = "Celery Tasks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at", "state"]),
            models.Index(fields=["task_name", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.task_name} - {self.state} ({self.created_at})"

    @property
    def execution_time(self):
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return round(delta.total_seconds(), 2)
        return None

    @property
    def is_running(self):
        return self.state in ["PENDING", "STARTED", "RETRY"]

    @property
    def is_completed(self):
        return self.state in ["SUCCESS", "FAILURE", "REVOKED"]
