import calendar
import pdb

# import schedule
import time
from datetime import date, datetime, timedelta

import frappe
import pytz
from frappe.utils import today

# from apscheduler.schedulers.blocking import BlockingScheduler


@frappe.whitelist(allow_guest=True)
def get_current_coupon_type():
	time = datetime.now()
	# Define time ranges
	coupon_type_list = frappe.get_list(
		"Hotpot Coupon Type",
		filters=[
			["start_hour", "<=", time.hour * 100 + time.minute],
			["end_hour", ">", time.hour * 100 + time.minute],
			["is_active", "=", True],
		],
		pluck="name",
	)

	if len(coupon_type_list) > 1:
		frappe.throw("Error: Multiple coupons found for this time of day. Please contact system manager")

	if len(coupon_type_list) == 1:
		return coupon_type_list[0]
	else:
		return frappe.throw("No coupon available at this time")


@frappe.whitelist(allow_guest=True)
def get_coupon_for_employee_id(employee_id):
	if not frappe.db.exists("Hotpot User", employee_id):
		return frappe.throw(f"Employee ID: {employee_id} does not exist")
	title = get_current_coupon_type()
	coupon_date = today()

	if not frappe.db.exists("Hotpot Coupon", f"{title}_{employee_id}_{coupon_date}"):
		coupon = frappe.new_doc(doctype="Hotpot Coupon")
		coupon.employee_id = employee_id
		coupon.coupon_date = datetime.now().date()
		coupon.coupon_time = datetime.now().replace(microsecond=0).time()
		coupon.title = title
		return coupon
	else:
		return frappe.get_doc("Hotpot Coupon", f"{title}_{employee_id}_{coupon_date}")


@frappe.whitelist(allow_guest=True)
def coupon_exists(name):
	if not frappe.db.exists("Hotpot Coupon", name):
		return None
	else:
		return frappe.get_doc("Hotpot Coupon", name)


@frappe.whitelist(allow_guest=True)
def create_coupon(data):
	if not frappe.db.exists("Hotpot Coupon", extract_coupon_info(data)):
		coupon = frappe.get_doc(coupon_from_info(data))
		coupon.served_by = frappe.session.user
		coupon.save(ignore_permissions=True)
		return {"created": True, "coupon": coupon}
	else:
		return {"created": False, "coupon": frappe.get_doc("Hotpot Coupon", extract_coupon_info(data))}


@frappe.whitelist(allow_guest=True)
def get_coupon_for_guest(data):
	current_time = datetime.now().astimezone(pytz.timezone("Asia/Kolkata"))
	if not frappe.db.exists("Hotpot User", data.get("mobile")):
		new_user = frappe.new_doc("Hotpot User")
		new_user.employee_name = data["name"]
		new_user.employee_id = data["mobile"]
		new_user.is_guest = True
		new_user.mobile_no = data["mobile"]
		new_user.guest_of = data["empId"]
		new_user.save(ignore_permissions=True)

	created_coupons = []
	meal_types = {
		"Breakfast": data.get("breakfast", False),
		"Lunch": data.get("lunch", False),
		"Evening Snack": data.get("evening_snacks", False),
		"Dinner": data.get("dinner", False),
	}

	for meal, is_selected in meal_types.items():
		if is_selected:
			coupon = frappe.new_doc("Hotpot Coupon")
			coupon.employee_id = data["mobile"]
			coupon.coupon_date = datetime.now().date()
			coupon.coupon_time = f"{current_time.hour}:{current_time.minute}:{current_time.second}"
			coupon.title = meal
			coupon.status = "Upcoming"
			if not frappe.db.exists(
				"Hotpot Coupon",
				meal + "_" + data["mobile"] + "_" + (datetime.now().date()).strftime("%Y-%m-%d"),
				created_coupons.append(coupon)
			):
				coupon.save(ignore_permissions=True)


	return created_coupons


