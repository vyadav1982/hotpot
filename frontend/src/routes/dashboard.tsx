import { DataTable } from '@/components/DataTable';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { ArrowUpDown } from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';
import { createFileRoute, Link } from '@tanstack/react-router';
import { ColumnDef } from '@tanstack/react-table';
import { format } from 'date-fns';
import { useFrappePostCall } from 'frappe-react-sdk';
import { Calendar as CalendarIcon } from 'lucide-react';
import { useContext, useEffect, useState } from 'react';
import { CouponContext, CouponProvider } from '@/utils/CouponProvider';
import {
  CouponCountContext,
  CouponCountProvider,
} from '@/utils/CouponCountProvider';
import { TopBar } from '@/components/TopBar';
import { UserContext } from '@/utils/auth/UserProvider';
import { useDialog } from '@/hooks/use-dialog';
import { Logo } from '@/components/Logo';
import { useDebouncedCallback } from 'use-debounce';
import { DateRangeContext, DateRangeProvider } from '@/utils/DateRangeProvider';
import { FullPageLoader } from '@/components/FullPageLoader';

export const Route = createFileRoute('/dashboard')({
  component: DashboardWrapperComponent,
});

type MealRecord = {
  empId: number;
  empName: string;
  breakfast: string;
  lunch: string;
  evening_snacks: string;
  dinner: string;
  date: string;
};

const columns: ColumnDef<MealRecord>[] = [
  {
    accessorKey: 'empId',
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="p-0"
        >
          Employee Id
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
  },
  {
    accessorKey: 'empName',
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="p-0"
        >
          Employee Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
  },
  { header: 'Breakfast', accessorKey: 'breakfast' },
  { header: 'Lunch', accessorKey: 'lunch' },
  { header: 'Evening Snacks', accessorKey: 'evening_snacks' },
  { header: 'Dinner', accessorKey: 'dinner' },
  {
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="p-0"
        >
          Date
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    accessorKey: 'date',
  },
];

function DashboardWrapperComponent() {
  return (
    <DateRangeProvider>
      <CouponProvider>
        <CouponCountProvider>
          <DashboardComponent key="dashboard" />
        </CouponCountProvider>
      </CouponProvider>
    </DateRangeProvider>
  );
}

