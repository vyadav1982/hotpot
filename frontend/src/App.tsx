import { Outlet } from '@tanstack/react-router';
import { FrappeProvider } from 'frappe-react-sdk';
import { UserProvider } from '@/utils/auth/UserProvider';
import Cookies from 'js-cookie';
import { Toaster } from '@/components/ui/toaster';
import { DialogProvider } from './utils/DialogProvider';
import { GenericDialog } from './components/GenericDialog';
import { ThemeToggle } from './components/ThemeToggle';

/** Following keys will not be cached in app cache */
const NO_CACHE_KEYS = [
  'frappe.desk.form.load.getdoctype',
  'frappe.desk.search.search_link',
  'frappe.model.workflow.get_transitions',
  'frappe.desk.reportview.get_count',
  'frappe.core.doctype.server_script.server_script.enabled',
];

export default function App() {
  const getSiteName = () => {
    if (
      // @ts-expect-error no error here
      window.frappe?.boot?.versions?.frappe &&
      // @ts-expect-error no error here
      (window.frappe.boot.versions.frappe.startsWith('15') ||
        // @ts-expect-error no error here
        window.frappe.boot.versions.frappe.startsWith('16'))
    ) {
      return (
        // @ts-expect-error no error here
        window.frappe?.boot?.sitename ?? import.meta.env.VITE_SITE_NAME
      );
    }
    return import.meta.env.VITE_SITE_NAME;
  };
  return (
    <>
      <FrappeProvider
        url={import.meta.env.VITE_FRAPPE_PATH ?? ''}
        socketPort={
          import.meta.env.VITE_SOCKET_PORT
            ? import.meta.env.VITE_SOCKET_PORT
            : undefined
        }
        swrConfig={{
          provider: localStorageProvider,
        }}
        siteName={getSiteName()}
      >
        <UserProvider>
          <DialogProvider>
            <div className="fixed bottom-3 right-8 z-50">
              <ThemeToggle />
            </div>
            <Outlet />
            <GenericDialog />
          </DialogProvider>
        </UserProvider>
      </FrappeProvider>
      <Toaster />
    </>
  );
}

function localStorageProvider() {
  // When initializing, we restore the data from `localStorage` into a map.
  // Check if local storage is recent (less than a week). Else start with a fresh cache.
  const timestamp = localStorage.getItem('app-cache-timestamp');
  let cache = '[]';
  if (timestamp && Date.now() - parseInt(timestamp) < 7 * 24 * 60 * 60 * 1000) {
    const localCache = localStorage.getItem('app-cache');
    if (localCache) {
      cache = localCache;
    }
  }
  const map = new Map<string, any>(JSON.parse(cache));

  // Before unloading the app, we write back all the data into `localStorage`.
  window.addEventListener('beforeunload', () => {
    // Check if the user is logged in
    const user_id = Cookies.get('user_id');
    if (!user_id || user_id === 'Guest') {
      localStorage.removeItem('app-cache');
      localStorage.removeItem('app-cache-timestamp');
    } else {
      const entries = map.entries();

      const cacheEntries = [];

      for (const [key, value] of entries) {
        let hasCacheKey = false;
        for (const cacheKey of NO_CACHE_KEYS) {
          if (key.includes(cacheKey)) {
            hasCacheKey = true;
            break;
          }
        }

        //Do not cache doctype meta and search link
        if (hasCacheKey) {
          continue;
        }
        cacheEntries.push([key, value]);
      }
      const appCache = JSON.stringify(cacheEntries);
      localStorage.setItem('app-cache', appCache);
      localStorage.setItem('app-cache-timestamp', Date.now().toString());
    }
  });

  // We still use the map for write & read for performance.
  return map;
}
