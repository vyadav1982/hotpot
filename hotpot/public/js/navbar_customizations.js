frappe.after_ajax(() => {
    const waitForDropdown = setInterval(() => {
        const dropdownMenu = document.getElementById('toolbar-user');

        if (dropdownMenu) {
            clearInterval(waitForDropdown);
            const roles = frappe.user_roles;
            const hasAdminRole = roles.includes('Administrator');

            if (!hasAdminRole) {
                dropdownMenu.innerHTML = '';

                const themeButton = document.createElement('button');
                themeButton.classList.add('btn-reset', 'dropdown-item', 'theme-button');
                themeButton.textContent = 'Toggle Theme';
                themeButton.onclick = () => new frappe.ui.ThemeSwitcher().show();

                const logoutButton = document.createElement('button');
                logoutButton.classList.add('btn-reset', 'dropdown-item', 'logout-button');
                logoutButton.textContent = 'Log out';
                logoutButton.onclick = () => frappe.app.logout();

                dropdownMenu.appendChild(themeButton);
                dropdownMenu.appendChild(logoutButton);
            }
        }
    }, 200);

    const workspacePages = ['Workspaces', 'dashboard'];

    const waitForFooter = setInterval(() => {
        const route = frappe.get_route();
        const isWorkspace = route && workspacePages.includes(route[0]);

        if (!isWorkspace) return;

        const footer = document.querySelector('.workspace-footer');

        if (footer) {
            clearInterval(waitForFooter);
            const roles = frappe.user_roles;
            const hasAdminRole = roles.includes('Administrator');

            if (!hasAdminRole) {
                footer.style.display = 'none';
                console.log('✅ Workspace footer hidden');
            }
        }
    }, 300);
});
