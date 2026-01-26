# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_data(filters=None):
    if not filters:
        filters = {}

    conditions = {"docstatus": 1}
    if filters.get("employee"):
        conditions["employee"] = filters["employee"]
    if filters.get("department"):
        conditions["department"] = filters["department"]
    if filters.get("designation"):
        conditions["designation"] = filters["designation"]

    documents = frappe.db.get_all(
        "Salary Increment",
        filters=conditions,
        fields=["*"],
        order_by="employee, modified desc"
    )

    data = []
    employee_count = {}

    for doc in documents:
        

        employee_id = doc.employee
        if employee_id not in employee_count:
            employee_count[employee_id] = 1
        else:
            employee_count[employee_id] += 1

        if employee_count[employee_id] <= 2:
            employee_display = employee_id if employee_count[employee_id] == 1 else ""
            if doc.increment_by == 'Percentage':
                row = [
                    employee_display,
                    doc.employee_name if employee_count[employee_id] == 1 else "",
                    doc.department if employee_count[employee_id] == 1 else "",
                    doc.designation if employee_count[employee_id] == 1 else "",

                    getdate(doc.modified),
                    doc.name,
                    doc.increment_by,
                    doc.salary_total,
                    doc.revised_total,
                    doc.revise_total,

                    doc.basic, doc.cca, doc.house_rent_allowance,
                    doc.special_allowance, doc.conveyance_allowance,
                    doc.medical_allowances, doc.shift_allowance,
                    doc.other_allowance, doc.uniform_allowance,
                    doc.magazine_allowances,

                    doc.basic_percent, doc.cca_percent, doc.house_rent_allowance_percent,
                    doc.special_allowance_percent, doc.conveyance_allowance_percent,
                    doc.medical_allowances_percent, doc.shift_allowance_percent,
                    doc.other_allowance_percent, doc.uniform_allowance_percent,
                    doc.magazine_allowances_percent,

                    doc.revise_basic, doc.revise_cca, doc.revise_hra,
                    doc.revise_special_allowance, doc.revise_conveyance_allowance,
                    doc.revise_allowances, doc.revise_shift_allowance,
                    doc.revise_other_allowance, doc.revise_uniform_allowance,
                    doc.revise_magazine_allowance, doc.revise_total
                ]
            elif doc.increment_by == 'Amount':
                row = [
                    employee_display,
                    doc.employee_name if employee_count[employee_id] == 1 else "",
                    doc.department if employee_count[employee_id] == 1 else "",
                    doc.designation if employee_count[employee_id] == 1 else "",

                    getdate(doc.modified),
                    doc.name,
                    doc.increment_by,
                    doc.salary_total,
                    doc.revised_total-doc.salary_total,
                    doc.revised_total,

                    doc.basic, doc.cca, doc.house_rent_allowance,
                    doc.special_allowance, doc.conveyance_allowance,
                    doc.medical_allowances, doc.shift_allowance,
                    doc.other_allowance, doc.uniform_allowance,
                    doc.magazine_allowances,

                    doc.revised_basic, doc.revised_cca, doc.revised_hra,
                    doc.revised_special_allowance, doc.revised_conveyance_allowance,
                    doc.revised_allowances, doc.revised_shift_allowance,
                    doc.revised_other_allowance, doc.revised_uniform_allowance,
                    doc.revised_magazine_allowance, 

                    doc.revise_basic, doc.revise_cca, doc.revise_hra,
                    doc.revise_special_allowance, doc.revise_conveyance_allowance,
                    doc.revise_allowances, doc.revise_shift_allowance,
                    doc.revise_other_allowance, doc.revise_uniform_allowance,
                    doc.revise_magazine_allowance
                ]

            data.append(row)

    return data


def get_columns():
    return [
        {"label": "Employee",        "fieldtype": "Link",     "options": "Employee",    "width": 140},
        {"label": "Employee Name",   "fieldtype": "Data",     "width": 140},
        {"label": "Department",      "fieldtype": "Link",     "options": "Department",  "width": 140},
        {"label": "Designation",     "fieldtype": "Link",     "options": "Designation", "width": 140},
        {"label": "Increment Date",  "fieldtype": "Date",     "width": 140},
        {"label": "Reference Document",   "fieldtype": "Link",     "options": "Salary Increment", "width": 140},
        {"label": "Increment By",    "fieldtype": "Data",     "width": 150},
        {"label": "Old Gross",       "fieldtype": "Currency", "width": 120},
        {"label": "Increment Amount",   "fieldtype": "Currency", "width": 120},
        {"label": "Revised Gross",   "fieldtype": "Currency", "width": 120},

        # Original Salary Components
        {"label": "Basic",           "fieldtype": "Currency"},
        {"label": "CCA",             "fieldtype": "Currency"},
        {"label": "HRA",             "fieldtype": "Currency"},
        {"label": "Special",         "fieldtype": "Currency"},
        {"label": "Conveyance",      "fieldtype": "Currency"},
        {"label": "Medical",         "fieldtype": "Currency"},
        {"label": "Shift",           "fieldtype": "Currency"},
        {"label": "Other",           "fieldtype": "Currency"},
        {"label": "Uniform",         "fieldtype": "Currency"},
        {"label": "Magazine",        "fieldtype": "Currency"},

        # # Increment Salary Components
        {"label": "Increment Basic",   "fieldtype": "Currency"},
        {"label": "Increment CCA",     "fieldtype": "Currency"},
        {"label": "Increment HRA",     "fieldtype": "Currency"},
        {"label": "Increment Special", "fieldtype": "Currency"},
        {"label": "Increment Conv.",   "fieldtype": "Currency"},
        {"label": "Increment Medical", "fieldtype": "Currency"},
        {"label": "Increment Shift",   "fieldtype": "Currency"},
        {"label": "Increment Other",   "fieldtype": "Currency"},
        {"label": "Increment Uniform", "fieldtype": "Currency"},
        {"label": "Increment Magazine","fieldtype": "Currency"},

        # Revised Salary Components
        {"label": "Revised Basic",   "fieldtype": "Currency"},
        {"label": "Revised CCA",     "fieldtype": "Currency"},
        {"label": "Revised HRA",     "fieldtype": "Currency"},
        {"label": "Revised Special", "fieldtype": "Currency"},
        {"label": "Revised Conv.",   "fieldtype": "Currency"},
        {"label": "Revised Medical", "fieldtype": "Currency"},
        {"label": "Revised Shift",   "fieldtype": "Currency"},
        {"label": "Revised Other",   "fieldtype": "Currency"},
        {"label": "Revised Uniform", "fieldtype": "Currency"},
        {"label": "Revised Magazine","fieldtype": "Currency"},
        
    ]
