import '@/index.css';

import { createRootRouteWithContext } from '@tanstack/react-router';
// Dev Tools (does not get bundled in production)
import { TanStackRouterDevtools } from '@tanstack/router-devtools';
import App from '@/App';
import { PageNotFound } from '@/components/PageNotFound';
import { FullPageLoader } from '@/components/FullPageLoader';

export const Route = createRootRouteWithContext<{
  sessionUser: string | null;
}>()({
  beforeLoad: async ({ location, context }) => {
    if (location.pathname != '/hotpot/coupon') {
      if (
        (!context.sessionUser || context.sessionUser === 'Guest') &&
        (location.pathname != '/hotpot/login' ||
          !location.href.startsWith('/hotpot/login?redirect-to'))
      ) {
        if (location.pathname !== '/hotpot/login') {
          if (
            location.pathname === '/hotpot' ||
            location.pathname === '/hotpot/'
          ) {
            window.location.href = '/hotpot/login';
          }
        }
      }

      if (!!context.sessionUser && location.href.startsWith('/hotpot/login')) {
        window.location.href = '/hotpot/server';
      } else {
        if (
          location.pathname === '/hotpot' ||
          location.pathname === '/hotpot/'
        ) {
          window.location.href = '/hotpot/login';
        }
      }
    } else if (
      context.sessionUser &&
      context.sessionUser !== 'Guest' &&
      context.sessionUser !== 'Administrator' &&
      location.pathname === '/hotpot/coupon'
    ) {
      window.location.href = '/hotpot/server';
    }
  },
  pendingComponent: () => <FullPageLoader />,
  errorComponent: () => <PageNotFound />,
  component: () => (
    <>
      <App></App>
      {import.meta.env.DEV && <TanStackRouterDevtools position="bottom-left" />}
    </>
  ),
  notFoundComponent: () => <PageNotFound />,
});
