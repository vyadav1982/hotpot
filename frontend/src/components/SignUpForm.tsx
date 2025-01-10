import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from './ui/card';
import { FrappeError, useFrappePostCall } from 'frappe-react-sdk';
import { Logo } from './Logo';
import React from 'react';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { AlertCircle, Eye, EyeOff } from 'lucide-react';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from '@/components/ui/form';
import { Input } from './ui/input';
import { Button } from './ui/button';

const signUpSchema = z
  .object({
    empId: z
      .string()
      .min(1, 'Emp ID is required'),
    name: z.string().min(1, 'Employee name is required'),
    email: z.string().email('Invalid email format'),
    mobile: z
      .string()
      .regex(/^\d{10}$/, 'Mobile number must be 10 digits')
      .min(1, 'Mobile number is required'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters long')
      .regex(
        /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
        'Password must contain at least one letter, one number, and one special character(@$!%*?&)',
      ),
    confirmPassword: z.string().min(1, 'Confirm password is required'),
  })
  .superRefine(({ password, confirmPassword }, ctx) => {
    if (password !== confirmPassword) {
      ctx.addIssue({
        code: 'custom',
        path: ['confirmPassword'],
        message: 'Passwords do not match',
      });
    }
  });

const SignUpForm = ({ handleCardChange, showToast }: any) => {
  const [error, setError] = React.useState<FrappeError | null>(null);
  const [showPassword, setShowPassword] = React.useState(false);
  const signUpForm = useForm<z.infer<typeof signUpSchema>>({
    resolver: zodResolver(signUpSchema),
    defaultValues: {
      empId: '',
      name: '',
      email: '',
      mobile: '',
      password: '',
      confirmPassword: '',
    },
  });
  const {
    call: signUp,
    error: signUpError,
    loading,
  } = useFrappePostCall('hotpot.api.login.user_signUp');
  const onSubmit = async () => {
    signUpForm.setValue("mobile","+91- "+signUpForm.getValues("mobile"))
    const {message} = await signUp({
      data: JSON.stringify(signUpForm.getValues()),
    });
    signUpForm.setValue("mobile",signUpForm.getValues("mobile").slice(5))
    showToast(message.status, message.message)
    if(signUpError){
      setError(signUpError);
    }
    console.log(message)
    if(message.status==='success'){
      handleCardChange('login');
    }
    setTimeout(() => {
      setError(null)
    }, 5000);
    console.log(loading);
    
  };
  return (
    <Card className="w-[350px] shadow-xl">
      <CardHeader className="space-y-1">
        <div className="flex items-center justify-center lg:hidden">
          <Logo className="h-16 w-16" />
        </div>
        <CardTitle className="text-center text-2xl">SignUp</CardTitle>
        <CardDescription className="text-center">
          Enter your details to continue
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>
              {error.message || 'Something went wrong'}
            </AlertDescription>
          </Alert>
        )}
        <Form {...signUpForm}>
          <form className="space-y-4">
            <FormField
              control={signUpForm.control}
              name="empId"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Input placeholder="Employee Id" type="text" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={signUpForm.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Input placeholder="Employee Name" type="text" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={signUpForm.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Input placeholder="Email" type="email" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={signUpForm.control}
              name="mobile"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Input placeholder="Phone no" type="text" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={signUpForm.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <div className="relative">
                      <Input
                        placeholder="Password"
                        type={showPassword ? 'text' : 'password'}
                        className="pr-10"
                        {...field}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={signUpForm.control}
              name="confirmPassword"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <div className="relative">
                      <Input
                        placeholder="Confirm Password"
                        type={showPassword ? 'text' : 'password'}
                        className="pr-10"
                        {...field}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </form>
        </Form>
      </CardContent>
      <CardFooter className="flex flex-col gap-4">
        <Button
          type="submit"
          className="w-full bg-orange-500 hover:bg-orange-600"
          onClick={signUpForm.handleSubmit(onSubmit)}
          disabled={loading}
        >
          Sign Up
        </Button>
        <div className="flex flex-row items-center gap-4">
          <p>Already have an Account?</p>
          <Button onClick={() => handleCardChange('login')}>Login</Button>
        </div>
      </CardFooter>
    </Card>
  );
};

export default SignUpForm;
