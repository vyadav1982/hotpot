import * as React from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Eye, EyeOff } from 'lucide-react';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from '@/components/ui/form';
import {
  AuthResponse,
  FrappeContext,
  FrappeError,
  useFrappeAuth,
  useFrappeGetCall,
} from 'frappe-react-sdk';
import { LoginContext, LoginInputs } from '@/types/Auth/Login';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';
import { Logo } from '@/components/Logo';
import SignUpForm from '@/components/SignUpForm';
import { useToast } from '@/hooks/use-toast';
import { isHotpotAdmin, isHotpotServer, isHotpotUser } from '@/utils/roles';

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
  const { login: hotpotlogin } = useFrappeAuth();
  const isSubmittingRef = React.useRef(false);
  const submitCountRef = React.useRef(0);
  const [selectedCard, setSelectedCard] = React.useState('login');
  const { toast } = useToast();
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const handleCardChange = (value: string) => {
    setSelectedCard(value);
  };
  const showToast = (status:string,message:string) => {
    if(status==='error'){
      toast({
        variant: 'destructive',
        title: 'Error',
        description: message,
        className:
          'bg-red-100 text-red-600 border border-red-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
      });
    }
    else{
      toast({
        title: 'Success',
        description: message,
        className:
          'bg-green-100 text-green-600 border border-green-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
      });
    }
  }

  const onLogin = React.useCallback(
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
          try {
            const response = await hotpotlogin({
              username: values.email,
              password: values.password,
            });
            const URL = import.meta.env.VITE_BASE_NAME
              ? `/${import.meta.env.VITE_BASE_NAME}`
              : ``;
            window.location.href = `${URL}/login`;
          } catch (error) {
            setError(error as FrappeError);
          }
        }
      } catch (error) {
        console.error('Login error:', error);
        setError(error as FrappeError);
      } finally {
        setTimeout(() => {
          setError(null);
        }, 5000);
        console.log(`Login attempt finished (count: ${currentSubmitCount})`);
        setIsLoggingIn(false);
        isSubmittingRef.current = false;
      }
    },
    [hotpotlogin, loginContext, isLoggingIn],
  );
  return (
    <div className="flex h-screen">
      <div className="hidden w-1/2 bg-gradient-to-br from-orange-400 to-orange-600 lg:flex lg:items-center lg:justify-center">
        <div className="text-center">
          <img
            src="/assets/hotpot/manifest/favicon.svg"
            alt="Hotpot Logo"
            className="mx-auto h-32 w-32"
          />
          <h1 className="mt-8 text-4xl font-bold text-white">
            Welcome to Hotpot
          </h1>
          <p className="mt-4 text-lg text-white/80">
            Your Digital Food Coupon Solution
          </p>
        </div>
      </div>
      <div className="flex w-full items-center justify-center bg-gradient-to-b from-orange-50 to-white p-4 lg:w-1/2">
        {selectedCard === 'login' ? (
          <Card className="w-[350px] shadow-xl">
            <CardHeader className="space-y-1">
              <div className="flex items-center justify-center lg:hidden">
                <Logo className="h-16 w-16" />
              </div>
              <CardTitle className="text-center text-2xl">Login</CardTitle>
              <CardDescription className="text-center">
                Enter your credentials to continue
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
              <Form {...form}>
                <form className="space-y-4">
                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormControl>
                          <Input
                            placeholder="Email"
                            autoComplete="email"
                            type="email"
                            {...field}
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
                        <FormControl>
                          <div className="relative">
                            <Input
                              placeholder="Password"
                              type={showPassword ? 'text' : 'password'}
                              autoComplete="current-password"
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
                disabled={isLoggingIn}
                onClick={form.handleSubmit(onLogin)}
              >
                {isLoggingIn ? 'Logging in...' : 'Login'}
              </Button>
              <div className="flex flex-row items-center gap-4">
                <p>Don't have an Account?</p>
                <Button onClick={() => setSelectedCard('signUp')}>
                  SignUp
                </Button>
              </div>
            </CardFooter>
          </Card>
        ) : (
          <SignUpForm handleCardChange = {handleCardChange} showToast={showToast}/>
        )}
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
