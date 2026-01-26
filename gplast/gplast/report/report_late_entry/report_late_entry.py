# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_time, time_diff_in_seconds
from datetime import datetime, timedelta

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Employee"), "fieldname": "employee_id", "fieldtype": "Link", "options": "Employee", "width": 130, "align": "left"},
        {"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 180},
        {"label": _("Designation"), "fieldname": "designation", "fieldtype": "Link", "options": "Designation", "width": 200},
        {"label": _("Designation Code"), "fieldname": "designation_code", "fieldtype": "Link", "options": "Sub Designation", "width": 120},
        {"label": _("Total Late"), "fieldname": "total_late", "fieldtype": "Int", "width": 100},
        {"label": _("Exceed Late"), "fieldname": "exceed_late", "fieldtype": "Int", "width": 100},
        {"label": _("Salary Deduction Days"), "fieldname": "salary_deduction_late", "fieldtype": "Data", "width": 180}
    ]

def get_data(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    conditions = {
        "attendance_date": ["BETWEEN", [from_date, to_date]],
        "late_entry": 1, "docstatus": ['!=',2]
    }

    if filters.get("employee"):
        conditions["employee"] = filters.get("employee")

    salary_deduction_days = {
        (4, 5, 6): 0.5, (7, 8, 9): 1, (10, 11, 12): 1.5,
        (13, 14, 15): 2, (16, 17, 18): 2.5, (19, 20, 21): 3,
        (22, 23, 24): 3.5, (25, 26, 27): 4, (28, 29, 30): 4.5,
        (31, 32, 33): 5
    }

    employees = frappe.db.get_all("Attendance",
                                  filters=conditions,
                                  fields=["employee"],
                                  distinct=True)

    result = []

    for emp in employees:
        employee = emp["employee"]

        late_count = frappe.db.count("Attendance",
                                     filters={
                                         "employee": employee,
                                         "attendance_date": ["BETWEEN", [from_date, to_date]],
                                         "late_entry": 1, "docstatus": ["!=",2],
                                         "late_entry_time": ["<=", "00:15:00"]
                                     })

        name = frappe.db.get_value("Employee",
                                   {"name": employee},
                                   ["employee_name", "department", "designation", "designation_code"],
                                   as_dict=True)

        deduction_days = 0
        exceed = 0
        
        if late_count > 3:
            exceed = late_count - 3

        for hours, days in salary_deduction_days.items():
            if late_count in hours:
                deduction_days = days
        if late_count:       
            result.append([
                employee,
                name.employee_name,
                name.department,
                name.designation,
                name.designation_code,
                late_count,
                exceed,
                deduction_days
            ])

    return result

