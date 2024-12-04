import { Moon, Sun } from 'lucide-react';
import { useTheme } from './ThemeProvider';
import { SidebarMenuButton, useSidebar } from './ui/sidebar';

export function ThemeToggle() {
  const { setTheme, theme } = useTheme();
  const { state } = useSidebar();
  const isCollapsed = state === 'collapsed';

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <SidebarMenuButton
      onClick={toggleTheme}
      className="gap-3"
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
    >
      <div className="relative size-4">
        <Sun className="absolute h-full w-full rotate-90 scale-0 transition-transform duration-200 ease-in-out dark:rotate-0 dark:scale-100" />
        <Moon className="absolute h-full w-full rotate-0 scale-100 transition-transform duration-200 ease-in-out dark:-rotate-90 dark:scale-0" />
      </div>
      {!isCollapsed && <span>Toggle theme</span>}
    </SidebarMenuButton>
  );
}
