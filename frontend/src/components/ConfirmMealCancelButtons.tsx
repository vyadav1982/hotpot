import { useState } from 'react';
import { Button } from './ui/button';
import { useToast } from '@/hooks/use-toast';


export const ConfirmMealCancelButtons = ({
  handleCancel,
}: {
  handleCancel: () => Promise<void>;
}) => {
  const [cancelButton, setCancelButton] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleConfirm = async () => {
    setIsLoading(true);
    try {
      await handleCancel();
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Error in cancelling meal.',
        className:
          'bg-red-100 text-red-600 border border-red-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
      });
    } finally {
      setIsLoading(false);
      setCancelButton(false);
    }
  };

  return (
    <div className="flex justify-center">
      {!cancelButton ? (
        <Button onClick={() => setCancelButton(true)} className="w-[200px]">
          Cancel Meal
        </Button>
      ) : (
        <div className="flex flex-col items-center">
          <p className="text-lg font-semibold tracking-wide drop-shadow-sm">
            Are you sure?
          </p>
          <div className="flex gap-4">
            <Button onClick={handleConfirm} disabled={isLoading}>
              {isLoading ? 'Processing...' : 'Yes'}
            </Button>
            <Button onClick={() => setCancelButton(false)}>No</Button>
          </div>
        </div>
      )}
    </div>
  );
};
