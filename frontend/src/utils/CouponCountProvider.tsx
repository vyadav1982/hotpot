import { ErrorBanner } from '@/components/ErrorBanner';
import { FullPageLoader } from '@/components/FullPageLoader';
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
import { DateRange } from 'react-day-picker';

export const CouponCountContext = createContext<{
  CouponsCount: any;
}>({
  CouponsCount: [],
});
interface CouponCountProviderProps extends PropsWithChildren {
  date: DateRange | undefined;
}

export const CouponCountProvider = ({
  children,
  date,
}: CouponCountProviderProps) => {
  const { mutate: globalMutate } = useSWRConfig();
  useEffect(() => {
    mutate();
    globalMutate(`hotpot.api.dashboard.get_coupon_type_count`);
  }, [date]);
  const {
    data,
    error: couponsError,
    mutate,
    isLoading,
  } = useFrappeGetCall<{ message: [] }>(
    'hotpot.api.dashboard.get_coupon_type_count',
    {
      params: {
        from: date?.from?.toLocaleDateString(),
        to: date?.to?.toLocaleDateString(),
      },
    },
    'hotpot.api.coupons.get_coupon_type_count',
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    },
  );

  // console.log("from", date?.from?.toLocaleDateString())
  // console.log("to", date?.to?.toLocaleDateString())
  console.log(date?.from?.toLocaleDateString("en-US", { year: "numeric", month: "2-digit", day: "2-digit" }));
  console.log(date?.to?.toLocaleDateString("en-US", { year: "numeric", month: "2-digit", day: "2-digit" }));
  const [newUpdatesAvailable, setNewUpdatesAvailable] = useState(false);

  useEffect(() => {
    let timeout: NodeJS.Timeout | undefined;
    if (newUpdatesAvailable) {
      timeout = setTimeout(() => {
        mutate();
        // Mutate the user list as well ??
        globalMutate(`hotpot.api.coupons.get_coupon_type_count`);
        setNewUpdatesAvailable(false);
      }, 1000); // 1 second
    }
    return () => clearTimeout(timeout);
  }, [newUpdatesAvailable]);

  /**
   * If a bulk import happens, this gets called multiple times potentially causing the server to go down.
   * Instead, throttle this - wait for all events to subside
   */
  useFrappeDocTypeEventListener('Hotpot Coupon ', () => {
    setNewUpdatesAvailable(true);
  });

  const { CouponsCount } = useMemo(() => {
    return {
      CouponsCount: data?.message ?? [],
    };
  }, [data]);

  if (isLoading) {
    return <FullPageLoader />;
  }
  if (couponsError) {
    return (
      <div className="mx-auto flex h-screen w-full items-center justify-center px-4 lg:w-1/2">
        <div className="w-full max-w-md">
          <ErrorBanner error={couponsError}></ErrorBanner>
        </div>
      </div>
    );
  }

  return (
    <CouponCountContext.Provider value={{ CouponsCount }}>
      {children}
    </CouponCountContext.Provider>
  );
};
