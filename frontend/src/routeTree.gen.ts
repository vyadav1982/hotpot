/* eslint-disable */

// @ts-nocheck

// noinspection JSUnusedGlobalSymbols

// This file was automatically generated by TanStack Router.
// You should NOT make any changes in this file as it will be overwritten.
// Additionally, you should also exclude this file from your linter and/or formatter to prevent it from being checked or modified.

// Import Routes

import { Route as rootRoute } from './routes/__root'
import { Route as ServerImport } from './routes/server'
import { Route as MenuImport } from './routes/menu'
import { Route as LoginImport } from './routes/login'
import { Route as GuestImport } from './routes/guest'
import { Route as DashboardImport } from './routes/dashboard'
import { Route as CouponImport } from './routes/coupon'
import { Route as UsersUserUserIdImport } from './routes/users/user.$userId'
import { Route as UsersHistoryUserIdImport } from './routes/users/history.$userId'

// Create/Update Routes

const ServerRoute = ServerImport.update({
  id: '/server',
  path: '/server',
  getParentRoute: () => rootRoute,
} as any)

const MenuRoute = MenuImport.update({
  id: '/menu',
  path: '/menu',
  getParentRoute: () => rootRoute,
} as any)

const LoginRoute = LoginImport.update({
  id: '/login',
  path: '/login',
  getParentRoute: () => rootRoute,
} as any)

const GuestRoute = GuestImport.update({
  id: '/guest',
  path: '/guest',
  getParentRoute: () => rootRoute,
} as any)

const DashboardRoute = DashboardImport.update({
  id: '/dashboard',
  path: '/dashboard',
  getParentRoute: () => rootRoute,
} as any)

const CouponRoute = CouponImport.update({
  id: '/coupon',
  path: '/coupon',
  getParentRoute: () => rootRoute,
} as any)

const UsersUserUserIdRoute = UsersUserUserIdImport.update({
  id: '/users/user/$userId',
  path: '/users/user/$userId',
  getParentRoute: () => rootRoute,
} as any)

const UsersHistoryUserIdRoute = UsersHistoryUserIdImport.update({
  id: '/users/history/$userId',
  path: '/users/history/$userId',
  getParentRoute: () => rootRoute,
} as any)

// Populate the FileRoutesByPath interface

declare module '@tanstack/react-router' {
  interface FileRoutesByPath {
    '/coupon': {
      id: '/coupon'
      path: '/coupon'
      fullPath: '/coupon'
      preLoaderRoute: typeof CouponImport
      parentRoute: typeof rootRoute
    }
    '/dashboard': {
      id: '/dashboard'
      path: '/dashboard'
      fullPath: '/dashboard'
      preLoaderRoute: typeof DashboardImport
      parentRoute: typeof rootRoute
    }
    '/guest': {
      id: '/guest'
      path: '/guest'
      fullPath: '/guest'
      preLoaderRoute: typeof GuestImport
      parentRoute: typeof rootRoute
    }
    '/login': {
      id: '/login'
      path: '/login'
      fullPath: '/login'
      preLoaderRoute: typeof LoginImport
      parentRoute: typeof rootRoute
    }
    '/menu': {
      id: '/menu'
      path: '/menu'
      fullPath: '/menu'
      preLoaderRoute: typeof MenuImport
      parentRoute: typeof rootRoute
    }
    '/server': {
      id: '/server'
      path: '/server'
      fullPath: '/server'
      preLoaderRoute: typeof ServerImport
      parentRoute: typeof rootRoute
    }
    '/users/history/$userId': {
      id: '/users/history/$userId'
      path: '/users/history/$userId'
      fullPath: '/users/history/$userId'
      preLoaderRoute: typeof UsersHistoryUserIdImport
      parentRoute: typeof rootRoute
    }
    '/users/user/$userId': {
      id: '/users/user/$userId'
      path: '/users/user/$userId'
      fullPath: '/users/user/$userId'
      preLoaderRoute: typeof UsersUserUserIdImport
      parentRoute: typeof rootRoute
    }
  }
}

// Create and export the route tree

