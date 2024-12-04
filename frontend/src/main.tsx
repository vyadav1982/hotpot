import React from 'react';
import ReactDOM from 'react-dom/client';

import { routeTree } from './routeTree.gen';
import { RouterProvider, createRouter } from '@tanstack/react-router';
import { getSessionUserId } from '@/utils/session';
import { ConfirmDialogProvider } from './components/common/confirm-dialog';
import { ThemeProvider } from './components/ThemeProvider';
import { FullPageLoader } from './components/FullPageLoader';

// @ts-expect-error no error here
import FrappePushNotification from '../public/frappe-push-notification';

const router = createRouter({
  basepath: '/hotpot',
  routeTree,
  defaultPreloadStaleTime: 0,
  context: {
    sessionUser: getSessionUserId(),
  },
  defaultErrorComponent: () => (
    <p>Something went wrong (from default error component)...</p>
  ),
  defaultPendingComponent: () => (
    <div className="p-1">
      <FullPageLoader />
    </div>
  ),
});

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

const registerServiceWorker = () => {
  // @ts-expect-error no error here
  window.frappePushNotification = new FrappePushNotification('hotpot');

  if ('serviceWorker' in navigator) {
    // @ts-expect-error no error here
    window.frappePushNotification
      .appendConfigToServiceWorkerURL('/assets/hotpot/hotpot/sw.js')
      .then((url: string) => {
        navigator.serviceWorker
          .register(url, {
            type: 'classic',
          })
          .then((registration) => {
            // @ts-expect-error no error here
            window.frappePushNotification.initialize(registration).then(() => {
              console.log('Frappe Push Notification initialized');
            });
          });
      })
      .catch((err: any) => {
        console.error('Failed to register service worker', err);
      });
  } else {
    console.error('Service worker not enabled/supported by browser');
  }
};

if (import.meta.env.DEV) {
  fetch('/api/method/hotpot.www.hotpot.get_context_for_dev', {
    method: 'POST',
  })
    .then((response) => response.json())
    .then((values) => {
      const v = JSON.parse(values.message);
      //@ts-expect-error it exists
      if (!window.frappe) window.frappe = {};
      //@ts-expect-error it exists
      window.frappe.boot = v;
      registerServiceWorker();
      ReactDOM.createRoot(document.getElementById('root')!).render(
        <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
          <React.StrictMode>
            <ConfirmDialogProvider>
              <RouterProvider router={router} />
            </ConfirmDialogProvider>
          </React.StrictMode>
        </ThemeProvider>,
      );
    });
} else {
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <React.StrictMode>
        <ConfirmDialogProvider>
          <RouterProvider router={router} />
        </ConfirmDialogProvider>
      </React.StrictMode>
    </ThemeProvider>,
  );
}
