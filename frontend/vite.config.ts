import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import proxyOptions from './proxyOptions';
import svgr from 'vite-plugin-svgr';
import { VitePWA } from 'vite-plugin-pwa';
import { TanStackRouterVite } from '@tanstack/router-vite-plugin';

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  return {
    plugins: [
      react(),
      TanStackRouterVite(),
      svgr(),
      VitePWA({
        registerType: 'autoUpdate',
        strategies: 'injectManifest',
        injectRegister: null,
        outDir: '../hotpot/public/hotpot',
        manifest: {
          name: 'HotPot',
          start_url: `/${env.VITE_BASE_NAME}`,
          short_name: 'Hotpot',
          description: 'Hotpot | Bon without Bone',
          display: 'standalone',
          icons: [
            {
              src: '/assets/hotpot/manifest/icon-192x192.png',
              sizes: '192x192',
              type: 'image/png',
            },
            {
              src: '/assets/hotpot/manifest/icon-512x512.png',
              sizes: '512x512',
              type: 'image/png',
            },
            {
              src: '/assets/hotpot/manifest/apple-touch-icon.png',
              sizes: '180x180',
              type: 'image/png',
            },
            {
              src: '/assets/hotpot/manifest/favicon-16x16.png',
              sizes: '16x16',
              type: 'image/png',
            },
            {
              src: '/assets/hotpot/manifest/favicon-32x32.png',
              sizes: '32x32',
              type: 'image/png',
            },
            {
              src: '/assets/hotpot/manifest/favicon.ico',
              sizes: '64x64 32x32 24x24 16x16',
              type: 'image/x-icon',
            },
          ],
        },
      }),
    ],
    server: {
      port: 8080,
      proxy: proxyOptions,
      hmr: {
        overlay: false,
      },
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    build: {
      outDir: '../hotpot/public/hotpot',
      emptyOutDir: true,
      target: 'es2015',
      rollupOptions: {
        onwarn(warning, warn) {
          if (warning.code === 'MODULE_LEVEL_DIRECTIVE') {
            return;
          }
          warn(warning);
        },
      },
    },
    optimizeDeps: {
      exclude: [],
    },
  };
});
