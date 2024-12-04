import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const calloutVariants = cva('relative w-full rounded-lg border p-4', {
  variants: {
    variant: {
      default: 'bg-background text-foreground',
      info: 'border-blue-200 bg-blue-100 text-blue-900 dark:border-blue-200/30 dark:bg-blue-900/30 dark:text-blue-200',
      warning:
        'border-yellow-200 bg-yellow-100 text-yellow-900 dark:border-yellow-200/30 dark:bg-yellow-900/30 dark:text-yellow-200',
      error:
        'border-red-200 bg-red-100 text-red-900 dark:border-red-200/30 dark:bg-red-900/30 dark:text-red-200',
      success:
        'border-green-200 bg-green-100 text-green-900 dark:border-green-200/30 dark:bg-green-900/30 dark:text-green-200',
    },
  },
  defaultVariants: {
    variant: 'default',
  },
});

export interface CalloutProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof calloutVariants> {
  icon?: React.ReactNode;
}

const Callout = React.forwardRef<HTMLDivElement, CalloutProps>(
  ({ className, variant, icon, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(calloutVariants({ variant }), className)}
        {...props}
      >
        {icon && (
          <div className="mr-4 flex h-4 w-4 items-center justify-center">
            {icon}
          </div>
        )}
        <div>{children}</div>
      </div>
    );
  },
);
Callout.displayName = 'Callout';

const CalloutIcon = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('mr-4 flex h-4 w-4 items-center justify-center', className)}
    {...props}
  />
));
CalloutIcon.displayName = 'CalloutIcon';

const CalloutText = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm [&:not(:first-child)]:mt-2', className)}
    {...props}
  />
));
CalloutText.displayName = 'CalloutText';

export { Callout, CalloutIcon, CalloutText };
