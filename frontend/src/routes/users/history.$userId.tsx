import { Logo } from '@/components/Logo';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useDialog } from '@/hooks/use-dialog';
import { UserContext } from '@/utils/auth/UserProvider';
import { DateRangeContext, DateRangeProvider } from '@/utils/DateRangeProvider';
import {
  PreviousCouponListContext,
  PreviousCouponListProvider,
} from '@/utils/PreviousCouponListProvider';
import { createFileRoute, Link } from '@tanstack/react-router';
import { format } from 'date-fns';
import { CalendarIcon } from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import { useContext, useState } from 'react';
import { DateRange } from 'react-day-picker';

export const Route = createFileRoute('/users/history/$userId')({
  component: HistoryWrapperComponent,
});
interface HistoryComponentProps {
  userId: string;
  page: number;
  setPage: React.Dispatch<React.SetStateAction<number>>;
}
function HistoryWrapperComponent() {
  const { userId } = Route.useParams();
  const [page, setPage] = useState(1);
  return (
    <DateRangeProvider>
      <PreviousCouponListProvider employee_id={userId} downPage={page}>
        <HistoryComponent
          key="history"
          userId={userId}
          page={page}
          setPage={setPage}
        />
      </PreviousCouponListProvider>
    </DateRangeProvider>
  );
}

function HistoryComponent({ userId, page, setPage }: HistoryComponentProps) {
  let { date, setDate } = useContext(DateRangeContext);
  const { showConfirmDialog } = useDialog();
  const { logout } = useContext(UserContext);
  const { previousCoupons, downcount } = useContext(PreviousCouponListContext);
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
  return (
    <div className="min-h-screen">
      <TopBar
        className="px-4 pt-3 sm:px-8"
        leftContent={
          <div className="flex items-center gap-3">
            <Link to="/login">
              <Logo className="h-10 w-10 cursor-pointer sm:h-12 sm:w-12" />
            </Link>
            <div className="text-lg font-bold sm:text-2xl">{userId}</div>
          </div>
        }
        rightContent={
          <div className="flex items-center gap-3">
            <Button variant="destructive" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        }
      />
      <div className="mx-4 my-4  flex  flex-col items-start justify-between gap-6  rounded-lg  p-4 shadow-lg">
        <Popover>
          <PopoverTrigger asChild>
            <Button
              id="date"
              variant="outline"
              className="flex items-center gap-4 rounded-full border border-gray-200 px-5 py-3 text-left font-medium shadow-md transition-all duration-200 hover:shadow-lg"
            >
              <CalendarIcon className="h-5 w-5 text-indigo-600" />
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
                <span className="">Select Date</span>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto rounded-lg p-0 shadow-xl">
            <Calendar
              initialFocus
              mode="range"
              defaultMonth={date?.from}
              selected={date}
              numberOfMonths={1}
              onSelect={(selected: DateRange | undefined) => {
                selected && setDate(selected);
              }}
              className="rounded-lg"
              disabled={(date) => date >= new Date()}
            />
          </PopoverContent>
        </Popover>

        <Table>
          {previousCoupons && previousCoupons.length > 0 ? (
            <TableCaption>A list of your Previous Coupons</TableCaption>
          ) : (
            <TableCaption>No Data at this moment.</TableCaption>
          )}
          <TableHeader>
            <TableRow>
              <TableHead className="w-[100px]">Meal</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Generation Time</TableHead>
              <TableHead>Coupon</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {previousCoupons.map((coupon, index) => (
              <TableRow
                key={
                  coupon.coupon_time +
                  '' +
                  coupon.coupon_date +
                  '' +
                  coupon.title
                }
              >
                <TableCell className="font-medium">{coupon.title}</TableCell>
                <TableCell>{coupon.coupon_date}</TableCell>
                <TableCell>
                  {coupon.coupon_time} ({coupon.creation.split(' ')[0]})
                </TableCell>
                <TableCell>
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button>Show Coupon</Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-[250px]">
                      <DialogHeader>
                        <DialogTitle>{`${previousCoupons[index].title} ${previousCoupons[index].coupon_date}`}</DialogTitle>
                        <DialogDescription>
                          <QRCodeSVG
                            value={`${previousCoupons[index].title}_${userId}_${previousCoupons[index].coupon_date}${previousCoupons[index].coupon_time}`}
                            size={200}
                            className="border-2 border-solid border-white"
                          />
                        </DialogDescription>
                      </DialogHeader>
                    </DialogContent>
                  </Dialog>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      {previousCoupons && previousCoupons.length > 0 && (
        <div className="flex items-center  justify-between  py-4">
          <div className="flex items-center justify-start space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                if (page - 1 < 1) {
                  return;
                } else {
                  setPage(page - 1);
                }
              }}
              disabled={page == 1}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page + 1)}
              disabled={
                downcount == 0 ||
                (!!downcount && page === Math.ceil(downcount / 10))
              }
            >
              Next
            </Button>
            <div>
              Showing page {page} out of{' '}
              {downcount && Math.ceil(downcount / 10)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
