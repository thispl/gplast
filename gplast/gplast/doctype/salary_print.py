from __future__ import unicode_literals
from csv import writer
from frappe import db
from inspect import getfile
from unicodedata import name
import frappe
from frappe.utils import cstr, add_days, date_diff, getdate
from frappe import _
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from frappe.utils.file_manager import get_file, upload
from frappe.model.document import Document
from datetime import datetime,timedelta,date,time
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr



# @frappe.whitelist()
# def get_attendance(employee, start_date, end_date):
# 	from frappe.utils import getdate, date_diff, add_days

# 	dates = get_dates(start_date, end_date)
# 	days_row = "<tr><td style='font-weight:bold; text-align:left;width:10%;'>Days</td>"
# 	attendance_row = "<tr><td style='font-weight:bold; text-align:left;width:10%;'>Attendance</td>"

# 	for date in dates:
# 		day = getdate(date).strftime("%d")
# 		days_row += f"<td style='font-weight:bold; text-align:left;'>{day}</td>"
# 		status = ""

# 		# Check if attendance is already marked
# 		if frappe.db.exists("Attendance", {'employee': employee, 'attendance_date': date, 'docstatus': ['!=', 2]}):
# 			doc = frappe.get_value("Attendance", {'employee': employee, 'attendance_date': date}, ['status', 'leave_type'], as_dict=True)

# 			if doc.status == "Present":
# 				status = "P"
# 			elif doc.status == "Absent":
# 				status = "A"
# 			elif doc.status == "Half Day":
# 				status = "HD"
# 			elif doc.status == "On Leave":
# 				leave_type = doc.leave_type
# 				if leave_type:
# 					is_lwp = frappe.db.get_value("Leave Type", leave_type, "is_lwp")
# 					status = "L" if is_lwp else "PL"
# 				else:
# 					status = "L"

# 		else:
# 			# Check shift assignment covering this date
# 			shift_type = frappe.db.get_value(
# 				"Shift Assignment",
# 				{
# 					"employee": employee,
# 					"docstatus": 1,
# 					"start_date": ["<=", date],
# 					"end_date": [">=", date]
# 				},
# 				"shift_type"
# 			)

# 			if shift_type:
# 				if shift_type == "WW":
# 					status = "W"
# 				else:
# 					# Check if the date is a holiday in that shift type's holiday list
# 					holiday_list = frappe.db.get_value("Shift Type", shift_type, "holiday_list")
# 					if holiday_list and frappe.db.exists("Holiday", {"parent": holiday_list, "holiday_date": date}):
# 						status = "PH"
# 					else:
# 						status = "A"
# 			else:
# 				status = "A"

# 		color = {
# 			"P": "green",
# 			"WW": "purple",
# 			"W": "purple",
# 			"A": "black",
# 			"HD": "black",
# 			"L": "black",
# 			"PL": "black",
# 			"PH": "black"
# 		}.get(status, "black")

# 		attendance_row += f"<td style='font-weight:bold; text-align:center; vertical-align:middle; height:30px; color:{color}'>{status}</td>"



# 	days_row += "</tr>"
# 	attendance_row += "</tr>"

# 	table_html = f"""
# 	<table border=1 style='width:100%; table-layout:fixed; font-size:9px; text-align:center; border-collapse:collapse;'>
# 		{days_row}
# 		{attendance_row}
# 	</table>
# 	"""

# 	return table_html

