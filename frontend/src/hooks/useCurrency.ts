import { useFrappeGetCall } from 'frappe-react-sdk';
import { useState } from 'react';

export function useCurrency() {
  let currency =
    // @ts-expect-error no error here
    window.frappe?.boot.sysdefaults.currency;

  const { data, error } = useFrappeGetCall<{
    message: { name: string; symbol: string };
  }>(
    'frappe.client.get_value',
    {
      doctype: 'Currency',
      filters: JSON.stringify({ name: currency }),
      fieldname: JSON.stringify(['symbol']),
    },
    undefined,
    {
      revalidateOnFocus: false,
    },
  );
  currency =
    // @ts-expect-error no error here
    data?.message.symbol ?? window.frappe?.boot.sysdefaults.currency ?? '₹';

  return { currency, error };
}
