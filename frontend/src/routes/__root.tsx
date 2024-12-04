import '@/index.css';

import { createRootRouteWithContext } from '@tanstack/react-router';
// Dev Tools (does not get bundled in production)
import { TanStackRouterDevtools } from '@tanstack/router-devtools';
import App from '@/App';

export const Route = createRootRouteWithContext<{
  sessionUser: string | null;
}>()({
  beforeLoad: async ({ location, context }) => {
    if (
      (!context.sessionUser || context.sessionUser === 'Guest') &&
      (location.pathname != '/hotpot/login' ||
        !location.href.startsWith('/hotpot/login?redirect-to'))
    ) {
      if (location.pathname !== '/hotpot/login') {
        if (location.pathname === '/hotpot' || location.pathname === '/hotpot/') {
          window.location.href = '/hotpot/login';
        } else {
          window.location.href = '/hotpot/login?redirect-to=' + location.pathname;
        }
      }
    }

    if (!!context.sessionUser && location.href.startsWith('/hotpot/login')) {
      window.location.href = '/hotpot';
    }
  },
  pendingComponent: () => <p>Login pending...</p>,
  errorComponent: () => <p>Login failed...</p>,
  component: () => (
    <>
      <App></App>
      {import.meta.env.DEV && <TanStackRouterDevtools position="bottom-left" />}
    </>
  ),
});