@frappe.whitelist()
def get_attendance(employee, start_date, end_date):
	from frappe.utils import getdate

	dates = get_dates(start_date, end_date)
	days_row = "<tr><td style='font-weight:bold; text-align:left;width:10%;font-size:10px;border-left:none;'>Days</td>"
	attendance_row = "<tr><td style='font-weight:bold; text-align:left;width:10%;font-size:10px;border-left:none;'>Attendance</td>"

	for i, date in enumerate(dates):
		day = getdate(date).strftime("%d")
		no_right_border = "border-right:none;" if i == len(dates) - 1 else ""
		# days_row += f"<td style='font-weight:bold; text-align:left;'>{day}</td>"
		days_row += f"<td style='font-weight:bold; text-align:left; {no_right_border}'>{day}</td>"
		status = ""

		# Check shift assignment covering this date
		shift_type = frappe.db.get_value(
			"Shift Assignment",
			{
				"employee": employee,
				"docstatus": ["!=",2],
				"start_date": ["<=", date],
				"end_date": [">=", date]
			},
			"shift_type"
		)

		# Check if holiday first
		holiday_status = ""
		holiday_list = frappe.db.get_value("Employee", employee, "holiday_list")
		if holiday_list:
			holidays = frappe.get_all(
				"Holiday",
				filters={"parent": holiday_list, "holiday_date": date},
				fields=["national_holiday", "festival_holiday"]
			)
			if holidays:
				holiday = holidays[0]
				if holiday.get("national_holiday") == 1:
					holiday_status = "NH"
				elif holiday.get("festival_holiday") == 1:
					holiday_status = "FH"
				else:
					holiday.get("weekly_off") == 1
					holiday_status = "WW"

		if holiday_status:
			status = holiday_status
		elif shift_type == "WW":
			status = "WW"
		else:
			if frappe.db.exists("Attendance", {'employee': employee, 'attendance_date': date, 'docstatus': ['!=', 2]}):
				doc = frappe.get_value("Attendance", {'employee': employee, 'attendance_date': date}, ['status', 'leave_type'], as_dict=True)

				if doc.status == "Present":
					status = "P"
				elif doc.status == "Absent":
					status = "A"
				elif doc.status == "Half Day":
					status = "HD"
				elif doc.status == "On Leave":
					leave_type = doc.leave_type
					if leave_type:
						if leave_type == "Casual Leave":
							status = "CL"
						elif leave_type == "Earned Leave":
							status ="EL"
						else:
							status = "L"
			else:
				status = " "

		color = {
			"P": "green",
			"WW": "purple",
			"W": "purple",
			"A": "black",
			"HD": "black",
			"L": "black",
			"PL": "black",
			"PH": "black",
			"NH": "purple",
			"FH": "purple"
		}.get(status, "black")

		# attendance_row += f"<td style='font-weight:bold; text-align:center; vertical-align:middle; height:30px; color:{color}'>{status}</td>"
		attendance_row += f"<td style='font-weight:bold; text-align:center; vertical-align:middle; height:30px; color:{color}; {no_right_border}'>{status}</td>"

	days_row += "</tr>"
	attendance_row += "</tr>"

	table_html = f"""
	<table border=1 style='width:100%; table-layout:fixed; font-size:9px; text-align:center; border-collapse:collapse;border-top:none;'>
		{days_row}
		{attendance_row}
	</table>
	"""

	return table_html


def get_dates(from_date, to_date):
	from frappe.utils import date_diff, add_days
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	return [add_days(from_date, i) for i in range(no_of_days)]




@frappe.whitelist()
def get_approved_leave_days(start_date, employee, leave_type):
	start_date_obj = frappe.utils.getdate(start_date)
	year = start_date_obj.year
	current_month_start = get_first_day(start_date_obj)
	current_month_end = get_last_day(start_date_obj)

	leave_days = frappe.db.sql("""
		SELECT SUM(total_leave_days) AS total_days
		FROM `tabLeave Application`
		WHERE docstatus = 1
		  AND workflow_state = 'Approved'
		  AND employee = %s
		  AND leave_type = %s
		  AND from_date <= %s
		  AND to_date >= %s
		  AND YEAR(from_date) <= %s
		  AND YEAR(to_date) >= %s
	""", (employee, leave_type, current_month_end, current_month_start, year, year), as_dict=True)

	return leave_days[0]['total_days'] if leave_days and leave_days[0]['total_days'] is not None else 0


# @frappe.whitelist()
# def get_total_leaves_allocated(start_date, employee, leave_type):
# 	year = getdate(start_date).year
# 	result = frappe.db.sql("""
# 		SELECT SUM(total_leaves_allocated) AS total_allocated
# 		FROM `tabLeave Allocation`
# 		WHERE docstatus = 1
# 		AND employee = %s
# 		AND leave_type = %s
# 		AND YEAR(from_date) = %s
# 		AND YEAR(to_date) = %s
# 	""", (employee, leave_type, year, year), as_dict=1)

