import frappe
import json

def set_response(http_status_code, status, message, data=None):
    frappe.local.response["http_status_code"] = http_status_code
    frappe.response["status"] = status
    frappe.response["message"] = message
    frappe.response["data"] = data

@frappe.whitelist(allow_guest=True)
def create_meal():
    try:
        if frappe.request.method != "POST":
            set_response(500, False, "Only POST method is allowed")
            return

        data = json.loads(frappe.request.data or "{}")

        meal_title = data.get("meal_title")
        day = data.get("day")
        meal_date = data.get("meal_date")
        meal_items = ",".join(data.get("meal_items", []))
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        buffer_coupon_count = data.get("buffer_coupon_count")

        if not meal_title or not day or not meal_date or not start_time or not end_time or not meal_items:
            set_response(400, False, "Missing required fields")
            return

        existing_meal = frappe.db.exists(
            "Hotpot Meal",
            {"title": meal_title, "day": day, "meal_date": meal_date}
        )
        if existing_meal:
            set_response(409, False, f"A meal with the title '{meal_title}' on '{day}' ({meal_date}) already exists")
            return

        meal_doc = frappe.get_doc({
            "doctype": "Hotpot Meal",
            "meal_title": meal_title,
            "day": day,
            "meal_date": meal_date,
            "meal_items": meal_items,
            "start_time": start_time,
            "end_time": end_time,
            "buffer_coupon_count": buffer_coupon_count,
        })

        meal_doc.insert()
        frappe.db.commit()

        set_response(201, True, "Meal created successfully", {"meal_id": meal_doc.name})
        return
    except Exception as e:
        set_response(500, False, f"Failed to create meal: {str(e)}")
        return

@frappe.whitelist(allow_guest=True)
def update_meal():
    try:
        if frappe.request.method != "PUT":
            set_response(500, False, "Only PUT method is allowed")
            return

        data = json.loads(frappe.request.data or "{}")
        meal_id = data.get("meal_id")
        if not meal_id:
            set_response(400, False, "Meal ID is required")
            return

        meal_doc = frappe.get_doc("Hotpot Meal", meal_id)
        if not meal_doc:
            set_response(404, False, "Meal not found")
            return

        for field in ["meal_title", "day", "meal_date", "meal_items", "start_time", "end_time", "buffer_coupon_count"]:
            if field in data:
                setattr(meal_doc, field, ",".join(data[field]) if field == "meal_items" else data[field])

        meal_doc.save()
        frappe.db.commit()

        set_response(200, True, "Meal updated successfully", {"meal_id": meal_doc.name})
        return
    except Exception as e:
        set_response(500, False, f"Failed to update meal: {str(e)}")
        return

@frappe.whitelist(allow_guest=True)
def delete_meal():
    try:
        if frappe.request.method != "DELETE":
            set_response(500, False, "Only DELETE method is allowed")
            return

        data = json.loads(frappe.request.data or "{}")
        meal_id = data.get("meal_id")
        if not meal_id:
            set_response(400, False, "Meal ID is required")
            return

        meal_doc = frappe.get_doc("Hotpot Meal", meal_id)
        if not meal_doc:
            set_response(404, False, "Meal not found")
            return

        meal_doc.delete()
        frappe.db.commit()

        set_response(200, True, "Meal deleted successfully")
        return
    except Exception as e:
        set_response(500, False, f"Failed to delete meal: {str(e)}")
        return

@frappe.whitelist(allow_guest=True)
def get_meals():
    try:
        if frappe.request.method != "GET":
            set_response(500, False, "Only GET method is allowed")
            return

        data = frappe.db.get_list("Hotpot Meal", fields=["*"])

        if not data:
            set_response(404, False, "No meal found")
            return

        set_response(200, True, "Fetched successfully", data)
        return
    except Exception as e:
        set_response(500, False, f"Failed to get meal: {str(e)}")
        return
