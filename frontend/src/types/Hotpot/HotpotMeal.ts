import { HotpotCoupons } from './HotpotCoupons'

export interface HotpotMeal{
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
	/**	Meal Title : Data	*/
	meal_title?: string
	/**	Day : Data	*/
	day?: string
	/**	Meal Items : Data	*/
	meal_items?: string
	/**	Start Time : Data	*/
	start_time?: string
	/**	End Time : Data	*/
	end_time?: string
	/**	Buffer Coupon Count : Int	*/
	buffer_coupon_count?: number
	/**	Coupons : Table - Hotpot Coupons	*/
	coupons?: HotpotCoupons[]
	/**	Is Active : Check	*/
	is_active?: 0 | 1
	/**	Meal Date : Date	*/
	meal_date?: string
}