import frappe


def get_discount(user):
	"""Get the discount for a hotpot user"""

	if user.discount != -1:
		return user.discount

	discount = frappe.db.get_value("Company Locations", user.location, "discount")
	if discount != -1:
		return discount

	discount = frappe.db.get_single_value("Hotpot Configurations", "discount")
	if discount != -1:
		return discount

	return 0
