export interface HotpotUser {
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
  /**	Employee ID : Data	*/
  employee_id: string;
  /**	Employee Name : Data	*/
  employee_name?: string;
  /**	Role : Select	*/
  role?: 'Hotpot User' | 'Hotpot Server';
  /**	E Mail : Data	*/
  email?: string;
  /**	Is Active : Check	*/
  is_active?: 0 | 1;
  /**	Breakfast : Check	*/
  breakfast?: 0 | 1;
  /**	Lunch : Check	*/
  lunch?: 0 | 1;
  /**	Evening Snack : Check	*/
  evening_snack?: 0 | 1;
  /**	Dinner : Check	*/
  dinner?: 0 | 1;
}
