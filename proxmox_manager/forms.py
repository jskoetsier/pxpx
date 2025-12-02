from django import forms

from .models import Node, ProxmoxCluster, VirtualMachine


class ProxmoxClusterForm(forms.ModelForm):
    class Meta:
        model = ProxmoxCluster
        fields = ["name", "api_url", "username", "password", "verify_ssl", "is_active"]
        widgets = {
            "password": forms.PasswordInput(),
            "api_url": forms.URLInput(
                attrs={"placeholder": "https://192.168.1.100:8006"}
            ),
            "username": forms.TextInput(attrs={"placeholder": "root@pam"}),
        }


class MigrationForm(forms.Form):
    target_node = forms.ModelChoiceField(
        queryset=Node.objects.none(),
        label="Target Node",
        help_text="Select the node to migrate the VM to",
    )
    online = forms.BooleanField(
        initial=True,
        required=False,
        label="Live Migration",
        help_text="Perform online/live migration (VM stays running)",
    )

    def __init__(self, *args, **kwargs):
        vm = kwargs.pop("vm", None)
        super().__init__(*args, **kwargs)

        if vm:
            self.fields["target_node"].queryset = Node.objects.filter(
                cluster=vm.node.cluster, status="online"
            ).exclude(id=vm.node.id)


class SnapshotForm(forms.Form):
    snapshot_name = forms.CharField(
        max_length=100,
        label="Snapshot Name",
        help_text="Enter a name for the snapshot",
        widget=forms.TextInput(attrs={"placeholder": "snapshot-name"}),
    )


class VMSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={"placeholder": "Search VMs by name or ID..."}),
    )
    cluster = forms.ModelChoiceField(
        queryset=ProxmoxCluster.objects.filter(is_active=True),
        required=False,
        label="Cluster",
    )
    status = forms.ChoiceField(
        choices=[("", "All")] + VirtualMachine.STATUS_CHOICES,
        required=False,
        label="Status",
    )
    vm_type = forms.ChoiceField(
        choices=[("", "All")] + VirtualMachine.TYPE_CHOICES,
        required=False,
        label="Type",
    )
