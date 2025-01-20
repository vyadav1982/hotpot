import { DataTable } from '@/components/DataTable';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { ArrowUpDown, LogOut, Menu } from 'lucide-react';
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
import { DateRange } from 'react-day-picker';
import { CouponContext, CouponProvider } from '@/utils/CouponProvider';
import {
  CouponCountContext,
  CouponCountProvider,
} from '@/utils/CouponCountProvider';
import { TopBar } from '@/components/TopBar';
import { UserContext } from '@/utils/auth/UserProvider';
import { useDialog } from '@/hooks/use-dialog';
import { Logo } from '@/components/Logo';
import { ProtectedRoute } from '@/utils/auth/ProtectedRoute';
import { useToast } from '@/hooks/use-toast';

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
  breakfast_time: string;
  lunch_time: string;
  snacks_time: string;
  dinner_time: string;
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
  {
    header: 'Breakfast',
    accessorKey: 'breakfast',
    cell: ({ row }) => {
      return (
        <div
          className={
            row.original.breakfast !== 'N/A'
              ? `flex justify-center rounded-full align-middle text-sm font-normal text-black ${
                  row.original.breakfast === 'Consumed'
                    ? 'bg-green-500 text-white'
                    : row.original.breakfast === 'Expired'
                      ? 'bg-red-500 text-white'
                      : 'bg-yellow-500 text-black'
                }`
              : ''
          }
          style={{
            width: `${row.original.breakfast.length + 4}ch`,
            minWidth: `${row.original.breakfast.length + 4}ch`,
          }}
          title={
            row.original.breakfast_time.trim()
              ? `Breakfast coupon created at ${(([h, m]) =>
                  `${h % 12 || 12}:${m} ${h >= 12 ? 'pm' : 'am'}`)(
                  row.original.breakfast_time.split(':').map(Number),
                )}`
              : 'No breakfast coupon created'
          }
        >
          {row.original.breakfast}
        </div>
      );
    },
  },
  {
    header: 'Lunch',
    accessorKey: 'lunch',
    cell: ({ row }) => {
      return (
        <div
          className={
            row.original.lunch !== 'N/A'
              ? `flex justify-center rounded-full align-middle text-sm font-normal text-black ${
                  row.original.lunch === 'Consumed'
                    ? 'bg-green-500 text-white'
                    : row.original.lunch === 'Expired'
                      ? 'bg-red-500 text-white'
                      : 'bg-yellow-500 text-black'
                }`
              : ''
          }
          style={{
            width: `${row.original.lunch.length + 4}ch`,
            minWidth: `${row.original.lunch.length + 4}ch`,
          }}
          title={
            row.original.lunch_time.trim()
              ? `Lunch coupon created at ${(([h, m]) =>
                  `${h % 12 || 12}:${m} ${h >= 12 ? 'pm' : 'am'}`)(
                  row.original.lunch_time.split(':').map(Number),
                )}`
              : 'No Lunch coupon created'
          }
        >
          {row.original.lunch}
        </div>
      );
    },
  },
  {
    header: 'Evening Snacks',
    accessorKey: 'evening_snacks',
    cell: ({ row }) => {
      return (
        <div
          className={
            row.original.evening_snacks !== 'N/A'
              ? `flex justify-center rounded-full align-middle text-sm font-normal text-black ${
                  row.original.evening_snacks === 'Consumed'
                    ? 'bg-green-500 text-white'
                    : row.original.evening_snacks === 'Expired'
                      ? 'bg-red-500 text-white'
                      : 'bg-yellow-500 text-black'
                }`
              : ''
          }
          style={{
            width: `${row.original.evening_snacks.length + 4}ch`,
            minWidth: `${row.original.evening_snacks.length + 4}ch`,
          }}
          title={
            row.original.snacks_time.trim()
              ? `Evening Snacks coupon created at ${(([h, m]) =>
                  `${h % 12 || 12}:${m} ${h >= 12 ? 'pm' : 'am'}`)(
                  row.original.snacks_time.split(':').map(Number),
                )}`
              : 'No Snacks coupon created'
          }
        >
          {row.original.evening_snacks}
        </div>
      );
    },
  },
  {
    header: 'Dinner',
    accessorKey: 'dinner',
    cell: ({ row }) => {
      return (
        <div
          className={
            row.original.dinner !== 'N/A'
              ? `flex flex-auto justify-center rounded-full align-middle text-sm font-normal text-black ${
                  row.original.dinner === 'Consumed'
                    ? 'bg-green-500 text-white'
                    : row.original.dinner === 'Expired'
                      ? 'bg-red-500 text-white'
                      : 'bg-yellow-500 text-black'
                }`
              : ''
          }
          style={{
            width: `${row.original.dinner.length + 4}ch`,
            minWidth: `${row.original.dinner.length + 4}ch`,
          }}
          title={
            row.original.dinner_time.trim()
              ? `Dinner coupon created at ${(([h, m]) =>
                  `${h % 12 || 12}:${m} ${h >= 12 ? 'pm' : 'am'}`)(
                  row.original.dinner_time.split(':').map(Number),
                )}`
              : 'No Dinner coupon created'
          }
        >
          {row.original.dinner}
        </div>
      );
    },
  },
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

interface RouteComponentProps {
  setDate: React.Dispatch<React.SetStateAction<DateRange | undefined>>;
  date: DateRange | undefined;
}

function DashboardWrapperComponent() {
  const [date, setDate] = useState<DateRange | undefined>({
    from: new Date(),
    to: new Date(),
  });
  console.log("getting date from dashboard wrapper:", date)
  return (
    <ProtectedRoute>
      <CouponProvider date={date}>
        <CouponCountProvider date={date}>
          <DashboardComponent setDate={setDate} date={date} />
        </CouponCountProvider>
      </CouponProvider>
    </ProtectedRoute>
  );
}

