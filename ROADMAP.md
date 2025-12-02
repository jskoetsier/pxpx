# PXMX Roadmap

This document outlines the planned features and improvements for PXMX - Proxmox Administration Dashboard.

---

## Version 1.1.0 - Enhanced Monitoring ✅ COMPLETED (January 2025)

**Theme: Better Observability & Task Management**

### Features

#### Task Status Visibility (Partially Complete - Backend in v1.1.1)
- [x] ✅ Task execution time metrics (v1.1.1)
- [x] ✅ CeleryTask model and database tracking (v1.1.1)
- [x] ✅ Task progress tracking backend (v1.1.1)
- [x] ✅ Task history API endpoints (v1.1.1)
- [x] ✅ Cancel/retry task API endpoints (v1.1.1)
- [ ] Real-time Celery task status in UI (backend ready, UI pending)
- [ ] Task progress bars for long-running operations (backend ready, UI pending)
- [ ] Task history page with filtering and search (backend ready, template pending)
- [ ] Cancel/retry failed tasks from UI (backend ready, UI buttons pending)

#### Advanced Monitoring
- [x] ✅ Real-time stats updates (30-second polling)
- [x] ✅ Universal sidebar stats on all pages
- [x] ✅ Automatic background syncing (Celery Beat - 5 minutes)
- [x] ✅ Live cluster stats on cluster detail page
- [ ] Historical resource usage graphs (24h, 7d, 30d)
- [ ] Customizable dashboard widgets
- [ ] Email/webhook notifications for critical events
- [ ] Alert rules for resource thresholds
- [ ] Downtime tracking and SLA reporting

#### User Experience
- [x] ✅ Smooth animations and pulse effects on updates
- [x] ✅ VM console access (direct Proxmox links + SSH tunnel guide)
- [ ] Configurable polling intervals
- [ ] Dark/light theme toggle
- [ ] User preferences (default views, filters)
- [ ] Keyboard shortcuts for common actions
- [ ] Quick search (global VM/node search)

#### Production Deployment
- [x] ✅ HTTPS/SSL with Let's Encrypt
- [x] ✅ Nginx reverse proxy configuration
- [x] ✅ Auto-renewal for SSL certificates
- [x] ✅ Podman Compose production deployment
- [x] ✅ Systemd service integration

### Technical Improvements
- [x] ✅ Real-time JavaScript polling on all pages
- [x] ✅ Cluster-specific stats API endpoint
- [x] ✅ Context variables in all views
- [x] ✅ Graceful fallbacks with default filters
- [x] ✅ Automatic disk size syncing
- [ ] WebSocket support for real-time updates
- [ ] Improved error handling and user feedback
- [ ] API rate limiting
- [ ] Enhanced logging and debugging tools
- [ ] Unit test coverage > 80%

---

## Version 1.2.0 - Bulk Operations (Q2 2025)

**Theme: Efficiency & Automation**

### Features

#### Bulk VM Management
- [ ] Multi-select VMs from list view
- [ ] Bulk start/stop/restart operations
- [ ] Bulk migration wizard
- [ ] Bulk snapshot creation
- [ ] Export VM configurations

#### Automation
- [ ] Scheduled tasks (auto-snapshots, shutdowns)
- [ ] VM templates management
- [ ] Clone VM functionality
- [ ] Automated backup schedules
- [ ] Maintenance mode (bulk operations planning)

#### Enhanced Filtering
- [ ] Advanced filter builder (multiple criteria)
- [ ] Saved filter presets
- [ ] Tag-based VM organization
- [ ] Custom VM grouping
- [ ] Smart collections (auto-updating based on criteria)

### Performance
- [ ] Pagination for large VM lists
- [ ] Lazy loading images and resources
- [ ] Database query optimization
- [ ] Redis caching improvements
- [ ] Background task queuing improvements

---

## Version 1.3.0 - Storage & Networking (Q3 2025)

**Theme: Complete Infrastructure Management**

### Features

#### Storage Management
- [ ] Storage overview across clusters
- [ ] Disk usage analytics
- [ ] ISO/template upload interface
- [ ] Backup/restore management
- [ ] Storage migration tools

#### Network Management
- [ ] Network topology visualization
- [ ] VLAN management
- [ ] Firewall rules viewer
- [ ] Network interface configuration
- [ ] IP address management (IPAM)

#### Container Support
- [ ] LXC container management
- [ ] Container templates
- [ ] Container console access
- [ ] Container-specific operations
- [ ] Resource limits configuration

### Security
- [ ] Two-factor authentication (2FA)
- [ ] Role-based access control (RBAC)
- [ ] Audit log export
- [ ] API key management
- [ ] Session management improvements

---

## Version 1.4.0 - Analytics & Reporting (Q4 2025)

**Theme: Insights & Intelligence**

### Features

