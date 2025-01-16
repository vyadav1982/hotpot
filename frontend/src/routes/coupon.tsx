import { createFileRoute } from '@tanstack/react-router';
import { Link } from '@tanstack/react-router';

import { useState, useEffect, useContext } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useFrappePostCall } from 'frappe-react-sdk';
import { ErrorBanner } from '@/components/ErrorBanner';
import { HotpotCoupon } from '@/types/Hotpot/HotpotCoupon';
import { TopBar } from '@/components/TopBar';
import { UserContext } from '@/utils/auth/UserProvider';
import { useDialog } from '@/hooks/use-dialog';
import { Logo } from '@/components/Logo';
import { ProtectedRoute } from '@/utils/auth/ProtectedRoute';
import { LogOut } from 'lucide-react';

export const Route = createFileRoute('/coupon')({
  component: () => (
    <ProtectedRoute>
      <CouponPage />
    </ProtectedRoute>
  ),
});

function CouponPage() {
  const { currentUser, logout, userName } = useContext(UserContext);
  const { showConfirmDialog } = useDialog();
  const userRole = 'Hotpot User';
  const [employeeId, setEmployeeId] = useState('');
  const [couponConsumed, setCouponConsumed] = useState(false);
  const [showQRCode, setShowQRCode] = useState(false);
  const [consumptionInfo, setConsumptionInfo] = useState<
    HotpotCoupon | undefined
  >();
  const [qrValue, setQrValue] = useState('');
  const { call: getCoupon, error: couponError } = useFrappePostCall(
    'hotpot.api.coupon.get_coupon_for_employee_id',
  );

  useEffect(() => {
    if (!employeeId) {
      setShowQRCode(false);
    }
  }, [employeeId]);

  const handleGenerateQRCode = async () => {
    if (employeeId) {
      try {
        const response = await getCoupon({
          employee_id: employeeId,
        });

        if (response) {
          if (response.message.__islocal) {
            const couponData = `${response.message.title}_${employeeId}_${response.message.coupon_date}${response.message.coupon_time}`;
            setQrValue(couponData);
            setShowQRCode(true);
          } else {
            setCouponConsumed(true);
            setConsumptionInfo(response.message);
          }
        }
      } catch (error) {
        console.log('Error getting coupon:', error);
        // You might want to show an error message to the user here
      }
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
          currentUser && (
            <div className="flex gap-2">
              <Link to="/server">
                <Button type="button" variant="outline">
                  Serve
                </Button>
              </Link>
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
          )
        }
      />

      <div className="container mx-auto flex-1 p-4">
        <Card className="mx-auto w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-center">Your QR Code</CardTitle>
            <CardDescription className="text-center">
              Show this to get your meal
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <ErrorBanner error={couponError} />
              {userRole === 'Hotpot User' && (
                <div className="space-y-2">
                  <Label htmlFor="employee-id">Employee ID</Label>
                  <Input
                    id="employee-id"
                    value={employeeId}
                    onChange={(e) => setEmployeeId(e.target.value)}
                    className="bg-white dark:bg-black"
                  />
                  <Button
                    onClick={handleGenerateQRCode}
                    className="w-full"
                    disabled={!employeeId}
                  >
                    Generate QR Code
                  </Button>
                </div>
              )}

              {userRole === 'Hotpot User' && showQRCode && !couponConsumed && (
                <div className="overflow-hidden rounded-lg border-2 border-solid border-orange-200 p-4 dark:border-orange-800">
                  <div className="flex aspect-square items-center justify-center bg-white dark:bg-black">
                    <QRCodeSVG
                      value={qrValue}
                      size={200}
                      className="border-2 border-solid border-white"
                    />
                  </div>
                </div>
              )}

              {couponConsumed && (
                <Alert>
                  <AlertTitle>Coupon Already Used</AlertTitle>
                  <AlertDescription>
                    This coupon has already been used. Please wait for the next
                    meal time.
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
