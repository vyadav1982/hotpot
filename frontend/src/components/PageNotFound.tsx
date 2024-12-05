import { Link } from '@tanstack/react-router';
import { Button } from './ui/button';

export function PageNotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-orange-50 to-white p-4 dark:from-orange-950 dark:to-black">
      <div className="flex flex-col items-center space-y-8 text-center">
        {/* Large 404 Text with responsive sizing */}
        <div className="relative">
          <h1 className="text-[120px] font-bold text-orange-500/10 dark:text-orange-500/20 sm:text-[180px]">
            404
          </h1>
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
            <img
              src="/assets/hotpot/manifest/favicon.svg"
              alt="Hotpot Logo"
              className="h-16 w-16 animate-[spin_3s_linear_infinite,bounce_1s_ease-in-out_infinite] sm:h-24 sm:w-24"
            />
          </div>
        </div>

        {/* Message with better dark mode contrast */}
        <div className="space-y-2">
          <h2 className="text-xl font-semibold tracking-tight text-orange-950 dark:text-orange-50 sm:text-2xl">
            Oops! Page not found
          </h2>
          <p className="text-sm text-orange-600/80 dark:text-orange-400/80 sm:text-base">
            The page you're looking for doesn't exist or has been moved
          </p>
        </div>

        {/* Back to Home Button with dark mode styles */}
        <Link to="/login">
          <Button
            variant="default"
            size="lg"
            className="bg-orange-500 hover:bg-orange-600 dark:bg-orange-600 dark:hover:bg-orange-700"
          >
            Back to Home
          </Button>
        </Link>
      </div>
    </div>
  );
}
