import { ErrorBanner } from '@/components/ErrorBanner';
import { FullPageLoader } from '@/components/FullPageLoader';
import { HotpotUser } from '@/types/Hotpot/HotpotUser';
import {
  useFrappeDocTypeEventListener,
  useFrappeGetCall,
  useSWRConfig,
} from 'frappe-react-sdk';
import {
  PropsWithChildren,
  createContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

export const UserListContext = createContext<{
  users: UserFields[];
}>({
  users: [],
});

export type UserFields = Pick<
  HotpotUser,
  'name' | 'employee_id' | 'employee_name'
>;

export const UserListProvider = ({ children }: PropsWithChildren) => {
  const { mutate: globalMutate } = useSWRConfig();
  const {
    data,
    error: usersError,
    mutate,
    isLoading,
  } = useFrappeGetCall<{ message: UserFields[] }>(
    'hotpot.api.users.get_list',
    undefined,
    'hotpot.api.users.get_list',
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    },
  );

  const [newUpdatesAvailable, setNewUpdatesAvailable] = useState(false);

  useEffect(() => {
    let timeout: NodeJS.Timeout | undefined;
    if (newUpdatesAvailable) {
      timeout = setTimeout(() => {
        mutate();
        // Mutate the user list as well ??
        // globalMutate(`user_list`);
        setNewUpdatesAvailable(false);
      }, 1000); // 1 second
    }
    return () => clearTimeout(timeout);
  }, [newUpdatesAvailable]);

  /**
   * If a bulk import happens, this gets called multiple times potentially causing the server to go down.
   * Instead, throttle this - wait for all events to subside
   */
  useFrappeDocTypeEventListener('Hotpot User', () => {
    setNewUpdatesAvailable(true);
  });

  const { users } = useMemo(() => {
    return {
      users: data?.message ?? [],
    };
  }, [data]);

  if (isLoading) {
    return <FullPageLoader />;
  }
  if (usersError) {
    return (
      <div className="mx-auto flex h-screen w-full items-center justify-center px-4 lg:w-1/2">
        <div className="w-full max-w-md">
          <ErrorBanner error={usersError}></ErrorBanner>
        </div>
      </div>
    );
  }

  return (
    <UserListContext.Provider value={{ users }}>
      {children}
    </UserListContext.Provider>
  );
};
