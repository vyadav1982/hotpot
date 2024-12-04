import { createContext, useCallback, useState, ReactNode } from 'react';

export interface DialogOptions {
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'default' | 'destructive';
  onConfirm?: () => Promise<void> | void;
  onCancel?: () => void;
  isLoading?: boolean;
}

interface DialogContextType {
  isOpen: boolean;
  options: DialogOptions | null;
  showDialog: (options: DialogOptions) => void;
  hideDialog: () => void;
}

export const DialogContext = createContext<DialogContextType>({
  isOpen: false,
  options: null,
  showDialog: () => {},
  hideDialog: () => {},
});

interface DialogProviderProps {
  children: ReactNode;
}

export function DialogProvider({ children }: DialogProviderProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [options, setOptions] = useState<DialogOptions | null>(null);

  const showDialog = useCallback((options: DialogOptions) => {
    setOptions(options);
    setIsOpen(true);
  }, []);

  const hideDialog = useCallback(() => {
    setIsOpen(false);
    setOptions(null);
  }, []);

  return (
    <DialogContext.Provider
      value={{
        isOpen,
        options,
        showDialog,
        hideDialog,
      }}
    >
      {children}
    </DialogContext.Provider>
  );
}
