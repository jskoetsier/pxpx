#!/bin/bash
# NoVNC Console Deployment Script
# This script deploys the NoVNC console feature to manage.koetsier.it

set -e

echo "🚀 Deploying NoVNC Console Feature"
echo "===================================="

# Commit all changes
echo "📦 Committing changes to git..."
git add .
git commit -m "Add embedded NoVNC console with SSH tunneling

- Created websockify_ssh_tunnel.py plugin for dynamic SSH tunnels
- Updated vm_console view to generate websockify tokens
- Created modern NoVNC console template with embedded viewer
- Token format: vmid_proxmoxhost_vncport for automatic tunnel creation
- Uses wss://manage.koetsier.it:6080 for websockify proxy
- Full-screen support and clean disconnect handling"

git push origin main

echo "✅ Changes committed and pushed"

# Deploy to remote server
echo ""
echo "🌐 Deploying to manage.koetsier.it..."

ssh root@manage.koetsier.it bash <<'ENDSSH'
set -e

cd /opt/pxmx

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Make websockify plugin executable
chmod +x websockify_ssh_tunnel.py

# Create systemd service for websockify
echo "⚙️  Creating websockify systemd service..."
cat > /etc/systemd/system/pxmx-websockify.service << 'EOF'
[Unit]
Description=PXMX Websockify VNC Proxy
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/pxmx
Environment=PYTHONPATH=/opt/pxmx
ExecStart=/usr/bin/websockify --web=/usr/share/novnc --cert=/etc/letsencrypt/live/manage.koetsier.it/fullchain.pem --key=/etc/letsencrypt/live/manage.koetsier.it/privkey.pem --token-plugin=/opt/pxmx/websockify_ssh_tunnel.py --token-source=WebsockifySSHTunnel 0.0.0.0:6080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
systemctl daemon-reload
systemctl enable pxmx-websockify
systemctl restart pxmx-websockify

# Update nginx to allow WebSocket connections on port 6080
echo "🔧 Updating nginx configuration..."
cat > /etc/nginx/sites-available/websockify << 'EOF2'
# WebSocket proxy for NoVNC
server {
    listen 6080 ssl;
    server_name manage.koetsier.it;

    ssl_certificate /etc/letsencrypt/live/manage.koetsier.it/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/manage.koetsier.it/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://127.0.0.1:6080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket timeouts
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
EOF2

ln -sf /etc/nginx/sites-available/websockify /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Restart web containers to pick up new code
cd /opt/pxmx
podman-compose restart web

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Service Status:"
systemctl status pxmx-websockify --no-pager | head -15

echo ""
echo "🎉 NoVNC Console is now available!"
echo "Visit: https://manage.koetsier.it and open any VM console"

ENDSSH

echo ""
echo "🎊 Deployment successful!"
echo "Test the console by visiting a VM and clicking 'Open Console'"
