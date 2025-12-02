# PXMX - Proxmox Administration Dashboard

A comprehensive Django-based web application for managing multiple Proxmox clusters from a single unified interface. PXMX provides a "Single Pane of Glass" for orchestrating VM migrations, monitoring resource usage, and controlling virtual machines across your Proxmox infrastructure.

![Django](https://img.shields.io/badge/Django-5.0-green) ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple) ![Celery](https://img.shields.io/badge/Celery-5.3-blue)

## Features

### Core Functionality
- **Multi-Cluster Management**: Connect and manage multiple Proxmox clusters from one dashboard
- **Unified VM Control**: Start, stop, reboot, and shutdown VMs across all clusters
- **Live Migration**: Migrate VMs between nodes with online/offline options
- **Resource Monitoring**: Real-time CPU, RAM, and disk usage statistics with 30-second polling
- **Snapshot Management**: Create and manage VM snapshots
- **Audit Logging**: Track all administrative actions with detailed logs
- **Console Access**: Direct links to Proxmox web console with SSH tunnel instructions
- **Automatic Syncing**: Celery Beat scheduler syncs all VMs every 5 minutes

### Dashboard Features
- Aggregate statistics across all clusters with real-time updates
- Node health visualization with live status
- Recent activity feed
- Resource usage graphs
- Load balancing suggestions
- Universal sidebar stats on all pages
- Smooth animations and pulse effects on data updates

## Technology Stack

- **Backend**: Django 5.0.2
- **Frontend**: Bootstrap 5.3.2 with Bootstrap Icons
- **Task Queue**: Celery 5.3.6 with Redis
- **Database**: PostgreSQL (recommended)
- **API Integration**: Proxmoxer 2.0.1

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- Redis 6 or higher
- Proxmox VE 7.x or 8.x clusters

## Quick Start with Podman/Docker Compose

The easiest way to run PXMX is using Podman Compose or Docker Compose:

### Prerequisites for Container Deployment
- Podman and podman-compose OR Docker and docker-compose
- No need for Python, PostgreSQL, or Redis on the host machine

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/pxmx.git
cd pxmx
```

### 2. Start with Podman Compose

```bash
# Using podman-compose (recommended for rootless containers)
podman-compose up -d

# OR using docker-compose
docker-compose up -d
```

This will:
- Build the Django application container
- Start PostgreSQL database
- Start Redis for Celery
- Start Celery worker
- Run migrations automatically
- Create a default admin user (username: `admin`, password: `admin`)
- Collect static files

### 3. Access the Application

Visit http://localhost:8000

- **Login**: admin / admin (change this immediately!)
- **Admin Panel**: http://localhost:8000/admin/

### 4. Stop the Application

```bash
# Using podman-compose
podman-compose down

# OR using docker-compose
docker-compose down

# To remove volumes as well (WARNING: deletes all data)
podman-compose down -v
```

### Container Management

```bash
# View logs
podman-compose logs -f

# View specific service logs
podman-compose logs -f web
podman-compose logs -f celery

# Restart services
podman-compose restart

# Execute commands in containers
podman-compose exec web python manage.py createsuperuser
podman-compose exec web python manage.py sync_proxmox --all
```

---

## Manual Installation (Without Containers)

If you prefer to run PXMX without containers:

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/pxmx.git
cd pxmx
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database

Create a PostgreSQL database:

```bash
sudo -u postgres psql
CREATE DATABASE pxmx_db;
CREATE USER pxmx_user WITH PASSWORD 'your_secure_password';
ALTER ROLE pxmx_user SET client_encoding TO 'utf8';
ALTER ROLE pxmx_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pxmx_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE pxmx_db TO pxmx_user;
\q
```

### 5. Configure Environment Variables

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` and configure:

```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost,127.0.0.1

DATABASE_URL=postgresql://pxmx_user:your_secure_password@localhost:5432/pxmx_db

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

PROXMOX_VERIFY_SSL=False  # Set to True in production with valid SSL certificates
```

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

### 8. Collect Static Files

```bash
python manage.py collectstatic --no-input
```

### 9. Start Redis Server

```bash
# On Ubuntu/Debian
sudo systemctl start redis-server

# On macOS with Homebrew
brew services start redis

# Or run directly
redis-server
```

### 10. Start Celery Worker

In a separate terminal:

```bash
source venv/bin/activate
celery -A pxmx worker --loglevel=info
```

### 11. Start Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000 in your browser.

## Configuration

### Adding Proxmox Clusters

1. Log in to the admin panel: http://localhost:8000/admin/
2. Navigate to "Proxmox Clusters"
3. Click "Add Proxmox Cluster"
4. Fill in the details:
   - **Name**: A friendly name for the cluster
   - **API URL**: The Proxmox API endpoint (e.g., https://192.168.1.100:8006)
   - **Username**: API username (e.g., root@pam or admin@pve)
   - **Password**: API password
   - **Verify SSL**: Enable if using valid SSL certificates
   - **Is Active**: Enable to sync this cluster

### Syncing Cluster Data

#### Via Web Interface
- Click "Sync All" in the sidebar
- Or go to Clusters → Select Cluster → "Sync Now"

#### Via Management Command

```bash
# Sync all active clusters
python manage.py sync_proxmox --all

# Sync specific cluster by ID
python manage.py sync_proxmox --cluster 1
```

#### Automated Sync with Cron

Add to your crontab for automatic syncing every 5 minutes:

```bash
*/5 * * * * /path/to/venv/bin/python /path/to/pxmx/manage.py sync_proxmox --all
```

## Usage Guide

### Dashboard
The main dashboard shows:
- Total VMs and their status (running/stopped)
- Node statistics (online/offline)
- Average CPU and RAM usage
- Recent activity log

### Managing VMs

#### Power Control
1. Navigate to "All VMs"
2. Click on a VM to view details
3. Use power control buttons:
   - **Start**: Boot the VM
   - **Stop**: Force stop the VM
   - **Reboot**: Restart the VM
   - **Shutdown**: Graceful shutdown via guest agent

#### VM Migration
1. Go to VM details
2. Click "Migrate"
3. Select target node
4. Choose migration type:
   - **Live Migration**: VM stays running during migration
   - **Offline Migration**: VM is stopped first
5. Click "Start Migration"

#### Creating Snapshots
1. Go to VM details
2. Click "Create Snapshot"
3. Enter a snapshot name
4. Click "Create Snapshot"

### Monitoring Nodes
- View node details including resource usage
- See all VMs running on each node
- Monitor for load balancing opportunities

## Production Deployment

### Using Gunicorn

```bash
gunicorn --workers 3 --bind 0.0.0.0:8000 pxmx.wsgi:application
```

### Using systemd

Create `/etc/systemd/system/pxmx.service`:

```ini
[Unit]
Description=PXMX Proxmox Dashboard
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/pxmx
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn --workers 3 --bind unix:/path/to/pxmx/pxmx.sock pxmx.wsgi:application

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/pxmx-celery.service`:

```ini
[Unit]
Description=PXMX Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/pxmx
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A pxmx worker --loglevel=info --detach

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable pxmx pxmx-celery
sudo systemctl start pxmx pxmx-celery
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/pxmx/staticfiles/;
    }

    location /media/ {
        alias /path/to/pxmx/media/;
    }

    location / {
        proxy_pass http://unix:/path/to/pxmx/pxmx.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Considerations

1. **SSL/TLS**: Always use HTTPS in production
2. **Firewall**: Restrict access to Proxmox API endpoints
3. **Passwords**: Store Proxmox passwords securely (consider using Django's encryption)
4. **Secret Key**: Use a strong, unique SECRET_KEY
5. **CSRF**: Keep CSRF protection enabled
6. **Permissions**: Set proper file permissions (644 for files, 755 for directories)

## Troubleshooting

### Celery tasks not running
- Ensure Redis is running: `redis-cli ping`
- Check Celery worker logs
- Verify CELERY_BROKER_URL in settings

### Cannot connect to Proxmox
- Check API URL format (include https:// and port :8006)
- Verify credentials
- Check network connectivity to Proxmox nodes
- For self-signed certificates, set verify_ssl=False

### Database connection errors
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database user has proper permissions

## API Compatibility

This application has been tested with:
- Proxmox VE 7.x
- Proxmox VE 8.x

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review Proxmox API documentation: https://pve.proxmox.com/wiki/Proxmox_VE_API

## Acknowledgments

- Built with Django and Bootstrap
- Proxmox integration via proxmoxer
- Icons by Bootstrap Icons

---

**Note**: This is an MVP (Minimum Viable Product). Future enhancements may include:
- Backup management
- Storage management
- Network configuration
- User role-based access control
- Real-time monitoring with WebSockets
- Advanced load balancing algorithms
- Multi-language support
