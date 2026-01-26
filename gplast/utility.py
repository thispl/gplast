import frappe
from frappe import _
# your_app.module_name.py

import frappe
from frappe import _
import math
import frappe
from frappe.utils.csvutils import read_csv_content
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,datetime,get_first_day,get_last_day,today)
from datetime import datetime
from datetime import timedelta
import locale
from datetime import date
from frappe.model.document import Document
import datetime 
import frappe,erpnext
from frappe.utils import cint
import json
from frappe.utils import date_diff, add_months,today,add_days,add_years,nowdate,flt
from frappe.model.mapper import get_mapped_doc
from frappe.utils.file_manager import get_file
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
import datetime
from datetime import date,datetime,timedelta
import openpyxl
from openpyxl import Workbook
import openpyxl
import xlrd
import re
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import GradientFill, PatternFill
# import pandas as pd
from frappe.utils import formatdate
from frappe.utils import now
from erpnext.setup.utils import get_exchange_rate

@frappe.whitelist()
def attendance_calc(from_date, to_date):

    salary_deduction_days = {
        (4, 5, 6): 0.5, (7, 8, 9): 1, (10, 11, 12): 1.5,
        (13, 14, 15): 2, (16, 17, 18): 2.5, (19, 20, 21): 3,
        (22, 23, 24): 3.5, (25, 26, 27): 4, (28, 29, 30): 4.5,
        (31, 32, 33): 5
    }

    employees = frappe.db.get_all("Attendance",
                                  {
                                    "docstatus": 1,
                                    "attendance_date": ["BETWEEN", [from_date, to_date]],
                                    "late_entry": 1
                                    },
                                  ["employee"])

    for emp in employees:

        late_count = frappe.db.count("Attendance",
                                     filters={
                                         "docstatus": 1,
                                         "employee": emp["employee"],
                                         "attendance_date": ["BETWEEN", [from_date, to_date]],
                                         "late_entry": 1,
                                         "late_entry_time": ["<=", "00:15:00"]
                                     })

        deduction_days = 0
        exceed = 0
        
        if late_count > 3:
            exceed = late_count - 3

        for hours, days in salary_deduction_days.items():
            if late_count in hours:
                deduction_days = days
    
                ad = frappe.db.get_all("Salary Structure Assignment",
                                       {"employee": emp["employee"]},
                                       ["*"],
                                       order_by = "from_date DESC")
                if ad:
                    if deduction_days > 0:
                        days = date_diff(to_date,from_date) + 1
                        salary_components = frappe.db.get_value(
                                                                "Employee",
                                                                {"employee": emp["employee"]},
                                                                ["basic", "cca", "house_rent_allowance",
                                                                "special_allowance", "shift_allowance",
                                                                "other_allowance", "arrear", "arrear_hra", "ctc"],
                                                                as_dict=True
                                                            )

                        if salary_components:
                            penalty = (salary_components["basic"] + salary_components["cca"] +
                                    salary_components["house_rent_allowance"] + salary_components["special_allowance"] +
                                    salary_components["shift_allowance"] + salary_components["other_allowance"] +
                                    salary_components["arrear"] + salary_components["arrear_hra"])
                        else:
                            penalty = 0

                        if frappe.db.exists('Late Penalty', {'emp_name': emp["employee"], 'from_date': from_date, 'to_date': to_date, "docstatus": ["!=", 2]}):
                            adsl = frappe.get_doc('Late Penalty', {'emp_name': emp["employee"], 'from_date': from_date, 'to_date': to_date})
                            adsl.emp_name = emp["employee"]
                            adsl.deduction_days = deduction_days
                            adsl.actual_late = late_count
                            adsl.late_days = exceed
                            adsl.from_date = from_date
                            adsl.to_date = to_date
                            adsl.late_penalty = (deduction_days * (int(penalty) / (days)))
                            adsl.save()
                        else:
                            adsl = frappe.new_doc("Late Penalty")
                            adsl.emp_name = emp["employee"]
                            adsl.deduction_days = deduction_days
                            adsl.actual_late = late_count
                            adsl.late_days = exceed
                            adsl.from_date = from_date
                            adsl.to_date = to_date
                            adsl.late_penalty = (deduction_days * (int(penalty) / (days)))
                            adsl.save()
    return "ok"
    
