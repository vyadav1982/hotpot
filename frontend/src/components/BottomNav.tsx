import * as React from 'react';
import { Link, useNavigate } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { navItems } from '@/components/navItems';

interface BottomNavProps {
  activeTab: number;
  setActiveTab: (index: number) => void;
}

export function BottomNav({ activeTab, setActiveTab }: BottomNavProps) {
  const bottomNavRef = React.useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  React.useEffect(() => {
    if (bottomNavRef.current) {
      const activeButton = bottomNavRef.current.querySelector(
        `a:nth-child(${activeTab + 1})`,
      );
      if (activeButton) {
        activeButton.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
          inline: 'center',
        });
      }
    }
  }, [activeTab]);

  const handleNavigation = (index: number) => {
    setActiveTab(index);
    navigate({ to: navItems[index].path });
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 border-t bg-background md:hidden">
      <div className="px-4 py-2">
        <div
          className="scrollbar-hide flex space-x-1 overflow-x-auto"
          ref={bottomNavRef}
        >
          {navItems.map((item, index) => (
            <Button
              key={item.label}
              variant={activeTab === index ? 'default' : 'ghost'}
              size="sm"
              onClick={() => handleNavigation(index)}
              className="flex h-16 min-w-[4rem] flex-1 flex-col items-center justify-center px-3 py-2"
              asChild
            >
              <Link to={item.path}>
                <item.icon className="mb-1 h-5 w-5" />
                <span className="whitespace-nowrap text-xs">{item.label}</span>
              </Link>
            </Button>
          ))}
        </div>
      </div>
    </nav>
  );
}
