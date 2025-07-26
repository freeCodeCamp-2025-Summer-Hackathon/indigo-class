// Dashboard tab switching logic
document.addEventListener('DOMContentLoaded', function () {
    const tabButtons = document.querySelectorAll('.dashboard-tab');
    const tabContents = document.querySelectorAll('.dashboard-tab-content');

    // Format date helper function
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
            hour12: true
        });
    }

    function setActiveTab(tab) {
        localStorage.setItem('activeTab', tab);

        // Remove active from all buttons
        tabButtons.forEach(btn => btn.classList.remove('active'));

        // Hide all tab contents
        tabContents.forEach(content => content.style.display = 'none');

        // Activate clicked button
        const activeButton = document.querySelector(`[data-tab="${tab}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }

        // Show corresponding tab content
        const activeContent = document.getElementById(`tab-${tab}`);
        if (activeContent) {
            activeContent.style.display = '';

            // Format dates in table cells
            const dateCells = activeContent.querySelectorAll('td');
            dateCells.forEach(cell => {
                const text = cell.textContent.trim();
                if (text.match(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/)) {
                    cell.textContent = formatDate(text);
                }
            });
        }
    }

    // Set initial active tab from localStorage or default to 'users'
    const initialTab = localStorage.getItem('activeTab') || 'users';
    setActiveTab(initialTab);

    // Add click handlers
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.getAttribute('data-tab');
            setActiveTab(tab);
        });
    });
});