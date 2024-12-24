import { useState } from 'react';
import { Button } from './ui/button';

export const ConfirmMealCancelButtons = ({
  handleCancel,
}: {
  handleCancel: () => Promise<void>;
}) => {
  const [cancelButton, setCancelButton] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleConfirm = async () => {
    setIsLoading(true);
    try {
      await handleCancel();
    } catch (error) {
      console.error('Error cancelling meal:', error);
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
