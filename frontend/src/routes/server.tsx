import { createFileRoute } from '@tanstack/react-router';
import { useState, useCallback, useEffect, useContext } from 'react';
import QrReader from 'react-qr-reader';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useFrappePostCall } from 'frappe-react-sdk';
import { ErrorBanner } from '@/components/ErrorBanner';
import { Camera } from 'lucide-react';
import { extractCouponInfo, getMealType } from '@/utils/coupon';
import { useDialog } from '@/hooks/use-dialog';
import { HotpotCoupon } from '@/types/Hotpot/HotpotCoupon';
import { ProtectedRoute } from '@/utils/auth/ProtectedRoute';
import { UserContext } from '@/utils/auth/UserProvider';

export const Route = createFileRoute('/server')({
  component: () => (
    <ProtectedRoute>
      <ServerPage />
    </ProtectedRoute>
  ),
});

function ServerPage() {
  const { logout } = useContext(UserContext);
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
      <div className="container mx-auto flex-1 p-4">
        <Card className="mx-auto w-full max-w-md">
          <CardHeader>
            <CardTitle>Hotpot Server Portal</CardTitle>
            <CardDescription>Scan employee QR codes here</CardDescription>
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
                  {couponExists === false ? (
                    <Button
                      onClick={() => handleCreateCoupon()}
                      className="w-full"
                    >
                      Issue {getMealType()}
                    </Button>
                  ) : couponExists === true ? (
                    <Alert>
                      <AlertTitle>
                        This coupon has already been Served.
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
                  ) : null}

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
      <div className="container mx-auto p-4">
        <div className="mx-auto w-full max-w-md">
          <Button
            variant="destructive"
            className="w-full"
            onClick={handleLogout}
          >
            Logout
          </Button>
        </div>
      </div>
    </div>
  );
}
