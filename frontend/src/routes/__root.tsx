import '@/index.css';

import { createRootRouteWithContext } from '@tanstack/react-router';
import App from '@/App';
import { PageNotFound } from '@/components/PageNotFound';
import { FullPageLoader } from '@/components/FullPageLoader';
import { isHotpotAdmin, isHotpotServer, isHotpotUser } from '@/utils/roles';

export const Route = createRootRouteWithContext<{
  sessionUser: string | null;
}>()({
  beforeLoad: async ({ location, context }) => {
    if (location.pathname === '/hotpot/') {
      window.location.href = '/hotpot/server';
    }
    if (
      (isHotpotAdmin() && isHotpotServer() && isHotpotUser()) ||
      isHotpotAdmin()
    ) {
      if (location.pathname.includes('/login')) {
        window.location.href = '/hotpot/guest';
      } else if (!location.pathname.includes('hotpot/guest')) {
        return;
      }
    } else if (isHotpotServer()) {
      if (location.pathname.includes('/login')) {
        window.location.href = '/hotpot/server';
      }
      if (
        !location.pathname.includes('/server') &&
        !location.pathname.includes('/dashboard')
      ) {
        return;
      }
    } else if (isHotpotUser()) {
      if (location.pathname.includes('/login')) {
        window.location.href = '/hotpot/server';
      }
      if (
        !location.pathname.includes('/users/user') &&
        !location.pathname.includes('/users/history')
      ) {
        return;
      }
    } else if (!location.pathname.includes('/login')) {
      window.location.href = '/hotpot/login';
    }
  },
  pendingComponent: () => <FullPageLoader />,
  errorComponent: () => <PageNotFound />,
  component: () => (
    <>
      <App></App>
    </>
  ),
  notFoundComponent: () => <PageNotFound />,
});
