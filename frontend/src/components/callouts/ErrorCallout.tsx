import * as React from 'react';
import { AlertTriangle } from 'lucide-react';
import CustomCallout from '@/components/callouts/CustomCallout';

interface ErrorCalloutProps {
  message?: string;
}

export const ErrorCallout: React.FC<
  React.PropsWithChildren<ErrorCalloutProps>
> = ({ children, message }) => {
  return (
    <CustomCallout
      variant="error"
      icon={<AlertTriangle className="h-4 w-4" />}
      textChildren={children || message || 'An error occurred'}
    />
  );
};

export default ErrorCallout;
