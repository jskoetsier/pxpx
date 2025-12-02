"""
Django management command to start the VNC websockify proxy server.
This server tunnels VNC connections from the web browser to Proxmox VMs via SSH.
"""

import subprocess
import sys

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Start websockify VNC proxy server for console access"

    def add_arguments(self, parser):
        parser.add_argument(
            "--host",
            type=str,
            default="0.0.0.0",
            help="Host to bind websockify server (default: 0.0.0.0)",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=6080,
            help="Port for websockify server (default: 6080)",
        )

    def handle(self, *args, **options):
        host = options["host"]
        port = options["port"]

        self.stdout.write(
            self.style.SUCCESS(f"Starting websockify VNC proxy server on {host}:{port}")
        )

        # Start websockify server
        # It will handle connections on port 6080 and forward them via SSH tunnels
        try:
            subprocess.run(
                [
                    "websockify",
                    f"{host}:{port}",
                    "--web=/usr/share/novnc",
                    "--ssl-only",
                    "--cert=/etc/letsencrypt/live/manage.koetsier.it/fullchain.pem",
                    "--key=/etc/letsencrypt/live/manage.koetsier.it/privkey.pem",
                ],
                check=True,
            )
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nShutting down VNC proxy server"))
            sys.exit(0)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error starting VNC proxy: {e}"))
            sys.exit(1)
