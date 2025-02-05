import { Moon, Sun } from 'lucide-react';
import { useTheme } from './ThemeProvider';
import { Button } from './ui/button';

export function ThemeToggle() {
  const { setTheme, theme } = useTheme();

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <Button
      onClick={toggleTheme}
      className="rounded-full w-4 h-8"
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
    >
      <div className="flex justify-center relative size-4">
        <Sun className="absolute h-full w-full rotate-90 scale-100 transition-transform duration-200 ease-in-out dark:rotate-0 dark:scale-0" />
        <Moon className="absolute h-full w-full rotate-0 scale-0 transition-transform duration-200 ease-in-out dark:-rotate-90 dark:scale-100" />
      </div>
      {/* <span>Toggle theme</span> */}
    </Button>
  );
}
