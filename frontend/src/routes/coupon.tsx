import { createFileRoute } from '@tanstack/react-router';

import { useState, useEffect } from 'react';
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

export const Route = createFileRoute('/coupon')({
  component: CouponPage,
});

function CouponPage() {
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
          console.log(response);
          if (response.message.__islocal) {
            const couponData = `${response.message.title}_${employeeId}_${response.message.coupon_date}${response.message.coupon_time}`;
            setQrValue(couponData);
            setShowQRCode(true);
          } else {
            setCouponConsumed(true);
            setConsumptionInfo(response.message);
            console.log(response.message);
          }
        }
      } catch (error) {
        console.log('Error getting coupon:', error);
        // You might want to show an error message to the user here
      }
    }
  };

  return (
    <div className="container mx-auto p-4">
      <Card className="mx-auto w-full max-w-md">
        <CardHeader>
          <CardTitle>Hotpot Coupon System</CardTitle>
          <CardDescription>Manage your hotpot coupons here</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {userRole === 'Hotpot User' && (
              <div className="space-y-2">
                <Label htmlFor="employee-id">Employee ID</Label>
                <Input
                  id="employee-id"
                  placeholder="Enter your employee ID"
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
                />
                <Button
                  className="w-full"
                  onClick={handleGenerateQRCode}
                  disabled={!employeeId}
                >
                  Generate QR Code
                </Button>
              </div>
            )}

            {userRole === 'Hotpot User' && showQRCode && !couponConsumed && (
              <div className="flex justify-center">
                <QRCodeSVG value={qrValue} size={200} />
              </div>
            )}

            {couponConsumed && (
              <Alert>
                <AlertTitle>Coupon Already Consumed</AlertTitle>
                <AlertDescription>
                  {consumptionInfo ? (
                    <>
                      <p>Time: {consumptionInfo.coupon_time}</p>
                      <p>Date: {consumptionInfo.coupon_date}</p>
                    </>
                  ) : (
                    <p>Coupon has been consumed successfully.</p>
                  )}
                </AlertDescription>
              </Alert>
            )}
          </div>
        </CardContent>
        <CardFooter className="flex justify-center">
          {userRole === 'Hotpot User' && !consumptionInfo && (
            <p className="text-sm text-gray-500">
              {'Show this QR code to the server'}
            </p>
          )}
        </CardFooter>
      </Card>
      <div className="mx-auto w-full max-w-md">
        <ErrorBanner error={couponError} />
      </div>
    </div>
  );
}
