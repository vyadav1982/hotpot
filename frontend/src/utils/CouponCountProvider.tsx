import { ErrorBanner } from '@/components/ErrorBanner';
import { FullPageLoader } from '@/components/FullPageLoader';
import {
  useFrappeDocTypeEventListener,
  useFrappeGetCall,
  useSWRConfig,
} from 'frappe-react-sdk';
import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { DateRangeContext } from './DateRangeProvider';

type CouponCountProviderState = {
  CouponsCount: any;
};

const initialState: CouponCountProviderState = {
  CouponsCount: undefined,
};

export const CouponCountContext =
  createContext<CouponCountProviderState>(initialState);

type CouponCountProviderProps = {
  children: React.ReactNode;
};

export const CouponCountProvider = ({
  children,
  ...props
}: CouponCountProviderProps) => {
  const { mutate: globalMutate } = useSWRConfig();

  const { date } = useContext(DateRangeContext);

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
    `hotpot.api.coupons.get_coupon_type_count_${date?.from?.toLocaleDateString()}_${date?.to?.toLocaleDateString()}`,
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
    <CouponCountContext.Provider {...props} value={{ CouponsCount }}>
      {children}
    </CouponCountContext.Provider>
  );
};
