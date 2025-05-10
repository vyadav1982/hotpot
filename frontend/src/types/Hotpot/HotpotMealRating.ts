
export interface HotpotMealRating{
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
	/**	Employee : Data	*/
	employee_id?: string
	/**	Meal : Data	*/
	meal_id?: string
	/**	Meal Item : Link - Hotpot Meal	*/
	meal_item_id?: string
	/**	Rating : Rating	*/
	rating?: any
	/**	Feedback : Small Text	*/
	feedback?: string
}