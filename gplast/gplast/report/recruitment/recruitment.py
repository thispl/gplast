# Copyright (c) 2024, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime, timedelta

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Designation"), "fieldname": "position", "fieldtype": "Link", "options": "Staffing Plan", "width": 300},
        {"label": _("Employee Count"), "fieldname": "employee_count", "fieldtype": "Int", "width": 150},
        {"label": _("Request Count"), "fieldname": "request_count", "fieldtype": "Int", "width": 150},
        {"label": _("Manpower Request"), "fieldname": "manpower_request", "fieldtype": "Int", "width": 150},
        {"label": _("Availability"), "fieldname": "availability", "fieldtype": "Int", "width": 150},
    ]

# def get_data(filters):
#     staffing_plan = frappe.db.get_all("Staffing Plan", {"docstatus": 1}, ["name"])
#     data = []
#     manpower_request = frappe.db.get_all("Manpower Request", {"docstatus":1, "depaertment":staffing_plan["department"]}, ["vacancy_count"])

#     for plan in staffing_plan:
#         doc = frappe.get_doc("Staffing Plan", plan.name)
#         for child in doc.staffing_details:
#             data.append({
#                 "position": plan.name,
#                 "employee_count": child.current_count,
#                 "request_count": child.vacancies,
#                 "manpower_request": 
#                 # "availability": ,
#             })

#     return data

def get_data(filters):
    staffing_plan = frappe.db.get_all("Staffing Plan", {"docstatus": 1}, ["name", "department"])
    data = []

    for plan in staffing_plan:
        doc = frappe.get_doc("Staffing Plan", plan.name)

        for child in doc.staffing_details:
            manpower_requests = frappe.db.get_value(
                "Manpower Request",{
                    "docstatus": 1,
                    "designation": plan.name
                },["vacancy_count"]
            )

            availability = child.current_count - child.vacancies

            data.append({
                "position": plan.name,
                "employee_count": child.current_count,
                "request_count": child.vacancies,
                "manpower_request": manpower_requests or 0,
                # "availability": availability,
            })

    return data


