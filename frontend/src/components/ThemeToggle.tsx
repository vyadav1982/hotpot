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
      className="h-8 w-4 rounded-full"
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
    >
      <div className="relative flex size-4 justify-center">
        <Sun className="absolute h-full w-full rotate-90 scale-100 transition-transform duration-200 ease-in-out dark:rotate-0 dark:scale-0" />
        <Moon className="absolute h-full w-full rotate-0 scale-0 transition-transform duration-200 ease-in-out dark:-rotate-90 dark:scale-100" />
      </div>
      {/* <span>Toggle theme</span> */}
    </Button>
  );
}
