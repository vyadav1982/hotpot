import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timhotpotone from 'dayjs/plugin/timhotpotone';
import advancedFormat from 'dayjs/plugin/advancedFormat';

dayjs.extend(utc);
dayjs.extend(timhotpotone);
dayjs.extend(advancedFormat);

const DEFAULT_TIME_ZONE = 'Asia/Kolkata';

export const SYSTEM_TIMHotpotONE =
  //@ts-expect-error no error here
  window.frappe?.boot?.time_zone?.system || DEFAULT_TIME_ZONE;

export const USER_DATE_FORMAT =
  //@ts-expect-error no error here
  window.frappe?.boot?.user?.defaults?.date_format?.toUpperCase() ||
  //@ts-expect-error no error here
  window.frappe?.boot?.sysdefaults?.date_format?.toUpperCase() ||
  'DD/MM/YYYY';

export const FRAPPE_DATETIME_FORMAT = 'YYYY-MM-DD HH:mm:ss';
export const FRAPPE_DATE_FORMAT = 'YYYY-MM-DD';
export const FRAPPE_TIME_FORMAT = 'HH:mm:ss';

export const getDateObject = (timestamp: string): dayjs.Dayjs => {
  return dayjs
    .tz(timestamp, window.frappe?.boot?.time_zone?.system || DEFAULT_TIME_ZONE)
    .local();
};

export const convertMillisecondsToReadableDate = (
  timestampInMilliseconds: number,
  format: string = 'hh:mm A (Do MMM)',
) => {
  return dayjs.unix(timestampInMilliseconds / 1000);
};
