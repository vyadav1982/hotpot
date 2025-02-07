import { ErrorBanner } from '@/components/ErrorBanner';
import { FullPageLoader } from '@/components/FullPageLoader';
import { HotpotCoupon } from '@/types/Hotpot/HotpotCoupon';
import { format } from 'date-fns';
import {
  useFrappeDocTypeEventListener,
  useFrappeGetCall,
  useFrappeGetDocCount,
  useSWRConfig,
} from 'frappe-react-sdk';
import {
  PropsWithChildren,
  createContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

export const UpcomingCouponListContext = createContext<{
  upcomingCoupons: CouponFields[];
  upcount: number | undefined;
}>({
  upcomingCoupons: [],
  upcount: 0,
});

export type CouponFields = Pick<
  HotpotCoupon,
  | 'name'
  | 'title'
  | 'coupon_date'
  | 'coupon_time'
  | 'creation'
  | 'coupon_status'
>;
interface UpcomingCouponListProps extends PropsWithChildren {
  employee_id: string;
  upPage: number;
}
export const UpcomingCouponListProvider = ({
  children,
  employee_id,
  upPage,
}: UpcomingCouponListProps) => {
  const { mutate: globalMutate } = useSWRConfig();
  const {
    data,
    error: upcomingCouponsError,
    mutate,
    isLoading,
  } = useFrappeGetCall<{ message: CouponFields[] }>(
    'hotpot.api.coupon.get_upcoming_coupon_list',
    {
      params: {
        employee_id: employee_id,
        page: upPage,
      },
    },
    `hotpot.api.coupon.get_upcoming_coupon_list${employee_id}${upPage}`,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    },
  );
  const { data: upcount } = useFrappeGetDocCount('Hotpot Coupon', [
    ['employee_id', '=', employee_id],
    ['coupon_date', '>=', format(new Date(), 'yyyy-MM-dd')],
    [
      'coupon_date',
      '<=',
      format(
        new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0),
        'yyyy-MM-dd',
      ),
    ],
    ['coupon_status', '=', 'Upcoming'],
  ]);

  const [newUpdatesAvailable, setNewUpdatesAvailable] = useState(false);

  useEffect(() => {
    let timeout: NodeJS.Timeout | undefined;
    if (newUpdatesAvailable) {
      timeout = setTimeout(() => {
        mutate();
        // Mutate the user list as well ??
        globalMutate(`hotpot.api.coupon.get_upcoming_coupon_list`);
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
    mutate();
    setNewUpdatesAvailable(true);
  });

  const { upcomingCoupons } = useMemo(() => {
    return {
      upcomingCoupons: data?.message ?? [],
    };
  }, [data]);

  if (isLoading) {
    return <FullPageLoader />;
  }
  if (upcomingCouponsError) {
    return (
      <div className="mx-auto flex h-screen w-full items-center justify-center px-4 lg:w-1/2">
        <div className="w-full max-w-md">
          <ErrorBanner error={upcomingCouponsError}></ErrorBanner>
        </div>
      </div>
    );
  }

  return (
    <UpcomingCouponListContext.Provider value={{ upcomingCoupons, upcount }}>
      {children}
    </UpcomingCouponListContext.Provider>
  );
};
