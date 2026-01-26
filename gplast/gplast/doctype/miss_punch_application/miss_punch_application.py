# Copyright (c) 2024, TEAMPROO and contributors
# For license information, please see license.txt
from email import message
import frappe
import datetime
import math
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,format_date)
from frappe.utils import cstr, cint, getdate,get_first_day, get_last_day, today, time_diff_in_hours   
from datetime import date, timedelta,time,datetime
from frappe import _
from frappe.utils.background_jobs import enqueue
import frappe
from frappe.utils import time_diff_in_hours
from datetime import datetime, timedelta
from frappe.model.document import Document
from gplast.mark_attendance import mark_att_with_employee,mark_wh_emp
from frappe.utils import formatdate

from frappe.utils import today, add_days
import datetime

class MissPunchApplication(Document):
    def validate(self):
        doctype = self.doctype
        old_state = frappe.db.get_value(doctype, self.name, "workflow_state")

        if old_state and old_state != self.workflow_state:
            self.previous_approval_date = today()
        
        
    def after_insert(self):
        user_roles = frappe.get_roles(frappe.session.user)
        hr = "Miss Punch Role" in user_roles
        # admin = "Administrator" in user_roles
        if (not hr):
            allowed_days = 0
            user_roles = frappe.get_roles(frappe.session.user)
            hod = "HOD" in user_roles
            if hod:
                allowed_days = 2
            else:
                allowed_days = 1

            current_date = today()
            if isinstance(current_date, str):
                current_date = datetime.strptime(current_date, "%Y-%m-%d").date()

            def is_working_day(check_date):
                return not check_holiday(check_date, self.employee)

            days_count = 0
            earliest_allowed = current_date
            while days_count < allowed_days:
                earliest_allowed = add_days(earliest_allowed, -1)
                if is_working_day(earliest_allowed):
                    days_count += 1

            if not self.attendance_date:
                return

            if isinstance(self.attendance_date, str):
                miss_date = datetime.strptime(self.attendance_date, "%Y-%m-%d").date()
            else:
                miss_date = self.attendance_date

            if miss_date < earliest_allowed:
                frappe.throw(
                    _("Miss Punch applications are allowed only for up to the previous {0} working days.")
                    .format(allowed_days)
                )


    # def validate(self):
    #     current_date=today()
    #     diff=date_diff(current_date,self.attendance_date)
    #     if diff>1:
    #         frappe.throw("Miss punch request should be raised on the next the itself. Old dates are not allowed.")
    def before_submit(self):
        self.approved_on = frappe.utils.today()
    def on_submit(self):
        if self.workflow_state == "Approved":
            att = frappe.db.exists('Attendance',{'attendance_date':self.attendance_date,'employee':self.employee,'docstatus':('!=',2)})
            if att:
                attendance = frappe.get_doc("Attendance",{'attendance_date':self.attendance_date,'employee':self.employee,'docstatus':('!=',2)})
                frappe.db.set_value("Attendance",attendance.name,"in_time",self.in_time)
                frappe.db.set_value("Attendance",attendance.name,"out_time",self.out_time)
                frappe.db.set_value("Attendance",attendance.name,"shift",self.shift)
                # frappe.db.set_value("Attendance",attendance.name,"status","Present")
                frappe.db.set_value("Attendance",attendance.name,"miss_punch_application",self.name)

                # in_t = str(self.in_time)
                # out_t = str(self.out_time)
                # # Convert datetime strings to Python datetime objects
                # datetime1 = get_datetime(in_t)
                # datetime2 = get_datetime(out_t)

                # # Calculate time difference
                # time_difference = datetime2 - datetime1
                # frappe.errprint(time_difference)
                # hours, remainder = divmod(time_difference.total_seconds(), 3600)
                # minutes, seconds = divmod(remainder, 60)

                # # Format the time difference as "HH:MM:SS"
                # formatted_time_difference = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

                # time_str = formatted_time_difference  # Replace with your actual time string

                # # Split the time string into hours, minutes, and seconds
                # hours, minutes, seconds = map(int, time_str.split(':'))
                # time_in_float = hours + minutes/60 + seconds/3600
                # frappe.db.set_value("Attendance",attendance.name,"custom_total_working_hours",time_difference)
                # frappe.db.set_value("Attendance",attendance.name,"working_hours",time_in_float)
                start_date = self.attendance_date  # This is your attendance_date
                to_date = add_days(start_date, 1)  # Adding 1 day to attendance_date

                # Call the function with corrected arguments
                wh, new_status = mark_wh(start_date, to_date, self.employee)
                ot_calculation(self.name)
                frappe.db.set_value("Attendance", attendance.name, "total_working_hours", wh)
                frappe.db.set_value("Attendance", attendance.name, "status", new_status)
                frappe.db.commit()
            
    
    from frappe.utils.data import date_diff, now_datetime, nowdate, today, add_days
    def on_cancel(self):
        # Fetch the attendance document linked with the custom on duty application
        attendance_list = frappe.get_value("Attendance", {
            'employee': self.employee,
            'miss_punch_application': self.name,
            "attendance_date": self.attendance_date
        }, ['name'])

        # If attendance exists, cancel it
        if attendance_list:
            attendance_obj = frappe.get_doc("Attendance", attendance_list)
            if attendance_obj.docstatus ==1:
                
                attendance_obj.cancel()
                mark_att_with_employee(self.attendance_date,self.attendance_date,self.employee)
                mark_wh_emp(self.attendance_date,self.attendance_date,self.employee)
                to_date = add_days(self.attendance_date,1)
                # update_on_duty(self.attendance_date, to_date, self.employee)
            if attendance_obj.docstatus ==0:
                frappe.db.set_value("Attendance",attendance_obj.name,'miss_punch_application','')
                frappe.db.set_value("Attendance",attendance_obj.name,'in_time',None)
                frappe.db.set_value("Attendance",attendance_obj.name,'out_time',None)
                frappe.db.set_value("Attendance",attendance_obj.name,'ot_hours','00:00:00')
                frappe.db.set_value("Attendance",attendance_obj.name,'total_working_hours',0)
                frappe.db.set_value("Attendance",attendance_obj.name,'overtime_hours',0)
                frappe.db.set_value("Attendance",attendance_obj.name,'late_entry_time','00:00:00')
                frappe.db.set_value("Attendance",attendance_obj.name,'status','Absent')
                mark_att_with_employee(self.attendance_date,self.attendance_date,self.employee)
                




            
            
