from email import message
import frappe
from frappe import _
import datetime, math
from datetime import date, timedelta, datetime,time
import datetime as dt
from frappe.utils import time_diff_in_hours
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from hrms.hr.doctype.shift_request.shift_request import ShiftRequest
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,today, format_date)
# import pandas as pd
import math
from frappe.utils import add_months, cint, flt, getdate, time_diff_in_hours
import datetime as dt
from datetime import datetime, timedelta
from frappe.utils import get_datetime, add_to_date
from hrms.hr.doctype.leave_application.leave_application import LeaveApplication


class CustomShiftRequest(ShiftRequest):
	def after_insert(self):
		if not self.assigned_shift:
			frappe.throw("Assigned shift is not set.")
		if self.assigned_shift==self.shift_type:
			frappe.throw("Assigned shift and requested shift cannot be same.")
	def before_submit(self):
		assignment = frappe.db.sql("""
			SELECT name FROM `tabShift Assignment`
			WHERE employee = %s AND start_date = %s
		""", (self.employee, self.from_date), as_dict=True)
		if assignment:
			for record in assignment:
				frappe.db.sql("""UPDATE `tabShift Assignment` SET docstatus = 2 WHERE name = %s""", (record['name'],))
				# frappe.db.sql("""DELETE FROM `tabShift Assignment` WHERE name = %s""", (record['name'],))
	def on_cancel(self):
		shift_assignment_list = frappe.get_list(
			"Shift Assignment", {"employee": self.employee, "shift_request": self.name}
		)
		if shift_assignment_list:
			for shift in shift_assignment_list:
				shift_assignment_doc = frappe.get_doc("Shift Assignment", shift["name"])
				shift_assignment_doc.cancel()
		shift=frappe.new_doc("Shift Assignment")
		shift.employee=self.employee
		shift.shift_type=self.assigned_shift
		shift.start_date=self.from_date
		shift.end_date=self.from_date
		shift.flags.ignore_permissions = 1
		shift.insert()
		shift.submit()
	def validate_approver(self):
		pass


