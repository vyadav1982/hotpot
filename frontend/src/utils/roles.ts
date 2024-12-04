export const hasHotpotUserRole = () => {
  if (import.meta.env.DEV) {
    return true;
  }
  //@ts-expect-error as we know frappe is defined
  return (window?.frappe?.boot?.user?.roles ?? []).includes('Hotpot User');
};

export const isSystemManager = () => {
  //@ts-expect-error as we know frappe is defined
  return (window?.frappe?.boot?.user?.roles ?? []).includes('System Manager');
};

export const isHotpotUser = () => {
  //@ts-expect-error as we know frappe is defined
  return (window?.frappe?.boot?.user?.roles ?? []).includes('Hotpot User');
};

export const isHotpotServer = () => {
  //@ts-expect-error as we know frappe is defined
  return (window?.frappe?.boot?.user?.roles ?? []).includes('Hotpot Server');
};

export const isHotpotAdmin = () => {
  //@ts-expect-error as we know frappe is defined
  return (window?.frappe?.boot?.user?.roles ?? []).includes('Hotpot Admin');
};

export const hasServerScriptEnabled = () => {
  if (import.meta.env.DEV) {
    return true;
  }
  // @ts-expect-error as we know frappe is defined
  return window?.frappe?.boot?.server_script_enabled;
};
