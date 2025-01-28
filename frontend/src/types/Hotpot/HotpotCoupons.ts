
export interface HotpotCoupons{
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
	/**	Title : Data	*/
	title?: string
	/**	Employee Id : Data	*/
	employee_id?: string
	/**	Coupon Status : Select	*/
	coupon_status?: "-1" | "0" | "1"
}