#### Analytics Dashboard
- [ ] Resource utilization trends
- [ ] Cost estimation/tracking
- [ ] Capacity planning recommendations
- [ ] Performance bottleneck detection
- [ ] VM lifecycle analytics

#### Reporting
- [ ] Scheduled PDF reports
- [ ] Custom report builder
- [ ] Compliance reports
- [ ] Capacity planning reports
- [ ] Uptime/availability reports

#### AI/ML Features
- [ ] Anomaly detection
- [ ] Resource optimization suggestions
- [ ] Predictive maintenance alerts
- [ ] Auto-scaling recommendations
- [ ] Workload analysis

### Integrations
- [ ] Prometheus metrics export
- [ ] Grafana dashboard templates
- [ ] Slack/Discord notifications
- [ ] PagerDuty integration
- [ ] Terraform provider

---

## Version 2.0.0 - Multi-Platform Support (2026)

**Theme: Beyond Proxmox**

### Major Features

#### Platform Support
- [ ] VMware vSphere integration
- [ ] OpenStack support
- [ ] Kubernetes cluster management
- [ ] Hybrid cloud management
- [ ] Multi-hypervisor dashboard

#### Enterprise Features
- [ ] Multi-tenancy support
- [ ] Billing/chargeback system
- [ ] Self-service portal
- [ ] Approval workflows
- [ ] Service catalog

#### Advanced Automation
- [ ] Infrastructure as Code (IaC) support
- [ ] GitOps integration
- [ ] CI/CD pipeline integration
- [ ] Auto-healing capabilities
- [ ] Disaster recovery automation

### Architecture
- [ ] Microservices architecture
- [ ] GraphQL API
- [ ] Plugin system
- [ ] Horizontal scaling support
- [ ] Multi-region deployment

---

## Continuous Improvements

These improvements will be made across all versions:

### Performance
- Continuous optimization of database queries
- Frontend performance improvements
- Reduced memory footprint
- Faster page load times
- Better caching strategies

### User Experience
- Accessibility improvements (WCAG 2.1 AA)
- Mobile-responsive enhancements
- Improved error messages
- Better onboarding experience
- In-app help and documentation

### Documentation
- Video tutorials
- Interactive demos
- API documentation
- Best practices guide
- Troubleshooting guide

### Testing
- Increased test coverage
- Integration tests
- E2E testing
- Performance testing
- Security audits

---

## Community Requests

Features requested by the community will be tracked here:

### High Priority
- [ ] VM console access (noVNC/SPICE)
- [ ] Mobile app (iOS/Android)
- [ ] REST API documentation
- [ ] VM cloning
- [ ] Snapshot scheduling

### Medium Priority
- [ ] Custom dashboards
- [ ] CSV/Excel export
- [ ] Multi-language support
- [ ] VM groups/tags
- [ ] Network diagrams

### Under Consideration
- [ ] Desktop application (Electron)
- [ ] Browser extension
- [ ] ChatOps integration
- [ ] Voice commands
- [ ] AR/VR visualization

---

## Long-Term Vision

### 3-Year Goals
1. **Market Leader**: Become the go-to management tool for Proxmox environments
2. **Enterprise Ready**: Full enterprise feature set with SLA guarantees
3. **Cloud Native**: Support all major cloud and on-prem platforms
4. **AI-Powered**: Intelligent automation and predictive analytics
5. **Community Driven**: Active open-source community with 1000+ contributors

### Success Metrics
- 10,000+ active installations
- 100+ enterprise customers
- 99.9% uptime for hosted version
- <100ms average API response time
- >90% user satisfaction rating

---

## How to Contribute

We welcome community input on our roadmap!

### Suggest a Feature
1. Open an issue on GitHub with the `feature-request` label
2. Describe the use case and expected behavior
3. Community votes via 👍 reactions
4. Team reviews and prioritizes quarterly

### Implement a Feature
1. Check the roadmap for unassigned features
2. Comment on the feature to claim it
3. Fork the repository and create a feature branch
4. Submit a PR with tests and documentation
5. Participate in code review

### Vote on Features
- Use 👍 on GitHub issues to vote
- Join our Discord for discussions
- Participate in quarterly community calls

---

## Release Cadence

- **Major releases** (x.0.0): Annually
- **Minor releases** (1.x.0): Quarterly
- **Patch releases** (1.0.x): As needed (bug fixes)
- **Security patches**: Immediate

---

## Deprecation Policy

- Features marked for deprecation will have 2 minor releases notice
- Breaking changes only in major releases
- Migration guides provided for all breaking changes
- Legacy API versions supported for 1 year

---

## Feedback

Have thoughts on our roadmap? We'd love to hear from you!

- **GitHub Issues**: https://github.com/jskoetsier/pxpx/issues
- **Email**: feedback@pxmx.io
- **Discord**: https://discord.gg/pxmx
- **Community Calls**: First Tuesday of each month

---

**Last Updated**: 2024-12-02
**Next Review**: 2025-03-01
