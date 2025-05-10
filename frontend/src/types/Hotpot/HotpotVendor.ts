
export interface HotpotVendor{
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
	/**	Vendor Name : Data	*/
	vendor_name?: string
	/**	Location : Link - Company Locations	*/
	location?: string
	/**	Latitude : Float	*/
	latitude?: number
	/**	Longitude : Float	*/
	longitude?: number
	/**	Is Active : Check	*/
	is_active?: 0 | 1
}