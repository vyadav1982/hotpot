// src/utils/DateRangeProvider.tsx
import React, { createContext, useState, ReactNode, useEffect } from 'react';
import { DateRange } from 'react-day-picker';

type DateRangeContextType = {
  selectedValue: string;
  setSelectedValue: (selectedValue: string) => void;
  date: DateRange;
  setDate: (date: DateRange) => void;
};

const defaultDate: DateRange = {
  from: new Date(),
  to: new Date(),
};

export const DateRangeContext = createContext<DateRangeContextType>({
  selectedValue: 'today',
  setSelectedValue: () => {},
  date: defaultDate,
  setDate: () => {},
});

type DateRangeProviderProps = {
  children: ReactNode;
};

export const DateRangeProvider: React.FC<DateRangeProviderProps> = ({
  children,
}) => {
  const [date, setDate] = useState<DateRange>(defaultDate);
  const [selectedValue, setSelectedValue] = useState('today');

  const setDateRange = (selectval: string) => {
    if (selectval === 'today') {
      setDate({
        from: new Date(),
        to: new Date(),
      });
    }
    if (selectval === 'custom') {
      setDate({
        from: date?.from,
        to: date?.to,
      });
    }
    if (selectval === 'this_week') {
      const date = new Date();
      setDate({
        from: new Date(
          date.setDate(
            date.getDate() - date.getDay() + (date.getDay() === 0 ? -6 : 1),
          ),
        ),
        to: new Date(),
      });
    }
    if (selectval === 'this_month') {
      setDate({
        from: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
        to: new Date(),
      });
    }
  };

  useEffect(() => {
    setDateRange(selectedValue);
  }, [selectedValue]);

  return (
    <DateRangeContext.Provider
      value={{ date, setDate, selectedValue, setSelectedValue }}
    >
      {children}
    </DateRangeContext.Provider>
  );
};
