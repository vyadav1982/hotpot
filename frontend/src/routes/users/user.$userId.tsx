import { Logo } from '@/components/Logo';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { useDialog } from '@/hooks/use-dialog';
import { UserContext } from '@/utils/auth/UserProvider';
import { createFileRoute, Link } from '@tanstack/react-router';
import { format, parse } from 'date-fns';
import {
  useFrappeDeleteDoc,
  useFrappeGetDoc,
  useFrappePostCall,
  useFrappePutCall,
  useFrappeUpdateDoc,
} from 'frappe-react-sdk';
import {
  ArrowUpRight,
  Badge,
  BadgeMinus,
  BadgePlus,
  CalendarIcon,
  Loader2,
  LogOut,
  Wallet,
} from 'lucide-react';
import { useContext, useEffect, useState } from 'react';
import { DateRange } from 'react-day-picker';
import { useToast } from '@/hooks/use-toast';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  UpcomingCouponListContext,
  UpcomingCouponListProvider,
} from '@/utils/UpcomingCouponListProvider';
import { QRCodeSVG } from 'qrcode.react';
import {
  PreviousCouponListContext,
  PreviousCouponListProvider,
} from '@/utils/PreviousCouponListProvider';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Qr } from '@/components/Qr';
import { PrevuousCouponCard } from '@/components/PreviousCouponCard';
import { ConfirmMealCancelButtons } from '@/components/ConfirmMealCancelButtons';
import CardPagination from '@/components/CardPagination';
import { ProtectedRoute } from '@/utils/auth/ProtectedRoute';
import Menu from '@/components/Menu';
export const Route = createFileRoute('/users/user/$userId')({
  component: UserWrapperComponent,
});
interface UserComponentProps {
  setDate: React.Dispatch<React.SetStateAction<DateRange | undefined>>;
  date: DateRange | undefined;
  userId: string;
  upPage: number;
  setUpPage: React.Dispatch<React.SetStateAction<number>>;
  downPage: number;
  setDownPage: React.Dispatch<React.SetStateAction<number>>;
}

