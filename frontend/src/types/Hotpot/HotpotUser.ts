import { DiscountedMealDay } from './DiscountedMealDay'

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
	/**	Role : Link - Role	*/
	role?: string
	/**	E Mail : Data	*/
	email: string
	/**	Mobile no. : Phone	*/
	mobile_no: string
	/**	Tag Id : Data	*/
	tag_id?: string
	/**	Password : Data	*/
	password?: string
	/**	Approval Id : JSON	*/
	approval_id?: any
	/**	FCM Token : Text	*/
	fcm_token?: string
	/**	Discount : Percent	*/
	discount?: number
	/**	Is Active : Check	*/
	is_active?: 0 | 1
	/**	Is Guest : Check	*/
	is_guest?: 0 | 1
	/**	Is Vendor : Check	*/
	is_vendor?: 0 | 1
	/**	Is Server : Check	*/
	is_server?: 0 | 1
	/**	Is Deleted : Check	*/
	is_deleted?: 0 | 1
	/**	Guest Of : Link - Hotpot User	*/
	guest_of?: string
	/**	Coupon Count : Int	*/
	coupon_count?: number
	/**	Location : Link - Company Locations	*/
	location?: string
	/**	Latitude : Float	*/
	latitude?: number
	/**	Longitude : Float	*/
	longitude?: number
	/**	Discounted Meal Days : Table - Discounted Meal Day	*/
	discounted_meal_days?: DiscountedMealDay[]
}