import frappe


def get_discount(user, vendor):
	"""Get the discount for a hotpot user with a vendor"""

	# Check if the user has a discount
	if user.discount != -1:
		return user.discount

	# Check if the location where vendor is situated has a discount
	discount = frappe.db.get_value("Company Locations", vendor.location, "discount")
	if discount != -1:
		return discount

	# Check if the global configuration has a discount
	discount = frappe.db.get_single_value("Hotpot Configurations", "discount")
	if discount != -1:
		return discount

	return 0
