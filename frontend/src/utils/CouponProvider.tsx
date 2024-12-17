import { ErrorBanner } from '@/components/ErrorBanner';
import { FullPageLoader } from '@/components/FullPageLoader';
import { HotpotCoupon } from '@/types/Hotpot/HotpotCoupon';
import {
  useFrappeDocTypeEventListener,
  useFrappeGetCall,
  useSWRConfig,
} from 'frappe-react-sdk';
import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { DateRangeContext } from './DateRangeProvider';

type CouponProviderState = {
  coupons:
    | Map<string, [{ coupon_title?: string; coupon_time?: string }]>
    | undefined;
  isLoading: boolean;
};

const initialState: CouponProviderState = {
  coupons: undefined,
  isLoading: false,
};

export const CouponContext = createContext<CouponProviderState>(initialState);

type CouponProviderProps = {
  children: React.ReactNode;
};

export type CouponFields = Pick<
  HotpotCoupon,
  'employee_id' | 'title' | 'coupon_date' | 'coupon_time' | 'served_by'
>;

export type CouponFieldsWithName = CouponFields & {
  employee_name: string;
};

export const CouponProvider = ({ children, ...props }: CouponProviderProps) => {
  const { mutate: globalMutate } = useSWRConfig();
  const { date } = useContext(DateRangeContext);
  const {
    data,
    error: couponsError,
    mutate,
    isLoading,
  } = useFrappeGetCall<{ message: CouponFieldsWithName[] }>(
    'hotpot.api.dashboard.get_coupon_list',
    {
      params: {
        from: date?.from?.toLocaleDateString(),
        to: date?.to?.toLocaleDateString(),
      },
    },
    `hotpot.api.dashboard.get_coupon_list_${date?.from?.toLocaleDateString()}_${date?.to?.toLocaleDateString()}`,
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
        globalMutate(`hotpot.api.dashboard.get_coupon_list`);
        setNewUpdatesAvailable(false);
      }, 1000); // 1 second
    }
    return () => clearTimeout(timeout);
  }, [newUpdatesAvailable]);

  /**
   * If a bulk import happens, this gets called multiple times potentially causing the server to go down.
   * Instead, throttle this - wait for all events to subside
   */
  useFrappeDocTypeEventListener('Hotpot Coupon', () => {
    console.log('running....frappe');
    mutate();
    setNewUpdatesAvailable(true);
  });

  const { coupons } = useMemo(() => {
    const myData = new Map<
      string,
      [{ coupon_title?: string; coupon_time?: string }]
    >();
    if (data?.message) {
      Array.isArray(data?.message) &&
        data.message.forEach((coupon: CouponFieldsWithName) => {
          const key = `${coupon.employee_id}//${coupon.coupon_date}//${coupon.employee_name}`;
          if (!myData.has(key)) {
            myData.set(key, [{}]);
          }
          const obj = myData.get(key);
          if (obj) {
            let entry: { coupon_title?: string; coupon_time?: string } = {};
            entry.coupon_title = coupon.title;
            entry.coupon_time = coupon.coupon_time;
            obj.push(entry);
          }
        });
    }
    return {
      coupons: data?.message ? myData : [],
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
    <CouponContext.Provider {...props} value={{ coupons, isLoading }}>
      {children}
    </CouponContext.Provider>
  );
};
