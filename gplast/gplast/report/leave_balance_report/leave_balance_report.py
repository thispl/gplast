# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, nowdate, get_last_day, get_first_day

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 180},
        {"label": "Leave Type", "fieldname": "leave_type", "fieldtype": "Link", "options": "Leave Type", "width": 150},
        {"label": "Total Allocated", "fieldname": "total_leaves_allocated", "fieldtype": "Float", "width": 150},
        {"label": "Leaves Taken", "fieldname": "leaves_taken", "fieldtype": "Float", "width": 130},
        {"label": "Remaining Leaves", "fieldname": "remaining_leaves", "fieldtype": "Float", "width": 150},
    ]

def get_data(filters):
    user = frappe.session.user
    is_admin = user == "Administrator"

    from_date = getdate(filters.get("from_date") or get_first_day(nowdate()))
    to_date = getdate(filters.get("to_date") or get_last_day(nowdate()))

    if is_admin:
        emp_ids = frappe.get_all("Employee", filters={"status": "Active"}, pluck="name")
    else:
        emp_id = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if not emp_id:
            return []
        emp_ids = [emp_id]

    # Leave Allocations
    allocations = frappe.get_all("Leave Allocation",
        filters={
            "employee": ["in", emp_ids],
            "docstatus": 1,
            "to_date": [">=", from_date],
            "from_date": ["<=", to_date]
        },
        fields=["leave_type", "total_leaves_allocated", "employee", "employee_name"]
    )

    # Leave Applications
    leave_app_filters = {
        "employee": ["in", emp_ids],
        "docstatus": 1,
        "workflow_state": "Approved",
        "from_date": ["<=", to_date],
        "to_date": [">=", from_date]
    }

    leave_apps = frappe.get_all("Leave Application",
        filters=leave_app_filters,
        fields=["employee", "leave_type", "from_date", "to_date"]
    )

    # Count leave days
    leave_taken_map = {}
    for app in leave_apps:
        overlap_start = max(getdate(app.from_date), from_date)
        overlap_end = min(getdate(app.to_date), to_date)
        days = (overlap_end - overlap_start).days + 1
        if days > 0:
            key = (app.employee, app.leave_type)
            leave_taken_map[key] = leave_taken_map.get(key, 0) + days

    # Final data
    data = []
    for alloc in allocations:
        key = (alloc.employee, alloc.leave_type)
        taken = leave_taken_map.get(key, 0)
        balance = alloc.total_leaves_allocated - taken

        data.append({
            "employee": alloc.employee,
            "employee_name": alloc.employee_name,
            "leave_type": alloc.leave_type,
            "total_leaves_allocated": alloc.total_leaves_allocated,
            "leaves_taken": taken,
            "remaining_leaves": balance
        })

    return data
