export interface HotpotCouponsHistory {
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
  /**	Employee Id : Data	*/
  employee_id: string;
  /**	Meal Id : Data	*/
  meal_id?: string;
  /**	Type : Data	*/
  type?: string;
  /**	Message : Small Text	*/
  message?: string;
}
