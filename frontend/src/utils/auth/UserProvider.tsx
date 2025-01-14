import {
  useFrappeAuth,
  useFrappeGetDoc,
  useFrappePostCall,
  useSWRConfig,
} from 'frappe-react-sdk';
import { FC, PropsWithChildren, useEffect, useState } from 'react';
import { createContext } from 'react';
import { isHotpotAdmin, isHotpotServer, isHotpotUser } from '../roles';

interface UserContextProps {
  isLoading: boolean;
  currentUser: string;
  logout: () => Promise<void>;
  updateCurrentUser: VoidFunction;
  userId: string;
}

export const UserContext = createContext<UserContextProps>({
  currentUser: '',
  isLoading: false,
  logout: () => Promise.resolve(),
  updateCurrentUser: () => {},
  userId:''
});

export const UserProvider: FC<PropsWithChildren> = ({ children }) => {
  const { mutate } = useSWRConfig();
  const { logout, currentUser, updateCurrentUser, isLoading } = useFrappeAuth();
  const [userId, setUserId] = useState('')
  const { call: getUser } = useFrappePostCall(
    'hotpot.api.users.get_hotpot_user_by_email',
  );

  const fetchUserDetails = async (currentUser: string) => {
    if (currentUser) {
      console.log(currentUser);
      try {
        const response = await getUser({ email: currentUser });
        const {name} = response.message.data;
        setUserId(name)
      } catch (error) {
        console.error('Error fetching user:', error);
      }
    } else {
      console.log('No current user provided');
    }
  };
  useEffect(() => {
    console.log(isHotpotUser())
    if (isHotpotUser() && !isHotpotAdmin() && !isHotpotServer() && currentUser?.trim()) {
      fetchUserDetails(currentUser);
    }
  }, [currentUser]);

  const handleLogout = async () => {
    localStorage.removeItem('app-cache');
    return logout()
      .then(() => {
        //Clear cache on logout
        localStorage.clear();
        return mutate(
          (key) => {
            if (key === 'hotpot.api.login.get_context') {
              return false;
            }
            return true;
          },
          undefined,
          false,
        );
      })
      .then(() => {
        //Reload the page so that the boot info is fetched again
        const URL = import.meta.env.VITE_BASE_NAME
          ? `${import.meta.env.VITE_BASE_NAME}`
          : ``;
        if (URL) {
          window.location.replace(`/${URL}/login`);
        } else {
          window.location.replace('/login');
        }

        // window.location.reload()
      });
  };

  return (
    <UserContext.Provider
      value={{
        isLoading,
        updateCurrentUser,
        logout: handleLogout,
        currentUser: currentUser ?? '',
        userId,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};
