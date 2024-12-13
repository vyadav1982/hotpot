import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { createFileRoute, Link } from '@tanstack/react-router';
import { useContext, useState } from 'react';
import { UserContext } from '@/utils/auth/UserProvider';

import { useDialog } from '@/hooks/use-dialog';
import { Input } from '@/components/ui/input';
import * as z from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Switch } from '@/components/ui/switch';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
} from '@/components/ui/form';
import { useFrappePostCall } from 'frappe-react-sdk';
import { QRCodeSVG } from 'qrcode.react';
import { ProtectedRoute } from '@/utils/auth/ProtectedRoute';
import { Loader2 } from 'lucide-react';
import { UserListContext, UserListProvider } from '@/utils/UserListProvider';
import { InputField } from '@/components/InputField';
import { Logo } from '@/components/Logo';

export const Route = createFileRoute('/guest')({
  component: () => (
    <ProtectedRoute>
      <UserListProvider>
        <AdminGuestPage />
      </UserListProvider>
    </ProtectedRoute>
  ),
});

const guestSchema = z.object({
  empId: z
    .string()
    .min(1, 'Emp ID is required')
    .transform((value) => Number(value))
    .refine((value) => !isNaN(value), 'Emp ID must be a valid number'),
  name: z.string().min(1, 'Guest name is required'),
  mobile: z
    .string()
    .regex(/^\d{10}$/, 'Mobile number must be 10 digits')
    .min(1, 'Mobile number is required'),
  breakfast: z
    .boolean()
    .transform((value) => value === true)
    .optional(),
  lunch: z
    .boolean()
    .transform((value) => value === true)
    .optional(),
  evening_snacks: z
    .boolean()
    .transform((value) => value === true)
    .optional(),
  dinner: z
    .boolean()
    .transform((value) => value === true)
    .optional(),
});

function AdminGuestPage() {
  const [showQr, setShowQr] = useState(false);
  const [qr, setQr] = useState([]);
  const { currentUser, logout } = useContext(UserContext);
  const { showConfirmDialog } = useDialog();
  const { users } = useContext(UserListContext);
  const form = useForm<z.infer<typeof guestSchema>>({
    resolver: zodResolver(guestSchema),
    defaultValues: {
      empId: '',
      name: '',
      mobile: '',
      breakfast: false,
      lunch: false,
      evening_snacks: false,
      dinner: false,
    },
  });
  let { reset } = form;
  const { call: getCoupon, loading } = useFrappePostCall(
    'hotpot.api.coupon.get_coupon_for_guest',
  );
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
  const onSubmit = (data: z.infer<typeof guestSchema>) => {
    handleGenerateQRCode(data);
  };
  const handleGenerateQRCode = async (data: z.infer<typeof guestSchema>) => {
    if (data.empId) {
      try {
        const response = await getCoupon({
          data: data,
        });

        if (response) {
          if (Array.isArray(response.message)) {
            setQr(response.message);
            setShowQr(true);
          } else {
            setShowQr(false);
            setQr([]);
          }
        }
      } catch (error) {
        console.log('Error getting coupon:', error);
      }
    }
  };
  function getName(item: any): string {
    switch (item.meal_title) {
      case 'Breakfast':
        return 'Breakfast';
      case 'Lunch':
        return 'Lunch';
      case 'Evening Snack':
        return 'Evening Snacks';
      case 'Dinner':
        return 'Dinner';
      default:
        return '';
    }
  }
  const resetForm = () => {
    reset();
    setShowQr(false);
    setQr([]);
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
            <div className="text-lg font-bold sm:text-2xl">{currentUser}</div>
          </div>
        }
        rightContent={
          <div className="flex gap-2">
            <Link to="/server">
              <Button type="button" variant="outline">
                serve
              </Button>
            </Link>
            <Button variant="destructive" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        }
      />
      <div className="container mx-auto flex-1 p-4">
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="mx-auto max-w-fit space-y-6"
          >
            <div className="flex flex-col sm:flex-row sm:space-x-4">
              <div className="flex-1">
                <FormField
                  control={form.control}
                  name="empId"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Guest Of</FormLabel>
                      <FormControl>
                        <InputField
                          placeholder={"Guest's host name"}
                          data={users}
                          labelField={'employee_name'}
                          valueField={'employee_id'}
                          {...field}
                        />
                      </FormControl>
                      {form.formState.errors.empId &&
                        form.formState.errors.empId.message && (
                          <p className="mt-1 text-sm text-red-500">
                            {form.formState.errors.empId.message}
                          </p>
                        )}
                    </FormItem>
                  )}
                />
              </div>
              <div className="flex-1">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Guest Name</FormLabel>
                      <FormControl>
                        <Input placeholder="Enter guest name" {...field} />
                      </FormControl>
                      {form.formState.errors.name &&
                        form.formState.errors.name.message && (
                          <p className="mt-1 text-sm text-red-500">
                            {form.formState.errors.name.message}
                          </p>
                        )}
                    </FormItem>
                  )}
                />
              </div>
              <div className="flex-1">
                <FormField
                  control={form.control}
                  name="mobile"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Guest Mobile No.</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Enter guest mobile number"
                          {...field}
                        />
                      </FormControl>
                      {form.formState.errors.mobile &&
                        form.formState.errors.mobile.message && (
                          <p className="mt-1 text-sm text-red-500">
                            {form.formState.errors.mobile.message}
                          </p>
                        )}
                    </FormItem>
                  )}
                />
              </div>

              <div className="flex items-center space-x-4">
                <FormField
                  control={form.control}
                  name="breakfast"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="mx-3 text-lg">Breakfast</FormLabel>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>
              <div className="flex items-center space-x-4">
                <FormField
                  control={form.control}
                  name="lunch"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="mx-3 text-lg">Lunch</FormLabel>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>
              <div className="flex items-center space-x-4">
                <FormField
                  control={form.control}
                  name="evening_snacks"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="mx-3 text-lg">
                        Evening Snacks
                      </FormLabel>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>
              <div className="flex items-center space-x-4">
                <FormField
                  control={form.control}
                  name="dinner"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="mx-3 text-lg">Dinner</FormLabel>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>
            </div>

            <div className="flex justify-center space-x-2">
              {loading ? (
                <Button disabled>
                  <Loader2 className="animate-spin" />
                  Generating...
                </Button>
              ) : (
                <Button
                  type="submit"
                  className="w-full sm:w-auto"
                  disabled={
                    !form.getValues('breakfast') &&
                    !form.getValues('lunch') &&
                    !form.getValues('evening_snacks') &&
                    !form.getValues('dinner')
                  }
                >
                  Generate QR for Guest
                </Button>
              )}
              <Button onClick={resetForm} className="w-full sm:w-auto">
                Reset
              </Button>
            </div>
          </form>
        </Form>
      </div>
      {showQr && (
        <div className="overflow-hidden rounded-xl border-2 border-dashed border-orange-300 bg-gray-50 p-6 shadow-md">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {qr && qr.length > 0 ? (
              qr.map((item: any, index) => (
                <div
                  key={index}
                  className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed bg-white p-4 shadow-md"
                >
                  <QRCodeSVG
                    value={`${item.meal_title}_${item.mobile}_${item.coupon_date}${item.coupon_time}`}
                    size={180}
                    className="border-2 border-solid"
                  />
                  <span className="mt-4 text-sm font-medium text-gray-700 ">
                    QR Code for {getName(item)}
                  </span>
                </div>
              ))
            ) : (
              <div className="col-span-full text-center text-gray-500 dark:text-gray-400">
                No QR codes to display.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