function UserWrapperComponent() {
  const [date, setDate] = useState<DateRange | undefined>({
    from: new Date(),
    to: new Date(),
  });
  const { userId } = Route.useParams();
  const [upPage, setUpPage] = useState(1);
  const [downPage, setDownPage] = useState(1);
  return (
    <ProtectedRoute>
      <UpcomingCouponListProvider employee_id={userId} upPage={upPage}>
        <PreviousCouponListProvider employee_id={userId} downPage={downPage}>
          <UserComponent
            setDate={setDate}
            date={date}
            userId={userId}
            upPage={upPage}
            setUpPage={setUpPage}
            downPage={downPage}
            setDownPage={setDownPage}
          />
        </PreviousCouponListProvider>
      </UpcomingCouponListProvider>
    </ProtectedRoute>
  );
}
function UserComponent({
  setDate,
  date,
  userId,
  setUpPage,
  upPage,
  downPage,
  setDownPage,
}: UserComponentProps) {
  const { logout, userName } = useContext(UserContext);
  const { showConfirmDialog } = useDialog();
  const [cards, setCards] = useState([]);
  const [selectedValue, setSelectedValue]: any = useState([]);
  const { toast } = useToast();
  let { upcomingCoupons, upcount } = useContext(UpcomingCouponListContext);
  const { previousCoupons, downcount } = useContext(PreviousCouponListContext);
  const [token, setToken] = useState(-1);
  const [couponHistory, setCouponHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('generate_coupon');
  const { call: getCouponType } = useFrappePostCall(
    'hotpot.api.dashboard.get_coupon_type_list',
  );
  const { call: getCouponsHistory } = useFrappePostCall(
    'hotpot.api.users.get_coupons_history',
  );
  const { call: updateCouponCount } = useFrappePutCall(
    'hotpot.api.users.update_coupon_count',
  );
  const { deleteDoc } = useFrappeDeleteDoc();

  const {
    call: generateCoupon,
    error: couponError,
    loading,
  } = useFrappePostCall('hotpot.api.coupon.create_coupon');
  const fetchCouponTypes = async () => {
    const response = await getCouponType({});
    setCards(response.message);
  };
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
        description: 'Error during logout.',
        className:
          'bg-red-100 text-red-600 border border-red-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
      });
    }
  };
  const handleClickDiv = (e: any) => {
    const newValue =
      e.target.innerText === 'Snacks' ? 'Evening Snack' : e.target.innerText;

    const val = selectedValue.find((value: any) => value == newValue);
    setSelectedValue((prevSelected: string[]) => {
      let updatedSelected = [...prevSelected, newValue];
      // use confgiurable value
      if (updatedSelected.length > 2) {
        updatedSelected.shift();
      }
      updatedSelected = updatedSelected.filter((v) => v !== val);

      return updatedSelected;
    });
  };
  const handleGenerateCoupon = async () => {
    if (!date?.from || !date?.to) {
      toast({
        variant: 'destructive',
        title: 'Warning',
        description: 'Please select a date range.',
        className:
          'bg-red-100 text-red-600 border border-red-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
      });
      return;
    }
    try {
      const response = await generateCoupon({
        params: {
          employee_id: userId,
          from_date: date?.from?.toLocaleDateString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
          }),
          to_date: date?.to?.toLocaleDateString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
          }),
          meal_type: selectedValue,
        },
      });

      const count = response.message.pop();
      setToken(count);
      if (response.message.length >= 1) {
        response.message.forEach((msg: string) => {
          toast({
            variant: 'destructive',
            title: `Error`,
            description: msg,
            className:
              'bg-red-100 text-red-600 border border-red-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
          });
        });
      } else {
        toast({
          title: 'Success',
          description: `Coupons have been generated successfully.`,
          className:
            'bg-green-100 text-green-600 border border-green-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
        });
      }
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Error in generating coupon.',
        className:
          'bg-red-100 text-red-600 border border-red-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
      });
    }
  };
  const handleCancelMeal = async (cancelMeal: any) => {
    const currentMealBuffer: any = cards.filter(
      (c: any) => c.name == cancelMeal.title,
    );
    const hour = new Date().getHours();
    const mint = new Date().getMinutes();
    if (
      new Date().toISOString().split('T')[0] == cancelMeal.coupon_date &&
      (Math.abs(hour * 100 + mint - currentMealBuffer[0].start_hour) <=
        currentMealBuffer[0].buffer_time * 100 ||
        hour * 100 + mint >= currentMealBuffer[0].start_hour ||
        hour * 100 + mint >= currentMealBuffer[0].end_hour)
    ) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Cannot cancel the coupon at this moment.',
        className:
          'bg-red-100 text-red-600 border border-red-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
      });
      return;
    }
    const message = deleteDoc('Hotpot Coupon', cancelMeal.name);
    message
      .then(() => {
        updateCouponCount({
          params: {
            token: (token + 1).toString(),
            userId: userId,
            coupon: cancelMeal,
          },
        })
          .then(() => {
            setToken(token + 1);
            toast({
              title: 'Success',
              description: 'Coupon count has been updated successfully.',
              className:
                'bg-green-100 text-green-600 border border-green-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
            });
          })
          .catch(() => {
            toast({
              variant: 'destructive',
              title: 'Error',
              description: 'Failed to update the coupon count.',
              className:
                'bg-red-100 text-red-600 border border-red-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
            });
          });
        toast({
          title: 'Success',
          description: 'Coupon has been cancelled successfully.',
          className:
            'bg-green-100 text-green-600 border border-green-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
        });
      })
      .catch(() => {
        toast({
          variant: 'destructive',
          title: 'Error',
          description: 'Failed to cancel the coupon.',
          className:
            'bg-red-100 text-red-600 border border-red-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
        });
      });
  };
  const { updateDoc } = useFrappeUpdateDoc();
  const handleFeedbackSubmit = ({
    coupon,
    selectedEmoji,
    feedback,
  }: any): Promise<string> => {
    return new Promise((resolve, reject) => {
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
          resolve('submitted');
        })
        .catch(() => {
          toast({
            variant: 'destructive',
            title: 'Error',
            description: 'Error in submitting feedback.',
            className:
              'bg-red-100 text-red-600 border border-red-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
          });
          reject('error');
        });
    });
  };
  const { data } = useFrappeGetDoc('Hotpot User', userId);
  useEffect(() => {
    const fetchCouponHistory = async () => {
      const response = await getCouponsHistory({ employee_id: userId });
      response.message.sort(
        (a: { creation: string }, b: { creation: string }) => {
          const dateA = new Date(a.creation).getTime();
          const dateB = new Date(b.creation).getTime();
          return dateB - dateA;
        },
      );
      setCouponHistory(response.message);
    };
    fetchCouponHistory();
    fetchCouponTypes();
    data && setToken(data.coupon_count);
  }, [data]);

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
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-3 p-4 ">
              {token >= 0 ? (
                <>
                  <div
                    className={`rounded-full p-3 ${
                      token > 50
                        ? 'bg-green-100 text-green-600'
                        : token > 20
                          ? 'bg-yellow-100 text-yellow-600'
                          : 'bg-red-100 text-red-600'
                    }`}
                  >
                    <Wallet
                      className={`h-6 w-6 ${
                        token > 50
                          ? 'text-green-600'
                          : token > 20
                            ? 'text-yellow-600'
                            : 'text-red-600'
                      }`}
                    />
                  </div>
                  <span className="hidden text-sm font-semibold sm:block ">
                    Coupon Count:
                  </span>
                  <span className="text-sm font-semibold ">{token}</span>
                </>
              ) : (
                <Loader2 className="animate-spin" />
              )}
            </div>
            <Button
              variant="destructive"
              className="hidden sm:block"
              onClick={handleLogout}
            >
              Logout
            </Button>
            <button className="block sm:hidden" onClick={handleLogout}>
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        }
      />
      <Tabs
        defaultValue="generate_coupon"
        value={activeTab}
        onValueChange={setActiveTab}
      >
        <TabsList className="hide-scrollbar flex items-start justify-center overflow-x-scroll pl-20">
          <TabsTrigger value="generate_coupon" className="tabs-trigger">
            Generate
          </TabsTrigger>
          <TabsTrigger value="upcoming_coupons" className="tabs-trigger">
            Upcoming
          </TabsTrigger>
          <TabsTrigger
            value="previously_generated_coupons"
            className="tabs-trigger"
          >
            Feedback
          </TabsTrigger>
          <TabsTrigger value="see_transaction_history" className="tabs-trigger">
            Transactions
          </TabsTrigger>
          <TabsTrigger value="menu_list" className="tabs-trigger">
            Menu
          </TabsTrigger>
        </TabsList>

        <TabsContent
          value="generate_coupon"
          className="tab-content rounded-lg  p-4"
        >
          <div className="flex flex-col gap-6 rounded-lg p-6 shadow-lg">
            <div className="flex items-center  justify-center">
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
                      <span className="text-gray-500">Select Date</span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto rounded-lg p-0 shadow-xl">
                  <Calendar
                    initialFocus
                    mode="range"
                    defaultMonth={date?.from}
                    selected={date}
                    onSelect={setDate}
                    numberOfMonths={1}
                    className="rounded-lg"
                    disabled={(date) =>
                      date <=
                        new Date(
                          new Date().setDate(new Date().getDate() - 1),
                        ) ||
                      date >
                        new Date(
                          new Date().getFullYear(),
                          new Date().getMonth() + 1,
                          0,
                        )
                    }
                  />
                </PopoverContent>
              </Popover>
            </div>
            <div className="flex flex-wrap justify-center gap-6">
              {cards.map((card: any) => (
                <div
                  key={card.name}
                  className={`border border-gray-300 ${selectedValue.includes(card.name) ? 'border-2 border-indigo-700' : ''} group relative flex h-32 w-32 transform cursor-pointer items-center justify-center rounded-xl transition-all duration-300 ease-in-out hover:scale-110`}
                  onClick={(e) => handleClickDiv(e)}
                >
                  <div className="z-10 text-lg font-semibold">
                    {card.name !== 'Evening Snack' ? card.name : 'Snacks'}
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-8 flex justify-center">
              {!loading ? (
                <Button
                  className="transform  font-semibold shadow-2xl transition-transform duration-300 hover:scale-105 "
                  disabled={selectedValue.length == 0}
                  onClick={handleGenerateCoupon}
                >
                  Generate Coupons
                </Button>
              ) : (
                <Button className="transform  font-semibold shadow-2xl transition-transform duration-300 hover:scale-105 ">
                  <Loader2 className="animate-spin" />
                  Generating Coupons....
                </Button>
              )}
            </div>
          </div>
        </TabsContent>
        <TabsContent value="upcoming_coupons">
          <div className="mx-4 grid grid-cols-1 gap-6 p-8 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {upcomingCoupons && upcomingCoupons.length === 0 && (
              <div className="text-center">No upcoming coupons found.</div>
            )}
            {upcomingCoupons &&
              upcomingCoupons.length > 0 &&
              upcomingCoupons.map((coupon, index) => (
                <Dialog key={coupon.name}>
                  <DialogTrigger asChild>
                    <Card
                      key={coupon.name}
                      className="transform rounded-lg shadow-lg transition-transform duration-200 ease-in-out hover:scale-105 hover:cursor-pointer"
                    >
                      <CardHeader className="p-0 pt-4">
                        <CardTitle className="flex items-center justify-between text-lg font-semibold">
                          <div className="mx-4 flex-1 overflow-clip text-left">
                            {coupon.title}
                          </div>
                          {coupon.coupon_status && (
                            <div
                              className="mx-4 rounded-full bg-yellow-300 px-3 py-1 text-sm font-normal text-black lg:mx-2
                              "
                            >
                              {coupon.coupon_status.toUpperCase()}
                            </div>
                          )}
                        </CardTitle>
                        <CardDescription className="mt-2 text-center text-sm ">
                          {new Date(coupon.coupon_date).toLocaleDateString(
                            'en-GB',
                            {
                              day: '2-digit',
                              month: 'short',
                              year: 'numeric',
                            },
                          )}
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="flex justify-center p-0 blur-[1.5px]">
                        <Qr />
                      </CardContent>
                    </Card>
                  </DialogTrigger>
                  <DialogContent className="mx-auto max-w-md rounded-lg p-6 shadow-lg">
                    <DialogTitle></DialogTitle>
                    <DialogHeader>
                      <DialogDescription className="text-center">
                        <div className="mb-2 flex justify-center">
                          <QRCodeSVG
                            value={`${upcomingCoupons[index].title}_${userId}_${upcomingCoupons[index].coupon_date}${upcomingCoupons[index].coupon_time}`}
                            size={200}
                            className=" border border-white"
                          />
                        </div>
                        <ConfirmMealCancelButtons
                          handleCancel={() =>
                            handleCancelMeal(upcomingCoupons[index])
                          }
                        />
                      </DialogDescription>
                    </DialogHeader>
                    <DialogFooter />
                  </DialogContent>
                </Dialog>
              ))}
          </div>
          {upcomingCoupons && upcomingCoupons.length > 0 && (
            <CardPagination
              page={upPage}
              totalPages={upcount}
              onPageChange={setUpPage}
            />
          )}
        </TabsContent>

        <TabsContent value="previously_generated_coupons">
          <div className="mx-4 grid grid-cols-1 gap-6 p-8 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
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
            <div className="flex flex-col items-center  justify-center gap-4 py-8">
              <div className="flex items-center gap-4">
                <Button
                  className="disabled:cursor-crosshair"
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    if (downPage - 1 < 1) {
                      return;
                    } else {
                      setDownPage(downPage - 1);
                    }
                  }}
                  disabled={downPage == 1}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setDownPage(downPage + 1)}
                  disabled={
                    downcount == 0 ||
                    (!!downcount && downPage === Math.ceil(downcount / 10))
                  }
                >
                  Next
                </Button>
                <div>
                  Page {downPage} - {downcount && Math.ceil(downcount / 10)}
                </div>
              </div>
              <div>
                <Link to={`/users/history/${userId}`}>
                  <Button size="sm" variant="outline">
                    Flashback
                    <ArrowUpRight />
                  </Button>
                </Link>
              </div>
            </div>
            // </div>
          )}
        </TabsContent>
        <TabsContent
          value="see_transaction_history"
          className="tab-content rounded-lg p-4 md:p-8"
        >
          <div className="relative border-l-2 border-gray-300 pl-4">
            {couponHistory.length === 0 && (
              <div className="text-center">No transaction history found.</div>
            )}
            {couponHistory &&
              couponHistory.map((history: any, index: number) =>
                'employee_id' in history ? (
                  <div key={`history-${index}`} className="mb-6 ml-4">
                    <div
                      className={`flex items-center justify-start space-x-4 ${
                        history.type === 'Creation'
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}
                    >
                      {history.type === 'Creation' ? (
                        <BadgePlus className="h-6 w-6" />
                      ) : (
                        <BadgeMinus className="h-6 w-6" />
                      )}
                      <div className="font-medium">{history.message}</div>
                    </div>
                    <div className="ml-10 text-sm ">
                      on{' '}
                      {format(
                        parse(
                          history.creation.split('.')[0],
                          'yyyy-MM-dd HH:mm:ss',
                          new Date(),
                        ),
                        'dd MMM yyyy h:mm a',
                      )}
                    </div>
                  </div>
                ) : (
                  'docname' in history &&
                  (() => {
                    const data = JSON.parse(history.data);
                    return (
                      <div key={`history-${index}`} className="mb-6 ml-4">
                        {data.changed.map((item: any, idx: number) => (
                          <div
                            key={`changed-${idx}`}
                            className="mb-4 flex items-start"
                          >
                            <Badge className="h-6 w-6 text-blue-600" />
                            <div className="ml-4">
                              <div className="font-medium ">
                                {history.modified_by} changed{' '}
                                <span className="font-bold ">
                                  {item[0].split('_')[0] +
                                    ' ' +
                                    item[0].split('_')[1]}
                                </span>{' '}
                                from{' '}
                                <span className="italic text-gray-600">
                                  {item[1]}
                                </span>{' '}
                                to{' '}
                                <span className="italic text-gray-600">
                                  {item[2]}
                                </span>
                              </div>
                              <div className="mt-1 text-sm text-gray-500">
                                on{' '}
                                {format(
                                  parse(
                                    history.creation.split('.')[0],
                                    'yyyy-MM-dd HH:mm:ss',
                                    new Date(),
                                  ),
                                  'dd MMM yyyy h:mm a',
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                        {data.added.map((item: any, idx: number) => (
                          <div
                            key={`added-${idx}`}
                            className="mb-4 flex items-start"
                          >
                            <Badge className="h-6 w-6 text-green-600" />
                            <div className="ml-4">
                              <div className="font-medium ">
                                {history.modified_by} added{' '}
                                <span className="font-bold text-gray-900">
                                  {item[0].split('_')[0] +
                                    ' ' +
                                    item[0].split('_')[1]}
                                </span>{' '}
                                with value{' '}
                                <span className="italic text-gray-600">
                                  {item[1]}
                                </span>
                              </div>
                              <div className="mt-1 text-sm text-gray-500">
                                on{' '}
                                {format(
                                  parse(
                                    history.creation.split('.')[0],
                                    'yyyy-MM-dd HH:mm:ss',
                                    new Date(),
                                  ),
                                  'dd MMM yyyy h:mm a',
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                        {data.removed.map((item: any, idx: number) => (
                          <div
                            key={`removed-${idx}`}
                            className="mb-4 flex items-start"
                          >
                            <Badge className="h-6 w-6 text-red-600" />
                            <div className="ml-4">
                              <div className="font-medium ">
                                {history.modified_by} removed{' '}
                                <span className="font-bold text-gray-900">
                                  {item[0].split('_')[0] +
                                    ' ' +
                                    item[0].split('_')[1]}
                                </span>{' '}
                                which was{' '}
                                <span className="italic text-gray-600">
                                  {item[1]}
                                </span>
                              </div>
                              <div className="mt-1 text-sm text-gray-500">
                                on{' '}
                                {format(
                                  parse(
                                    history.creation.split('.')[0],
                                    'yyyy-MM-dd HH:mm:ss',
                                    new Date(),
                                  ),
                                  'dd MMM yyyy h:mm a',
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    );
                  })()
                ),
              )}
          </div>
        </TabsContent>
        <TabsContent
          value="menu_list"
          className="tab-content rounded-lg p-4 md:p-8"
        >
          <Menu />
        </TabsContent>
      </Tabs>
    </div>
  );
}