@frappe.whitelist()
def additional_salary(from_date,to_date):
    employees = frappe.get_all("Employee", {"status": "Active", 'date_of_joining': ['<=', from_date]}, ["*"])
    for emp in employees:
        
        lp = frappe.db.get_value("Late Penalty",
                                 {"emp_name": emp["name"], "from_date": from_date, "to_date": to_date},
                                 ["emp_name", "deduction_days", "from_date", "late_penalty"], as_dict=True)
        if lp:
            if lp.deduction_days > 0:
                date_str1 = lp.from_date
                date_str2 = emp.date_of_joining
                date_obj1 = datetime.strptime(str(date_str1), '%Y-%m-%d').date()
                date_obj2 = datetime.strptime(str(date_str2),'%Y-%m-%d').date()
                if date_obj1 > date_obj2:
                    payroll_date = date_obj1
                else:
                    payroll_date = date_obj2
                if frappe.db.exists('Additional Salary', {'employee': emp.name, 'payroll_date': payroll_date, "docstatus": ["!=", 2]}):
                    ad = frappe.get_doc('Additional Salary', {'employee': emp.name, 'payroll_date': payroll_date})
                    ad.employee = emp.name
                    ad.salary_component = "Late Penalty"
                    ad.company = emp.company
                    ad.amount = lp.late_penalty
                    ad.payroll_date = payroll_date
                    ad.save(ignore_permissions=True)
                    ad.submit()
                else:
                    ad = frappe.new_doc('Additional Salary')
                    ad.employee = emp.name
                    ad.salary_component = "Late Penalty"
                    ad.company = emp.company
                    ad.amount = lp.late_penalty
                    ad.payroll_date = payroll_date
                    ad.save(ignore_permissions=True)
                    ad.submit()
    return "ok"


# @frappe.whitelist()
# def process_permission(from_date, to_date):
# 	lp = 0
# 	hours = 0
# 	employees = frappe.get_all("Employee", {"status": "Active"}, ["*"])
# 	for emp in employees:
# 		lp_lists = frappe.db.sql("""
# 			select * from `tabAttendance Permission` 
# 			where employee = %s and permission_date between %s and %s
# 		""", (emp.name, from_date, to_date), as_dict=True)
        

# 		for lp_list in lp_lists:
# 			if lp_list:
# 				lp = lp_list
# 				# frappe.errprint(lp)
                
# 				if not frappe.db.exists("Leave deduction depend on Permission", {"employee": lp.get("employee")}):
# 					ad = frappe.new_doc('Leave deduction depend on Permission')
# 					leave_ledger_entries = frappe.get_all("Leave Ledger Entry", ["*"])

# 					for entry in leave_ledger_entries:
# 						frappe.errprint(entry)
# 					# leave_entry = frappe.new_doc("Leave Ledger Entry")
# 					# leave_entry.save(ignore_permissions=True)
# 					ad.employee = lp.get("employee")
# 					ad.employee_name=lp.get('employee_name')
# 					ad.from_date=from_date
# 					ad.to_date=to_date
# 					if lp.get('employee') == ad.employee:
# 						frappe.errprint(lp.get('name'))
# 						frappe.errprint(lp.get('permission_hour'))
# 						hours += int(lp.get('permission_hour'))
# 					ad.permission_hours = hours
# 					if (ad.permission_hours == 4  or ad.permission_hours == 5):
# 						ad.leave_days=' 0.5'
# 					elif (ad.permission_hours == 6 or ad.permission_hours == 7):
# 						ad.leave_days='1'
# 					elif (ad.permission_hours == 8 or ad.permission_hours == 9):
# 						ad.leave_days='1.5'
# 					elif (ad.permission_hours ==10  or ad.permission_hours == 11):
# 						ad.leave_days='2'
# 					frappe.db.commit()
# 					ad.save(ignore_permissions=True)
# 					frappe.errprint("Late Penalty Created via Additional Salary")
# 				else:
# 					ad = frappe.get_doc('Leave deduction depend on Permission', {"employee": lp.get("employee")})
# 					# if frappe.db.exists("Leave Ledger Entry",{'employee':ad.employee}):
# 					# leave = frappe.db.get_value("Leave Ledger Entry", ["employee",'leave_type','leaves'],as_dict=1)
                    
# 					ad.employee = lp.get("employee")
# 					ad.employee_name=lp.get('employee_name')
# 					ad.from_date=from_date
# 					ad.to_date=to_date

