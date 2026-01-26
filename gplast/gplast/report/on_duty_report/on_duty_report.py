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
		{"label": _("Emp.No"), "fieldname": "emp_no", "fieldtype": "Link", "options": "Employee", "width": 150, "align": "center"},
		{"label": _("Name"), "fieldname": "name", "fieldtype": "Data", "width": 150, "align": "center"},
		{"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 150, "align": "center"},
		{"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150, "align": "center"},
		{"label": _("Unit"), "fieldname": "unit", "fieldtype": "Data", "width": 150, "align": "center"},
		{"label": _("Applied Date"), "fieldname": "applied_date", "fieldtype": "Date", "width": 150, "align": "center"},
		{"label": _("From Date & Time"), "fieldname": "from_date_time", "fieldtype": "Data", "width": 200, "align": "center"},
		{"label": _("To Date & Time"), "fieldname": "to_date_time", "fieldtype": "Data", "width": 200, "align": "center"},
		{"label": _("Place"), "fieldname": "place", "fieldtype": "Data", "width": 150, "align": "center"},
		{"label": _("Purpose"), "fieldname": "purpose", "fieldtype": "Data", "width": 150, "align": "center"},
		{"label": _("Application Status"), "fieldname": "application_status", "fieldtype": "Data", "width": 150, "align": "center"},
	]

def get_data(filters):

	conditions = {
		"docstatus": ["!=", 2], "workflow_state": ["!=", "Rejected"], "entry_applied_date": ["BETWEEN", [filters.get("from_date"), filters.get("to_date")]]
	}

	if filters.get("employee"):
		conditions["employee"] = filters.get("employee")
	
	on_duty_application = frappe.db.get_all("On Duty Application",
										 filters = conditions,
										 fields = ["employee", "employee_name", "department", "company", "entry_applied_date",
					 					"from_date", "from_time", "to_date", "to_time", "address", "purpose", "workflow_state"], order_by="from_date ASC")
	
	result = []

	for on_duty in on_duty_application:

		unit = frappe.db.get_value("Employee", {"employee": on_duty["employee"]}, ["unit"])

		result.append([
			on_duty["employee"],
			on_duty["employee_name"],
			on_duty["department"],
			on_duty["company"],
			unit,
			on_duty["entry_applied_date"],
			f"{on_duty['from_date'].strftime('%d-%m-%Y')} {on_duty['from_time']}",
			f"{on_duty['to_date'].strftime('%d-%m-%Y')} {on_duty['to_time']}",
			on_duty["address"],
			on_duty["purpose"],
			on_duty["workflow_state"]
		])

	return result
