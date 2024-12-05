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

export const getMealType = () => {
  const hour = new Date().getHours();
  if (hour >= 6 && hour < 11) return 'Breakfast';
  if (hour >= 11 && hour < 15) return 'Lunch';
  if (hour >= 15 && hour < 18) return 'Evening Snacks';
  return 'Dinner';
};
