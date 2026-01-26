# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate, getdate
from frappe.utils import get_last_day
from frappe.utils import get_first_day
from frappe.utils import getdate, add_days, nowdate

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    return columns, data, None, chart

def get_columns():
    return [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 180},
        {"label": "Leave Type", "fieldname": "leave_type", "fieldtype": "Link", "options": "Leave Type", "width": 150},
        {"label": "Total Leave Days", "fieldname": "total_leave_days", "fieldtype": "Float", "width": 150},
    ]


def get_data(filters):
	from_date = getdate(filters.get("from_date") or get_first_day(nowdate()))
	to_date = getdate(filters.get("to_date") or get_last_day(nowdate()))

	conditions = """
		WHERE
			docstatus = 1
			AND workflow_state = 'Approved'
			AND from_date <= %(to_date)s
			AND to_date >= %(from_date)s
	"""

	if filters.get("employee"):
		conditions += " AND employee = %(employee)s"

	data = frappe.db.sql(f"""
		SELECT
			employee,
			employee_name,
			leave_type,
			SUM(
				DATEDIFF(
					LEAST(to_date, %(to_date)s),
					GREATEST(from_date, %(from_date)s)
				) + 1
			) AS total_leave_days
		FROM `tabLeave Application`
		{conditions}
		GROUP BY employee, employee_name, leave_type
	""", {
		"from_date": from_date,
		"to_date": to_date,
		"employee": filters.get("employee")
	}, as_dict=True)

	return data


def get_chart_data(data):
    if not data:
        return {}

    labels = [row["leave_type"] for row in data]
    values = [row["total_leave_days"] for row in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": "Leave Taken", "values": values}]
        },
        "type": "pie",
        "colors": ["#34c38f", "#f46a6a", "#556ee6", "#f1b44c"]
    }
