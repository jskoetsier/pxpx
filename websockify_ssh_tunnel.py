#!/usr/bin/env python3
"""
WebsockifySSHTunnel - Custom Websockify target plugin
Creates SSH tunnels to Proxmox hosts on-demand
Token format: vmid_proxmox_host_vnc_port
Example: 100_95.216.80.121_5900
"""

import os
import subprocess
import sys
import threading
import time

# Track active SSH tunnels
tunnels = {}
tunnel_lock = threading.Lock()


class WebsockifySSHTunnel:
    """Creates SSH tunnels on-demand for websockify"""

    def __init__(self, token):
        self.token = token
        try:
            # Token format: vmid_proxmox_host_vnc_port
            parts = token.split("_")
            self.vmid = parts[0]
            self.proxmox_host = parts[1]
            self.vnc_port = int(parts[2])

            # Use a consistent local port for this VM
            self.local_port = 15000 + int(self.vmid)

        except Exception as e:
            print(f"Error parsing token {token}: {e}", file=sys.stderr)
            raise ValueError(f"Invalid token format: {token}")

    def create_tunnel(self):
        """Create SSH tunnel to Proxmox host"""
        tunnel_key = f"{self.proxmox_host}:{self.vnc_port}"

        with tunnel_lock:
            # Check if tunnel already exists
            if tunnel_key in tunnels:
                proc = tunnels[tunnel_key]
                if proc.poll() is None:
                    print(
                        f"SSH tunnel already exists for {tunnel_key}", file=sys.stderr
                    )
                    return self.local_port

            # Create new SSH tunnel
            cmd = [
                "ssh",
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "UserKnownHostsFile=/dev/null",
                "-o",
                "ExitOnForwardFailure=yes",
                "-N",
                "-L",
                f"{self.local_port}:localhost:{self.vnc_port}",
                f"root@{self.proxmox_host}",
            ]

            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                )

                # Wait a bit for tunnel to establish
                time.sleep(0.5)

                if proc.poll() is None:
                    tunnels[tunnel_key] = proc
                    print(
                        f"Created SSH tunnel: {tunnel_key} -> localhost:{self.local_port}",
                        file=sys.stderr,
                    )
                    return self.local_port
                else:
                    stderr = proc.stderr.read().decode() if proc.stderr else ""
                    print(f"Failed to create SSH tunnel: {stderr}", file=sys.stderr)
                    raise Exception(f"SSH tunnel failed: {stderr}")

            except Exception as e:
                print(f"Error creating SSH tunnel: {e}", file=sys.stderr)
                raise

    def get_target(self):
        """Return target for websockify (localhost:local_port)"""
        local_port = self.create_tunnel()
        return f"localhost:{local_port}"


def get_target(token):
    """Main entry point for websockify token plugin"""
    try:
        tunnel = WebsockifySSHTunnel(token)
        target = tunnel.get_target()
        print(f"Token {token} -> {target}", file=sys.stderr)
        return target
    except Exception as e:
        print(f"Error getting target for token {token}: {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    # Test the module
    if len(sys.argv) > 1:
        token = sys.argv[1]
        target = get_target(token)
        if target:
            print(f"Target: {target}")
        else:
            print("Failed to get target")
            sys.exit(1)
    else:
        print("Usage: websockify_ssh_tunnel.py <token>")
        sys.exit(1)
