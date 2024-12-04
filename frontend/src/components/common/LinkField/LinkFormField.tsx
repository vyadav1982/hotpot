import * as React from 'react';
import { useFormContext, ControllerProps } from 'react-hook-form';
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import LinkField, { LinkFieldProps } from './LinkField';

interface LinkFormFieldProps
  extends Omit<LinkFieldProps, 'value' | 'setValue'> {
  name: string;
  rules?: ControllerProps['rules'];
  disabled?: boolean;
  label?: string;
  description?: string;
  readOnly?: boolean;
}

const LinkFormField = React.forwardRef<HTMLDivElement, LinkFormFieldProps>(
  (
    { name, rules, label, description, readOnly = false, ...linkFieldProps },
    ref,
  ) => {
    const { control } = useFormContext();

    return (
      <FormField
        control={control}
        name={name}
        rules={rules}
        render={({ field }) => (
          <FormItem ref={ref}>
            {label && <FormLabel>{label}</FormLabel>}
            <FormControl>
              <LinkField
                value={field.value}
                setValue={field.onChange}
                readOnly={readOnly}
                {...linkFieldProps}
              />
            </FormControl>
            {description && <FormDescription>{description}</FormDescription>}
            <FormMessage />
          </FormItem>
        )}
      />
    );
  },
);

LinkFormField.displayName = 'LinkFormField';

export default LinkFormField;