# 	return result[0].total_allocated if result and result[0].total_allocated else 0

@frappe.whitelist()
def get_total_leaves_allocated(start_date, employee, leave_type):
	from frappe.utils import getdate
	import datetime

	start_date = getdate(start_date)
	year = start_date.year
	year_start = datetime.date(year, 1, 1)
	year_end = datetime.date(year, 12, 31)

	# Get all leave allocations overlapping the year
	allocations = frappe.db.sql("""
		SELECT name, from_date, to_date, total_leaves_allocated
		FROM `tabLeave Allocation`
		WHERE docstatus = 1
		AND employee = %s
		AND leave_type = %s
		AND (
			from_date <= %s AND to_date >= %s
		)
	""", (employee, leave_type, year_end, year_start), as_dict=1)

	total_allocation = 0

	for alloc in allocations:
		alloc_from = getdate(alloc.from_date)
		alloc_to = getdate(alloc.to_date)
		allocated = alloc.total_leaves_allocated

		# Case 1: Allocation spans multiple years (like Jul 2024 to Jun 2025)
		if alloc_from.year != alloc_to.year:
			# Check leaves taken in previous year (before current year)
			leave_taken = frappe.db.sql("""
				SELECT SUM(total_leave_days)
				FROM `tabLeave Application`
				WHERE employee = %s
				AND leave_type = %s
				AND from_date BETWEEN %s AND %s
				AND docstatus = 1
			""", (
				employee, leave_type,
				alloc_from,
				datetime.date(year, 1, 1) - datetime.timedelta(days=1)
			))[0][0] or 0

			remaining = allocated - leave_taken
			total_allocation += remaining
		else:
			# Case 2: Allocation is within same year
			total_allocation += allocated

	return total_allocation


# @frappe.whitelist()
# def get_total_leaves_allocated(start_date, employee, leave_type):
# 	from frappe.utils import getdate

# 	year = getdate(start_date).year

# 	result = frappe.db.sql("""
# 		SELECT SUM(total_leaves_allocated) AS total_allocated
# 		FROM `tabLeave Allocation`
# 		WHERE docstatus = 1
# 		AND employee = %s
# 		AND leave_type = %s
# 		AND (
# 			YEAR(from_date) = %s
# 			OR YEAR(to_date) = %s
# 		)
# 	""", (employee, leave_type, year, year), as_dict=1)

# 	return result[0].total_allocated if result and result[0].total_allocated else 0


@frappe.whitelist()
def get_balance_leaves(start_date, employee, leave_type):
	a = get_total_leaves_allocated(start_date, employee, leave_type) or 0
	opening = get_approved_leave_days_except_current_month(start_date, employee, leave_type) or 0
	availed = get_approved_leave_days(start_date, employee, leave_type) or 0
	
	# frappe.msgprint(f"Allocated: {a}")
	# frappe.msgprint(f"Approved except current month: {opening}")
	# frappe.msgprint(f"Approved current month: {availed}")

	balance = a - ( opening + availed)
	if balance < 0:
		balance = 0
	# frappe.msgprint(f"Balance calculated: {balance}")
	return balance






from frappe.utils import get_first_day, get_last_day

@frappe.whitelist()
def get_approved_leave_days_except_current_month(start_date, employee, leave_type):
	start_date_obj = frappe.utils.getdate(start_date)
	year = start_date_obj.year
	month = start_date_obj.month

	current_month_start = get_first_day(start_date_obj)
	current_month_end = get_last_day(start_date_obj)

	leave_days = frappe.db.sql("""
		SELECT SUM(total_leave_days) AS total_days
		FROM `tabLeave Application`
		WHERE docstatus = 1
		  AND workflow_state = 'Approved'
		  AND employee = %s
		  AND leave_type = %s
		  AND (
			  to_date < %s
			  OR from_date > %s
		  )
		  AND YEAR(from_date) = %s
	""", (employee, leave_type, current_month_start, current_month_end, year), as_dict=True)

	return leave_days[0]['total_days'] if leave_days and leave_days[0]['total_days'] is not None else 0



