from django.core.management.base import BaseCommand
from proxmox_manager.models import ProxmoxCluster
from proxmox_manager.tasks import sync_cluster_data


class Command(BaseCommand):
    help = "Sync data from Proxmox clusters"

    def add_arguments(self, parser):
        parser.add_argument(
            "--cluster",
            type=int,
            help="Sync specific cluster by ID",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Sync all active clusters",
        )

    def handle(self, *args, **options):
        if options["cluster"]:
            try:
                cluster = ProxmoxCluster.objects.get(id=options["cluster"])
                self.stdout.write(f"Syncing cluster: {cluster.name}")
                result = sync_cluster_data.delay(cluster.id)
                self.stdout.write(
                    self.style.SUCCESS(f"Sync task initiated: {result.id}")
                )
            except ProxmoxCluster.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Cluster with ID {options["cluster"]} not found')
                )

        elif options["all"]:
            clusters = ProxmoxCluster.objects.filter(is_active=True)
            self.stdout.write(f"Syncing {clusters.count()} active clusters")

            for cluster in clusters:
                self.stdout.write(f"  - {cluster.name}")
                sync_cluster_data.delay(cluster.id)

            self.stdout.write(self.style.SUCCESS("All sync tasks initiated"))

        else:
            self.stdout.write(self.style.ERROR("Please specify --cluster ID or --all"))
            self.stdout.write("Usage: python manage.py sync_proxmox --all")
            self.stdout.write("   or: python manage.py sync_proxmox --cluster 1")