@frappe.whitelist(allow_guest=True)
def create_coupon(params):
	params = frappe.parse_json(params)
	employee_id = params.get("employee_id")
	from_date = params.get("from_date")
	to_date = params.get("to_date")
	meal_type = params.get("meal_type")
	month1, date1, year1 = from_date.split("/")
	month2, date2, year2 = to_date.split("/")
	from_date = year1 + "-" + month1 + "-" + date1
	to_date = year2 + "-" + month2 + "-" + date2
	if not frappe.db.exists("Hotpot User", employee_id):
		return frappe.throw(f"Employee ID: {employee_id} does not exist")
	query = """
        select coupon_count
        from `tabHotpot User`
        where employee_id = %s
    """
	coupon_count = frappe.db.sql(query, employee_id, as_dict=True)
	if not coupon_count:
		return {"message": "No coupon available for this employee"}
	from_date = datetime.strptime(from_date, "%Y-%m-%d")
	to_date = datetime.strptime(to_date, "%Y-%m-%d")
	coupon_count = coupon_count[0].get("coupon_count")
	day_difference = (to_date - from_date).days
	# if (day_difference) * len(meal_type) > coupon_count:
	# 	return {"message": "Not enough coupons available for this employee"}
	query = """
        select title,start_hour
        from `tabHotpot Coupon Type`
    """
	meal_types = {row["title"]: row["start_hour"] for row in frappe.db.sql(query, as_dict=True)}
	current_time = datetime.now().astimezone(pytz.timezone("Asia/Kolkata"))
	output = []
	for x in range(day_difference + 1):
		for meal in meal_type:
			db_meal_value = frappe.db.get_value("Hotpot Coupon Type", meal, "value")
			# check coupon_count and value first
			if coupon_count < db_meal_value:
				output.append(
					f"Insufficient coupons for {meal} on {(from_date + timedelta(days=x)).strftime('%d %b %Y')}"
				)
				continue
			# booking in between buffer time
			if (
				from_date + timedelta(days=x)
				== datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
				and abs((current_time.hour * 100 + current_time.minute) - (meal_types[meal]))
				<= (frappe.db.get_value("Hotpot Coupon Type", meal, "buffer_time")) * 100
			):
				output.append(
					f"Very less time left for {meal} on {(from_date + timedelta(days=x)).strftime('%d %b %Y')}"
				)
				continue
			# booking in meal time or after meal time
			if not (
				from_date + timedelta(days=x)
				== datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
				and (
					(current_time.hour * 100 + current_time.minute)
					>= frappe.db.get_value("Hotpot Coupon Type", meal, "end_hour")
					or (current_time.hour * 100 + current_time.minute)
					>= frappe.db.get_value("Hotpot Coupon Type", meal, "start_hour")
				)
			):
				coupon = frappe.new_doc("Hotpot Coupon")
				coupon.employee_id = employee_id
				coupon.coupon_date = (from_date + timedelta(days=x)).strftime("%Y-%m-%d")
				coupon.coupon_time = f"{current_time.hour}:{current_time.minute}:{current_time.second}"
				coupon.title = meal
				coupon.status = "Upcoming"
				if not frappe.db.exists(
					"Hotpot Coupon",
					meal + "_" + employee_id + "_" + (from_date + timedelta(days=x)).strftime("%Y-%m-%d"),
				):
					coupon.save(ignore_permissions=True)
					coupon_count = coupon_count - db_meal_value
					doc = frappe.new_doc("Hotpot Coupons History")
					doc.employee_id = employee_id
					doc.type = "Creation"
					doc.message = f"You Created a coupon for {meal} ({datetime.strptime(coupon.coupon_date, '%Y-%m-%d').strftime('%d %b %Y')}) "
					doc.insert()
				else:
					output.append(
						f"Already present {meal} on {(from_date + timedelta(days=x)).strftime('%d %b %Y')}"
					)
			else:
				output.append(
					f"Time passed for  {meal} on {(from_date + timedelta(days=x)).strftime('%d %b %Y')}"
				)
	query = """
        update `tabHotpot User`
        set coupon_count = %s 
        where employee_id = %s
    """
	doc = frappe.get_doc("Hotpot User", employee_id)
	doc.coupon_count = int(coupon_count)
	doc.save()
	frappe.db.commit()
	frappe.db.sql(query, (coupon_count, employee_id))
	output.append(coupon_count)
	return output


@frappe.whitelist(allow_guest=True)
def get_upcoming_coupon_list(params):
	params = frappe.parse_json(params)
	employee_id = params.get("employee_id")
	page = params.get("page")
	today = date.today()
	last_day = calendar.monthrange(today.year, today.month)[1]
	last_date = date(today.year, today.month, last_day)
	# last_date = today + timedelta(days=30)
	offset = (page - 1) * 10
	# form today onwards

	query = """
        select name,title,coupon_time,coupon_date,creation,status
        from `tabHotpot Coupon`
        where employee_id=%s and coupon_date>=%s and coupon_date<=%s and status ='Upcoming'
        order by coupon_date asc
        limit %s offset %s 
    """
	result = frappe.db.sql(query, (employee_id, today, last_date, 10, offset), as_dict=True)
	return result


