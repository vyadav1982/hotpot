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
	/**	Is Active : Check	*/
	is_active?: 0 | 1
	/**	Is Employee : Check	*/
	is_employee?: 0 | 1
	/**	Is Vendor : Check	*/
	is_vendor?: 0 | 1
	/**	Is Server : Check	*/
	is_server?: 0 | 1
	/**	Is Guest : Check	*/
	is_guest?: 0 | 1
	/**	Is Deleted : Check	*/
	is_deleted?: 0 | 1
	/**	Employee : Link - Employee	*/
	employee?: string
	/**	Discount : Percent	*/
	discount?: number
	/**	Employee ID : Data	*/
	employee_id?: string
	/**	Wallet Balance : Int	*/
	coupon_count?: number
	/**	RFID Card Id : Data	*/
	tag_id?: string
	/**	Of : Link - Hotpot User	*/
	guest_of?: string
	/**	Name : Data	*/
	full_name: string
	/**	E Mail : Data	*/
	email?: string
	/**	Mobile no. : Phone	*/
	mobile_no?: string
	/**	Location : Link - Company Locations	*/
	location: string
	/**	FCM Token : Text	*/
	fcm_token?: string
	/**	User : Link - User	*/
	user?: string
	/**	Latitude : Float	*/
	latitude?: number
	/**	Longitude : Float	*/
	longitude?: number
	/**	Approval Id : JSON	*/
	approval_id?: any
	/**	Discounted Meal Days : Table - Discounted Meal Day	*/
	discounted_meal_days?: DiscountedMealDay[]
}