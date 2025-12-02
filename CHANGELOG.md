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

## [Unreleased]

### Planned Features
See ROADMAP.md for upcoming features and improvements.

### Known Issues
- Background polling rate is fixed at 30 seconds (will be configurable in future release)
- Celery task status not exposed in UI (planned for v1.1.0)
- No bulk VM operations yet (planned for v1.2.0)

---

[1.0.0]: https://github.com/jskoetsier/pxpx/releases/tag/v1.0.0
