frappe.after_ajax(() => {
    const waitForDropdown = setInterval(() => {
        const dropdownMenu = document.getElementById('toolbar-user');

        if (dropdownMenu) {
            clearInterval(waitForDropdown); // Stop checking once it's found

            const roles = frappe.user_roles;
            const hasAdminRole = roles.includes('Administrator');

            if (!hasAdminRole) {
                dropdownMenu.innerHTML = '';

                // Toggle Theme Button
                const themeButton = document.createElement('button');
                themeButton.classList.add('btn-reset', 'dropdown-item', 'theme-button');
                themeButton.textContent = 'Toggle Theme';
                themeButton.onclick = () => {
                    return new frappe.ui.ThemeSwitcher().show();
                };

                // Logout Button
                const logoutButton = document.createElement('button');
                logoutButton.classList.add('btn-reset', 'dropdown-item', 'logout-button');
                logoutButton.textContent = 'Log out';
                logoutButton.onclick = () => {
                    return frappe.app.logout();
                };

                dropdownMenu.appendChild(themeButton);
                dropdownMenu.appendChild(logoutButton);
            }
        }
    }, 200); // Check every 200ms
});
