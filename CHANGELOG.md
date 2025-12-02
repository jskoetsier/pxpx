# Changelog

All notable changes to PXMX - Proxmox Administration Dashboard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-02

### 🎉 Initial Release

This is the first production-ready release of PXMX, a modern Django-based administration dashboard for Proxmox Virtual Environment.

### ✨ Added

#### Core Features
- **Multi-Cluster Management**: Connect and manage multiple Proxmox clusters from a single dashboard
- **Virtual Machine Control**: Start, stop, reboot, and shutdown VMs with one click
- **Live Migration**: Migrate VMs between nodes with online/offline migration options
- **Snapshot Management**: Create and manage VM snapshots with custom naming
- **Resource Monitoring**: Real-time CPU, RAM, and disk usage tracking for nodes and VMs
- **Audit Logging**: Complete activity log for all cluster operations and VM actions

#### User Interface
- **Modern Glassmorphism Design**: Beautiful gradient cards with backdrop blur effects
- **Responsive Layout**: Grid-based design that works on all screen sizes
- **Animated Progress Bars**: Visual CPU, RAM, and disk usage indicators with smooth animations
- **Color-Coded Status Badges**: Instant visual feedback with pulsing animations
- **Empty States**: Helpful guidance when no data is available
- **Breadcrumb Navigation**: Clear location indicators on all pages

#### Real-Time Features
- **Background Polling**: Automatic dashboard updates every 30 seconds
- **AJAX Sync**: Sync data without page reloads
- **Toast Notifications**: Beautiful gradient notifications for all actions
- **Live Stats Updates**: Dashboard stats refresh automatically during sync
- **Pulse Animations**: Values pulse when updated
- **Fast Sync Polling**: 2-second updates during active sync operations

#### Dashboard Pages
1. **Main Dashboard**: Kanban-style board with cluster overview, VM statistics, and recent activity
2. **Cluster List**: Grid view of all clusters with stats and quick actions
3. **Cluster Detail**: Complete cluster view with nodes, VMs, and resource usage
4. **Node Detail**: Individual node statistics with VM list and resource graphs
5. **VM List**: Filterable, searchable list of all VMs with inline actions
6. **VM Detail**: Complete VM information with power controls and migration options
7. **VM Migration**: Wizard-style migration interface with visual node selection
8. **Snapshot Creation**: Simple form for creating VM snapshots
9. **Audit Log**: Timeline-style log of all cluster activities

#### Technical Features
- **Celery Integration**: Asynchronous task processing for all Proxmox operations
- **Docker Support**: Complete Docker Compose setup for easy deployment
- **Redis Backend**: Fast caching and message queue
- **PostgreSQL Database**: Reliable data storage
- **API Endpoints**: RESTful endpoints for dashboard and cluster statistics
- **Security**: Login required for all operations, CSRF protection enabled

### 🔧 Infrastructure

#### Deployment
- **Docker Compose**: Complete containerized deployment
- **Nginx**: Reverse proxy configuration included
- **Static Files**: Properly served via Django whitenoise
- **Environment Variables**: Secure configuration management
- **Remote Deploy Script**: One-command deployment to production server

#### Database
- **Automatic Migrations**: Database schema auto-updates on deployment
- **Model Relationships**: Properly defined foreign keys and relationships
- **Efficient Queries**: Optimized with select_related and prefetch_related

#### Background Tasks
- **Cluster Sync**: Automatic synchronization of cluster data from Proxmox API
- **VM Power Actions**: Asynchronous start/stop/reboot/shutdown operations
- **VM Migration**: Background migration tasks with progress tracking
- **Snapshot Creation**: Non-blocking snapshot operations

### 📊 Monitoring & Observability

- **Celery Beat**: Scheduled periodic sync tasks
- **Task Tracking**: All Celery tasks logged to database
- **Audit Trail**: Complete activity logging with user attribution
- **Error Handling**: Graceful error messages and logging

### 🎨 Design System

