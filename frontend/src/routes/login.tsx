import * as React from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  AuthResponse,
  FrappeError,
  useFrappeGetCall,
  useFrappePostCall,
} from 'frappe-react-sdk';
import { LoginContext, LoginInputs } from '@/types/Auth/Login';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

export const Route = createFileRoute('/login')({
  component: LoginPage,
});

const loginSchema = z.object({
  email: z.string().refine((value) => {
    return (
      value === 'Administrator' || z.string().email().safeParse(value).success
    );
  }, 'Please enter a valid email address'),
  password: z.string(),
});

type LoginFormValues = z.infer<typeof loginSchema>;

function LoginPage() {
  const { data: loginContext } = useLoginContext();
  const [showPassword, setShowPassword] = React.useState(false);
  const [error, setError] = React.useState<FrappeError | null>(null);
  const [isLoggingIn, setIsLoggingIn] = React.useState(false);
  const passwordRef = React.useRef<HTMLInputElement>(null);
  const { call: hotpotlogin } = useFrappePostCall('hotpot.api.firebase_login');
  const isSubmittingRef = React.useRef(false);
  const submitCountRef = React.useRef(0);

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = React.useCallback(
    async (values: LoginInputs) => {
      if (isSubmittingRef.current || isLoggingIn) {
        console.log('Preventing duplicate submission');
        return;
      }

      const currentSubmitCount = ++submitCountRef.current;
      console.log(`Login attempt started (count: ${currentSubmitCount})`);

      isSubmittingRef.current = true;
      setIsLoggingIn(true);
      setError(null);

      try {
        if (loginContext?.message?.two_factor_is_enabled) {
          console.log('2FA is enabled, sending first request');
          const res: AuthResponse = await hotpotlogin({
            username: values.email,
            password: values.password,
          });
          if (res?.verification && res?.tmp_id) {
            console.log('2FA verification received');
            // handle two factor things here
            // setIsTwoFactorEnabled(true);
            // setLoginWithTwoFAResponse(res);
          }
        } else {
          const retval = await hotpotlogin({
            email: values.email,
            password: values.password,
          });
          if (retval.message.status === 'error') {
            setError(retval.message as FrappeError);
          } else {
            const URL = import.meta.env.VITE_BASE_NAME
              ? `/${import.meta.env.VITE_BASE_NAME}`
              : ``;
            window.location.replace(`${URL}/`);
          }
        }
      } catch (error) {
        console.error('Login error:', error);
        setError(error as FrappeError);
      } finally {
        console.log(`Login attempt finished (count: ${currentSubmitCount})`);
        setIsLoggingIn(false);
        isSubmittingRef.current = false;
      }
    },
    [hotpotlogin, loginContext, isLoggingIn],
  );

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const handleKeyDown = (
    e: React.KeyboardEvent<HTMLInputElement>,
    fieldName: 'email' | 'password',
  ) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (fieldName === 'email') {
        passwordRef.current?.focus();
      } else if (fieldName === 'password') {
        form.handleSubmit(onSubmit)();
      }
    }
  };

  return (
    <div className="flex h-screen">
      <div className="hidden w-1/2 bg-gray-100 lg:block">
        <img
          src="/placeholder.png?height=800&width=800"
          alt="Login"
          className="h-full w-full object-cover"
        />
      </div>
      <div className="flex w-full items-center justify-center lg:w-1/2">
        <Card className="w-[350px]">
          <CardHeader>
            <CardTitle>Login</CardTitle>
            <CardDescription>
              Enter your email and password to login.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <Alert variant="destructive" className="mb-4">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>
                  {error.message ||
                    'An error occurred during login. Please try again.'}
                </AlertDescription>
              </Alert>
            )}
            <Form {...form}>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (!isSubmittingRef.current && !isLoggingIn) {
                    form.handleSubmit(onSubmit)();
                  } else {
                    console.log('Form submission prevented');
                  }
                }}
                className="space-y-8"
              >
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Enter your email"
                          {...field}
                          onKeyDown={(e) => handleKeyDown(e, 'email')}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Password</FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Input
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Enter your password"
                            {...field}
                            ref={passwordRef}
                            onKeyDown={(e) => handleKeyDown(e, 'password')}
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                            onClick={togglePasswordVisibility}
                          >
                            {showPassword ? (
                              <EyeOff className="h-4 w-4 text-gray-500" />
                            ) : (
                              <Eye className="h-4 w-4 text-gray-500" />
                            )}
                            <span className="sr-only">
                              {showPassword ? 'Hide password' : 'Show password'}
                            </span>
                          </Button>
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button type="submit" className="w-full" disabled={isLoggingIn}>
                  {isLoggingIn ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Logging in...
                    </>
                  ) : (
                    'Login'
                  )}
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

const useLoginContext = () => {
  // GET call for Login Context (settings for social logins, email link etc)
  return useFrappeGetCall<LoginContext>(
    'hotpot.api.login.get_context',
    {
      'redirect-to': '/hotpot',
    },
    'hotpot.api.login.get_context',
    {
      revalidateOnMount: true,
      revalidateOnReconnect: false,
      revalidateOnFocus: false,
    },
  );
};
