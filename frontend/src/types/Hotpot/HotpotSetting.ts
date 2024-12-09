import { HotpotCouponType } from './HotpotCouponType';

export interface HotpotSetting {
  name: string;
  creation: string;
  modified: string;
  owner: string;
  modified_by: string;
  docstatus: 0 | 1 | 2;
  parent?: string;
  parentfield?: string;
  parenttype?: string;
  idx?: number;
  /**	 : Table - Hotpot Coupon Type	*/
  table_jseo?: HotpotCouponType[];
}
