import { useContext, ReactNode } from 'react';
import { UserContext } from './UserProvider';
import { Navigate } from '@tanstack/react-router';
import { FullPageLoader } from '@/components/FullPageLoader';

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { currentUser, isLoading } = useContext(UserContext);

  if (isLoading) {
    return <FullPageLoader />;
  } else if (!currentUser || currentUser === 'Guest') {
    return <Navigate to="/login" />;
  }
  return <>{children}</>;
};
