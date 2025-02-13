# import frappe
# import pytz
# from datetime import datetime, timedelta

# def get_user_timezone():
# 	from pytz import timezone

# 	user_info = frappe._dict()
# 	frappe.utils.add_user_info(frappe.session.user, user_info)
# 	return timezone(
# 		frappe.get_cached_value("User", frappe.session.user, "time_zone")
# 		or frappe.utils.get_system_timezone()
# 	)

# def get_utc_datetime_str(date_str):
# 	local_tz = get_user_timezone()
# 	print(type(date_str))
# 	if type(date_str) is datetime.datetime:
# 		date_str  = date_str.strftime('%Y-%m-%d %H:%M:%S')
# 	local_datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
# 	localized_datetime = local_tz.localize(local_datetime)
# 	utc_datetime = localized_datetime.astimezone(pytz.utc)
# 	utc_datetime_str = utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
# 	return utc_datetime_str

# def get_utc_date(date_str):
# 	print(type(date_str))
# 	if type(date_str) is str:
# 		print("hello")
# 		date_str = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
# 	date_str=date_str.strftime("%Y-%m-%d %H:%M:%S")
# 	utc_datetime_str = get_utc_datetime_str(date_str)
# 	utc_date = datetime.strptime(utc_datetime_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
# 	return utc_date

# def get_utc_time(date_str):
# 	date_str=date_str.strftime("%Y-%m-%d %H:%M:%S")
# 	utc_datetime_str = get_utc_datetime_str(date_str)
# 	utc_time = datetime.strptime(utc_datetime_str, "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
# 	return utc_time



import frappe
import pytz
from datetime import datetime

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
    print(user_tz)
    
    if user_tz == pytz.utc or getattr(user_tz, 'zone', None) == 'UTC':
        return datetime.utcnow().strftime("%H:%M:%S")
    
    utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    local_time_now = utc_now.astimezone(user_tz).strftime("%H:%M:%S")
    return local_time_now


def get_utc_datetime_str(date_str):
    if not isinstance(date_str, str):
        raise ValueError("Expected date_str as a string in format 'YYYY-MM-DD HH:MM:SS'")
    
    local_tz = get_user_timezone()
    local_datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    
    if local_tz == pytz.utc or getattr(local_tz, 'zone', None) == 'UTC':
        return local_datetime
    
    localized_datetime = local_tz.localize(local_datetime)
    utc_datetime = localized_datetime.astimezone(pytz.utc)
    return utc_datetime.replace(tzinfo=None)


def get_utc_date(date):
    if isinstance(date, str):
        raise ValueError("Expected date as a date in format 'YYYY-MM-DD HH:MM:SS'")
    utc_datetime_str = date.strftime("%Y-%m-%d %H:%M:%S")
    return utc_datetime_str.split(" ")[0]

def get_utc_time(date):
    if  isinstance(date, str):
        raise ValueError("Expected date as a date in format 'YYYY-MM-DD HH:MM:SS'")
    utc_datetime_str = date.strftime("%Y-%m-%d %H:%M:%S")
    return utc_datetime_str.split(" ")[1]
