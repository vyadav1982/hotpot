import * as React from 'react';
import { Link, useNavigate } from '@tanstack/react-router';
import {
  ChevronsUpDown,
  LogOut,
  User,
  PanelLeftClose,
  PanelLeft,
} from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  useSidebar,
} from '@/components/ui/sidebar';
import { UserContext } from '@/utils/auth/UserProvider';
import useCurrentHotpotUser from '@/hooks/useCurrentHotpotUser';
import { cn } from '@/lib/utils';
import { ThemeToggle } from './ThemeToggle';

interface SidebarProps {
  navItems: Array<{ icon: React.ElementType; label: string; path: string }>;
  activeTab: number;
  setActiveTab: (index: number) => void;
}

export function AppSidebar({
  navItems,
  activeTab,
  setActiveTab,
}: SidebarProps) {
  const { logout } = React.useContext(UserContext);
  const navigate = useNavigate();
  const { myProfile } = useCurrentHotpotUser();
  const { state } = useSidebar();

  const getInitials = (name?: string) => {
    if (!name) return '';
    const [firstName, lastName] = name.split(' ');
    return firstName[0].toUpperCase() + (lastName?.[0] ?? '').toUpperCase();
  };

  return (
    <>
      <Sidebar collapsible="icon">
        <SidebarHeader>
          <SidebarMenu>
            <SidebarMenuItem>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <SidebarMenuButton
                    size="lg"
                    className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                  >
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={myProfile?.user_image} alt="User" />
                      <AvatarFallback className="text-sm">
                        {getInitials(myProfile?.full_name)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="grid flex-1 text-left text-sm leading-tight">
                      <span className="truncate font-semibold">
                        {myProfile?.full_name}
                      </span>
                      <span className="truncate text-xs">
                        {myProfile?.email}
                      </span>
                    </div>
                    <ChevronsUpDown className="ml-auto size-4" />
                  </SidebarMenuButton>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg"
                  align="start"
                  side="bottom"
                  sideOffset={4}
                >
                  <DropdownMenuLabel className="text-sm font-normal text-muted-foreground">
                    {myProfile?.email ?? 'My Account'}
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => navigate({ to: '/profile' })}
                    className="cursor-pointer gap-2"
                  >
                    <User className="h-4 w-4" />
                    <span>Profile</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={logout}
                    className="cursor-pointer gap-2 text-destructive focus:text-destructive dark:text-red-400"
                  >
                    <LogOut className="h-4 w-4" />
                    <span>Logout</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>
        <SidebarContent className={cn(state === 'collapsed' && 'pl-2')}>
          <SidebarMenu>
            {navItems.map((item, index) => (
              <SidebarMenuItem key={item.label}>
                <Link to={item.path}>
                  <SidebarMenuButton
                    onClick={() => setActiveTab(index)}
                    isActive={activeTab === index}
                    className="gap-3"
                    tooltip={item.label}
                  >
                    <item.icon className="size-4 shrink-0" />
                    <span>{item.label}</span>
                  </SidebarMenuButton>
                </Link>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarContent>
        <SidebarFooter>
          <SidebarMenu>
            <SidebarMenuItem>
              <ThemeToggle />
            </SidebarMenuItem>
            <SidebarMenuItem>
              <CollapseButton />
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
        <SidebarRail />
      </Sidebar>
    </>
  );
}

function CollapseButton() {
  const { toggleSidebar, state } = useSidebar();
  const isCollapsed = state === 'collapsed';

  return (
    <SidebarMenuButton
      onClick={toggleSidebar}
      className="gap-3"
      tooltip={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
    >
      {isCollapsed ? (
        <PanelLeft className="size-4 shrink-0" />
      ) : (
        <PanelLeftClose className="size-4 shrink-0" />
      )}
      <span>Collapse Sidebar</span>
    </SidebarMenuButton>
  );
}