function DashboardComponent() {
  const { currentUser, logout } = useContext(UserContext);
  const { showConfirmDialog } = useDialog();
  const [cards, setCards] = useState([]);
  const { date, setDate, selectedValue, setSelectedValue } =
    useContext(DateRangeContext);
  const convertMapToArray = (mapData: any) => {
    const entryMap = new Map<string, MealRecord>();
    const initializeMeals = () => ({
      breakfast: 'Not consumed',
      lunch: 'Not consumed',
      evening_snacks: 'Not consumed',
      dinner: 'Not consumed',
    });

    mapData.forEach((value: any, key: any) => {
      const [empId, date, employee_name] = key.split('//');
      const mapKey = `${empId}_${date}`;
      let entry = entryMap.get(mapKey);
      if (!entry) {
        entry = {
          empId,
          empName: employee_name,
          date,
          ...initializeMeals(),
        };
        entryMap.set(mapKey, entry);
      }

      value.forEach((coupon: any) => {
        if (Object.keys(coupon).length > 0) {
          switch (coupon.coupon_title) {
            case 'Dinner':
              entry.dinner = coupon.coupon_time;
              break;
            case 'Lunch':
              entry.lunch = coupon.coupon_time;
              break;
            case 'Evening Snack':
              entry.evening_snacks = coupon.coupon_time;
              break;
            case 'Breakfast':
              entry.breakfast = coupon.coupon_time;
              break;
          }
        }
      });
    });
    return Array.from(entryMap.values());
  };

  const { coupons, isLoading } = useContext(CouponContext);
  const { CouponsCount } = useContext(CouponCountContext);
  const [data, setData] = useState<MealRecord[]>([]);

  useEffect(() => {
    setData(convertMapToArray(coupons));
  }, [coupons]);

  const { call: getCouponType } = useFrappePostCall(
    'hotpot.api.dashboard.get_coupon_type_list',
  );
  const fetchCouponTypes = async () => {
    const response = await getCouponType({});
    setCards(response.message);
  };

  useEffect(() => {
    fetchCouponTypes();
  }, []);

  // Create a debounced version of setDate
  const debouncedSetCouponDate = useDebouncedCallback((selected) => {
    setDate({
      from: selected?.from,
      to: selected?.to,
    });
  }, 300);

  const handleLogout = async () => {
    try {
      await showConfirmDialog({
        title: 'Confirm Logout',
        description: 'Are you sure you want to logout?',
        confirmLabel: 'Logout',
        variant: 'destructive',
        onConfirm: async () => {
          await logout();
        },
      });
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  if (isLoading) {
    return <FullPageLoader />;
  }

  return (
    <div className="min-h-screen">
      <TopBar
        className="px-4 pt-3 sm:px-8"
        leftContent={
          <div className="flex items-center gap-3">
            <Link to="/login">
              <Logo className="h-10 w-10 cursor-pointer sm:h-12 sm:w-12" />
            </Link>
            <div className="text-lg font-bold sm:text-2xl">{currentUser}</div>
          </div>
        }
        rightContent={
          <div className="flex gap-2">
            <Link to="/server">
              <Button type="button" variant="outline">
                Serve
              </Button>
            </Link>
            <Button variant="destructive" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        }
      />
      <div className="px-24">
        {/* Header Section */}
        <Card className="my-6 flex flex-wrap items-center justify-between rounded-lg p-4 shadow-md">
          <div className="flex items-center gap-4">
            {'Total Consumed Coupons : '}
            {CouponsCount.total_coupons}
          </div>
          <div className="flex">
            {selectedValue === 'custom' && (
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    id="date"
                    variant={'outline'}
                    className={cn(
                      'mr-2 flex w-[300px] items-center justify-start gap-2 rounded-md border text-left font-medium shadow-md',
                      !date && 'text-muted-foreground',
                    )}
                  >
                    <CalendarIcon className="h-5 w-5" />
                    {date?.from ? (
                      date.to ? (
                        <>
                          {format(date.from, 'LLL dd, y')} -{' '}
                          {format(date.to, 'LLL dd, y')}
                        </>
                      ) : (
                        format(date.from, 'LLL dd, y')
                      )
                    ) : (
                      'Select Date'
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto rounded-lg border p-0 shadow-lg">
                  <Calendar
                    initialFocus
                    mode="range"
                    defaultMonth={date?.from}
                    selected={date}
                    onSelect={(selected) => {
                      console.log(selected);
                      debouncedSetCouponDate(selected);
                    }}
                    numberOfMonths={2}
                    className="p-2"
                  />
                </PopoverContent>
              </Popover>
            )}

            <Select value={selectedValue} onValueChange={setSelectedValue}>
              <SelectTrigger className="w-[180px] rounded-md border font-medium shadow-md">
                <SelectValue placeholder="Select a filter" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem value="today">Today</SelectItem>
                  <SelectItem value="this_week">This Week</SelectItem>
                  <SelectItem value="this_month">This Month</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
        </Card>

        {/* Cards Section */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {cards.map((item: any, index: number) => (
            <Card key={index} className="rounded-lg border shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg font-bold">{item.name}</CardTitle>
                <CardDescription className="text-sm">
                  {item.start_hour} - {item.end_hour}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {item.name === 'Breakfast' && (
                  <p className="text-sm">
                    Total Consumed Coupon: {CouponsCount.breakfast_coupons}
                  </p>
                )}
                {item.name === 'Lunch' && (
                  <p className="text-sm">
                    Total Consumed Coupon: {CouponsCount.lunch_coupons}
                  </p>
                )}
                {item.name === 'Evening Snack' && (
                  <p className="text-sm">
                    Total Consumed Coupon :{' '}
                    {CouponsCount.evening_snacks_coupons}
                  </p>
                )}
                {item.name === 'Dinner' && (
                  <p className="text-sm">
                    Total Consumed Coupon: {CouponsCount.dinner_coupons}
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Table Section */}
        <div className="mt-6 rounded-lg border p-4 shadow-lg">
          <DataTable columns={columns} data={data} />
        </div>
      </div>
    </div>
  );
}