@frappe.whitelist()
def get_weekly_off_count_shift(employee, start_date, end_date):
	import datetime
	from frappe.utils import getdate

	start_date = getdate(start_date)
	end_date = getdate(end_date)

	year = start_date.year
	year_start = datetime.date(year, 1, 1)
	year_end = datetime.date(year, 12, 31)

	start_month = start_date.month
	end_month = end_date.month

	total_days = 0

	shift_assignments = frappe.get_all("Shift Assignment",
		filters={
			"employee": employee,
			"shift_type": "WW",
			"docstatus": 1,
			"start_date": ["<=", year_end],
			"end_date": [">=", year_start]
		},
		fields=["start_date", "end_date"]
	)

	# Loop through shifts and count days excluding those in start and end month
	for shift in shift_assignments:
		shift_start = getdate(shift.start_date)
		shift_end = getdate(shift.end_date)

		# Get the overlapping date range within the year
		valid_start = max(shift_start, year_start)
		valid_end = min(shift_end, year_end)

		# Loop day by day and exclude if the day falls in start or end month
		current = valid_start
		while current <= valid_end:
			total_days += 1
			current += datetime.timedelta(days=1)

	return total_days


# @frappe.whitelist()
# def get_ww_shift_days_excluding_start_end_months(employee, exclude_month, year):
# 	import frappe
# 	from frappe.utils import getdate, add_days

# 	# Ensure correct types
# 	exclude_month = int(exclude_month)
# 	year = int(year)

# 	start_date = getdate(f"{year}-01-01")
# 	end_date = getdate(f"{year}-12-31")
# 	total_days = 0

# 	frappe.msgprint(f"Employee: {employee}, Exclude Month: {exclude_month}, Year: {year}")

# 	# Get all WW shift assignments for the employee within the year
# 	shift_assignments = frappe.get_all(
# 		"Shift Assignment",
# 		filters={
# 			"employee": employee,
# 			"shift_type": "WW",
# 			"docstatus": 1,
# 			"start_date": ["<=", end_date],
# 			"end_date": [">=", start_date]
# 		},
# 		fields=["start_date", "end_date"]
# 	)

# 	frappe.msgprint(f"Total WW shift assignments found: {len(shift_assignments)}")

# 	for shift in shift_assignments:
# 		shift_start = getdate(shift.start_date)
# 		shift_end = getdate(shift.end_date)

# 		frappe.msgprint(f"Shift from {shift_start} to {shift_end}")

# 		valid_start = max(shift_start, start_date)
# 		valid_end = min(shift_end, end_date)

# 		current_day = valid_start
# 		while current_day <= valid_end:
# 			if not (current_day.month == exclude_month and current_day.year == year):
# 				total_days += 1
# 			current_day = add_days(current_day, 1)

# 	frappe.msgprint(f"Total WW days (excluding month {exclude_month}): {total_days}")
# 	return total_days

@frappe.whitelist()
def get_ww_shift_days_excluding_start_end_months(employee, exclude_month_str):
	import frappe
	from frappe.utils import getdate, add_days
	exclude_date = getdate(exclude_month_str)
	exclude_month = exclude_date.month
	exclude_year = exclude_date.year

	start_date = getdate(f"{exclude_year}-01-01")
	end_date = getdate(f"{exclude_year}-12-31")
	total_days = 0


	shift_assignments = frappe.get_all("Shift Assignment",
		filters={
			"employee": employee,
			"shift_type": "WW",
			"docstatus": 1,
			"start_date": ["<=", end_date],
			"end_date": [">=", start_date]
		},
		fields=["start_date", "end_date"]
	)


	for shift in shift_assignments:
		shift_start = getdate(shift.start_date)
		shift_end = getdate(shift.end_date)
		current_day = max(shift_start, start_date)
		last_day = min(shift_end, end_date)

		while current_day <= last_day:
			if not (current_day.month == exclude_month and current_day.year == exclude_year):
				total_days += 1
			current_day = add_days(current_day, 1)

	return total_days



# @frappe.whitelist()
# def get_ww_shift_days_excluding_start_end_months(employee, start_date, end_date):
# 	import datetime
# 	from frappe.utils import getdate

