import { MealMenuItems } from './MealMenuItems'
import { HotpotMealRating } from './HotpotMealRating'
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
	/**	Vendor : Link - Hotpot User	*/
	vendor_id: string
	/**	Meal Title : Data	*/
	meal_title: string
	/**	Max Meal Count : Int	*/
	max_meal_count?: number
	/**	Category : Link - Hotpot Meal Category	*/
	category: string
	/**	Is Special : Check	*/
	is_special?: 0 | 1
	/**	Is Active : Check	*/
	is_active?: 0 | 1
	/**	Is Deleted : Check	*/
	is_deleted?: 0 | 1
	/**	Meal Date : Datetime	*/
	meal_date: string
	/**	Start Time : Datetime	*/
	start_time: string
	/**	End Time : Datetime	*/
	end_time: string
	/**	Meal Rate : Int	*/
	meal_weight?: number
	/**	Lead Time : Int	*/
	lead_time?: number
	/**	Cancellation Time : Int	*/
	cancellation_time?: number
	/**	Repeat Type : Select	*/
	repeat_type?: "once" | "daily" | "specific_days"
	/**	Repeat Days : Data	*/
	repeat_days?: string
	/**	Approval Id : Link - Hotpot Approvals	*/
	approval_id?: string
	/**	Meal Items : Data	*/
	meal_items: string
	/**	Buffer Count Enabled : Check	*/
	buffer_count_enabled?: 0 | 1
	/**	Buffer Coupon Count : Int	*/
	buffer_coupon_count?: number
	/**	Menu Items : Table - Meal Menu Items	*/
	menu_items?: MealMenuItems[]
	/**	Ratings : Table - Hotpot Meal Rating	*/
	ratings?: HotpotMealRating[]
	/**	Coupons : Table - Hotpot Coupons	*/
	coupons?: HotpotCoupons[]
}