# 					if lp.get('employee') == ad.employee:
# 						frappe.errprint(lp.get('name'))
# 						frappe.errprint(lp.get('permission_hour'))
# 						hours += int(lp.get('permission_hour'))
# 					ad.permission_hours = hours
# 					if (ad.permission_hours == 4  or ad.permission_hours == 5):
# 						ad.leave_days=' 0.5'
# 					elif (ad.permission_hours == 6 or ad.permission_hours == 7):
# 						ad.leave_days='1'
# 					elif (ad.permission_hours == 8 or ad.permission_hours == 9):
# 						ad.leave_days='1.5'
# 					elif (ad.permission_hours ==10  or ad.permission_hours == 11):
# 						ad.leave_days='2'
# 					leave_ledger_entries = frappe.get_all("Leave Ledger Entry", ["*"])
# 					ad_employee = ad.employee  

# 					for entry in leave_ledger_entries:
# 						frappe.errprint(entry)
                        
# 						if entry.employee == ad_employee:
# 							leave = float(ad.leave_days) - float(entry.leaves)
# 							frappe.errprint(leave)
# 							frappe.db.set_value("Leave Ledger Entry", entry.name, "leaves", leave)
# 							frappe.get_doc("Leave Ledger Entry", entry.name).submit()
# 					frappe.db.commit()

# 					ad.save(ignore_permissions=True)
# 					frappe.errprint("Late Penalty Created via Additional Salary")

# 	return "ok"
# @frappe.whitelist()
# def leave_permission(from_date, to_date, leave_deduction):
#     employees = frappe.get_all('Employee', {'status': 'Active'}, ['name', 'employee_name'])
    
#     for emp in employees:
#         leave_ledger_entries = frappe.get_all(
#             "Leave Ledger Entry",
#             filters={'employee': emp.name, 'leave_type': leave_deduction},
#             fields=["*"],
#             order_by="name DESC, creation DESC",
#             limit_page_length=1
#         )

#         if leave_ledger_entries:
#             latest_leave_entry = leave_ledger_entries[0]
#             lp_lists = frappe.db.sql("""
#                 SELECT * FROM `tabLeave deduction depend on Permission`
#                 WHERE from_date BETWEEN %s AND %s AND employee = %s
#             """, (from_date, to_date, emp.name), as_dict=True)
#             for lp_list in lp_lists:
#                 if latest_leave_entry.leave>0:
#                     ad = frappe.new_doc('Leave Ledger Entry')
#                     ad.employee = emp.name
#                     ad.employee_name = emp.employee_name
#                     ad.from_date = lp_list.get("from_date")
#                     ad.to_date = lp_list.get("to_date")
#                     ad.leave_type = latest_leave_entry.leave_type
#                     ad.transaction_type = latest_leave_entry.transaction_type
#                     ad.leaves = float(latest_leave_entry.leaves) - float(lp_list.get("leave_days"))
#                     ad.transaction_name = latest_leave_entry.transaction_name

#                     ad.save()
#                     frappe.db.commit()
#                     frappe.errprint("Leave Ledger Entry updated for employee: {}".format(emp.name))
#         else:
#             leave_ledger_entries = frappe.get_all(
#             "Leave Ledger Entry",
#             filters={'employee': emp.name},
#             fields=["*"],
#             order_by="name DESC, creation DESC",
#             limit_page_length=1
#             )
#             latest_leave_entry = leave_ledger_entries[0]
#             lp_lists = frappe.db.sql("""
#                 SELECT * FROM `tabLeave deduction depend on Permission`
#                 WHERE from_date BETWEEN %s AND %s AND employee = %s
#             """, (from_date, to_date, emp.name), as_dict=True)
#             for lp_list in lp_lists:
#                 if latest_leave_entry.leave=<0:
#                     ad = frappe.new_doc('Leave Ledger Entry')
#                     ad.employee = emp.name
#                     ad.employee_name = emp.employee_name
#                     ad.from_date = lp_list.get("from_date")
#                     ad.to_date = lp_list.get("to_date")
#                     ad.leave_type = leave_deduction
#                     ad.transaction_type = latest_leave_entry.transaction_type
#                     ad.leaves = float(latest_leave_entry.leaves) + float(lp_list.get("leave_days"))
#                     ad.transaction_name = latest_leave_entry.transaction_name

#                     ad.save()
#                     frappe.db.commit()
#                     frappe.errprint("Leave Ledger Entry updated for employee: {}".format(emp.name))


#     return "ok"

