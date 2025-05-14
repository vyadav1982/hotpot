import frappe


def get_dominant_role_for_user(userid):
	"""Get the dominant role of the user."""
	if not frappe.session.user:
		return None
	roles = frappe.get_roles(userid)

	priority = ["Hotpot Admin", "Hotpot HR", "Hotpot User"]

	for role in priority:
		if role in roles:
			return role

	return None


def get_dominant_role_for_current_user():
	"""Get the dominant role of the user."""
	if not frappe.session.user:
		return None
	roles = frappe.get_roles(frappe.session.user)

	priority = ["Hotpot Admin", "Hotpot HR", "Hotpot User"]

	for role in priority:
		if role in roles:
			return role

	return None


def has_role(role):
	"""Check if the user has a specific role."""
	if not frappe.session.user:
		return False

	return role in frappe.get_roles(frappe.session.user)


def has_any_of_role(roles):
	"""Check if the user has any of roles."""
	return any(role in frappe.get_roles(frappe.session.user) for role in roles)
