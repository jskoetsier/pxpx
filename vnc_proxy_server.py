#!/usr/bin/env python3
"""
WebSocket VNC Proxy for Proxmox Console Access
This script creates SSH tunnels from manage.koetsier.it to Proxmox hosts
and proxies VNC connections through websockify for browser-based console access.
"""

import os
import re
import subprocess
import sys
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Add Django settings
sys.path.insert(0, "/opt/pxmx")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pxmx.settings")

import django

django.setup()

from proxmox_manager.models import VirtualMachine

# Track active SSH tunnels
active_tunnels = {}
tunnel_lock = threading.Lock()


def create_ssh_tunnel(proxmox_host, vnc_port, local_port):
    """Create an SSH tunnel from local port to Proxmox VNC port"""
    tunnel_key = f"{proxmox_host}:{vnc_port}"

    with tunnel_lock:
        if tunnel_key in active_tunnels and active_tunnels[tunnel_key].poll() is None:
            print(f"SSH tunnel already exists for {tunnel_key}")
            return True

        try:
            # Create SSH tunnel: ssh -L local_port:localhost:vnc_port root@proxmox_host
            cmd = [
                "ssh",
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "UserKnownHostsFile=/dev/null",
                "-N",
                "-L",
                f"{local_port}:localhost:{vnc_port}",
                f"root@{proxmox_host}",
            ]

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            # Give tunnel time to establish
            time.sleep(1)

            if process.poll() is None:
                active_tunnels[tunnel_key] = process
                print(f"Created SSH tunnel: {tunnel_key} -> localhost:{local_port}")
                return True
            else:
                stderr = process.stderr.read().decode()
                print(f"Failed to create SSH tunnel: {stderr}")
                return False

        except Exception as e:
            print(f"Error creating SSH tunnel: {e}")
            return False


def cleanup_tunnel(proxmox_host, vnc_port):
    """Clean up SSH tunnel"""
    tunnel_key = f"{proxmox_host}:{vnc_port}"

    with tunnel_lock:
        if tunnel_key in active_tunnels:
            process = active_tunnels[tunnel_key]
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            del active_tunnels[tunnel_key]
            print(f"Cleaned up SSH tunnel: {tunnel_key}")


def start_websockify_for_port(proxmox_host, vnc_port, ws_port):
    """Start a websockify instance for a specific VNC port"""
    # First, create SSH tunnel
    local_vnc_port = 5900 + ws_port  # Use unique local port
    if not create_ssh_tunnel(proxmox_host, vnc_port, local_vnc_port):
        return False

    try:
        # Start websockify to proxy WebSocket -> local VNC tunnel
        cmd = ["websockify", f"0.0.0.0:{ws_port}", f"localhost:{local_vnc_port}"]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        time.sleep(1)

        if process.poll() is None:
            print(f"Started websockify on port {ws_port} -> localhost:{local_vnc_port}")
            return True
        else:
            stderr = process.stderr.read().decode()
            print(f"Failed to start websockify: {stderr}")
            cleanup_tunnel(proxmox_host, vnc_port)
            return False

    except Exception as e:
        print(f"Error starting websockify: {e}")
        cleanup_tunnel(proxmox_host, vnc_port)
        return False


if __name__ == "__main__":
    print("VNC WebSocket Proxy Server starting...")
    print("This server will create SSH tunnels to Proxmox hosts as needed")

    # For simplicity, we'll use a single websockify instance with dynamic port mapping
    # Run websockify on port 6080 with SSL
    try:
        subprocess.run(
            [
                "websockify",
                "0.0.0.0:6080",
                "--web=/usr/share/novnc",
                "--cert=/etc/letsencrypt/live/manage.koetsier.it/fullchain.pem",
                "--key=/etc/letsencrypt/live/manage.koetsier.it/privkey.pem",
                "--target-config=/opt/pxmx/vnc-targets.conf",
            ]
        )
    except KeyboardInterrupt:
        print("\nShutting down VNC proxy server...")
        # Clean up all tunnels
        with tunnel_lock:
            for tunnel_key, process in active_tunnels.items():
                if process.poll() is None:
                    process.terminate()
        sys.exit(0)