from datetime import datetime, time
import frappe

def ot_calculation(name):
    attendance_records = frappe.db.sql("""SELECT * FROM `tabAttendance` WHERE miss_punch_application = %s""", (name,), as_dict=True)
    for att in attendance_records:
        ot_hours = "00:00:00"

        if att.shift and att.out_time and att.in_time:
            shift_et = frappe.db.get_value("Shift Type", {'name': att.shift}, ['end_time'])

            out_time = datetime.strptime(str(att.out_time), '%Y-%m-%d %H:%M:%S').time()
            shift_et = datetime.strptime(str(shift_et), '%H:%M:%S').time()

            if shift_et < out_time:
                difference = time_diff_in_timedelta_1(shift_et, out_time)
                diff_time = datetime.strptime(str(difference), '%H:%M:%S').time()

                if diff_time.hour > 0:
                    if diff_time.minute >= 50:
                        ot_hours = time(diff_time.hour + 1, 0, 0)
                    else:
                        ot_hours = time(diff_time.hour, 0, 0)
                elif diff_time.hour == 0:
                    if diff_time.minute >= 50:
                        ot_hours = time(1, 0, 0)
                    else:
                        ot_hours = "00:00:00"
                else:
                    ot_hours = "00:00:00"
        else:
            ot_hours = "00:00:00"

        if ot_hours != "00:00:00":
            ftr = [3600, 60, 1]
            hr = sum([a * b for a, b in zip(ftr, map(int, str(ot_hours).split(':')))])
            ot_hr = round(hr / 3600, 1)
        else:
            ot_hr = '0.0'

        # frappe.db.set_value("Attendance", att.name, "custom_ot_hours", ot_hours)
        frappe.db.set_value("Attendance", att.name, "overtime_hours", ot_hr)

def time_diff_in_timedelta_1(time1, time2):
    datetime1 = datetime.combine(datetime.min, time1)
    datetime2 = datetime.combine(datetime.min, time2)
    return datetime2 - datetime1