# 	start_date = getdate(start_date)
# 	end_date = getdate(end_date)
# 	start_month = start_date.month
# 	end_month = end_date.month

# 	total_days = 0

# 	# Fetch WW shift assignments that overlap with the full year
# 	shift_assignments = frappe.get_all("Shift Assignment",
# 		filters={
# 			"employee": employee,
# 			"shift_type": "WW",
# 			"docstatus": 1,
# 			"start_date": ["<=", end_date],
# 			"end_date": [">=", start_date]
# 		},
# 		fields=["start_date", "end_date"]
# 	)

# 	# Filter out those whose start or end date fall in the start/end month
# 	for shift in shift_assignments:
# 		shift_start = getdate(shift.start_date)
# 		shift_end = getdate(shift.end_date)

# 		# Skip if the assignment starts or ends in the same month as the range start or end
# 		if shift_start.month == start_month and shift_end.month == end_month:
# 			continue

# 		# Limit the shift range within the full year
# 		valid_start = max(shift_start, start_date)
# 		valid_end = min(shift_end, end_date)
# 		total_days += (valid_end - valid_start).days + 1

# 	return total_days

@frappe.whitelist()
def get_ww_shift_count_for_month(employee, start_date, end_date):
	start_date = getdate(start_date)
	end_date = getdate(end_date)
	total_days = 0

	shift_assignments = frappe.get_all("Shift Assignment",
		filters={
			"employee": employee,
			"shift_type": "WW",
			"docstatus": 1,
			"end_date": [">=", start_date],
			"start_date": ["<=", end_date]
		},
		fields=["start_date", "end_date"]
	)

	for shift in shift_assignments:
		shift_start = max(getdate(shift.start_date), start_date)
		shift_end = min(getdate(shift.end_date), end_date)

		day_count = (shift_end - shift_start).days + 1
		total_days += day_count

	return total_days



@frappe.whitelist()
def get_balance_weekoff(employee,start_date,end_date):
	a=get_weekly_off_count_shift(employee,start_date,end_date)
	opening=get_ww_shift_days_excluding_start_end_months(employee,start_date)
	availed=get_ww_shift_count_for_month(employee,start_date,end_date)
	opening=opening or 0
	availed=availed or 0
	balance= a - (opening +availed)
	if balance<0:
		balance=0
	return balance

@frappe.whitelist()
def get_weekly_off_count_for_this_nh(employee,start_date,end_date):
	holiday_list_name = frappe.db.get_value("Employee", employee, "holiday_list")
	if not holiday_list_name:
		return 0
	holidays = frappe.get_all("Holiday", filters={"parent": holiday_list_name, "national_holiday": 1,"holiday_date":["between",[start_date,end_date]]})
	return len(holidays)
# @frappe.whitelist()
def get_weekly_off_count_for_this_fh(employee,start_date,end_date):
	holiday_list_name = frappe.db.get_value("Employee", employee, "holiday_list")
	if not holiday_list_name:
		return 0
	holidays = frappe.get_all("Holiday", filters={"parent": holiday_list_name, "festival_holiday": 1,"holiday_date":["between",[start_date,end_date]]})
	return len(holidays)

@frappe.whitelist()
def get_weekly_count_for_this_nh_fh(employee,start_date,end_date):
	opening=get_weekly_off_count_for_this_nh(employee,start_date,end_date)
	availed=get_weekly_off_count_for_this_fh(employee,start_date,end_date)
	a = opening + availed
	if a < 0:
		return 0
	return a

@frappe.whitelist()
def get_weekly_off_count_for_other_nh(employee, start_date, end_date):
	import datetime
	from frappe.utils import getdate
	start_date = getdate(start_date)
	end_date = getdate(end_date)
	year = start_date.year
	year_start = datetime.date(year, 1, 1)
	year_end = datetime.date(year, 12, 31)
	holiday_list_name = frappe.db.get_value("Employee", employee, "holiday_list")
	if not holiday_list_name:
		return 0
	all_nh = frappe.get_all(
		"Holiday",
		filters={
			"parent": holiday_list_name,
			"national_holiday": 1,
			"holiday_date": ["between", [year_start, year_end]]
		},
		fields=['holiday_date']
	)
	filtered_nh = [
		h for h in all_nh if not (start_date <= h.holiday_date <= end_date)
	]
	return len(filtered_nh)