function DashboardComponent({ setDate, date }: RouteComponentProps) {
  const { currentUser, logout, userName } = useContext(UserContext);
  const { showConfirmDialog } = useDialog();
  const [cards, setCards] = useState([]);
  const [selectedValue, setSelectedValue] = useState('today');
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { toast } = useToast();

  const convertMapToArray = (mapData: any) => {
    const entryMap = new Map<string, MealRecord>();
    const initializeMeals = () => ({
      breakfast: 'N/A',
      lunch: 'N/A',
      evening_snacks: 'N/A',
      dinner: 'N/A',
    });

    mapData.forEach((value: any, key: any) => {
      const [empId, date, employee_name] = key.split('//');
      const mapKey = `${empId}_${date}`;
      let entry = entryMap.get(mapKey);
      if (!entry) {
        entry = {
          empId,
          empName: employee_name,
          date: new Date(date).toLocaleDateString('en-GB', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
          }),
          ...initializeMeals(),
          breakfast_time: '',
          lunch_time: '',
          snacks_time: '',
          dinner_time: '',
        };
        entryMap.set(mapKey, entry);
      }

      value.forEach((coupon: any) => {
        if (Object.keys(coupon).length > 0) {
          switch (coupon.coupon_title) {
            case 'Dinner':
              entry.dinner = coupon.status;
              entry.dinner_time = coupon.coupon_time;
              break;
            case 'Lunch':
              entry.lunch = coupon.status;
              entry.lunch_time = coupon.coupon_time;
              break;
            case 'Evening Snack':
              entry.evening_snacks = coupon.status;
              entry.snacks_time = coupon.coupon_time;
              break;
            case 'Breakfast':
              entry.breakfast = coupon.status;
              entry.breakfast_time = coupon.coupon_time;
              break;
          }
        }
      });
    });
    return Array.from(entryMap.values());
  };

  const { coupons } = useContext(CouponContext);
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
  const setDateRange = () => {
    if (selectedValue === 'today') {
      setDate({
        from: new Date(),
        to: new Date(),
      });
    }
    if (selectedValue === 'custom') {
      setDate({
        from: date?.from,
        to: date?.to,
      });
    }
    if (selectedValue === 'this_week') {
      const date = new Date();
      setDate({
        from: new Date(
          date.setDate(
            date.getDate() - date.getDay() + (date.getDay() === 0 ? -6 : 1),
          ),
        ),
        to: new Date(),
      });
    }
    if (selectedValue === 'this_month') {
      setDate({
        from: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
        to: new Date(),
      });
    }
  };

  useEffect(() => {
    fetchCouponTypes();
  }, []);

  useEffect(() => {
    setDateRange();
  }, [selectedValue]);

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
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Error during logout',
        className:
          'bg-red-100 text-red-600 border border-red-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
      });
    }
  };

  return (
    <div className="min-h-screen">
      <TopBar
        className="px-4 pt-3 sm:px-8"
        leftContent={
          <div className="flex items-center gap-3">
            <Link to="/login">
              <Logo className="h-10 w-10 cursor-pointer sm:h-12 sm:w-12" />
            </Link>
            <div className="text-lg font-bold sm:text-2xl" title={userName}>
              <span className="block sm:hidden">
                {userName.length > 10
                  ? `${userName.slice(0, 10)}...`
                  : userName}
              </span>
              <span className="hidden sm:block">{userName}</span>
            </div>{' '}
          </div>
        }
        rightContent={
          <div>
            <div className="flex items-center justify-between lg:hidden">
              <Button
                type="button"
                variant="outline"
                className="p-2"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
              >
                <Menu className="h-5 w-5" />
              </Button>
            </div>

            {isMenuOpen && (
              <div className="absolute right-4 z-50 mt-2 space-y-2 rounded-md bg-white p-4 shadow-lg lg:hidden">
                <Link to="/server" className="block">
                  <Button type="button" variant="outline" className="w-full">
                    Serve
                  </Button>
                </Link>
                <Link to="/menu" className="block">
                  <Button type="button" variant="outline" className="w-full">
                    Menu
                  </Button>
                </Link>
                <Button
                  variant="destructive"
                  onClick={handleLogout}
                  className="w-full"
                >
                  Logout
                </Button>
              </div>
            )}

            <div className="hidden gap-2 lg:flex">
              <Link to="/server" className="w-full">
                <Button type="button" variant="outline">
                  Serve
                </Button>
              </Link>
              <Link to="/menu" className="w-full">
                <Button type="button" variant="outline">
                  Menu
                </Button>
              </Link>
              <Button variant="destructive" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        }
      />
      <div className="mb-4 px-24">
        <Card className="my-6 flex flex-wrap items-center justify-between rounded-lg p-4 shadow-md ">
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
                      setDate({
                        from: selected?.from,
                        to: selected?.to,
                      });
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

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {cards.map((item: any, index: number) => (
            <Card key={index} className="rounded-lg border shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg font-bold">{item.name}</CardTitle>
                <CardDescription className="text-sm">
                  {`${Math.floor(item.start_hour / 100)}:${String(item.start_hour % 100).padStart(2, '0')}`}{' '}
                  -{' '}
                  {`${Math.floor(item.end_hour / 100)}:${String(item.end_hour % 100).padStart(2, '0')}`}
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

        <div className="mt-6 overflow-x-auto rounded-lg border p-4 shadow-lg">
          <DataTable columns={columns} data={data} />
        </div>
      </div>
    </div>
  );
}
