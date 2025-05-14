
export interface HotpotConfigurations{
	name: string
	creation: string
	modified: string
	owner: string
	modified_by: string
	docstatus: 0 | 1 | 2
	parent?: string
	parentfield?: string
	parenttype?: string
	idx?: number
	/**	Free Birthday Meal : Check	*/
	free_birthday_meal?: 0 | 1
	/**	Free Joining Day Meal : Check	*/
	free_joining_day_meal?: 0 | 1
	/**	Can Generate for Guest : Check	*/
	can_generate_for_guest?: 0 | 1
	/**	Allow Meal on Sunday : Check	*/
	allow_meal_on_sunday?: 0 | 1
	/**	Discount : Percent	*/
	discount?: number
}