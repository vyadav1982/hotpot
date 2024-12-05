import { createContext, useCallback, useRef, useState } from 'react';
import {
  Dialog,
  DialogFooter,
  DialogDescription,
  DialogTitle,
  DialogClose,
  DialogContent,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface ConfirmOptions {
  isOpen?: boolean;
  actionType?: 'danger' | 'warning' | 'primary';
  title?: string;
  description?: string;
}

export const ConfirmContext = createContext<
  (data: ConfirmOptions) => Promise<boolean>
>(() => Promise.resolve(false));

export function ConfirmDialogProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [state, setState] = useState<ConfirmOptions>({
    isOpen: false,
    title: '',
  });

  const fn = useRef<(choice: boolean) => void>();

  const confirm = useCallback(
    (data: ConfirmOptions) => {
      return new Promise((resolve: (value: boolean) => void) => {
        setState({ ...data, isOpen: true });
        fn.current = (choice: boolean) => {
          resolve(choice);
          setState({ ...data, isOpen: false });
        };
      });
    },
    [setState],
  );

  return (
    <ConfirmContext.Provider value={confirm}>
      {children}
      <Dialog
        open={state.isOpen}
        onOpenChange={() => fn.current && fn.current(false)}
      >
        <DialogContent>
          <DialogTitle>{state.title}</DialogTitle>

          {state.description && (
            <DialogDescription>{state.description}</DialogDescription>
          )}

          <DialogFooter>
            <DialogClose asChild>
              <Button
                variant={'outline'}
                onClick={() => fn.current && fn.current(false)}
              >
                Cancel
              </Button>
            </DialogClose>
            <Button
              color={
                state.actionType == 'danger'
                  ? 'rose'
                  : state.actionType == 'warning'
                    ? 'yellow'
                    : 'lime'
              }
              onClick={() => fn.current && fn.current(true)}
            >
              Confirm
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </ConfirmContext.Provider>
  );
}
