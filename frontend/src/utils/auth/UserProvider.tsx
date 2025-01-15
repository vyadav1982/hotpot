import {
  useFrappeAuth,
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
  userName:string;
}

export const UserContext = createContext<UserContextProps>({
  currentUser: '',
  isLoading: false,
  logout: () => Promise.resolve(),
  updateCurrentUser: () => {},
  userId:'',
  userName: '',
});

export const UserProvider: FC<PropsWithChildren> = ({ children }) => {
  const { mutate } = useSWRConfig();
  const { logout, currentUser, updateCurrentUser, isLoading } = useFrappeAuth();
  const [userId, setUserId] = useState('')
  const [userName, setUserName] = useState('');
  const { call: getUser } = useFrappePostCall(
    'hotpot.api.users.get_hotpot_user_by_email',
  );

  const fetchUserDetails = async (currentUser: string) => {
    if (currentUser) {
      try {
        const response = await getUser({ email: currentUser });
        const {employee_id,employee_name} = response.message.data;
        setUserId(employee_id)
        setUserName(employee_name)
      } catch (error) {
        console.error('Error fetching user:', error);
      }
    } else {
      console.log('No current user provided');
    }
  };
  useEffect(() => {
    if ((isHotpotUser() && !isHotpotAdmin() && !isHotpotServer() && currentUser?.trim()) || (!isHotpotAdmin() && isHotpotServer() && currentUser?.trim())) {
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
        userName,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};
