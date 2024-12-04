import { useCurrency } from '@/hooks/useCurrency';
import { cn } from '@/lib/utils';
import { getFormattedNumber } from '@/utils/numbers';

interface AmountCellProps {
  amount?: number;
  className?: string;
}

export function AmountCell({ amount, className }: AmountCellProps) {
  const { currency } = useCurrency();

  if (amount === undefined || amount === null) {
    return null;
  }

  return (
    <div className={cn('text-right', className)}>
      {`${currency} `}
      {getFormattedNumber(amount)}
    </div>
  );
}
