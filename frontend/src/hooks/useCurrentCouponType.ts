import { useFrappeGetCall } from 'frappe-react-sdk';

const useCurrentCouponType = () => {
  const { data, mutate } = useFrappeGetCall<{ message: string }>(
    'hotpot.api.coupon.get_current_coupon_type',
    undefined,
    'get_current_coupon_type',
    {
      // revalidateIfStale: false,
      revalidateOnFocus: false,
      shouldRetryOnError: false,
      revalidateOnReconnect: true,
    },
  );

  return {
    currentCouponType: data?.message,
    mutate,
  };
};

export default useCurrentCouponType;
