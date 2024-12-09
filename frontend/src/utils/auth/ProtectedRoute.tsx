import { useContext, ReactNode } from 'react';
import { UserContext } from './UserProvider';
import { Navigate, useRouterState } from '@tanstack/react-router';
import { FullPageLoader } from '@/components/FullPageLoader';
import { isHotpotAdmin } from '../roles';

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { currentUser, isLoading } = useContext(UserContext);
  const router = useRouterState();

  if (isLoading) {
    return <FullPageLoader />;
  } else if (!currentUser || currentUser === 'Guest') {
    return <Navigate to="/login" />;
  } else if (router.location.pathname === '/hotpot/guest' && !isHotpotAdmin()) {
    return <Navigate to="/login" />;
  }
  return <>{children}</>;
};