#### Color Palette
- **Purple**: `#9333ea` - Primary actions, cluster operations
- **Cyan**: `#22d3ee` - Virtual machines, secondary actions
- **Green**: `#4ade80` - Success states, online status
- **Orange**: `#fb923c` - Warnings, stopped VMs
- **Pink**: `#ec4899` - Gradients and highlights
- **Blue**: `#3b82f6` - Info states, notifications

#### Components
- **Task Cards**: Glassmorphism cards with backdrop blur
- **Progress Bars**: Animated gradient progress indicators
- **Status Badges**: Color-coded with pulsing animations
- **Icon Containers**: Gradient 40px rounded squares
- **Action Buttons**: Large gradient buttons with hover effects
- **Toast Notifications**: Slide-in notifications with auto-dismiss

### 🔐 Security

- **Authentication**: Django admin authentication required
- **CSRF Protection**: All forms protected against CSRF attacks
- **SQL Injection**: Protected via Django ORM
- **XSS Protection**: All user input properly escaped
- **Secure Passwords**: Proxmox credentials encrypted in database

### 📚 Documentation

- **README.md**: Complete setup and deployment instructions
- **QUICKSTART.md**: Quick start guide for development
- **PROJECT_SUMMARY.md**: Technical overview and architecture
- **Environment Examples**: `.env.example` for easy configuration
- **Inline Comments**: Well-commented code throughout

### 🐛 Bug Fixes

- Fixed Proxmox authentication to include `@pam` realm
- Fixed template syntax errors (removed Jinja2 `selectattr` filters)
- Fixed database migrations for all models
- Fixed CSS validation errors in templates
- Fixed AJAX request handling with proper headers

### 📦 Dependencies

#### Python
- Django 4.2+
- Celery 5.3+
- Redis 5.0+
- psycopg2-binary 2.9+
- proxmoxer 2.0+
- requests 2.31+

#### Frontend
- Bootstrap Icons 1.11+
- Modern CSS Grid
- Vanilla JavaScript (no jQuery)

### 🚀 Performance

- **Fast Page Loads**: Optimized queries and minimal JavaScript
- **Background Processing**: All heavy operations run asynchronously
- **Caching**: Redis caching for frequently accessed data
- **Efficient Polling**: Smart polling intervals (30s background, 2s during sync)
- **Lazy Loading**: Templates load only required data

### 🔄 Migration from Manual Proxmox

This is the first version, so no migration path is needed. To start using PXMX:

1. Deploy using Docker Compose
2. Create a superuser account
3. Add your Proxmox clusters via admin interface
4. Run initial sync
5. Start managing your infrastructure!

### 📝 Notes

- Tested with Proxmox VE 7.x and 8.x
- Requires Python 3.9+
- Supports multiple authentication realms (PAM, PVE, LDAP)
- Works with standalone Proxmox nodes or full clusters

### 🙏 Acknowledgments

- Built with Django and Bootstrap Icons
- Inspired by modern dashboard designs
- Thanks to the Proxmox community for excellent API documentation

---

## [1.1.0] - 2025-12-02

### 🚀 Major Release - Enhanced Monitoring & Automation

This release focuses on production readiness with HTTPS/SSL support, automatic syncing, console access, and comprehensive real-time statistics across all pages.

### ✨ Added

#### HTTPS/SSL Support
- **Let's Encrypt Integration**: Automatic SSL certificate provisioning via certbot
- **Nginx Reverse Proxy**: Production-ready reverse proxy configuration on port 443
- **Auto-Renewal**: Systemd timer for automatic certificate renewal (90-day expiry)
- **HTTP Redirect**: Automatic HTTP → HTTPS redirection for security
- **Deployment**: Live on `https://manage.koetsier.it` with valid SSL certificate (expires March 2, 2026)

#### Automatic Disk Size Syncing
- **Celery Beat Scheduler**: Automated periodic tasks every 5 minutes
- **VM Sync Task**: Automatic synchronization of all VMs from all Proxmox clusters
- **Disk Size Tracking**: Accurate disk size display (32GB, 60GB, 250GB, etc.)
- **Background Processing**: Non-blocking sync operations via Celery workers
- **Commit**: `8684ed8`

