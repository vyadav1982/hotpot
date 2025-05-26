from datetime import datetime

import frappe
import pytz


def get_user_timezone():
	from pytz import timezone

	user_info = frappe._dict()
	frappe.utils.add_user_info(frappe.session.user, user_info)
	return timezone(
		frappe.get_cached_value("User", frappe.session.user, "time_zone")
		or frappe.utils.get_system_timezone()
	)


def get_local_time_now():
	user_tz = get_user_timezone()

	if user_tz == pytz.utc or getattr(user_tz, "zone", None) == "UTC":
		return datetime.utcnow().strftime("%H:%M:%S")

	utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
	local_time_now = utc_now.astimezone(user_tz).strftime("%H:%M:%S")
	return local_time_now


def get_utc_datetime_obj(date_str):
	if not isinstance(date_str, str):
		raise ValueError("Expected date_str as a string in format 'YYYY-MM-DD HH:MM:SS'")

	local_tz = get_user_timezone()
	local_datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

	if local_tz == pytz.utc or getattr(local_tz, "zone", None) == "UTC":
		return local_datetime

	localized_datetime = local_tz.localize(local_datetime)
	utc_datetime = localized_datetime.astimezone(pytz.utc)
	return utc_datetime.replace(tzinfo=None)


def get_utc_datetime_obj_v2(date_str):
	if not date_str:
		return None  # Or return "" if your DB expects a string

	return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def get_local_datetime_obj(utc_input):
	if isinstance(utc_input, str):
		try:
			utc_datetime = datetime.strptime(utc_input, "%Y-%m-%d %H:%M:%S")
			utc_datetime = pytz.utc.localize(utc_datetime)
		except ValueError:
			raise ValueError("Invalid datetime string format. Expected 'YYYY-MM-DD HH:MM:SS'")

	elif isinstance(utc_input, datetime):
		if utc_input.tzinfo is None:
			utc_datetime = pytz.utc.localize(utc_input)
		else:
			utc_datetime = utc_input.astimezone(pytz.utc)

	else:
		raise ValueError("Expected utc_input as a string or datetime object")
	local_tz = get_user_timezone()
	local_datetime = utc_datetime.astimezone(local_tz)
	return local_datetime.replace(tzinfo=None)


def get_utc_date(date):
	if isinstance(date, str):
		raise ValueError("Expected date as a date in format 'YYYY-MM-DD HH:MM:SS'")
	utc_datetime_str = date.strftime("%Y-%m-%d %H:%M:%S")
	return utc_datetime_str.split(" ")[0]


def get_utc_time(date):
	if isinstance(date, str):
		raise ValueError("Expected date as a date in format 'YYYY-MM-DD HH:MM:SS'")
	utc_datetime_str = date.strftime("%Y-%m-%d %H:%M:%S")
	return utc_datetime_str.split(" ")[1]
