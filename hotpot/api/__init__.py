import frappe
from frappe.auth import LoginManager


@frappe.whitelist()
def track_untrack_doc(doctype, docname, track=False):
	"""
	track_untrack_doc sets the _liked_by field of a document using toggle_like(doctype, docname, track).
	if value of track is "Yes" then current user will be added to _liked_by
	if value of track is "No" then current user will be removed from _liked_by

	:arg doctype: doctype of the document
	:arg docname: name of the document
	:arg track: whether to track or untrack

	:returns: None
	"""
	from frappe.desk.like import toggle_like

	if track:
		toggle_like(doctype, docname, "Yes")
	else:
		toggle_like(doctype, docname, "No")


@frappe.whitelist()
def get_current_user_info():
	"""
	Get the current user's full name and user image.

	Returns:
		dict: A dictionary with keys 'full_name' and 'user_image' containing the user's full name and profile image, respectively.
	"""
	if not frappe.session.user:
		return {"status": "error", "message": "No user is currently logged in"}

	# Get the user's full name and profile image
	return frappe.db.get_value(
		"Hotpot User",
		frappe.session.user,
		["employee_name", "employee_id", "email"],
		as_dict=True,
	)