#### Console Access Implementation
- **Direct Console Links**: One-click access to Proxmox web console (opens in new window)
- **SSH Tunnel Instructions**: Step-by-step guide for firewalled environments
- **Console Page**: New dedicated console access page at `/vm/<id>/console/`
- **Template**: `/templates/proxmox_manager/vm_console.html`
- **Commits**: `b70ce65`, `76b6764`, `8f49df3`

#### Real-Time Stats - Cluster Detail Page
- **JavaScript Polling**: Automatic stats refresh every 30 seconds
- **API Endpoint**: `/api/cluster/{cluster_id}/stats/` for cluster-specific stats
- **Live Updates**: Node count, VM count, online nodes, running VMs update without page reload
- **Smooth Animations**: Pulse effects on stat changes
- **Commits**: `390e6bd`, `59cb427`

#### Real-Time Stats - Right Sidebar (All Pages)
- **Universal Stats**: Sidebar stats now visible on ALL pages including:
  - `/vms/` - VM list page
  - `/vms/<id>/` - VM detail page
  - `/clusters/` - Cluster list page
  - `/clusters/<id>/` - Cluster detail page
  - `/nodes/<id>/` - Node detail page
  - `/audit-log/` - Audit log page
- **Context Variables**: All views now pass required stats context to templates
- **JavaScript Enhancement**: Background polling updates sidebar stats every 30 seconds
- **Template IDs**: Sidebar elements now have unique IDs for JavaScript updates:
  - `sidebar-clusters`, `sidebar-nodes`, `sidebar-total-vms`, `sidebar-running-vms`
  - `sidebar-online`, `sidebar-total`, `sidebar-cpu`, `sidebar-ram`
- **Graceful Fallbacks**: Default filters prevent errors when stats are unavailable
- **Commits**: `79e7ccd`, `be85f19`

### 🔧 Technical Improvements

#### Backend Enhancements
- **Views Context**: Updated all views to pass comprehensive stats context
- **API Endpoints**: New cluster stats API for real-time data fetching
- **Celery Beat**: Production-ready periodic task scheduler
- **Database Aggregations**: Efficient CPU/RAM average calculations using Django ORM

#### Frontend Enhancements
- **JavaScript Refactor**: `/static/js/realtime-sync.js` now updates both dashboard and sidebar
- **Polling Strategy**: Smart polling intervals (30s background, fast during sync)
- **Pulse Animations**: Visual feedback for stat updates
- **Error Handling**: Graceful degradation when API calls fail

#### Deployment & Infrastructure
- **Production Stack**: Podman Compose with all services running:
  - `nginx` - Reverse proxy with SSL (ports 443, 80)
  - `pxmx_web` - Django/Gunicorn
  - `pxmx_celery` - Async task worker
  - `pxmx_celery_beat` - Periodic scheduler
  - `pxmx_db` - PostgreSQL
  - `pxmx_redis` - Redis cache/broker
- **Ubuntu 25.04**: Production server deployment
- **Systemd Integration**: Service management and auto-start

### 🐛 Bug Fixes

- **Sidebar Stats Disappearing**: Fixed stats not showing on VM list, cluster list, node detail, and audit log pages
- **Context Variables**: Added missing context variables to all view functions
- **Template Safety**: Added `|default` filters to prevent template errors when stats are unavailable
- **JavaScript Scope**: Fixed sidebar update functionality to work across all pages

### 🔐 Security

- **HTTPS Only**: All traffic encrypted with Let's Encrypt SSL certificates
- **Secure Headers**: Nginx configured with security best practices
- **Certificate Auto-Renewal**: No manual intervention required for certificate expiry

### 📊 Performance

- **Efficient Polling**: Only updates stats when data changes
- **Minimal API Calls**: Smart caching and background updates
- **Database Optimization**: Aggregate queries for stats calculations
- **Redis Caching**: Fast data retrieval for frequently accessed stats

### 📚 Documentation

- **Context Summary**: Comprehensive project status documentation
- **Deployment Guide**: Production deployment instructions
- **Console Access Guide**: User instructions for VM console access

### 🎯 Production Status

