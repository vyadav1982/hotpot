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
import { createFileRoute } from '@tanstack/react-router';
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
export const Route = createFileRoute('/dashboard')({
  component: () => {
    const [date, setDate] = useState<DateRange | undefined>({
      from: new Date(),
      to: new Date(),
    });
    return (
      <CouponProvider date={date}>
        <CouponCountProvider date={date}>
          <RouteComponent setDate={setDate} date={date} />
        </CouponCountProvider>
      </CouponProvider>
    );
  },
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
interface RouteComponentProps {
  setDate: React.Dispatch<React.SetStateAction<DateRange | undefined>>;
  date: DateRange | undefined;
}
function RouteComponent({ setDate, date }: RouteComponentProps) {
  const [cards, setCards] = useState([]);
  const [selectedValue, setSelectedValue] = useState('today');
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

  const { coupons } = useContext(CouponContext);
  const { CouponsCount } = useContext(CouponCountContext);
  const data = convertMapToArray(coupons);
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
      setDate(date);
    }
    if (selectedValue === 'this_week') {
      let date = new Date();
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
        from: new Date(2024, new Date().getMonth(), 1),
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
  return (
    <div className="min-h-screen bg-[#040917] p-6 text-white">
      {/* Header Section */}
      <div className="mb-6 flex flex-wrap items-center justify-between rounded-lg bg-[#0e1a30] p-4 shadow-lg">
        <div className="flex items-center gap-4">
          {
            <div>
              {'Total Consumed Coupons : '}
              {CouponsCount.total_coupons}
            </div>
          }
          {selectedValue === 'custom' && (
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  id="date"
                  variant={'outline'}
                  className={cn(
                    'flex w-[300px] items-center justify-start gap-2 rounded-md border border-[#1e2d48] bg-[#131c2b] text-left font-medium text-white shadow-md hover:bg-[#1a273b]',
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
              <PopoverContent className="w-auto rounded-lg border border-[#1e2d48] bg-[#131c2b] p-0 shadow-lg">
                <Calendar
                  initialFocus
                  mode="range"
                  defaultMonth={date?.from}
                  selected={date}
                  onSelect={setDate}
                  numberOfMonths={2}
                  className="p-2"
                />
              </PopoverContent>
            </Popover>
          )}
        </div>
        <Select value={selectedValue} onValueChange={setSelectedValue}>
          <SelectTrigger className="w-[180px] rounded-md border border-[#1e2d48] bg-[#131c2b] font-medium text-white shadow-md hover:bg-[#1a273b]">
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

      {/* Cards Section */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {cards.map((item: any, index: number) => (
          <Card
            key={index}
            className="rounded-lg border border-[#1e2d48] bg-[#0e1a30] shadow-lg transition-transform hover:scale-105 hover:shadow-xl"
          >
            <CardHeader>
              <CardTitle className="text-lg font-bold text-white">
                {item.name}
              </CardTitle>
              <CardDescription className="text-sm text-[#9da6b4]">
                {item.start_hour} - {item.end_hour}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {item.name === 'Breakfast' && (
                <p className="text-sm text-[#c5cedd]">
                  Total Consumed Coupon: {CouponsCount.breakfast_coupons}
                </p>
              )}
              {item.name === 'Lunch' && (
                <p className="text-sm text-[#c5cedd]">
                  Total Consumed Coupon: {CouponsCount.lunch_coupons}
                </p>
              )}
              {item.name === 'Evening Snack' && (
                <p className="text-sm text-[#c5cedd]">
                  Total Consumed Coupon : {CouponsCount.evening_snacks_coupons}
                </p>
              )}
              {item.name === 'Dinner' && (
                <p className="text-sm text-[#c5cedd]">
                  Total Consumed Coupon: {CouponsCount.dinner_coupons}
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Table Section */}
      <div className="mt-6 rounded-lg border border-[#1e2d48] bg-[#0e1a30] p-4 shadow-lg">
        <DataTable columns={columns} data={data} />
      </div>
    </div>
  );
}
