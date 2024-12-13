import { createFileRoute } from '@tanstack/react-router';
import { useState, useCallback, useEffect, useContext } from 'react';
import QrReader from 'react-qr-reader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useFrappePostCall } from 'frappe-react-sdk';
import { ErrorBanner } from '@/components/ErrorBanner';
import { Camera, CookingPot, TriangleAlert } from 'lucide-react';
import {
  coupon_from_info,
  extractCouponInfo,
  is_coupon_valid,
} from '@/utils/coupon';
import { useDialog } from '@/hooks/use-dialog';
import { HotpotCoupon } from '@/types/Hotpot/HotpotCoupon';
import { ProtectedRoute } from '@/utils/auth/ProtectedRoute';
import { UserContext } from '@/utils/auth/UserProvider';
import { TopBar } from '@/components/TopBar';
import { Link } from '@tanstack/react-router';
import useCurrentCouponType from '@/hooks/useCurrentCouponType';

export const Route = createFileRoute('/server')({
  component: () => (
    <ProtectedRoute>
      <ServerPage />
    </ProtectedRoute>
  ),
});

function ServerPage() {
  const { currentUser, logout } = useContext(UserContext);
  const { currentCouponType } = useCurrentCouponType();
  const [scanning, setScanning] = useState(false);
  const [scannedData, setScannedData] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [couponExists, setCouponExists] = useState<boolean | null>(null);
  const [delayScan] = useState(500);
  const [isReaderReady, setIsReaderReady] = useState(false);
  const [couponDoc, setCouponDoc] = useState<HotpotCoupon | undefined>(
    undefined,
  );
  const { showConfirmDialog } = useDialog();

  const { call: checkCouponExists, error: apiError } = useFrappePostCall(
    'hotpot.api.coupon.coupon_exists',
  );

  const {
    call: createCoupon,
    error: apiCreateError,
    loading: creatingCoupon,
  } = useFrappePostCall('hotpot.api.coupon.create_coupon');

  const handleScan = useCallback(
    async (data: string | null) => {
      if (data) {
        setScanning(false);
        setScannedData(data);
        const processedData = extractCouponInfo(data);
        if (processedData) {
          try {
            const response = await checkCouponExists({
              name: processedData,
            });
            setCouponExists(!!response.message);
            if (response.message) {
              setCouponDoc(response.message);
            }
          } catch (error) {
            console.error('Error checking coupon:', error);
            setError('Error checking coupon status. Please try again.');
            setCouponExists(null);
          }
        } else {
          setError('Invalid QR code format');
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

  const handleCreateCoupon = async () => {
    if (!scannedData) return;

    try {
      await showConfirmDialog({
        title: 'Issue Meal',
        description:
          'Are you sure you want to issue this meal? This action cannot be undone.',
        confirmLabel: 'Confirm',
        variant: 'default',
        isLoading: creatingCoupon,
        onConfirm: async () => {
          const response = await createCoupon({
            data: scannedData,
          });
          if (response.message) {
            if (!response.message.created) {
              setCouponExists(!response.message.created);
            }
            setCouponDoc(response.message.coupon);
          }
        },
      });
    } catch (error) {
      console.error('Error creating coupon:', error);
      setError('Error creating coupon. Please try again.');
      setCouponExists(null);
    }
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
      console.error('Error during logout:', error);
    }
  };

  useEffect(() => {
    return () => {
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
              <img
                src="/assets/hotpot/manifest/favicon.svg"
                alt="Hotpot Logo"
                className=" h-10 w-10 cursor-pointer sm:h-12 sm:w-12"
              />
            </Link>
            <div className="text-lg font-bold sm:text-2xl">{currentUser}</div>
          </div>
        }
        rightContent={
          <div className="flex gap-2">
            <Link to="/dashboard" className="w-full">
              <Button type="button" variant="outline">
                Dashboard
              </Button>
            </Link>
            <Button variant="destructive" onClick={handleLogout}>
              Logout
            </Button>
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

              {scannedData && (
                <div className="space-y-4">
                  {couponExists === false && !!scannedData && !couponDoc ? (
                    <>
                      <Alert
                        className={
                          is_coupon_valid(
                            coupon_from_info(scannedData),
                            currentCouponType,
                          )
                            ? ''
                            : 'bg-red-50'
                        }
                      >
                        {is_coupon_valid(
                          coupon_from_info(scannedData),
                          currentCouponType,
                        ) ? (
                          <AlertTitle>Coupon yet to be Served</AlertTitle>
                        ) : (
                          <AlertTitle className="flex items-center gap-2">
                            <TriangleAlert className="text-red-600" />
                            ERROR: Coupon Cannot be Served
                          </AlertTitle>
                        )}
                        <AlertDescription>
                          <>
                            <p>
                              Employee:{' '}
                              {coupon_from_info(scannedData)?.employee_id}
                            </p>
                            <p>Type: {coupon_from_info(scannedData)?.title}</p>
                            <p>
                              Time: {coupon_from_info(scannedData)?.coupon_time}
                            </p>
                            <p>
                              Date: {coupon_from_info(scannedData)?.coupon_date}
                            </p>
                          </>
                        </AlertDescription>
                      </Alert>
                      <Button
                        onClick={() => handleCreateCoupon()}
                        className="w-full"
                        disabled={
                          !is_coupon_valid(
                            coupon_from_info(scannedData),
                            currentCouponType,
                          )
                        }
                      >
                        {is_coupon_valid(
                          coupon_from_info(scannedData),
                          currentCouponType,
                        )
                          ? 'Issue ' + currentCouponType
                          : 'Invalid / Expired Coupon'}
                      </Button>
                    </>
                  ) : couponExists === true ? (
                    <Alert className="bg-red-50">
                      <AlertTitle className="gap-2">
                        <TriangleAlert className="text-red-600" />
                        ERROR: Meal has already been Served.
                      </AlertTitle>
                      <AlertDescription>
                        <>
                          <p>Type: {couponDoc?.title}</p>
                          <p>Time: {couponDoc?.coupon_time}</p>
                          <p>Date: {couponDoc?.coupon_date}</p>
                          <p>Served By: {couponDoc?.served_by}</p>
                        </>
                      </AlertDescription>
                    </Alert>
                  ) : (
                    <Alert className="bg-green-50">
                      <AlertTitle className="gap-2">
                        <CookingPot className="text-green-600" />
                        SUCCESS: Meal Served{' '}
                      </AlertTitle>
                      <AlertDescription>
                        <>
                          <p>Type: {couponDoc?.title}</p>
                          <p>Time: {couponDoc?.coupon_time}</p>
                          <p>Date: {couponDoc?.coupon_date}</p>
                          <p>Served By: {couponDoc?.served_by}</p>
                        </>
                      </AlertDescription>
                    </Alert>
                  )}

                  <Button
                    onClick={handleReset}
                    variant="outline"
                    className="w-full"
                  >
                    Scan Another
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
        <div className="mx-auto w-full max-w-md">
          <ErrorBanner error={apiCreateError} />
        </div>
      </div>
    </div>
  );
}