@frappe.whitelist()
class CustomSalarySlip(SalarySlip):
	
	def get_date_details(self):
		start_date = getdate(self.start_date)
		end_date = getdate(self.end_date)
		holiday_list = frappe.db.get_value("Employee", self.employee, "holiday_list")
		total_days = (end_date - start_date).days + 1
		working_days = 0
		working_days1 = 0 
		crt_work_days = 0
		for i in range(total_days):
			current_date = add_days(start_date, i)
			is_holiday = frappe.db.exists("Holiday",{"holiday_date": current_date, "parent": holiday_list})
			shift_type = frappe.db.get_value("Shift Assignment",{"employee": self.employee, "start_date": ["<=", current_date],"end_date": [">=", current_date]},"shift_type")
			# is_holiday_include_nh = frappe.db.get_value("Holiday",{"holiday_date": current_date, "parent": holiday_list},["name", "national_holiday"],as_dict=True)
			holiday = frappe.db.get_value("Holiday",{"holiday_date": current_date,"parent": holiday_list},["name", "national_holiday"],as_dict=True)
			if not is_holiday and shift_type != "WW":
				working_days += 1
			if not is_holiday:		
				att_status = frappe.db.get_value("Attendance",{"employee":self.employee, "attendance_date": current_date,"docstatus": 1}, "status")
				leave_type = frappe.db.get_value("Attendance",{"employee":self.employee, "attendance_date": current_date,"docstatus": 1}, "leave_type")
				if att_status =="Present":
					working_days1 += 1
				elif att_status == "Half Day":
					working_days1 +=0.5 
				elif att_status == "On Leave":
					if leave_type == "Compensatory Off":
						working_days1 +=1
			if self.employment_type == "Contract" and holiday:
				if holiday.national_holiday:
					working_days += 1
					crt_work_days += 1


		self.total_present_days_in_a_month = working_days
		self.present_days_in_a_month_except_nh_fh_ww = crt_work_days
		self.total_present_days_of_employee = working_days1
		
		if start_date.month == 8 or start_date.month == 1:
			self.pt = 0
			pt_parent = frappe.db.get_value("Employee", {"name": self.employee}, "zone_id")
			allowances = frappe.db.get_value(
				"Employee",
				{"name": self.employee},
				["basic","cca","house_rent_allowance","special_allowance","shift_allowance","other_allowance",],as_dict=True)
			fixed = sum(allowances.values()) if allowances else 0
			if start_date.month == 8:
				fiscal_year = start_date.year
				apr_01 = f"{fiscal_year}-04-01"
				jul_31 = f"{fiscal_year}-07-31"

				slips = frappe.get_all(
					"Salary Slip",
					filters={
						"employee": self.employee,
						"start_date": [">=", apr_01],
						"end_date": ["<=", jul_31],
						"docstatus": ["!=", 2]
					},
					fields=["gross_pay"]
				)
				total_apr_jul = sum(slip["gross_pay"] for slip in slips if slip.get("gross_pay"))
				gross_pay = self.gross_pay or 0
				total_value = total_apr_jul + float(gross_pay) + fixed
			elif start_date.month == 1:	
				fiscal_year = start_date.year
				oct_01 = f"{fiscal_year - 1}-10-01"
				dec_31 = f"{fiscal_year - 1}-12-31"

				slips = frappe.get_all(
					"Salary Slip",
					filters={
						"employee": self.employee,
						"start_date": [">=", oct_01],
						"end_date": ["<=", dec_31],
						"docstatus": ["!=", 2]
					},
					fields=["gross_pay"]
				)
				total_oct_dec = sum(slip["gross_pay"] for slip in slips if slip.get("gross_pay"))
				gross_pay = self.gross_pay or 0
				total_value = total_oct_dec + float(self.gross_pay) + (fixed * 2)
			else:
				return 0	

			pt_details = frappe.get_all(
				"PT Transaction Details",filters={"parent": pt_parent},fields=["from_salary", "to_salary", "pt_amount"])
			for row in pt_details:
				if row["from_salary"] <= total_value <= row["to_salary"]:
					self.pt = row["pt_amount"]

		ot_records = frappe.get_all('Over Time',filters={'employee': self.employee,'ot_date': ['between', [self.start_date, self.end_date]],'docstatus': 1},fields=['overtime_hours'])
		self.ot_ = sum([r.overtime_hours or 0 for r in ot_records])
		self.tiffen_allowance = len([r for r in ot_records if (r.overtime_hours or 0) >= 8])
		
		base_filters = {
			'employee': self.employee,
			'status': ['in', ['Present', 'Half Day']],
			'attendance_date': ['between', [self.start_date, self.end_date]],
			'docstatus': 1
		}
		
		self.b_shift = frappe.db.count('Attendance', {**base_filters, 'shift': 'B','weekly_off': 0})
		self.c_shift = frappe.db.count('Attendance', {**base_filters, 'shift': 'C','weekly_off': 0})
		self.late_count = frappe.db.count('Attendance', {**base_filters, 'late_entry': 1 ,"late_entry_time":['<=',"00:15:59"]})
		self.late_count_deduction = 0
		if self.late_count > 0:
			if 0 <= self.late_count <= 3:
				self.late_count_deduction = 0
			elif 4 <= self.late_count <= 5:
				self.late_count_deduction = 0.5
			elif 6 <= self.late_count <= 7:
				self.late_count_deduction = 1
			elif 8 <= self.late_count <= 9:
				self.late_count_deduction = 1.5
			elif 10 <= self.late_count <= 11:
				self.late_count_deduction = 2
			elif 12 <= self.late_count <= 13:
				self.late_count_deduction = 2.5
		
	def before_save(self):
		for d in self.deductions:
			round_up = frappe.db.get_value("Salary Component", d.salary_component, "round_up")
			if round_up:
				d.amount = math.ceil(d.amount)
		if self.total_deduction:
			self.total_deduction = math.ceil(self.total_deduction)		

def time_to_minutes(time_val):
    if not time_val:
        return 0

    if isinstance(time_val, timedelta):
        return time_val.total_seconds() / 60

    if isinstance(time_val, str):
        h, m, s = map(int, time_val.split(":"))
        return h * 60 + m + s / 60

    return 0


class CustomLeaveApplication(LeaveApplication):

    def validate(self):
        super().validate()
        self.validate_half_day_with_attendance()

    def validate_half_day_with_attendance(self):

        if not self.half_day or not self.session:
            return

        attendance = frappe.db.get_value(
            "Attendance",
            {
                "employee": self.employee,
                "attendance_date": self.from_date,
                "docstatus": ["!=", 2]
            },
            [
                "late_entry",
                "early_exit",
                "late_entry_time",
                "early_exit_time"
            ],
            as_dict=True
        )

        if not attendance:
            return
        late_minutes = time_to_minutes(attendance.late_entry_time)
        early_minutes = time_to_minutes(attendance.early_exit_time)

        TWO_HOURS = 120
        if attendance.late_entry == 1 and attendance.early_exit == 0:
            if late_minutes > TWO_HOURS  and self.session == "Second Half":
                frappe.throw(
                    "Second Half leave cannot be applied because late entry exceeds 2 hours."
                )
        if attendance.early_exit == 1 and attendance.late_entry == 0:
            if early_minutes > TWO_HOURS and self.session == "First Half":
                frappe.throw(
                    "First Half leave cannot be applied because early exit exceeds 2 hours."
                )
        if attendance.late_entry == 1 and attendance.early_exit == 1:
            if (
                late_minutes < TWO_HOURS
                and early_minutes > TWO_HOURS
                and self.session == "First Half"
            ):
                frappe.throw(
                    "The Attendance has been already marked as First Half."
                )
            if (
                late_minutes > TWO_HOURS
                and early_minutes < TWO_HOURS
                and self.session == "Second Half"
            ):
                frappe.throw(
                    "The Attendance has been already marked as Second Half."
                )
