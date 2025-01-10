import { ErrorBanner } from '@/components/ErrorBanner';
import { FullPageLoader } from '@/components/FullPageLoader';
import { HotpotCoupon } from '@/types/Hotpot/HotpotCoupon';
import { format } from 'date-fns';
import {
  Filter,
  useFrappeDocTypeEventListener,
  useFrappeGetCall,
  useFrappeGetDocCount,
  useSWRConfig,
} from 'frappe-react-sdk';
import {
  PropsWithChildren,
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { DateRangeContext } from './DateRangeProvider';

export const PreviousCouponListContext = createContext<{
  previousCoupons: CouponFields[];
  downcount: number | undefined;
}>({
  previousCoupons: [],
  downcount: 0,
});

export type CouponFields = Pick<
  HotpotCoupon,
  'title' | 'coupon_date' | 'coupon_time' | 'creation' | 'emoji_reaction' | 'feedback' | 'name' | 'status'
>;
interface UpcomingCouponListProps extends PropsWithChildren {
  employee_id: string;
  downPage: number;
}
export const PreviousCouponListProvider = ({
  children,
  employee_id,
  downPage,
}: UpcomingCouponListProps) => {
  const { mutate: globalMutate } = useSWRConfig();
  const { date } = useContext(DateRangeContext);
  useEffect(() => {
    mutate();
  }, [downPage, date]);
  const filters: Filter[] = [
    ['employee_id', '=', employee_id],
    ...(window.location.pathname.includes('history')
      ? ([
          [
            'coupon_date',
            '>=',
            format(
              date?.from ||
                new Date(new Date().getFullYear(), new Date().getMonth(), 1),
              'yyyy/MM/dd',
            ),
          ],
          ['coupon_date', '<', format(date?.to || new Date(), 'yyyy/MM/dd')],
        ] as Filter[])
      : ([
          [
            'coupon_date',
            '>=',
            format(
              new Date(new Date().getFullYear(), new Date().getMonth(), -30),
              'yyyy/MM/dd',
            ),
          ],
          ['coupon_date', '<', format(new Date(), 'yyyy/MM/dd')],
        ] as Filter[])),
  ];

  const { data: downcount } = useFrappeGetDocCount('Hotpot Coupon', filters);
  const {
    data,
    error: previousCouponsError,
    mutate,
    isLoading,
  } = useFrappeGetCall<{ message: CouponFields[] }>(
    'hotpot.api.coupon.get_past_coupon_list',
    {
      params: {
        employee_id: employee_id,
        from_date: window.location.pathname.includes('history')
          ? format(date?.from || new Date(), 'yyyy/MM/dd')
          : format(
              new Date(new Date().getFullYear(), new Date().getMonth(), -30),
              'yyyy/MM/dd',
            ),

        to_date: window.location.pathname.includes('history')
          ? format(date?.to || new Date(), 'yyyy/MM/dd')
          : format(new Date(), 'yyyy/MM/dd'),
        page: downPage,
      },
    },
    'hotpot.api.coupon.get_past_coupon_list',
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
        globalMutate(`hotpot.api.previousCoupons.get_list`);
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

  const { previousCoupons } = useMemo(() => {
    return {
      previousCoupons: data?.message ?? [],
    };
  }, [data]);

  if (isLoading) {
    return <FullPageLoader />;
  }
  if (previousCouponsError) {
    return (
      <div className="mx-auto flex h-screen w-full items-center justify-center px-4 lg:w-1/2">
        <div className="w-full max-w-md">
          <ErrorBanner error={previousCouponsError}></ErrorBanner>
        </div>
      </div>
    );
  }

  return (
    <PreviousCouponListContext.Provider value={{ previousCoupons, downcount }}>
      {children}
    </PreviousCouponListContext.Provider>
  );
};
