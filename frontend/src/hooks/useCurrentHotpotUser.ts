import { HotpotUser } from '@/types/Hotpot/HotpotUser';
import { useFrappeGetCall } from 'frappe-react-sdk';

const useCurrentHotpotUser = () => {
  const { data, mutate } = useFrappeGetCall<{ message: HotpotUser }>(
    'hotpot.api.users.get_current_user',
    undefined,
    'my_profile',
    {
      // revalidateIfStale: false,
      revalidateOnFocus: false,
      shouldRetryOnError: false,
      revalidateOnReconnect: true,
    },
  );

  return {
    myProfile: data?.message,
    mutate,
  };
};

export default useCurrentHotpotUser;
