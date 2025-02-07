export interface HotpotMealRating {
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
  /**	Rating : Data	*/
  rating?: string;
  /**	Feedback : Data	*/
  feedback?: string;
  /**	Meal Id : Data	*/
  meal_id?: string;
  /**	Employee Id : Data	*/
  employee_id?: string;
}
