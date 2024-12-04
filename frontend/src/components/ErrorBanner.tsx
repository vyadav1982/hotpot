import * as React from 'react';
import { FrappeError } from 'frappe-react-sdk';
import { ErrorCallout } from '@/components/callouts/ErrorCallout';

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

const getErrorMessages = (error?: FrappeError | null): ParsedErrorMessage[] => {
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
  const messages = React.useMemo(() => getErrorMessages(error), [error]);

  if (messages.length === 0 || !error) return null;

  return (
    <ErrorCallout>
      {overrideHeading && (
        <h3 className="mb-2 text-lg font-semibold">{overrideHeading}</h3>
      )}
      {messages.map((m, i) => (
        <div key={i} className="mb-2">
          {m.title && m.title !== 'Message' && m.title !== 'Error' && (
            <h4 className="font-medium">{m.title}</h4>
          )}
          <div
            dangerouslySetInnerHTML={{
              __html: m.message,
            }}
          />
        </div>
      ))}
      {children}
    </ErrorCallout>
  );
};

export const getErrorMessage = (error?: FrappeError | null): string => {
  const messages = getErrorMessages(error);
  return messages.map((m) => m.message).join('\n');
};
