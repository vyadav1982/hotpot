
export interface DiscountedMealDay{
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
	/**	Description : Data	*/
	description: string
	/**	Discount Date : Date	*/
	discount_date: string
	/**	Discount : Percent	*/
	discount: number
}