# @frappe.whitelist()
# def leave_deduction(leave,employee,leave_type):
#     employees = frappe.get_all('Employee', {'status': 'Active'}, ['name', 'employee_name'])
#     v=0
#     for emp in employees:
#         leave_ledger_entries = frappe.get_all(
#             "Leave Ledger Entry",
#             filters={'employee':employee, 'leave_type':leave_type or ''},
#             fields=["*"],
#             order_by="name DESC, creation DESC",
#             limit_page_length=1
#         )

#         if leave_ledger_entries:
#             latest_leave_entry = leave_ledger_entries[0]
#             v = float(latest_leave_entry.leaves) - float(leave)
#     return v
@frappe.whitelist()
def total_value(permission_hours,employee):
    total_hours = 0
    employees = frappe.get_all('Attendance Permission', {'employee': employee}, ['*'])

    for emp in employees:
        permission_hour_str = emp.get('permission_hour', '')
        if permission_hour_str and permission_hour_str.strip().isdigit():
            kl = int(permission_hour_str)
            total_hours += kl

    return total_hours

@frappe.whitelist()
def get_status(employee):
    leave_ledger_entries_casual = frappe.get_all(
        "Leave Ledger Entry",
        filters={'employee': employee, 'leave_type': 'Casual Leave'},
        fields=["*"],
        order_by="creation DESC",
        limit_page_length=1
    )

    leave_ledger_entries_privilege = frappe.get_all(
        "Leave Ledger Entry",
        filters={'employee': employee, 'leave_type': 'Privilege Leave'},
        fields=["*"],
        order_by="creation DESC",
        limit_page_length=1
    )

    latest_leave_entry_casual = leave_ledger_entries_casual[0] if leave_ledger_entries_casual else None
    latest_leave_entry_privilege = leave_ledger_entries_privilege[0] if leave_ledger_entries_privilege else None

    # Initialize data
    data = ''

    print("Latest Casual Leave Entry:", latest_leave_entry_casual)
    print("Latest Privilege Leave Entry:", latest_leave_entry_privilege)

    if latest_leave_entry_casual or latest_leave_entry_privilege:
        data += '<table border="1" width="100%"><tr style="">'
        data += '<td style="text-align: center;"><b>Leave Type</b></td>'
        data += '<td style="text-align: center;"><b>Total Leave</b></td></tr>'

    if latest_leave_entry_casual:
        print("Casual Leave Entry Leaves:", latest_leave_entry_casual.leaves)
        data += '<tr style=""><td style="text-align: center;"><b>Casual leave</b></td>'
        data += '<td style="text-align: center;"><b>%s</b></td></tr>' % (latest_leave_entry_casual.leaves)

    if latest_leave_entry_privilege:
        print("Privilege Leave Entry Leaves:", latest_leave_entry_privilege.leaves)
        data += '<tr style=""><td style="text-align: center;"><b>Privilege Leave</b></td>'
        data += '<td style="text-align: center;"><b>%s</b></td></tr>' % (latest_leave_entry_privilege.leaves)

    data += '</table>'
    return data

@frappe.whitelist()
def get_to_date(from_date):
    return get_last_day(from_date)

