import { Logo } from '@/components/Logo';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { PrevuousCouponCard } from '@/components/PreviousCouponCard';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
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
import { useContext, useState } from 'react';
import { DateRange } from 'react-day-picker';
import { useFrappeUpdateDoc } from 'frappe-react-sdk';
import { useToast } from '@/hooks/use-toast';
import CardPagination from '@/components/CardPagination';
import { ProtectedRoute } from '@/utils/auth/ProtectedRoute';

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
    <ProtectedRoute>
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
    </ProtectedRoute>
  );
}

function HistoryComponent({ userId, page, setPage }: HistoryComponentProps) {
  let { date, setDate } = useContext(DateRangeContext);
  const { showConfirmDialog } = useDialog();
  const { logout,userName } = useContext(UserContext);
  const { previousCoupons, downcount } = useContext(PreviousCouponListContext);
  const { toast } = useToast();
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
  const { updateDoc } = useFrappeUpdateDoc();
  const handleFeedbackSubmit = ({ coupon, selectedEmoji, feedback }: any) => {
    updateDoc('Hotpot Coupon', coupon.name, {
      emoji_reaction: selectedEmoji,
      feedback: feedback,
    })
      .then(() => {
        toast({
          title: 'Success',
          description: 'Feedback submitted successfully.',
          className:
            'bg-green-100 text-green-600 border border-green-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
        });
      })
      .catch(() => {
        toast({
          variant: 'destructive',
          title: 'Error',
          description: 'Error in submittin feedback.',
          className:
            'bg-red-100 text-red-600 border border-red-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
        });
      });
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
            <div className="text-lg font-bold sm:text-2xl">{userName}</div>
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
      <div className="mx-4 my-4  flex  flex-col items-center justify-center gap-6  rounded-lg  p-4 ">
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
        <div className=" grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {previousCoupons && previousCoupons.length === 0 && (
            <div className="w-full text-center">
              No previous coupons founds.
            </div>
          )}
          {previousCoupons &&
            previousCoupons.length > 0 &&
            previousCoupons.map((coupon: any) => (
              <PrevuousCouponCard
                key={coupon?.coupon_time + coupon?.coupon_date + coupon.title}
                coupon={coupon}
                handleFeedbackSubmit={handleFeedbackSubmit}
              />
            ))}
        </div>

        {previousCoupons && previousCoupons.length > 0 && (
          <CardPagination
            page={page}
            totalPages={downcount}
            onPageChange={setPage}
          />
        )}
      </div>
    </div>
  );
}