**All features fully operational on https://manage.koetsier.it**:
- ✅ Dashboard with real-time stats (30s polling)
- ✅ VM List with sidebar stats
- ✅ VM Detail with sidebar stats and console access
- ✅ Cluster List with sidebar stats
- ✅ Cluster Detail with real-time stats
- ✅ Node Detail with sidebar stats
- ✅ Audit Log with sidebar stats
- ✅ Automatic syncing every 5 minutes
- ✅ HTTPS/SSL with auto-renewal

### 🔄 Breaking Changes

None - this release is fully backward compatible with v1.0.0.

### ⚠️ Known Issues

- Console access requires direct network access to Proxmox nodes or SSH tunnel setup
- NoVNC embedded console not implemented (simplified to direct links)
- Background polling rate is fixed at 30 seconds (will be configurable in future release)
- No bulk VM operations yet (planned for v1.2.0)

---

## [1.1.1] - 2025-12-02

### 🔧 Minor Release - Task Tracking Infrastructure

This release adds backend infrastructure for Celery task monitoring and management.

### ✨ Added

#### Task Tracking System
- **CeleryTask Model**: Database model to track all Celery task executions
- **Task Lifecycle Tracking**: Automatic tracking of task state, progress, and execution time
- **Helper Functions**:
  - `track_task()` - Create task tracking record
  - `update_task_progress()` - Update task progress percentage and message
  - `complete_task()` - Mark task as completed with result/error
- **Progress Monitoring**: All sync tasks now report progress (0-100%)
- **Execution Metrics**: Track task start time, completion time, and total execution time
- **Database Indexes**: Optimized queries for task history and filtering

#### API Endpoints
- **GET /tasks/** - Task history page with filtering and search
- **GET /api/tasks/\<task_id\>/status/** - Get individual task status
- **GET /api/tasks/running/** - Get all currently running tasks
- **POST /api/tasks/\<task_id\>/retry/** - Retry failed tasks
- **POST /api/tasks/\<task_id\>/cancel/** - Cancel running tasks

#### Admin Interface
- **CeleryTask Admin**: View and manage tasks in Django admin
- **Execution Time Display**: Shows formatted execution time for completed tasks
- **Advanced Filtering**: Filter by state, task name, user, VM, cluster
- **Search**: Search by task ID, task name, user, or VM name

### 🔧 Technical Improvements

#### Enhanced Task Tracking
- **Sync Tasks**: Both `sync_cluster_data` and `sync_vms_for_node` now report detailed progress
- **Progress Messages**: Human-readable progress updates (e.g., "Syncing node pve1", "Fetching VMs")
- **Error Handling**: Better error tracking with full tracebacks stored
- **Task States**: Track PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED states

#### Database Optimization
- **Composite Indexes**: Optimized for common queries (state + created_at, task_name + created_at)
- **Select Related**: Efficient queries with user, VM, and cluster relationships
- **Pagination**: Task list supports pagination for large datasets

### 📊 Features Ready for UI

Backend infrastructure is complete for:
- ✅ Real-time task status monitoring
- ✅ Task progress bars (backend ready, UI pending)
- ✅ Task history with filtering
- ✅ Retry failed tasks
- ✅ Cancel running tasks
- ✅ Task execution metrics

### 🔄 Breaking Changes

None - this release is fully backward compatible with v1.1.0.

### ⚠️ Known Issues

- Task tracking UI components not yet implemented (templates and JavaScript pending)
- Task progress bars need frontend implementation
- No visual notification of task completion yet

### 📝 Notes

This release focuses on backend infrastructure. UI components (templates, JavaScript, progress bars) will be added in subsequent releases.

---

## [Unreleased]

### Planned Features
See ROADMAP.md for upcoming features and improvements.

### Known Issues
- Task tracking UI components pending (templates, JavaScript)
- No bulk VM operations yet (planned for v1.2.0)

---

[1.0.0]: https://github.com/jskoetsier/pxpx/releases/tag/v1.0.0
[1.1.0]: https://github.com/jskoetsier/pxpx/releases/tag/v1.1.0
[1.1.1]: https://github.com/jskoetsier/pxpx/releases/tag/v1.1.1
