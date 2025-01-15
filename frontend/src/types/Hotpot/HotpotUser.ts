
export interface HotpotUser{
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
	/**	Employee ID : Data	*/
	employee_id: string
	/**	Employee Name : Data	*/
	employee_name?: string
	/**	Role : Select	*/
	role?: "Hotpot User" | "Hotpot Server"
	/**	E Mail : Data	*/
	email?: string
	/**	Mobile no. : Phone	*/
	mobile_no?: string
	/**	Password : Data	*/
	password?: string
	/**	Is Active : Check	*/
	is_active?: 0 | 1
	/**	Is Guest : Check	*/
	is_guest?: 0 | 1
	/**	Guest Of : Link - Hotpot User	*/
	guest_of?: string
	/**	Coupon Count : Int	*/
	coupon_count?: number
}