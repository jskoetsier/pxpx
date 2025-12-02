// Real-time sync functionality
class RealtimeSync {
    constructor() {
        this.syncingClusters = new Set();
        this.pollInterval = null;
        this.toastContainer = this.createToastContainer();
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

    showToast(message, type = 'info') {
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
        }, 4000);
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

                // Start polling for updates
                this.startPolling(clusterId);
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

                // Start global polling
                this.startPolling();
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

    startPolling(clusterId = null) {
        // Clear existing poll if any
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }

        // Poll every 2 seconds
        this.pollInterval = setInterval(async () => {
            if (this.syncingClusters.size === 0) {
                clearInterval(this.pollInterval);
                this.pollInterval = null;
                return;
            }

            // Refresh dashboard stats
            await this.refreshDashboard();

            // Check if sync is complete (simple timeout-based for now)
            // In a production app, you'd check Celery task status
            setTimeout(() => {
                this.syncingClusters.clear();
                this.showToast('Sync completed!', 'success');

                // Re-enable all sync buttons
                document.querySelectorAll('[data-sync-button]').forEach(btn => {
                    btn.disabled = false;
                    if (btn.dataset.originalHTML) {
                        btn.innerHTML = btn.dataset.originalHTML;
                    }
                });

                // Reload page to show updated data
                setTimeout(() => window.location.reload(), 1000);
            }, 5000); // Assume sync takes ~5 seconds
        }, 2000);
    }

    async refreshDashboard() {
        try {
            const response = await fetch('/api/dashboard/stats/');
            const data = await response.json();

            // Update dashboard stats if elements exist
            if (document.getElementById('total-vms')) {
                document.getElementById('total-vms').textContent = data.stats.total_vms;
            }
            if (document.getElementById('running-vms')) {
                document.getElementById('running-vms').textContent = data.stats.running_vms;
            }
            if (document.getElementById('stopped-vms')) {
                document.getElementById('stopped-vms').textContent = data.stats.stopped_vms;
            }
            if (document.getElementById('total-nodes')) {
                document.getElementById('total-nodes').textContent = data.stats.total_nodes;
            }
            if (document.getElementById('online-nodes')) {
                document.getElementById('online-nodes').textContent = data.stats.online_nodes;
            }

        } catch (error) {
            console.error('Failed to refresh dashboard:', error);
        }
    }

    async refreshClusterStats(clusterId) {
        try {
            const response = await fetch(`/api/cluster/${clusterId}/stats/`);
            const data = await response.json();

            // Update cluster page stats if elements exist
            // This can be customized based on your page structure
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

    .spin {
        animation: spin 1s linear infinite;
        display: inline-block;
    }
`;
document.head.appendChild(style);

// Export for use in HTML
window.realtimeSync = realtimeSync;
