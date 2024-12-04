import { HotpotUser } from '@/types/Hotpot/HotpotUser';
import { useFrappeGetCall } from 'frappe-react-sdk';

const useCurrentUserInfo = () => {
  const { data, error, isLoading, mutate } = useFrappeGetCall<{
    message: HotpotUser;
  }>('hotpot.api.get_current_user_info', undefined, 'myprofile', {
    // revalidateIfStale: false,
    revalidateOnFocus: false,
    shouldRetryOnError: false,
    revalidateOnReconnect: true,
  });

  return {
    myProfile: data?.message,
    error,
    isLoading,
    mutate,
  };
};

export default useCurrentUserInfo;
