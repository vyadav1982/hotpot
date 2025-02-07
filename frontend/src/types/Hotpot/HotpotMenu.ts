export interface HotpotMenu {
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
  /**	Day : Data	*/
  day?: string;
  /**	Special : Check	*/
  special?: 0 | 1;
  /**	Active : Check	*/
  active?: 0 | 1;
  /**	Breakfast : Data	*/
  breakfast?: string;
  /**	Breakfast Special : Check	*/
  breakfast_special?: 0 | 1;
  /**	Lunch : Data	*/
  lunch?: string;
  /**	Lunch Special : Check	*/
  lunch_special?: 0 | 1;
  /**	Snacks : Data	*/
  snacks?: string;
  /**	Snacks Special : Check	*/
  snacks_special?: 0 | 1;
  /**	Dinner : Data	*/
  dinner?: string;
  /**	Dinner Special : Check	*/
  dinner_special?: 0 | 1;
}
