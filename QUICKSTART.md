# Quick Start Guide - Podman Compose

This guide will help you get PXMX up and running using Podman Compose in just a few minutes.

## Prerequisites

Install Podman and podman-compose:

### Fedora/RHEL/CentOS
```bash
sudo dnf install podman podman-compose
```

### Ubuntu/Debian
```bash
sudo apt install podman
pip3 install podman-compose
```

### macOS
```bash
brew install podman podman-compose
```

## Quick Start

### 1. Clone and Navigate

```bash
git clone https://github.com/yourusername/pxmx.git
cd pxmx
```

### 2. Start Everything

```bash
make up
# OR
podman-compose up -d
```

This single command will:
- ✅ Build the Django application container
- ✅ Start PostgreSQL database
- ✅ Start Redis cache
- ✅ Start Celery worker for background tasks
- ✅ Run all database migrations
- ✅ Create default admin user (username: `admin`, password: `admin`)
- ✅ Collect static files

### 3. Access the Application

Open your browser and go to:

🌐 **http://localhost:8000**

**Login Credentials:**
- Username: `admin`
- Password: `admin`

⚠️ **IMPORTANT:** Change the default password immediately after first login!

## Next Steps

### 1. Add Your First Proxmox Cluster

1. Log in at http://localhost:8000
2. Click "Settings" in the sidebar (goes to admin panel)
3. Click "Proxmox Clusters"
4. Click "Add Proxmox Cluster"
5. Fill in:
   - **Name**: e.g., "Production Cluster"
   - **API URL**: e.g., `https://192.168.1.100:8006`
   - **Username**: e.g., `root@pam`
   - **Password**: Your Proxmox password
   - **Verify SSL**: Uncheck if using self-signed certificates
   - **Is Active**: Check this box
6. Click "Save"

### 2. Sync Your Cluster Data

Option A - Via Web Interface:
- Click "Sync All" in the sidebar

Option B - Via Command Line:
```bash
make sync
# OR
podman-compose exec web python manage.py sync_proxmox --all
```

### 3. Start Managing VMs

- View all VMs: Click "All VMs" in sidebar
- Manage specific VM: Click on any VM to see details
- Migrate VM: Click "Migrate" button on VM details page
- Control power: Use Start/Stop/Reboot buttons

## Common Commands

### Using Make (Recommended)

```bash
# View all available commands
make help

# Start services
make up

# Stop services
make down

# View logs
make logs

# View specific service logs
make logs-web
make logs-celery

# Restart all services
make restart

# Open Django shell
make shell

# Open bash in container
make bash

# Sync Proxmox data
make sync

# Create additional superuser
make createsuperuser

# Complete cleanup (removes all data)
make clean
```

### Using Podman Compose Directly

```bash
# Start
podman-compose up -d

# Stop
podman-compose down

# View logs
podman-compose logs -f

# Execute commands
podman-compose exec web python manage.py sync_proxmox --all
podman-compose exec web python manage.py createsuperuser

# Rebuild after code changes
podman-compose up -d --build
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, edit `docker-compose.yml`:

```yaml
web:
  ports:
    - "8080:8000"  # Change 8000 to 8080 (or any free port)
```

Then access at http://localhost:8080

### Container Won't Start

Check logs:
```bash
make logs
# OR
podman-compose logs
```

### Database Connection Issues

Reset everything:
```bash
make clean  # Warning: This deletes all data!
make up
```

### Cannot Connect to Proxmox

1. Verify Proxmox is accessible from your host:
   ```bash
   curl -k https://YOUR_PROXMOX_IP:8006
   ```

2. Check network connectivity from container:
   ```bash
   podman-compose exec web ping YOUR_PROXMOX_IP
   ```

3. If using self-signed certificates, ensure "Verify SSL" is unchecked

## Production Deployment

For production, update `docker-compose.yml`:

1. Change SECRET_KEY to a strong random value
2. Set DEBUG=False
3. Update ALLOWED_HOSTS with your domain
4. Change default admin password
5. Consider using environment file instead of hardcoded values

Create `.env.prod`:
```bash
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Then modify docker-compose.yml to use `env_file: .env.prod`

## Data Persistence

All data is stored in Docker/Podman volumes:
- `postgres_data`: Database
- `static_volume`: Static files
- `media_volume`: Uploaded files

These persist even when containers are stopped.

To backup:
```bash
# Backup database
podman-compose exec db pg_dump -U pxmx_user pxmx_db > backup.sql

# Restore database
cat backup.sql | podman-compose exec -T db psql -U pxmx_user pxmx_db
```

## Switching to Docker

If you prefer Docker Compose over Podman:

```bash
# Use make with Docker
make COMPOSE=docker-compose up

# Or use docker-compose directly
docker-compose up -d
```

## Need Help?

- Check the main README.md for detailed documentation
- View logs: `make logs`
- Open an issue on GitHub
- Check Proxmox connectivity and credentials

---

**You're all set!** 🎉

Start by adding your Proxmox cluster and syncing the data. Happy managing!
