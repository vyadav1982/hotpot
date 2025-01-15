import { createFileRoute } from '@tanstack/react-router';
import { useState, useCallback, useEffect, useContext } from 'react';
import QrReader from 'react-qr-reader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useFrappePostCall, useFrappeUpdateDoc } from 'frappe-react-sdk';
import { ErrorBanner } from '@/components/ErrorBanner';
import { Camera, CookingPot, Loader2, Menu, TriangleAlert } from 'lucide-react';
import { coupon_from_info, extractCouponInfo } from '@/utils/coupon';
import { useDialog } from '@/hooks/use-dialog';
import { HotpotCoupon } from '@/types/Hotpot/HotpotCoupon';
import { ProtectedRoute } from '@/utils/auth/ProtectedRoute';
import { UserContext } from '@/utils/auth/UserProvider';
import { TopBar } from '@/components/TopBar';
import { Link } from '@tanstack/react-router';
import { Logo } from '@/components/Logo';
import { useToast } from '@/hooks/use-toast';

export const Route = createFileRoute('/server')({
  component: () => (
    <ProtectedRoute>
      <ServerPage />
    </ProtectedRoute>
  ),
});

type MealTiming = {
  name: string;
  start_hour: number;
  end_hour: number;
  buffer_time: number;
};

function ServerPage() {
  const { currentUser, logout, userName } = useContext(UserContext);
  const [scanning, setScanning] = useState(false);
  const [scannedData, setScannedData] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [couponExists, setCouponExists] = useState<boolean | null>(null);
  const [delayScan] = useState(500);
  const [isReaderReady, setIsReaderReady] = useState(false);
  const { updateDoc, loading } = useFrappeUpdateDoc();
  const [couponType, setCouponType] = useState<MealTiming[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const [disableServe, setDisableServe] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { call: getCouponType } = useFrappePostCall(
    'hotpot.api.dashboard.get_coupon_type_list',
  );
  const [couponDoc, setCouponDoc] = useState<HotpotCoupon | undefined>(
    undefined,
  );
  const { showConfirmDialog } = useDialog();

  const { call: checkCouponExists, error: apiError } = useFrappePostCall(
    'hotpot.api.coupon.coupon_exists',
  );

  const handleScan = useCallback(
    async (data: string | null) => {
      if (data) {
        setScanning(false);
        setScannedData(data);
        setIsLoading(true);
        const processedData = extractCouponInfo(data);
        if (processedData) {
          try {
            const response = await checkCouponExists({
              name: processedData,
            });
            if (response.message) {
              setIsLoading(false);
              setCouponDoc(response.message);
            } else {
              setCouponDoc(undefined);
              setIsLoading(false);
            }
          } catch (error) {
            console.error('Error checking coupon:', error);
            setError('Error checking coupon status. Please try again.');
            setCouponExists(null);
            setIsLoading(false);
          }
        } else {
          setIsLoading(false);
        }
      }
    },
    [checkCouponExists],
  );

  const handleError = useCallback((err: unknown) => {
    console.error('QR Scanner error:', err);
    setError(
      'Error accessing camera. Please make sure camera permissions are granted and try again.',
    );
    setScanning(false);
  }, []);

  const handleReset = useCallback(() => {
    setScanning(false);
    setIsReaderReady(false);
    setScannedData(null);
    setCouponExists(null);
    setCouponDoc(undefined);
    setError(null);
  }, []);

  const handleStopScanner = useCallback(() => {
    setScanning(false);
    setIsReaderReady(false);
  }, []);

  const startScanner = useCallback(() => {
    setError(null);
    setScanning(true);
    setTimeout(() => setIsReaderReady(true), 100);
  }, []);

  function formatHour(hour: any) {
    const h = Math.floor(hour / 100);
    const m = hour % 100;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
  }

  async function handleServeCoupon(couponDoc: any) {
    setDisableServe(false);
    return new Promise<void>((resolve, reject) => {
      updateDoc('Hotpot Coupon', couponDoc.name, {
        docstatus: 1,
        served_by: currentUser,
        status: 'Redeemed',
      })
        .then(() => {
          resolve();
          setDisableServe(true);
          toast({
            title: 'Success',
            description: `Meal served successfully.`,
            className:
              'bg-green-100 text-green-600 border border-green-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
          });
        })
        .catch((error) => {
          toast({
            variant: 'destructive',
            title: `Error`,
            description: "Couldn't serve meal. Please try again.",
            className:
              'bg-red-100 text-red-600 border border-red-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
          });
          reject(error);
          setError(error);
        });
    });
  }

  function getMealTimeRange(title: string | undefined) {
    const meal = couponType.find((meal) => meal.name === title);
    if (!meal) {
      return { startHour: 0, endHour: 0 };
    }

    return { startHour: meal.start_hour, endHour: meal.end_hour };
  }
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

  useEffect(() => {
    const fetchCouponTypes = async () => {
      const response = await getCouponType({});
      setCouponType(response.message);
    };
    return () => {
      fetchCouponTypes();
      setScanning(false);
      setIsReaderReady(false);
    };
  }, []);

  return (
    <div className="flex min-h-screen flex-col">
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
              <div className="absolute right-4 mt-2 space-y-2 rounded-md bg-white p-4 shadow-lg lg:hidden">
                <Link to="/dashboard" className="block">
                  <Button type="button" variant="outline" className="w-full">
                    Dashboard
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
              <Link to="/dashboard" className="w-full">
                <Button type="button" variant="outline">
                  Dashboard
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

      <div className="container mx-auto flex-1 p-4">
        <Card className="mx-auto w-full max-w-md">
          <CardHeader>
            {scannedData && couponExists === false ? (
              <CardTitle className="text-center">Serving Now</CardTitle>
            ) : (
              <CardTitle className="text-center">Scan QR codes here</CardTitle>
            )}
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <ErrorBanner error={apiError} />

              {error && (
                <Alert variant="destructive">
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {!scanning && !scannedData && (
                <Button onClick={startScanner} className="w-full" size="lg">
                  <Camera className="mr-2 h-5 w-5" />
                  Start Scanner
                </Button>
              )}

              {scanning && isReaderReady && (
                <div className="space-y-2">
                  <div className="aspect-square overflow-hidden rounded-lg">
                    <QrReader
                      delay={delayScan}
                      facingMode="environment"
                      onError={handleError}
                      onScan={handleScan}
                    />
                  </div>
                  <Button
                    onClick={handleStopScanner}
                    variant="outline"
                    className="w-full"
                  >
                    Stop Scanner
                  </Button>
                </div>
              )}

              {isLoading ? (
                <div className="flex items-center justify-center">
                  <Loader2 className="h-12 w-12 animate-spin text-primary" />
                </div>
              ) : (
                scannedData && (
                  <div className="space-y-4">
                    {(() => {
                      const couponInfo = coupon_from_info(scannedData);

                      if (!couponInfo) {
                        return (
                          <Alert className="bg-red-300">
                            <AlertTitle className="flex items-center gap-2">
                              <TriangleAlert className="text-red-600" />
                              ERROR: Invalid Coupon Scanned
                            </AlertTitle>
                            <AlertDescription>
                              <p>
                                The scanned data does not match any valid coupon
                                format.
                              </p>
                            </AlertDescription>
                          </Alert>
                        );
                      }

                      if (!couponDoc) {
                        return (
                          <Alert className="bg-red-300">
                            <AlertTitle className="flex items-center gap-2">
                              <TriangleAlert className="text-red-600" />
                              ERROR: Coupon Not Found
                            </AlertTitle>
                            <AlertDescription>
                              <p>The coupon does not exist in our records.</p>
                            </AlertDescription>
                          </Alert>
                        );
                      }

                      const { coupon_date, coupon_time, title } = couponInfo;
                      const { startHour, endHour } = getMealTimeRange(title);
                      const currentTime = new Date();
                      if (
                        new Date().toISOString().split('T')[0] !== coupon_date
                      ) {
                        return (
                          <Alert className="bg-yellow-400">
                            <AlertTitle className="flex items-center gap-2">
                              <TriangleAlert className="text-yellow-600" />
                              NOTICE: Coupon Not Valid for Today
                            </AlertTitle>
                            <AlertDescription>
                              <p>The coupon is valid only for {coupon_date}.</p>
                            </AlertDescription>
                          </Alert>
                        );
                      }

                      const currentHour = parseInt(
                        `${currentTime.getHours()}${currentTime.getMinutes().toString().padStart(2, '0')}`,
                      );
                      if (currentHour < startHour) {
                        return (
                          <Alert className="bg-blue-300">
                            <AlertTitle className="flex items-center gap-2">
                              <TriangleAlert className="text-blue-600" />
                              NOTICE: Too Early to Serve
                            </AlertTitle>
                            <AlertDescription>
                              <p>
                                Please come between {formatHour(startHour)} and{' '}
                                {formatHour(endHour)} to redeem this meal.
                              </p>
                            </AlertDescription>
                          </Alert>
                        );
                      }

                      if (currentHour > endHour) {
                        return (
                          <Alert className="bg-red-300">
                            <AlertTitle className="flex items-center gap-2">
                              <TriangleAlert className="text-red-600" />
                              ERROR: Meal Serving Time Passed
                            </AlertTitle>
                            <AlertDescription>
                              <p>
                                The meal serving time for this coupon has ended.
                              </p>
                            </AlertDescription>
                          </Alert>
                        );
                      }

                      if (couponDoc.docstatus === 1) {
                        return (
                          <Alert className="bg-red-300">
                            <AlertTitle className="flex items-center gap-2">
                              <TriangleAlert className="text-red-600" />
                              ERROR: Coupon Already Consumed
                            </AlertTitle>
                            <AlertDescription>
                              <>
                                <p>Type: {couponDoc.title}</p>
                                <p>Served By: {couponDoc.served_by}</p>
                                <p>
                                  Serving Time:{' '}
                                  {couponDoc.modified.slice(10).slice(0, 9)}
                                </p>
                              </>
                            </AlertDescription>
                          </Alert>
                        );
                      }

                      return (
                        <>
                          <Alert className="bg-green-300">
                            <AlertTitle className="flex items-center gap-2">
                              <CookingPot className="text-green-600" />
                              SUCCESS: Meal Ready to Be Served
                            </AlertTitle>
                            <AlertDescription>
                              <>
                                <p>Type: {title}</p>
                                <p>Time: {coupon_time}</p>
                                <p>Date: {coupon_date}</p>
                              </>
                            </AlertDescription>
                          </Alert>
                          {!loading ? (
                            <Button
                              onClick={() => handleServeCoupon(couponDoc)}
                              className="w-full"
                            >
                              Serve Meal
                            </Button>
                          ) : (
                            <Button
                              onClick={() => handleServeCoupon(couponDoc)}
                              className="w-full"
                            >
                              <Loader2 className="animate-spin" />
                              Serving Meal....
                            </Button>
                          )}
                        </>
                      );
                    })()}

                    <Button
                      onClick={handleReset}
                      variant="outline"
                      className="w-full"
                    >
                      Scan Another
                    </Button>
                  </div>
                )
              )}
            </div>
          </CardContent>
        </Card>
        <div className="mx-auto w-full max-w-md">
          <ErrorBanner error={apiError} />
        </div>
      </div>
    </div>
  );
}
