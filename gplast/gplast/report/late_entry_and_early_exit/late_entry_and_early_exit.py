# # Copyright (c) 2025, Teampro and contributors
# # For license information, please see license.txt


# import frappe
# from frappe import _
# from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
# 	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
# from datetime import datetime, timedelta

# def execute(filters=None):
# 	columns = get_columns()
# 	data = get_data(filters)
# 	return columns, data

# def get_columns():
# 	return[
# 		_("Employee") + ":Link/Employee:100",
# 		_("Employee Name") + ":Data:100",
# 		_("Department") + ":Link/Department:100",
# 		_("Designation") + ":Link/Designation:100",
# 		_("Designation Code") + ":Link/Sub Designation:100",
# 		_("Total Late") + ":Int:100",
# 		_("Total Early Exit") + ":Int:100",
# 		_("Total") + ":Int:100",
# 		_("Total Exceed") + ":Int:100",
# 		_("Salary Deduction Days") + ":Float:100"
# 	]

# def get_data(filters):
# 	data=[]

# 	# if not filters.from_date or not filters.to_date:
# 	# 	return data

# 	if filters.from_date and filters.to_date:
# 		employees=frappe.get_all("Attendance",filters = {"attendance_date":["between",[filters.from_date, filters.to_date]],'docstatus':['!=',2]},fields=["name","employee","employee_name","department","late_entry","early_exit","shift","out_time","in_time"],order_by="employee asc")
    
# 	if filters.employee:
# 		employees=frappe.get_all("Attendance",filters = {'docstatus':['!=',2],"attendance_date":["between",[filters.from_date, filters.to_date]],"employee":filters.employee},fields=["name","employee","employee_name","department","late_entry","early_exit","shift","out_time","in_time"],order_by="employee asc")

# 	salary_deduction_days = {
# 		(4, 5, 6): 0.5, (7, 8, 9): 1, (10, 11, 12): 1.5,
# 		(13, 14, 15): 2, (16, 17, 18): 2.5, (19, 20, 21): 3,
# 		(22, 23, 24): 3.5, (25, 26, 27): 4, (28, 29, 30): 4.5,
# 		(31, 32, 33): 5
# 	}

# 	employee_count = {}
# 	count =0
# 	# frappe.errprint(employees)

# 	for i in employees:
# 		employee = i["employee"]
# 		# frappe.errprint(i["name"])
# 		late_entry_count = frappe.db.sql("""
# 			SELECT COUNT(*) 
# 			FROM `tabAttendance` 
# 			WHERE 
# 				attendance_date BETWEEN %(from_date)s AND %(to_date)s
# 				AND employee = %(employee)s
# 				AND late_entry = 1
# 				AND TIME(late_entry_time) < '00:15:59'
# 		""", {
# 			"from_date": filters.from_date,
# 			"to_date": filters.to_date,
# 			"employee": employee
# 		})[0][0]
# 		early_exit_count = frappe.db.sql("""
# 			SELECT COUNT(*) 
# 			FROM `tabAttendance` 
# 			WHERE 
# 				attendance_date BETWEEN %(from_date)s AND %(to_date)s
# 				AND employee = %(employee)s
# 				AND early_exit = 1
# 				AND TIME(early_exit_time) < '00:15:59'
# 		""", {
# 			"from_date": filters.from_date,
# 			"to_date": filters.to_date,
# 			"employee": employee
# 		})[0][0]


# 		# late_entry_count = frappe.db.count("Attendance", {"attendance_date": ["between", [filters.from_date, filters.to_date]], "employee": employee, "late_entry": 1,'late_entry_time':['']})
# 		# early_exit_count = frappe.db.count("Attendance", {"attendance_date": ["between", [filters.from_date, filters.to_date]], "employee": employee, "early_exit": 1})
# 		# total_count = late_entry_count + early_exit_count
# 		# frappe.errprint(employee)
# 		# if i.early_exit and i["out_time"] and i["shift"]:
# 		# 	shift_end_time = frappe.db.get_value("Shift Type", {"name": i["shift"]}, "end_time")
# 		# 	if shift_end_time is None:
# 		# 		shift_end_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
# 		# 	elif isinstance(shift_end_time, timedelta):
# 		# 		shift_end_time = (datetime.min + shift_end_time).time()
# 		# 	elif isinstance(shift_end_time, datetime):
# 		# 		shift_end_time = shift_end_time.time()

