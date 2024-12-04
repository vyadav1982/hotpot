import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { statuses } from '@/utils/statuses';

export type Status =
  | 'Unsettled'
  | 'Pending'
  | 'Approved'
  | 'Submitted'
  | 'Saved'
  | 'Settled - Part'
  | 'Rejected'
  | 'Settled'
  | 'Approved - Part'
  | 'Unclaimed'
  | 'Claimed';

interface StatusBadgeProps {
  status: Status;
  className?: string;
  showIcon?: boolean;
}

export function StatusBadge({
  status,
  className,
  showIcon = true,
}: StatusBadgeProps) {
  const statusConfig = statuses.find((s) => s.value === status);

  if (!statusConfig) return null;

  const Icon = statusConfig.icon;
  const { bg, text, border } = statusConfig.colors;

  return (
    <Badge
      variant="outline"
      className={cn(
        'gap-1 border font-medium transition-none',
        bg,
        text,
        border,
        `hover:bg-${bg}`,
        `hover:text-${text}`,
        className,
      )}
    >
      {showIcon && Icon && <Icon className="h-3 w-3" />}
      {statusConfig.label}
    </Badge>
  );
}
