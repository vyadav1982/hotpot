
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
	/**	Employee Code : Data	*/
	employee_code?: string
	/**	Guest Employee Code : Data	*/
	guest_employee_code?: string
	/**	Employee Id : Data	*/
	employee_id?: string
	/**	Coupon Status : Select	*/
	coupon_status?: "-1" | "0" | "1" | "2"
	/**	Coupon Date : Datetime	*/
	coupon_date?: string
	/**	Served By : Data	*/
	served_by?: string
	/**	Guest Of : Link - Hotpot User	*/
	guest_of?: string
	/**	Approval Id : Link - Hotpot Approvals	*/
	approval_id?: string
	/**	Birthday Coupon : Check	*/
	birthday_coupon?: 0 | 1
	/**	Joining Day : Check	*/
	joining_day?: 0 | 1
	/**	Email : Data	*/
	email?: string
	/**	Coupon Weight : Float	*/
	coupon_weight?: number
}