@frappe.whitelist()
def get_weekly_off_count_for_other_fh(employee,start_date,end_date):
	import datetime
	from frappe.utils import getdate
	start_date = getdate(start_date)
	end_date = getdate(end_date)
	year = start_date.year
	year_start = datetime.date(year, 1, 1)
	year_end = datetime.date(year, 12, 31)
	holiday_list_name = frappe.db.get_value("Employee", employee, "holiday_list")
	if not holiday_list_name:
		return 0
	all_nh = frappe.get_all(
		"Holiday",
		filters={
			"parent": holiday_list_name,
			"festival_holiday": 1,
			"holiday_date": ["between", [year_start, year_end]]
		},
		fields=['holiday_date']
	)
	filtered_fh = [
		h for h in all_nh if not (start_date <= h.holiday_date <= end_date)
	]
	return len(filtered_fh)
	
@frappe.whitelist()
def get_weekly_count_for_other_nh_fh(employee,start_date,end_date):
	opening=get_weekly_off_count_for_other_nh(employee,start_date,end_date)
	availed=get_weekly_off_count_for_other_fh(employee,start_date,end_date)
	a = opening + availed
	if a < 0:
		return 0
	return a

@frappe.whitelist()
def get_weekly_off_count_nh(employee,start_date,end_date):
	import datetime
	start_date = getdate(start_date) 
	year = start_date.year
	year_start = datetime.date(year, 1, 1)
	year_end = datetime.date(year, 12, 31)
	holiday_list_name = frappe.db.get_value("Employee", employee, "holiday_list")
	if not holiday_list_name:
		return 0
	holidays = frappe.get_all("Holiday", filters={"parent": holiday_list_name, "national_holiday": 1,"holiday_date":["between",[year_start,year_end]]})
	return len(holidays) 

@frappe.whitelist()
def get_weekly_off_count_fh(employee,start_date,end_date):
	import datetime
	start_date = getdate(start_date) 
	year = start_date.year
	year_start = datetime.date(year, 1, 1)
	year_end = datetime.date(year, 12, 31)
	holiday_list_name = frappe.db.get_value("Employee", employee, "holiday_list")
	if not holiday_list_name:
		return 0
	holidays = frappe.get_all("Holiday", filters={"parent": holiday_list_name, "festival_holiday": 1,"holiday_date":["between",[year_start,year_end]]})
	return len(holidays) 

@frappe.whitelist()
def get_weekly_count_nh_fh(employee,start_date,end_date):
	opening=get_weekly_off_count_nh(employee,start_date,end_date)
	availed=get_weekly_off_count_fh(employee,start_date,end_date)
	a = opening + availed
	if a < 0:
		return 0
	return a

@frappe.whitelist()
def get_balance_nh_fh(employee,start_date,end_date):
	a=get_weekly_count_nh_fh(employee,start_date,end_date)
	opening=get_weekly_count_for_other_nh_fh(employee,start_date,end_date)
	availed=get_weekly_count_for_this_nh_fh(employee,start_date,end_date)
	opening=opening or 0
	availed=availed or 0
	balance= a - (opening +availed)
	if balance<0:
		balance=0
	return balance

import frappe

@frappe.whitelist()
def inr_format(value):
	try:
		value = float(value)
		return "{:,.2f}".format(value).replace(",", "X").replace(".", ",").replace("X", ",").replace(",", ".", 1)
	except:
		return value

@frappe.whitelist()
def get_worked_days(worked,employee,start_date,end_date):
	nh=get_weekly_count_for_this_nh_fh(employee,start_date,end_date)
	ww=get_ww_shift_count_for_month(employee,start_date,end_date)
	workeddays = worked - (nh+ww)
	if workeddays<0:
		workeddays=0
	return workeddays

@frappe.whitelist()
def get_interview_date(designation):
	return frappe.db.get_value("Interview", {"designation": designation, "docstatus": ["!=", 2]}, "scheduled_on")
