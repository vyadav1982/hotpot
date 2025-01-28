
export interface HotpotMealItems{
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
	/**	Item Name : Date	*/
	item_name?: string
	/**	Is Active : Check	*/
	is_active?: 0 | 1
}