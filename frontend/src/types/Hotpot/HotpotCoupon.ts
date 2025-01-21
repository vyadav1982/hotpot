
export interface HotpotCoupon{
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
	/**	Amended From : Link - Hotpot Coupon	*/
	amended_from?: string
	/**	Employee Id : Link - Hotpot User	*/
	employee_id: string
	/**	Title : Select	*/
	title: "Breakfast" | "Lunch" | "Evening Snack" | "Dinner"
	/**	Coupon Date : Date	*/
	coupon_date?: string
	/**	Coupon Time : Time	*/
	coupon_time?: string
	/**	Served By : Link - User	*/
	served_by?: string
	/**	Emoji Reaction : Data	*/
	emoji_reaction?: string
	/**	Feedback : Data	*/
	feedback?: string
	/**	Status : Select	*/
	status?: "Upcoming" | "Expired" | "Consumed"
}