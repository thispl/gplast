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
		{"label": _("Emp.no"), "fieldname": "emp_no", "fieldtype": "Link", "options": "Employee", "width": 150, "align": "center"},
		{"label": _("Name"), "fieldname": "name", "fieldtype": "Data", "width": 150, "align": "center"},
		{"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 150, "align": "center"},
		{"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150, "align": "center"},
		{"label": _("Unit"), "fieldname": "unit", "fieldtype": "Data", "width": 100, "align": "center"},
		{"label": _("Applied Date"), "fieldname": "applied_date", "fieldtype": "Date", "width": 150, "align": "center"},
		{"label": _("Miss Punch Date"), "fieldname": "misspunch_date", "fieldtype": "Date", "width": 150, "align": "center"},
		{"label": _("Miss Punch Direction"), "fieldname": "misspunch_direction", "fieldtype": "Data", "width": 150, "align": "center"},
		{"label": _("Regularization Status"), "fieldname": "regularization_status", "fieldtype": "Data", "width": 150, "align": "center"},
	]

def get_data(filters):

	conditions = {
		"docstatus": ["!=", 2], "workflow_state": ["!=", "Rejected"], "attendance_date": ["BETWEEN", [filters.get("from_date"), filters.get("to_date")]]
	}

	if filters.get("employee"):
		conditions["employee"] = filters.get("employee")
	
	misspunch_application = frappe.db.get_all("Miss Punch Application",
										   filters = conditions,
										   fields = ["employee", "employee_name", "company", "department", "entry_applied_date",
					   						"attendance_date", "workflow_state", "in", "out"], order_by="attendance_date ASC")
	
	result = []

	for miss in misspunch_application:

		unit = frappe.db.get_value("Employee", {"employee": miss["employee"]}, ["unit"])

		in_out = ""

		if miss["in"] == 1:
			in_out = "OUT"
		elif miss["out"] == 1:
			in_out = "IN"
		else:
			in_out = ""

		result.append([
			miss["employee"],
			miss["employee_name"],
			miss["department"],
			miss["company"],
			unit,
			miss["entry_applied_date"],
			miss["attendance_date"],
			in_out,
			miss["workflow_state"]
		])

	return result