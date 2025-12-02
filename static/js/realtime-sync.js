// Real-time sync functionality with continuous background polling
class RealtimeSync {
    constructor() {
        this.syncingClusters = new Set();
        this.syncPollInterval = null;
        this.backgroundPollInterval = null;
        this.toastContainer = this.createToastContainer();
        this.pollRate = 30000; // 30 seconds for background polling
        this.syncPollRate = 2000; // 2 seconds during active sync

        // Start background polling on page load
        this.startBackgroundPolling();
    }

    createToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    showToast(message, type = 'info', duration = 4000) {
        const toast = document.createElement('div');
        const colors = {
            success: 'linear-gradient(135deg, #10b981, #34d399)',
            error: 'linear-gradient(135deg, #ef4444, #dc2626)',
            info: 'linear-gradient(135deg, #3b82f6, #60a5fa)',
            warning: 'linear-gradient(135deg, #f59e0b, #fbbf24)'
        };

        toast.style.cssText = `
            background: ${colors[type] || colors.info};
            color: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            min-width: 300px;
            animation: slideIn 0.3s ease-out;
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 500;
        `;

        const icons = {
            success: '<i class="bi bi-check-circle-fill"></i>',
            error: '<i class="bi bi-x-circle-fill"></i>',
            info: '<i class="bi bi-info-circle-fill"></i>',
            warning: '<i class="bi bi-exclamation-triangle-fill"></i>'
        };

        toast.innerHTML = `${icons[type] || icons.info} <span>${message}</span>`;
        this.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    async syncCluster(clusterId, button = null) {
        if (this.syncingClusters.has(clusterId)) {
            this.showToast('Sync already in progress for this cluster', 'warning');
            return;
        }

        this.syncingClusters.add(clusterId);

        // Update button state
        if (button) {
            const originalHTML = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Syncing...';
            button.dataset.originalHTML = originalHTML;
        }

        try {
            const response = await fetch(`/clusters/${clusterId}/sync/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            const data = await response.json();

            if (data.status === 'started') {
                this.showToast(data.message, 'success');

                // Switch to fast polling during sync
                this.startSyncPolling(clusterId);
            }
        } catch (error) {
            console.error('Sync error:', error);
            this.showToast('Failed to initiate sync', 'error');
            this.syncingClusters.delete(clusterId);

            if (button) {
                button.disabled = false;
                button.innerHTML = button.dataset.originalHTML;
            }
        }
    }

    async syncAllClusters(button = null) {
        // Update button state
        if (button) {
            const originalHTML = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Syncing All...';
            button.dataset.originalHTML = originalHTML;
        }

        try {
            const response = await fetch('/clusters/sync-all/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            const data = await response.json();

            if (data.status === 'started') {
                this.showToast(data.message, 'success');

                // Add all cluster IDs to syncing set
                data.tasks.forEach(task => {
                    this.syncingClusters.add(task.cluster_id);
                });

                // Switch to fast polling during sync
                this.startSyncPolling();
            }
        } catch (error) {
            console.error('Sync error:', error);
            this.showToast('Failed to initiate sync', 'error');

            if (button) {
                button.disabled = false;
                button.innerHTML = button.dataset.originalHTML;
            }
        }
    }

    startSyncPolling(clusterId = null) {
        // Clear existing sync poll if any
        if (this.syncPollInterval) {
            clearInterval(this.syncPollInterval);
        }

        // Fast poll every 2 seconds during sync
        this.syncPollInterval = setInterval(async () => {
            if (this.syncingClusters.size === 0) {
                clearInterval(this.syncPollInterval);
                this.syncPollInterval = null;
                return;
            }

            // Refresh dashboard stats
            await this.refreshDashboard();
        }, this.syncPollRate);

        // Assume sync completes after 5 seconds
        setTimeout(() => {
            this.syncingClusters.clear();
            this.showToast('Sync completed! Refreshing...', 'success');

            // Re-enable all sync buttons
            document.querySelectorAll('[data-sync-button]').forEach(btn => {
                btn.disabled = false;
                if (btn.dataset.originalHTML) {
                    btn.innerHTML = btn.dataset.originalHTML;
                }
            });

            // Clear sync polling
            if (this.syncPollInterval) {
                clearInterval(this.syncPollInterval);
                this.syncPollInterval = null;
            }

            // Reload page to show updated data
            setTimeout(() => window.location.reload(), 1000);
        }, 5000);
    }

    startBackgroundPolling() {
        // Initial refresh
        this.refreshDashboard(true);

        // Poll every 30 seconds in the background
        this.backgroundPollInterval = setInterval(async () => {
            await this.refreshDashboard(true);
        }, this.pollRate);

        console.log('Background polling started (every 30 seconds)');
    }

    stopBackgroundPolling() {
        if (this.backgroundPollInterval) {
            clearInterval(this.backgroundPollInterval);
            this.backgroundPollInterval = null;
            console.log('Background polling stopped');
        }
    }

    async refreshDashboard(silent = false) {
        try {
            const response = await fetch('/api/dashboard/stats/');
            const data = await response.json();

            // Update dashboard stats if elements exist
            this.updateElement('total-vms', data.stats.total_vms);
            this.updateElement('running-vms', data.stats.running_vms);
            this.updateElement('stopped-vms', data.stats.stopped_vms);
            this.updateElement('total-nodes', data.stats.total_nodes);
            this.updateElement('online-nodes', data.stats.online_nodes);
            this.updateElement('avg-cpu', data.stats.avg_cpu + '%');
            this.updateElement('avg-ram', data.stats.avg_ram + '%');

            // Update sidebar stats
            this.updateElement('sidebar-nodes', data.stats.total_nodes);
            this.updateElement('sidebar-total-vms', data.stats.total_vms);
            this.updateElement('sidebar-running-vms', data.stats.running_vms);
            this.updateElement('sidebar-online', data.stats.online_nodes);
            this.updateElement('sidebar-total', data.stats.total_nodes);
            this.updateElement('sidebar-cpu', data.stats.avg_cpu + '%');
            this.updateElement('sidebar-ram', data.stats.avg_ram + '%');

            // Update last updated indicator
            this.updateLastRefreshTime();

            if (!silent) {
                console.log('Dashboard stats refreshed');
            }

        } catch (error) {
            if (!silent) {
                console.error('Failed to refresh dashboard:', error);
            }
        }
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element && element.textContent !== String(value)) {
            element.textContent = value;
            // Add pulse animation on update
            element.style.animation = 'pulse 0.5s ease-in-out';
            setTimeout(() => {
                element.style.animation = '';
            }, 500);
        }
    }

    updateLastRefreshTime() {
        const timeElement = document.getElementById('last-refresh-time');
        if (timeElement) {
            const now = new Date();
            timeElement.textContent = now.toLocaleTimeString();
            timeElement.style.color = 'var(--accent-green)';
            setTimeout(() => {
                timeElement.style.color = 'var(--text-secondary)';
            }, 1000);
        }
    }

    async refreshClusterStats(clusterId) {
        try {
            const response = await fetch(`/api/cluster/${clusterId}/stats/`);
            const data = await response.json();

            // Update cluster page stats if elements exist
            console.log('Cluster stats updated:', data);

        } catch (error) {
            console.error('Failed to refresh cluster stats:', error);
        }
    }
}

// Initialize on page load
const realtimeSync = new RealtimeSync();

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }

    @keyframes spin {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }

    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.1);
        }
    }

    .spin {
        animation: spin 1s linear infinite;
        display: inline-block;
    }
`;
document.head.appendChild(style);

// Export for use in HTML
window.realtimeSync = realtimeSync;

// Stop polling when user leaves the page
window.addEventListener('beforeunload', () => {
    realtimeSync.stopBackgroundPolling();
});