@frappe.whitelist()
def early_exit_calc(from_date, to_date):

    attendance = frappe.db.get_all("Attendance",
                                   {"attendance_date": ["BETWEEN", [from_date, to_date]],  "out_time": ["!=", ""], "docstatus": 1},
                                   ["employee", "shift", "out_time"])
    
    salary_deduction_days = {
        (4, 5, 6): 0.5, (7, 8, 9): 1, (10, 11, 12): 1.5,
        (13, 14, 15): 2, (16, 17, 18): 2.5, (19, 20, 21): 3,
        (22, 23, 24): 3.5, (25, 26, 27): 4, (28, 29, 30): 4.5,
        (31, 32, 33): 5
    }
    
    employee_count = {}

    for att in attendance:
        employee = att["employee"]
        shift_end_time = frappe.db.get_value("Shift Type", {"name": att["shift"]}, "end_time")
        
        if shift_end_time is None:
            shift_end_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
        elif isinstance(shift_end_time, timedelta):
            shift_end_time = (datetime.min + shift_end_time).time()
        elif isinstance(shift_end_time, datetime):
            shift_end_time = shift_end_time.time()
        
        if isinstance(att["out_time"], datetime):
            att_out_time = att["out_time"].time()
        elif isinstance(att["out_time"], str):
            att_out_time = datetime.strptime(att["out_time"], "%H:%M:%S").time()
        else:
            att_out_time = att["out_time"]
        
        time_difference = (datetime.combine(datetime.min, shift_end_time) - datetime.combine(datetime.min, att_out_time)).total_seconds() / 60
        
        if 0 < time_difference <= 15:
            employee_count[employee] = employee_count.get(employee, 0) + 1
    
    for employee, count in employee_count.items():
        deduction_days = next((deduction for range_keys, deduction in salary_deduction_days.items() if count in range_keys), 0)
    
        ad = frappe.db.get_all("Salary Structure Assignment",
                                {"employee": employee},
                                ["*"],
                                order_by = "from_date DESC")
        if ad:
            if deduction_days > 0:
                days = date_diff(to_date,from_date) + 1
                salary_components = frappe.db.get_value(
                                                        "Employee",
                                                        {"employee": employee},
                                                        ["basic", "cca", "house_rent_allowance",
                                                        "special_allowance", "shift_allowance",
                                                        "other_allowance", "arrear", "arrear_hra", "ctc"],
                                                        as_dict=True
                                                    )

                if salary_components:
                    penalty = (salary_components["basic"] + salary_components["cca"] +
                            salary_components["house_rent_allowance"] + salary_components["special_allowance"] +
                            salary_components["shift_allowance"] + salary_components["other_allowance"] +
                            salary_components["arrear"] + salary_components["arrear_hra"])
                else:
                    penalty = 0

                if frappe.db.exists('Early Exit Penalty', {'emp_name': employee, 'from_date': from_date, 'to_date': to_date, "docstatus": ["!=", 2]}):
                    adsl = frappe.get_doc('Early Exit Penalty', {'emp_name': employee, 'from_date': from_date, 'to_date': to_date})
                    adsl.emp_name = employee
                    adsl.deduction_days = deduction_days
                    adsl.actual_early_exit = count
                    adsl.early_exit_days = count - 3 if count > 3 else 0
                    adsl.from_date = from_date
                    adsl.to_date = to_date
                    adsl.early_exit_penalty = (deduction_days * (int(penalty) / (days)))
                    adsl.save()
                else:
                    adsl = frappe.new_doc("Early Exit Penalty")
                    adsl.emp_name = employee
                    adsl.deduction_days = deduction_days
                    adsl.actual_early_exit = count
                    adsl.early_exit_days = count - 3 if count > 3 else 0
                    adsl.from_date = from_date
                    adsl.to_date = to_date
                    adsl.early_exit_penalty = (deduction_days * (int(penalty) / (days)))
                    adsl.save()
    return "ok"


@frappe.whitelist()
def early_exit_additional_salary(from_date,to_date):
    employees = frappe.get_all("Employee", {"status": "Active", 'date_of_joining': ['<=', from_date]}, ["*"])
    for emp in employees:
        
        lp = frappe.db.get_value("Early Exit Penalty",
                                 {"emp_name": emp["name"], "from_date": from_date, "to_date": to_date},
                                 ["emp_name", "deduction_days", "from_date", "early_exit_penalty"], as_dict=True)
        if lp:
            if lp.deduction_days > 0:
                date_str1 = lp.from_date
                date_str2 = emp.date_of_joining
                date_obj1 = datetime.strptime(str(date_str1), '%Y-%m-%d').date()
                date_obj2 = datetime.strptime(str(date_str2),'%Y-%m-%d').date()
                if date_obj1 > date_obj2:
                    payroll_date = date_obj1
                else:
                    payroll_date = date_obj2
                if frappe.db.exists('Additional Salary', {'employee': emp.name, 'payroll_date': payroll_date, "docstatus": ["!=", 2]}):
                    ad = frappe.get_doc('Additional Salary', {'employee': emp.name, 'payroll_date': payroll_date})
                    ad.employee = emp.name
                    ad.salary_component = "Early Exit Penalty"
                    ad.company = emp.company
                    ad.amount = lp.early_exit_penalty
                    ad.payroll_date = payroll_date
                    ad.save(ignore_permissions=True)
                    ad.submit()
                else:
                    ad = frappe.new_doc('Additional Salary')
                    ad.employee = emp.name
                    ad.salary_component = "Early Exit Penalty"
                    ad.company = emp.company
                    ad.amount = lp.early_exit_penalty
                    ad.payroll_date = payroll_date
                    ad.save(ignore_permissions=True)
                    ad.submit()
    return "ok"
