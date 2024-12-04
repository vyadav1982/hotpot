import * as React from 'react';
import {
  Outlet,
  useRouter,
  useNavigate,
  createFileRoute,
} from '@tanstack/react-router';
import { useSwipeable } from 'react-swipeable';
import { SidebarProvider } from '@/components/ui/sidebar';
import { AppSidebar } from '@/components/Sidebar';
import { BottomNav } from '@/components/BottomNav';
import {
  navItems as navItemsUser,
  navItemsApprover,
} from '@/components/navItems';
import { useIsMobile } from '@/hooks/use-mobile';
import { ProtectedRoute } from '@/utils/auth/ProtectedRoute';
import { DialogProvider } from '@/utils/DialogProvider';
import { GenericDialog } from '@/components/GenericDialog';

export const ActiveTabContext = React.createContext<
  | {
      activeTab: number;
      setActiveTab: React.Dispatch<React.SetStateAction<number>>;
      swipeHandlers: ReturnType<typeof useSwipeable>;
      isMobile: boolean;
    }
  | undefined
>(undefined);

export const Route = createFileRoute('/_index')({
  component: () => {
    return (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    );
  },
});

function Layout() {
  const [activeTab, setActiveTab] = React.useState(0);
  const router = useRouter();
  const navigate = useNavigate();
  const isMobile = useIsMobile();
  const navItems = navItemsUser;

  React.useEffect(() => {
    const currentPath = router.state.location.pathname;
    const newActiveTab = navItems.findIndex(
      (item) => item.path === currentPath,
    );
    if (newActiveTab !== -1 && newActiveTab !== activeTab) {
      setActiveTab(newActiveTab);
    }
  }, [router.state.location.pathname, activeTab]);

  const swipeHandlers = useSwipeable({
    onSwipedLeft: () => {
      if (isMobile) {
        const nextTab = Math.min(navItems.length - 1, activeTab + 1);
        setActiveTab(nextTab);
        navigate({ to: navItems[nextTab].path });
      }
    },
    onSwipedRight: () => {
      if (isMobile) {
        const prevTab = Math.max(0, activeTab - 1);
        setActiveTab(prevTab);
        navigate({ to: navItems[prevTab].path });
      }
    },
    trackMouse: true,
  });

  return (
    <ActiveTabContext.Provider
      value={{ activeTab, setActiveTab, swipeHandlers, isMobile }}
    >
      <DialogProvider>
        <SidebarProvider defaultOpen={false}>
          <div className="flex h-screen w-full">
            <AppSidebar
              navItems={navItems}
              activeTab={activeTab}
              setActiveTab={setActiveTab}
            />
            <div
              className="flex-1 overflow-auto"
              {...(isMobile ? swipeHandlers : {})}
            >
              <Outlet />
            </div>
            <BottomNav activeTab={activeTab} setActiveTab={setActiveTab} />
          </div>
        </SidebarProvider>
        <GenericDialog />
      </DialogProvider>
    </ActiveTabContext.Provider>
  );
}
