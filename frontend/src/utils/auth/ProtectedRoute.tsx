import { useContext, ReactNode } from 'react';
import { UserContext } from './UserProvider';
import { Navigate, Route, useRouterState } from '@tanstack/react-router';
import { FullPageLoader } from '@/components/FullPageLoader';
import { isHotpotAdmin, isHotpotServer, isHotpotUser } from '../roles';

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { currentUser, isLoading, userId } = useContext(UserContext);
  const router = useRouterState();

  if (
    isLoading ||
    (isHotpotUser() && !isHotpotAdmin() && !isHotpotServer() && userId == '')
  ) {
    return <FullPageLoader />;
  }
  if (!currentUser || currentUser === 'Guest') {
    return <Navigate to="/login" />;
  }
  if (
    (isHotpotAdmin() && isHotpotServer() && isHotpotUser()) ||
    isHotpotAdmin()
  ) {
    if (router.location.pathname !== '/hotpot/guest') {
      return <Navigate to="/guest" />;
    }
  } else if (isHotpotUser()) {
    const userAllowedPaths = [`/hotpot/users/user/${userId}`, `/hotpot/users/history/${userId}`];
    if (
      !userAllowedPaths.some((path) => router.location.pathname.includes(path))
    ) {
      return <Navigate to="/users/user/$userId" params={{ userId: userId }} />;
    }
  } else if (isHotpotServer()) {
    const serverAllowedPaths = [
      '/hotpot/server',
      '/hotpot/dashboard',
      '/hotpot/',
    ];
    if (
      !serverAllowedPaths.some((path) =>
        router.location.pathname.includes(path),
      )
    ) {
      return <Navigate to="/server" />;
    }
  } else {
    return <Navigate to="/login" />;
  }

  return <>{children}</>;
};
