import { HotpotCoupon } from '@/types/Hotpot/HotpotCoupon';

export function extractCouponInfo(input: string) {
  // Split the string by underscore
  const parts = input.split('_');

  // Check if we have at least 3 parts (Breakfast, ID, and Date)
  if (parts.length < 3) {
    console.error('Invalid input format');
    return null;
  }

  // Extract the first two parts (Breakfast and ID)
  const prefix = parts.slice(0, 2).join('_');

  // Extract the date part (assuming it's always in YYYY-MM-DD format)
  const datePart = parts[2].substring(0, 10);

  // Combine the parts
  return `${prefix}_${datePart}`;
}

export function coupon_from_info(
  input_str: string,
): Partial<HotpotCoupon> | null {
  // Split the string by underscore
  const parts = input_str.split('_');

  // Check if we have at least 3 parts (Breakfast, ID, and Date)
  if (parts.length < 3) {
    console.log('Invalid input format');
    return null;
  }

  // Extract the title
  const title = parts[0] as 'Breakfast' | 'Lunch' | 'Evening Snack' | 'Dinner';
  const employee_id = parts[1];

  // Extract the date part (assuming it's always in YYYY-MM-DD format)
  const coupon_date = parts[2].slice(0, 10);
  const coupon_time = parts[2].slice(11);

  // Combine the parts
  return {
    title,
    employee_id,
    coupon_date,
    coupon_time,
  };
}

export function today() {
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function is_coupon_valid(
  coupon: Partial<HotpotCoupon> | null,
  couponType: string | undefined,
) {
  return (
    !!coupon && couponType === coupon?.title && today() === coupon?.coupon_date
  );
}
