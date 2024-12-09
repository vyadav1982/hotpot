export interface HotpotCouponType {
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
  /**	Title : Data	*/
  title: string;
  /**	Start Hour : Int	*/
  start_hour?: number;
  /**	End Hour : Int	*/
  end_hour?: number;
  /**	Is Active : Check	*/
  is_active?: 0 | 1;
}
