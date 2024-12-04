import * as React from 'react';
import { useCombobox } from 'downshift';
import { Filter, SearchResult, useSearch } from 'frappe-react-sdk';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { useIsDesktop } from '@/hooks/useMediaQuery';

export interface LinkFieldProps {
  doctype: string;
  filters?: Filter[];
  label?: string;
  placeholder?: string;
  value: string;
  setValue: (value: string) => void;
  disabled?: boolean;
  autofocus?: boolean;
  dropdownClass?: string;
  required?: boolean;
  suggestedItems?: SearchResult[];
  readOnly?: boolean;
}

const LinkField = React.memo(
  ({
    doctype,
    filters,
    label,
    placeholder,
    value,
    required,
    setValue,
    disabled,
    autofocus,
    dropdownClass,
    suggestedItems,
    readOnly = false,
  }: LinkFieldProps) => {
    const [searchText, setSearchText] = React.useState(value ?? '');
    const isDesktop = useIsDesktop();
    const { data } = useSearch(doctype, searchText, filters);

    const items = React.useMemo(
      () => [...(suggestedItems ?? []), ...(data?.message ?? [])],
      [suggestedItems, data],
    );

    const {
      isOpen,
      getLabelProps,
      getMenuProps,
      getInputProps,
      highlightedIndex,
      getItemProps,
      selectedItem,
    } = useCombobox({
      items,
      inputValue: searchText,
      onInputValueChange: ({ inputValue }) => {
        if (!readOnly) {
          setSearchText(inputValue ?? '');
          if (!inputValue) {
            setValue('');
          }
        }
      },
      itemToString: (item) => item?.value ?? '',
      onSelectedItemChange: ({ selectedItem }) => {
        if (!readOnly) {
          setValue(selectedItem?.value ?? '');
        }
      },
    });

    return (
      <div className="relative w-full">
        <div className="flex flex-col space-y-1.5">
          <Label {...getLabelProps()} className={cn(required && 'required')}>
            {label}
          </Label>
          <Input
            placeholder={placeholder ?? `Search ${doctype}`}
            disabled={disabled || readOnly}
            autoFocus={isDesktop && autofocus && !readOnly}
            {...getInputProps()}
            readOnly={readOnly}
          />
        </div>
        {!readOnly && (
          <ul
            {...getMenuProps()}
            className={cn(
              'absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-md bg-background shadow-md sm:w-[550px]',
              !isOpen && 'hidden',
              dropdownClass,
            )}
          >
            {isOpen && items.length === 0 && (
              <li className="px-3 py-2 text-sm text-muted-foreground">
                No results found
              </li>
            )}
            {isOpen &&
              items.map((item, index) => (
                <li
                  className={cn(
                    'flex cursor-pointer items-center gap-2 px-3 py-2',
                    highlightedIndex === index && 'bg-accent',
                    selectedItem === item && 'font-medium',
                  )}
                  key={`${item.value}`}
                  {...getItemProps({ item, index })}
                >
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">
                      {item.label ?? item.value}
                    </span>
                    {item.description && (
                      <span className="text-xs text-muted-foreground">
                        {item.description}
                      </span>
                    )}
                  </div>
                </li>
              ))}
          </ul>
        )}
      </div>
    );
  },
);

LinkField.displayName = 'LinkField';

export default LinkField;
