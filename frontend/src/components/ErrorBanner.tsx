import * as React from 'react';
import { FrappeError } from 'frappe-react-sdk';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { AlertTriangle } from 'lucide-react';

interface ErrorBannerProps {
  error?: Partial<FrappeError> | null;
  overrideHeading?: string;
  children?: React.ReactNode;
}

interface ParsedErrorMessage {
  message: string;
  title?: string;
  indicator?: string;
}

const getErrorMessages = (
  error?: Partial<FrappeError> | null,
): ParsedErrorMessage[] => {
  if (!error) return [];
  let eMessages: ParsedErrorMessage[] = [];

  if (error._server_messages) {
    try {
      eMessages = JSON.parse(error._server_messages).map((m: any) => {
        try {
          return JSON.parse(m);
        } catch {
          return m;
        }
      });
    } catch {
      // If parsing fails, we'll fall back to the default error message
    }
  }

  if (eMessages.length === 0) {
    const indexOfFirstColon = error.exception?.indexOf(':');
    if (indexOfFirstColon && indexOfFirstColon !== -1) {
      const exception = error.exception.slice(indexOfFirstColon + 1).trim();
      if (exception) {
        eMessages = [{ message: exception, title: 'Error' }];
      }
    }

    if (eMessages.length === 0) {
      eMessages = [
        { message: error.message, title: 'Error', indicator: 'red' },
      ];
    }
  }

  return eMessages;
};

export const ErrorBanner: React.FC<ErrorBannerProps> = ({
  error,
  overrideHeading,
  children,
}) => {
  const [visibleError, setVisibleError] =
    React.useState<Partial<FrappeError> | null>(null);
  const messages = React.useMemo(
    () => getErrorMessages(visibleError),
    [visibleError],
  );

  React.useEffect(() => {
    if (error) {
      setVisibleError(error);
      const timer = setTimeout(() => {
        setVisibleError(null);
      }, 3000);
      return () => clearTimeout(timer);
    } else {
      setVisibleError(null);
    }
  }, [error]);

  if (messages.length === 0 || !visibleError) return null;

  return (
    <Alert variant="destructive" className="flex items-center gap-2">
      <AlertTriangle className="h-4 w-4" />
      <AlertDescription className="m-0 flex items-center gap-2">
        {overrideHeading && (
          <AlertTitle className="mb-2 text-lg font-semibold">
            {overrideHeading}
          </AlertTitle>
        )}
        {messages.map((m, i) => (
          <div key={i} className="flex items-center gap-1">
            {m.title && m.title !== 'Message' && m.title !== 'Error' && (
              <span className="font-medium">{m.title}:</span>
            )}
            <span
              dangerouslySetInnerHTML={{
                __html: m.message,
              }}
            />
          </div>
        ))}
        {children}
      </AlertDescription>
    </Alert>
  );
};

export const getErrorMessage = (error?: FrappeError | null): string => {
  const messages = getErrorMessages(error);
  return messages.map((m) => m.message).join('\n');
};
