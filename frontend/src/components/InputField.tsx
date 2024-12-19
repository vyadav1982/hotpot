import { useEffect, useRef, useState } from 'react';
import { Input } from '@/components/ui/input';
export const InputField = ({
  placeholder,
  data,
  labelField,
  valueField,
  ...field
}: any) => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [selectedName, setSelectedName] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const filteredData = query
    ? data
        .filter((item: any) =>
          item[labelField].toLowerCase().includes(query.toLowerCase()),
        )
        .slice(0, 5)
    : data.slice(0, 5);

  const handleOutsideClick = (e: MouseEvent) => {
    if (
      dropdownRef.current &&
      !dropdownRef.current.contains(e.target as Node)
    ) {
      setIsOpen(false);
    }
  };

  useEffect(() => {
    data = data.slice(0, 5);
    if (field.value === '') {
      setSelectedName('');
    }
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, [field]);

  const handleSelect = (item: any) => {
    setSelectedName(item[labelField]);
    setQuery('');
    field.onChange(item[valueField]);
    setIsOpen(false);
  };

  return (
    <div className="relative w-full">
      <Input
        type="text"
        value={query || selectedName}
        placeholder={placeholder}
        onChange={(e) => {
          setQuery(e.target.value);
          setSelectedName('');
        }}
        onFocus={() => setIsOpen(true)}
        onClick={(e) => {
          e.stopPropagation();
          setIsOpen(true);
        }}
      />

      {isOpen && (
        <div
          ref={dropdownRef}
          className="absolute z-10 my-1 w-full rounded-md border shadow-md "
        >
          {filteredData.length > 0 ? (
            filteredData.map((item: any) => (
              <div
                key={item[valueField]}
                onClick={() => handleSelect(item)}
                className="cursor-pointer px-3 py-2 text-sm hover:bg-slate-100 dark:hover:bg-[#1d1b18]"
              >
                  {item[labelField]} ({item[valueField]})
              </div>
            ))
          ) : (
            <div className="text-white-500 px-3 py-2 text-sm">
              No results found
            </div>
          )}
        </div>
      )}
    </div>
  );
};
