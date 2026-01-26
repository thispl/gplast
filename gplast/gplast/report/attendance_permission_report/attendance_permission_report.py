# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
    return[
		{"label": _("Employee ID"), "fieldname": "employee_id", "fieldtype": "Link", "options": "Employee", "width": 200, "align": "left"},
		{"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
		{"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 200},
		{"label": _("Designation"), "fieldname": "desigantion", "fieldtype": "Link", "options": "Designation", "width": 200},
		{"label": _("Desigantion Code"), "fieldname": "designation_code", "fieldtype": "Link", "options": "Sub Designation", "width": 150},
		{"label": _("Total Permissions"), "fieldname": "total_permission", "fieldtype": "Data", "width": 150},
        {"label": _("Penalty"), "fieldname": "penalty", "fieldtype": "Data", "width": 100},
		{"label": _("Late Entry"), "fieldname": "late_entry", "fieldtype": "Data", "width": 150},
		{"label": _("Early Exit"), "fieldname": "early_exit", "fieldtype": "Data", "width": 150},
		{"label": _("Leave Days"), "fieldname": "leave_days", "fieldtype": "Data", "width": 150},
		{"label": _("Approved"), "fieldname": "approved", "fieldtype": "Data", "width": 150},
		{"label": _("Unapproved"), "fieldname": "unapproved", "fieldtype": "Data", "width": 150}
	]

def get_data(filters):
    conditions = ""

    if filters.get("employee"):
        conditions = f"AND employee = '{filters.get('employee')}'"

    data = []
    
    query = f"""
        SELECT employee, employee_name, department, designation
        FROM `tabAttendance Permission`
        WHERE permission_date BETWEEN %s AND %s
        AND docstatus != 2
        AND workflow_state != 'Rejected'
        {conditions}
        GROUP BY employee
    """

    employees = frappe.db.sql(query, (filters["from_date"], filters["to_date"]), as_dict=True)
    
    leave_hours = {
        (4, 5): 0.5, (6, 7): 1, (8, 9): 1.5,
        (10, 11): 2, (12, 13): 2.5, (14, 15): 3,
        (16, 17): 3.5, (18, 19): 4, (20, 21): 4.5,
        (22, 23): 5
    }
    
    for employee in employees:
        first_half_permission_count = 0
        second_half_permission_count = 0
        approved = 0
        unapproved = 0

        permissions = frappe.db.get_all(
            "Attendance Permission",
            filters={
                "employee": employee["employee"],
                "docstatus": ["!=", 2],
                "workflow_state": ["!=", "Rejected"],
                "permission_date": ["between", [filters["from_date"], filters["to_date"]]]
            },
            fields=["permission_hour", "session", "reason", "workflow_state"]
        )

        total_permission_count = 0

        for permission in permissions:
            permission_hours = int(permission["permission_hour"])
            total_permission_count += permission_hours

            if permission["session"] == "First Half":
                first_half_permission_count += permission_hours
            elif permission["session"] == "Second Half":
                second_half_permission_count += permission_hours

            if permission["workflow_state"] == "Approved":
                approved += permission_hours
            else:
                unapproved += permission_hours

        designation_code = frappe.db.get_value(
            "Employee",
            {"employee": employee["employee"]},
            ["designation_code"]
        )
        
        leave_days = 0
        for hours, days in leave_hours.items():
            if total_permission_count in hours:
                leave_days = days

        data.append([
            employee["employee"],
            employee["employee_name"],
            employee["department"],
            employee["designation"],
            designation_code or "",
            total_permission_count,
            max(0, total_permission_count - 3),
            first_half_permission_count,
            second_half_permission_count,
            leave_days,
            approved,
            unapproved
        ])

    return data

