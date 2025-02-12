import frappe
import pytz
from datetime import datetime, timedelta

def get_user_timezone():
	from pytz import timezone

	user_info = frappe._dict()
	frappe.utils.add_user_info(frappe.session.user, user_info)
	return timezone(
		frappe.get_cached_value("User", frappe.session.user, "time_zone")
		or frappe.utils.get_system_timezone()
	)

def get_utc_datetime_str(date_str):
	local_tz = get_user_timezone()
	local_datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
	localized_datetime = local_tz.localize(local_datetime)
	utc_datetime = localized_datetime.astimezone(pytz.utc)
	utc_datetime_str = utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
	return utc_datetime_str

def get_utc_date(date_str):
	date_str=date_str.strftime("%Y-%m-%d %H:%M:%S")
	utc_datetime_str = get_utc_datetime_str(date_str)
	utc_date = datetime.strptime(utc_datetime_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
	return utc_date

def get_utc_time(date_str):
	date_str=date_str.strftime("%Y-%m-%d %H:%M:%S")
	utc_datetime_str = get_utc_datetime_str(date_str)
	utc_time = datetime.strptime(utc_datetime_str, "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
	return utc_time