@frappe.whitelist(allow_guest=True)
def get_past_coupon_list(params):
	params = frappe.parse_json(params)
	employee_id = params.get("employee_id")
	from_date = params.get("from_date")
	to_date = params.get("to_date")
	year1, month1, date1 = from_date.split("/")
	year2, month2, date2 = to_date.split("/")
	from_date = year1 + "-" + month1 + "-" + date1
	to_date = year2 + "-" + month2 + "-" + date2
	page = params.get("page")
	offset = (page - 1) * 10
	query = """
        select title,end_hour
        from `tabHotpot Coupon Type`
    """
	meal_types = {row["title"]: row["end_hour"] for row in frappe.db.sql(query, as_dict=True)}
	update_coupon_status(employee_id, meal_types, to_date,from_date)
	query = """
        select title,coupon_time,coupon_date,creation,name,emoji_reaction,feedback,status
        from `tabHotpot Coupon`
        where employee_id=%s and coupon_date<=%s and coupon_date>=%s and status!='Upcoming'
        order by coupon_date desc
        limit %s offset %s
    """
	result = frappe.db.sql(query, (employee_id, to_date, from_date, 10, offset), as_dict=True)
	return result


@frappe.whitelist(allow_guest=True)
def cancel_meal(coupon_id):
	# params = frappe.parse_json(params)
	# coupon_id = params.get('coupon_id')
	query = """
        delete from `tabHotpot Coupon`
        where name=%s
    """
	frappe.db.sql(query, (coupon_id,))
	return {"message": "Coupon Cancelled Successfully"}


@frappe.whitelist(allow_guest=True)
def update_coupon_status(employee_id, meal_types, to_date, from_date):
    if isinstance(from_date, str):
        from_date = datetime.strptime(from_date, "%Y-%m-%d")
    if isinstance(to_date, str):
        to_date = datetime.strptime(to_date, "%Y-%m-%d")

    current_time = int(datetime.now().astimezone(pytz.timezone("Asia/Kolkata")).strftime("%H%M"))
    today = datetime.now().astimezone(pytz.timezone("Asia/Kolkata")).date()

    date = from_date
    while date <= to_date:
        coupons_to_update = frappe.get_all(
            "Hotpot Coupon",
            filters={"employee_id": employee_id, "status": ["=", "Upcoming"], "coupon_date": ["=", date]},
            fields=["name", "title", "status"],
        )

        for coupon in coupons_to_update:
            meal_end_hour = int(meal_types.get(coupon["title"]))
            
            if date.date() == today:  # Check only for today's date
                if current_time >= meal_end_hour:
                    doc = frappe.get_doc("Hotpot Coupon", coupon["name"])
                    doc.status = "Expired"
                    doc.save()
                    frappe.db.commit()
            else:  # For future dates, directly update status
                doc = frappe.get_doc("Hotpot Coupon", coupon["name"])
                doc.status = "Expired"
                doc.save()
                frappe.db.commit()

        date += timedelta(days=1)



def extract_coupon_info(input_str: str) -> str | None:
	# Split the string by underscore
	parts = input_str.split("_")

	# Check if we have at least 3 parts (Breakfast, ID, and Date)
	if len(parts) < 3:
		print("Invalid input format")
		return None

	# Extract the first two parts (Breakfast and ID)
	prefix = "_".join(parts[:2])

	# Extract the date part (assuming it's always in YYYY-MM-DD format)
	date_part = parts[2][:10]

	# Combine the parts
	return f"{prefix}_{date_part}"


def coupon_from_info(input_str: str) -> str | None:
	# Split the string by underscore
	parts = input_str.split("_")

	# Check if we have at least 3 parts (Breakfast, ID, and Date)
	if len(parts) < 3:
		print("Invalid input format")
		return None

	# Extract the title
	title = parts[0]
	employee_id = parts[1]

	# Extract the date part (assuming it's always in YYYY-MM-DD format)
	coupon_date = parts[2][:10]
	coupon_time = parts[2][11:]

	# Combine the parts
	return frappe._dict(
		doctype="Hotpot Coupon",
		title=title,
		employee_id=employee_id,
		coupon_date=coupon_date,
		coupon_time=coupon_time,
	)


# def change_status():
# 	print("&&"*10)

# schedule.every(10).seconds.do(change_status)

# while True:
# 	schedule.run_pending()
# 	time.sleep(1)

# while(True):
#     print('hello geek!')
#     time.sleep(300)


# def myTask():
# 	print ("Executed at: ",datetime.now())

# scheduler=BlockingScheduler()
# scheduler.add_job(myTask,'cron',hour =11,minute=11)

# try:
# 	scheduler.start()
# except(keyboardInterrupt,SystemExit):
# 	pass
