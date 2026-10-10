/**
 * Apartment Visit Management System (AVMS) - Client UI Helpers
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Sidebar Toggle
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('open');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });
    }

    // 2. Alert Dismissal
    document.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', () => {
            const alert = btn.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 200);
            }
        });
    });

    // 3. Confirm Delete Actions
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('submit', (e) => {
            const msg = el.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });
});

/**
 * Trigger browser print dialog for printable pass tickets
 */
function printPassCard() {
    window.print();
}