@frappe.whitelist()
def miss_punch_mail_alert():
    yesterday = add_days(frappe.utils.today(), -1)
    attendance = frappe.db.sql("""
        SELECT * FROM `tabAttendance` LEFT JOIN `tabEmployee` 
        ON `tabAttendance`.employee = `tabEmployee`.name
        WHERE `tabAttendance`.attendance_date = %s AND `tabAttendance`.docstatus != 2
        order by `tabAttendance`.employee
    """, (yesterday,), as_dict=True)
    
    staff = """
        <div style="text-align: center;">
            <h2 style="font-size: 16px;">Miss Punch Report</h2>
        </div>
        <table style="border-collapse: collapse; width: 100%; border: 1px solid black; font-size: 10px;">
            <tr style="border: 1px solid black;">
                <th style="padding: 4px; border: 1px solid black;">Employee</th>
                <th style="padding: 4px; border: 1px solid black;">Employee Name</th>
                <th style="padding: 4px; border: 1px solid black;">Department</th>
                <th style="padding: 4px; border: 1px solid black;">Attendance Date</th>
                <th style="padding: 4px; border: 1px solid black;">In Time</th>
                <th style="padding: 4px; border: 1px solid black;">Out Time</th>
                <th style="padding: 4px; border: 1px solid black;">Shift</th>
            </tr>
    """
    no_punches = True
    for att in attendance:
        if att.in_time and not att.out_time:
            no_punches = False
            staff += """
            <tr style="border: 1px solid black;">
                <td style="padding: 4px; border: 1px solid black;">{0}</td>
                <td style="padding: 4px; border: 1px solid black;">{1}</td>
                <td style="padding: 4px; border: 1px solid black;">{2}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{3}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{4}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{5}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{6}</td>
            </tr>
            """.format(att.employee, att.employee_name, att.department,
                    format_date(att.attendance_date) or ' ', format_datetime(att.in_time) or ' ',
                    format_datetime(att.out_time) or ' ', att.shift or ' ')
        elif not att.in_time and att.out_time:
            no_punches = False
            staff += """
            <tr style="border: 1px solid black;">
                <td style="padding: 4px; border: 1px solid black;">{0}</td>
                <td style="padding: 4px; border: 1px solid black;">{1}</td>
                <td style="padding: 4px; border: 1px solid black;">{2}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{3}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{4}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{5}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{6}</td>
            </tr>
            """.format(att.employee, att.employee_name, att.department,
                    format_date(att.attendance_date) or ' ', format_datetime(att.in_time) or ' ',
                    format_datetime(att.out_time) or ' ', att.shift or ' ')

    if no_punches:
        staff = """
        <div style="text-align: center;">
            <h2 style="font-size: 16px;">No missed punch for yesterday.</h2>
        </div>
        """
    else:
        staff += "</table>"

    recipients = ["deepak.ma@groupteampro.com"]

    

    frappe.sendmail(
        recipients=recipients,
        subject='Miss Punch Report',
        message="""Dear Sir,<br><br>
                Kindly find the attached Employee Miss Punch List for yesterday:<br>{0}
                """.format(staff)
    )

def mark_wh(from_date, to_date, employee):
    attendance_records = frappe.db.get_all(
        'Attendance',
        filters={
            'attendance_date': ('between', (from_date, to_date)),
            'docstatus': ('!=', '2'),
            'employee': employee
        },
        fields=['name', 'in_time', 'out_time', 'status', 'shift_status']
    )

    for att in attendance_records:
        in_time = att.get('in_time')
        out_time = att.get('out_time')

        if in_time and out_time:
            if isinstance(in_time, str):
                in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
            if isinstance(out_time, str):
                out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')

            wh = time_diff_in_hours(out_time, in_time)
            if wh:
                wh = round(wh, 1)
                if wh >= 8:
                    if att.get('shift_status') == "Matched":
                        new_status = 'Present'
                    else:
                        new_status = 'Absent'
                elif 4 <= wh < 8:
                    if att.get('shift_status') == "Matched":
                        new_status = 'Half Day'
                    else:
                        new_status = 'Absent'
                else:
                    if att.get('leave_application'):
                        new_status = 'Half Day'
                    else:
                        new_status = 'Absent'

                return wh, new_status
    return None, None


@frappe.whitelist()  
def check_holiday(date,emp):
    holiday_list = frappe.db.get_value('Employee',emp,'holiday_list')
    holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
    left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
    if holiday:
        if holiday[0].weekly_off == 1:
            return "WW"
        else:
            return "HH"