import { useContext } from 'react';
import { DialogContext, DialogOptions } from '@/utils/DialogProvider';

export function useDialog() {
  const context = useContext(DialogContext);

  if (!context) {
    throw new Error('useDialog must be used within a DialogProvider');
  }

  const showConfirmDialog = async (options: DialogOptions) => {
    return new Promise<void>((resolve, reject) => {
      context.showDialog({
        ...options,
        onConfirm: async () => {
          try {
            await options.onConfirm?.();
            resolve();
          } catch (error) {
            reject(error);
          } finally {
            context.hideDialog();
          }
        },
        onCancel: () => {
          options.onCancel?.();
          context.hideDialog();
        },
      });
    });
  };

  return {
    ...context,
    showConfirmDialog,
  };
}