# 		# 	out_time = i["out_time"]
# 		# 	if isinstance(out_time, datetime):
# 		# 		att_out_time = out_time.time()
# 		# 	elif isinstance(out_time, str):
# 		# 		att_out_time = datetime.strptime(out_time, "%H:%M:%S").time()
# 		# 	else:
# 		# 		att_out_time = out_time

# 		# 	time_difference = (datetime.combine(datetime.min, shift_end_time) - datetime.combine(datetime.min, att_out_time)).total_seconds() / 60
# 		# 	# frappe.errprint(employee_count)
# 		# 	if 0 < time_difference <= 15:
# 		# 		# employee_count[employee] = employee_count.get(employee, 0) + 1
# 		# 		employee_count[employee] = employee_count.get(employee, count) + 1
# 		# 		# frappe.errprint(employee_count)

# 		# elif i.late_entry and i["in_time"] and i["shift"]:
# 		# 	shift_start_time = frappe.db.get_value("Shift Type", {"name": i["shift"]}, "start_time")
# 		# 	if shift_start_time is None:
# 		# 		shift_start_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
# 		# 	elif isinstance(shift_start_time, timedelta):
# 		# 		shift_start_time = (datetime.min + shift_start_time).time()
# 		# 	elif isinstance(shift_start_time, datetime):
# 		# 		shift_start_time = shift_start_time.time()

# 		# 	in_time = i.get("in_time") or i.get("out_time")
# 		# 	if isinstance(in_time, datetime):
# 		# 		att_in_time = in_time.time()
# 		# 	elif isinstance(in_time, str):
# 		# 		att_in_time = datetime.strptime(in_time, "%H:%M:%S").time()
# 		# 	else:
# 		# 		att_in_time = in_time

# 		# 	time_difference = (datetime.combine(datetime.min, att_in_time) - datetime.combine(datetime.min, shift_start_time)).total_seconds() / 60

# 		# 	if 0 < time_difference <= 15:
# 		# 		# employee_count[employee] += employee_count.get(employee, count) + 1
# 		# 		employee_count[employee] = employee_count.get(employee, count) + 1

# 	data = []
    
# 	for employee, count in employee_count.items():
# 		# deduction_days = next((deduction for range_keys, deduction in salary_deduction_days.items() if count in range_keys), 0)
# 		deduction_days = 0
# 		# frappe.errprint(f"{employee} {count}")
# 		for r, d in salary_deduction_days.items():
# 			if count in r:
# 				deduction_days = d
# 				break

# 		emp_details = frappe.db.get_value("Employee", {"name": employee}, ["employee_name", "department", "designation", "designation_code"], as_dict=True)
# 		# late_entry_count = frappe.db.count("Attendance", filters={"attendance_date": ["between", [filters.from_date, filters.to_date]], "employee": employee, "late_entry": 1})
# 		# early_exit_count = frappe.db.count("Attendance", filters={"attendance_date": ["between", [filters.from_date, filters.to_date]], "employee": employee, "early_exit": 1})
# 		total_count = late_entry_count + early_exit_count
# 		data.append([
# 			employee,
# 			emp_details.employee_name,
# 			emp_details.department,
# 			emp_details.designation,
# 			emp_details.designation_code,
# 			late_entry_count,
# 			early_exit_count,
# 			total_count,
# 			total_count - 3 if total_count > 3 else 0,
# 			deduction_days
# 		])

# 	return data

        
# 		# if late_entry_count !=0 or early_exit_count !=0:
# 		# 	row=[
# 		# 		i.employee,
# 		# 		i.employee_name,
# 		# 		i.department,
# 		# 		emp_designation,
# 		# 		emp_designation_code,
# 		# 		late_entry_count,
# 		# 		early_exit_count,
# 		# 		total_count,
# 		# 		total_count - 3 if total_count > 3 else 0,
# 		# 		# i.

# 		# 	]
# 		# 	data.append(row)
# 	# return data


# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate
from datetime import datetime, timedelta

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        _("Employee") + ":Link/Employee:100",
        _("Employee Name") + ":Data:100",
        _("Department") + ":Link/Department:100",
        _("Designation") + ":Link/Designation:100",
        _("Designation Code") + ":Link/Sub Designation:100",
        _("Total Late") + ":Int:100",
        _("Total Early Exit") + ":Int:100",
        _("Total") + ":Int:100",
        _("Total Exceed") + ":Int:100",
        _("Salary Deduction Days") + ":Float:100"
    ]

def get_data(filters):
    if not (filters.from_date and filters.to_date):
        return []


    salary_deduction_days = {
        (4, 5, 6): 0.5, (7, 8, 9): 1, (10, 11, 12): 1.5,
        (13, 14, 15): 2, (16, 17, 18): 2.5, (19, 20, 21): 3,
        (22, 23, 24): 3.5, (25, 26, 27): 4, (28, 29, 30): 4.5,
        (31, 32, 33): 5
    }

    employee_data = {}
    conditions = [
        "attendance_date BETWEEN %(from_date)s AND %(to_date)s",
        "docstatus != 2",
        "( (late_entry = 1 AND TIME(late_entry_time) <= '00:15:59') OR (early_exit = 1 AND TIME(early_exit_time) <= '00:15:59') )"
    ]
    if filters.get('employee'):
        conditions.append("employee = %(employee)s")

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT employee FROM `tabAttendance`
        WHERE {where_clause}
    """
    attendances = frappe.db.sql(query, filters, as_dict=1)



    for att in attendances:
        emp = att.employee
        if emp not in employee_data:
            employee_data[emp] = {"late": 0, "early": 0}

    # Get only late entries below 15 mins
    if filters.get('employee'):
        late_entries = frappe.db.sql("""
            SELECT employee FROM `tabAttendance`
            WHERE attendance_date BETWEEN %(from_date)s AND %(to_date)s
            AND late_entry = 1 AND TIME(late_entry_time) < '00:15:59'
            AND docstatus != 2 AND employee =%(employee)s
        """, filters, as_dict=1)
    else:
        late_entries = frappe.db.sql("""
            SELECT employee FROM `tabAttendance`
            WHERE attendance_date BETWEEN %(from_date)s AND %(to_date)s
            AND late_entry = 1 AND TIME(late_entry_time) < '00:15:59'
            AND docstatus != 2
        """, filters, as_dict=1)

    for row in late_entries:
        employee_data.setdefault(row.employee, {"late": 0, "early": 0})
        employee_data[row.employee]["late"] += 1
    if filters.get('employee'):
        early_exits = frappe.db.sql("""
            SELECT employee FROM `tabAttendance`
            WHERE attendance_date BETWEEN %(from_date)s AND %(to_date)s
            AND early_exit = 1 AND TIME(early_exit_time) < '00:15:59'
            AND docstatus != 2  AND employee =%(employee)s
        """, filters, as_dict=1)
    else:
        early_exits = frappe.db.sql("""
        SELECT employee FROM `tabAttendance`
        WHERE attendance_date BETWEEN %(from_date)s AND %(to_date)s
        AND early_exit = 1 AND TIME(early_exit_time) < '00:15:59'
        AND docstatus != 2
    """, filters, as_dict=1)

    for row in early_exits:
        employee_data.setdefault(row.employee, {"late": 0, "early": 0})
        employee_data[row.employee]["early"] += 1

    data = []
    for emp, counts in employee_data.items():
        emp_details = frappe.db.get_value(
            "Employee",
            {"name": emp},
            ["employee_name", "department", "designation", "designation_code"],
            as_dict=True
        )

        total = counts["late"] + counts["early"]
        total_exceed = total - 3 if total > 3 else 0
        deduction_days = 0
        for r, d in salary_deduction_days.items():
            if total in r:
                deduction_days = d
                break

        data.append([
            emp,
            emp_details.employee_name,
            emp_details.department,
            emp_details.designation,
            emp_details.designation_code,
            counts["late"],
            counts["early"],
            total,
            total_exceed,
            deduction_days
        ])

    return data