export interface FileRoutesByFullPath {
  '/coupon': typeof CouponRoute
  '/dashboard': typeof DashboardRoute
  '/guest': typeof GuestRoute
  '/login': typeof LoginRoute
  '/menu': typeof MenuRoute
  '/server': typeof ServerRoute
  '/users/history/$userId': typeof UsersHistoryUserIdRoute
  '/users/user/$userId': typeof UsersUserUserIdRoute
}

export interface FileRoutesByTo {
  '/coupon': typeof CouponRoute
  '/dashboard': typeof DashboardRoute
  '/guest': typeof GuestRoute
  '/login': typeof LoginRoute
  '/menu': typeof MenuRoute
  '/server': typeof ServerRoute
  '/users/history/$userId': typeof UsersHistoryUserIdRoute
  '/users/user/$userId': typeof UsersUserUserIdRoute
}

export interface FileRoutesById {
  __root__: typeof rootRoute
  '/coupon': typeof CouponRoute
  '/dashboard': typeof DashboardRoute
  '/guest': typeof GuestRoute
  '/login': typeof LoginRoute
  '/menu': typeof MenuRoute
  '/server': typeof ServerRoute
  '/users/history/$userId': typeof UsersHistoryUserIdRoute
  '/users/user/$userId': typeof UsersUserUserIdRoute
}

export interface FileRouteTypes {
  fileRoutesByFullPath: FileRoutesByFullPath
  fullPaths:
    | '/coupon'
    | '/dashboard'
    | '/guest'
    | '/login'
    | '/menu'
    | '/server'
    | '/users/history/$userId'
    | '/users/user/$userId'
  fileRoutesByTo: FileRoutesByTo
  to:
    | '/coupon'
    | '/dashboard'
    | '/guest'
    | '/login'
    | '/menu'
    | '/server'
    | '/users/history/$userId'
    | '/users/user/$userId'
  id:
    | '__root__'
    | '/coupon'
    | '/dashboard'
    | '/guest'
    | '/login'
    | '/menu'
    | '/server'
    | '/users/history/$userId'
    | '/users/user/$userId'
  fileRoutesById: FileRoutesById
}

export interface RootRouteChildren {
  CouponRoute: typeof CouponRoute
  DashboardRoute: typeof DashboardRoute
  GuestRoute: typeof GuestRoute
  LoginRoute: typeof LoginRoute
  MenuRoute: typeof MenuRoute
  ServerRoute: typeof ServerRoute
  UsersHistoryUserIdRoute: typeof UsersHistoryUserIdRoute
  UsersUserUserIdRoute: typeof UsersUserUserIdRoute
}

const rootRouteChildren: RootRouteChildren = {
  CouponRoute: CouponRoute,
  DashboardRoute: DashboardRoute,
  GuestRoute: GuestRoute,
  LoginRoute: LoginRoute,
  MenuRoute: MenuRoute,
  ServerRoute: ServerRoute,
  UsersHistoryUserIdRoute: UsersHistoryUserIdRoute,
  UsersUserUserIdRoute: UsersUserUserIdRoute,
}

export const routeTree = rootRoute
  ._addFileChildren(rootRouteChildren)
  ._addFileTypes<FileRouteTypes>()

/* ROUTE_MANIFEST_START
{
  "routes": {
    "__root__": {
      "filePath": "__root.tsx",
      "children": [
        "/coupon",
        "/dashboard",
        "/guest",
        "/login",
        "/menu",
        "/server",
        "/users/history/$userId",
        "/users/user/$userId"
      ]
    },
    "/coupon": {
      "filePath": "coupon.tsx"
    },
    "/dashboard": {
      "filePath": "dashboard.tsx"
    },
    "/guest": {
      "filePath": "guest.tsx"
    },
    "/login": {
      "filePath": "login.tsx"
    },
    "/menu": {
      "filePath": "menu.tsx"
    },
    "/server": {
      "filePath": "server.tsx"
    },
    "/users/history/$userId": {
      "filePath": "users/history.$userId.tsx"
    },
    "/users/user/$userId": {
      "filePath": "users/user.$userId.tsx"
    }
  }
}
ROUTE_MANIFEST_END */
