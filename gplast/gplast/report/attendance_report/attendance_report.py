# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Date"), "fieldname": "attendance_date", "fieldtype": "Date", "width": 120,"align": "left"},
        {"label": _("Employee No"), "fieldname": "employee", "fieldtype": "Data", "options": "Employee", "width": 120,"align": "left"},
        {"label": _("Employe Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 150,"align": "left"},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 150,"align": "left"},
        {"label": _("Designation"), "fieldname": "designation", "fieldtype": "Link", "options": "Designation", "width": 150,"align": "left"},
        {"label": _("Shift"), "fieldname": "shift", "fieldtype": "Link", "options": "Shift Type", "width": 70,"align": "center"},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100, "align": "center"},        {"label": _("In Time"), "fieldname": "in_time", "fieldtype": "Datetime", "width": 170,"align": "left"},
        {"label": _("Out Time"), "fieldname": "out_time", "fieldtype": "Datetime", "width": 170,"align": "left"},
        {"label": _("Working Hours"), "fieldname": "working_hours", "fieldtype": "Float", "width": 120,"align": "left"},
        {"label": _("OT Hours"), "fieldname": "overtime_hours", "fieldtype": "Float", "width": 120,"align": "left"},
    ]

	
def get_data(filters):
    conditions = []
    values = {}

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("attendance_date BETWEEN %(from_date)s AND %(to_date)s")
        values["from_date"] = filters.get("from_date")
        values["to_date"] = filters.get("to_date")

    if filters.get("employee"):
        conditions.append("employee = %(employee)s")
        values["employee"] = filters.get("employee")

    condition_str = " and " + " and ".join(conditions) if conditions else ""

    query = f"""
        SELECT
            attendance_date,
            employee,
            employee_name,
            department,
            designation,
            shift,
            in_time,
            out_time,
            status,
            total_working_hours as working_hours,
            overtime_hours
        FROM `tabAttendance`
        WHERE docstatus != 2
        {condition_str}
        ORDER BY attendance_date ASC
    """

    return frappe.db.sql(query, values, as_dict=True)
