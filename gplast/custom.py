# your_app.module_name.py

import frappe
from frappe import _
from frappe.utils import time_diff

# your_app.module_name.py

import frappe
from frappe import throw,_
import math
import frappe
import frappe.utils
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
# from frappe.utils import add_to_date, get_datetime_str
import frappe
from frappe.utils import add_to_date, add_days
import frappe
from frappe.utils import add_to_date, add_days, get_datetime_str, get_datetime, time_diff_in_hours

from dateutil.relativedelta import relativedelta
from frappe.utils import (
    DATE_FORMAT,
    add_days,
    add_to_date,
    cint,
    comma_and,
    date_diff,
    flt,
    get_link_to_form,
    getdate,
)
from frappe import _
from frappe.utils import getdate, get_first_day, get_last_day
from frappe.utils import get_datetime, time_diff_in_seconds
from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on,is_lwp
from collections import Counter
# from hrms.hr.doctype.shift_request.shift_request import validate_overlapping_shift_requests


@frappe.whitelist()
def validate_shift_request(doc, method):
    if not doc.employee or not doc.from_date or not doc.to_date:
        return

    overlapping = frappe.db.sql("""
        SELECT name FROM `tabShift Request`
        WHERE employee = %s
        AND docstatus < 2
        AND name != %s
        AND (
            (from_date BETWEEN %s AND %s)
            OR (to_date BETWEEN %s AND %s)
            OR (%s BETWEEN from_date AND to_date)
            OR (%s BETWEEN from_date AND to_date)
        )
    """, (doc.employee, doc.name, doc.from_date, doc.to_date, doc.from_date, doc.to_date, doc.from_date, doc.to_date))

    if overlapping:
        frappe.throw(_("Shift Request overlaps with existing request(s): {0}").format(", ".join([o[0] for o in overlapping])))


@frappe.whitelist()
def check_eligibility_for_privilege_leave(doc, method):
    if doc.leave_type == 'Privilege Leave':
        year = getdate(doc.from_date).year  
        sdate = getdate(get_first_day(f"{year}-01-01"))  
        edate = getdate(get_last_day(f"{year}-12-31"))
        
        pl_leave_count = frappe.db.count('Leave Application', {
            'employee': doc.employee,
            'from_date': ['between', [sdate, edate]],
            'to_date': ['between', [sdate, edate]],
            'leave_type': doc.leave_type,
            'docstatus': ('!=', 2)
        })
        
        if pl_leave_count > 3:
            frappe.throw(
                f"You can only apply {doc.leave_type} a maximum of three times per year.")

    
        if doc.total_leave_days < 3:
            frappe.throw(
                f"Leave application for {doc.leave_type} must be for more than three days."
            )

    if doc.leave_type == "Casual Leave":
        dates = get_dates(doc.from_date ,doc.to_date)
        flag = True
        for date in dates:
            if flag:
                hh = check_holiday(date,doc.employee)
                if not hh:
                    if frappe.db.exists("Shift Assignment",{'start_date':date,'employee':doc.employee,'shift_type':'WW','docstatus':('=','1')} ):
                        frappe.msgprint("Weekly Off (WW) is added to Casual Leave (CL)")
                        flag = False
                else :
                    frappe.msgprint("Holiday is added to Casual Leave (CL)")
                    flag = False  

        previous_day=add_days(doc.from_date , -1)
        next_day=add_days(doc.to_date,+1)

        flag1=True
        while(flag1):
            if frappe.db.exists("Shift Assignment",{'start_date':previous_day,'employee':doc.employee,'shift_type':'WW','docstatus':1}):
                previous_day=add_days(previous_day , -1)
                if frappe.db.exists("Shift Assignment", {'start_date':previous_day,'employee':doc.employee,'shift_type':'WW','docstatus':1}):
                    previous_day=add_days(previous_day , -1)
                    if frappe.db.exists("Leave Application",{'from_date':previous_day,'employee':doc.employee,'docstatus':('!=',2)}):
                        flag1=False
                        # frappe.throw("CL leave has already been applied for the day before your Weekly Off.")
                        leave_doc_name = frappe.db.get_value("Leave Application", {'to_date':previous_day,'employee':doc.employee,'docstatus':('!=',2)},['name'])
                        form_link = get_link_to_form("Leave Application", leave_doc_name)
                        msg = _(
                            "CL leave application has been already applied before the Weekly Off. Leave Application: {0}"
                        ).format(
                            form_link
                        )
                        frappe.throw(msg)

                else:
                    if frappe.db.exists("Leave Application",{'to_date':previous_day,'employee':doc.employee,'docstatus':('!=',2)}):
                        flag1=False
                        # frappe.throw("CL leave has already been applied for the day before your Weekly Off.")
                        leave_doc_name = frappe.db.get_value("Leave Application", {'to_date':previous_day,'employee':doc.employee,'docstatus':('!=',2)},['name'])
                        form_link = get_link_to_form("Leave Application", leave_doc_name)
                        msg = _(
                            "CL leave application has been already applied before the Weekly Off. Leave Application: {0}"
                        ).format(
                            form_link
                        )
                        frappe.throw(msg)
                    else:
                        flag1=False 
            else:
                flag1=False

        flag2=True
        while(flag2):
            if frappe.db.exists("Shift Assignment",{'start_date':next_day,'employee':doc.employee,'shift_type':'WW','docstatus':1}):
                next_day=add_days(next_day , +1)
                if frappe.db.exists("Shift Assignment", {'start_date':next_day,'employee':doc.employee,'shift_type':'WW','docstatus':1}):
                    next_day=add_days(next_day , +1)
                    if frappe.db.exists("Leave Application",{'from_date':next_day,'employee':doc.employee,'docstatus':('!=',2)}):
                        flag2=False
                        # frappe.throw("CL leave has already been applied for the day after your Weekly Off.")
                        leave_doc_name = frappe.db.get_value("Leave Application", {'from_date':next_day,'employee':doc.employee,'docstatus':('!=',2)},['name'])
                        form_link = get_link_to_form("Leave Application", leave_doc_name)
                        msg = _(
                            "CL leave application has been already applied after the Weekly Off. Leave Application: {0}"
                        ).format(
                            form_link
                        )
                        frappe.throw(msg)

                else:
                    if frappe.db.exists("Leave Application",{'from_date':next_day,'employee':doc.employee,'docstatus':('!=',2)}):
                        flag2=False
                        # frappe.throw("CL leave has already been applied for the day after your Weekly Off.")
                        leave_doc_name = frappe.db.get_value("Leave Application", {'from_date':next_day,'employee':doc.employee,'docstatus':('!=',2)},['name'])
                        form_link = get_link_to_form("Leave Application", leave_doc_name)
                        msg = _(
                            "CL leave application has been already applied after the Weekly Off. Leave Application: {0}"
                        ).format(
                            form_link
                        )
                        frappe.throw(msg)
                    else:
                        flag2=False 
            else:
                flag2=False        

                     
@frappe.whitelist()
def update_previous_workflow_state_on_creation(doc, method):
    doc.previous_workflow_state ='Preview'
@frappe.whitelist()
def update_previous_approval_date_on_validation(doc, method):
    from frappe.utils import today

    doctype = doc.doctype
    old_state = frappe.db.get_value(doctype, doc.name, "workflow_state")

    if old_state and old_state != doc.workflow_state:
        doc.previous_approval_date = today()

            


@frappe.whitelist()
def create_notifications_based_on_the_pending():
    from collections import defaultdict
    from frappe.utils import today, add_days

    doctypes = [
        'Leave Application',
        'On Duty Application',
        'Miss Punch Application',
        'Attendance Permission',
        'Over Time',
        'Compensatory Leave Request'
    ]

    approver_fields_map = {
        'Leave Application': ['leave_approver_2', 'leave_approver_3', 'leave_approver_4'],
        'On Duty Application': ['leave_approver_2', 'leave_approver_3', 'leave_approver_4'],
        'Miss Punch Application': ['level_approver_2', 'level_approver_3', 'level_approver_4'],
        'Attendance Permission': ['level_approver_2', 'level_approver_3', 'level_approver_4'],
        'Over Time': ['level_approver_2', 'level_approver_3', 'level_approver_4'],
        'Compensatory Leave Request':['level_2_approver', 'level_3_approver', 'level_4_approver']
    }

    approver_docs_map = defaultdict(lambda: defaultdict(list))

    for doctype in doctypes:
        approver_fields = approver_fields_map[doctype]
        extra_fields = []

        if doctype == 'Leave Application':
            extra_fields = ['employee', 'employee_name', 'from_date', 'to_date', 'total_leave_days', 'leave_type']
        elif doctype == 'On Duty Application':
            extra_fields = ['employee', 'employee_name', 'from_date', 'to_date', 'total_number_of_days', 'shift', 'session', 'from_time', 'to_time']
        elif doctype == 'Miss Punch Application':
            extra_fields = ['employee', 'employee_name', 'attendance_date', 'shift', 'in_time', 'out_time']
        elif doctype == 'Attendance Permission':
            extra_fields = ['employee', 'employee_name', 'permission_date', 'shift', 'session', 'permission_hours', 'from_time', 'to_time']
        elif doctype == 'Over Time':
            extra_fields = ['employee', 'employee_name', 'ot_date', 'shift', 'overtime_hours']
        elif doctype == 'Compensatory Leave Request':
            extra_fields = ['employee', 'employee_name', 'work_from_date', 'work_end_date', 'leave_type']

        fields = ['name', 'total_leave_approvers', 'workflow_state'] + approver_fields + extra_fields

        documents = frappe.db.get_all(
            doctype,
            filters={
                'docstatus': 0,
                'workflow_state': ['not in', ['Rejected', 'Approved']],
                'previous_approval_date': ['<', today()]
            },
            fields=fields,
            order_by='workflow_state'
        )

        for doc in documents:
            receiver = None
            level_label = None

            if doc.workflow_state == "Pending for Manager" and doc.total_leave_approvers > 1:
                receiver = doc.get(approver_fields[0])
                level_label = "Pending from Manager - Pending from Manager 1"
            elif doc.workflow_state == "Pending for Manager 1" and doc.total_leave_approvers > 2:
                receiver = doc.get(approver_fields[1])
                level_label = "Pending from Manager 1 - Pending from Manager 2"
            elif doc.workflow_state == "Pending for Manager 2" and doc.total_leave_approvers > 3:
                receiver = doc.get(approver_fields[2])
                level_label = "Pending from Manager 2 - Pending from Manager 3"

            if receiver and level_label:
                doc["doctype"] = doctype 
                approver_docs_map[receiver][level_label].append(doc)

    for receiver, levels in approver_docs_map.items():
        message = """<b>Dear Approver,</b><br><br>
        <p>The following documents are pending for more than 1 day and have been escalated to you:</p><br>"""

        for level_label, doc_list in levels.items():
            docs_by_doctype = defaultdict(list)
            for doc in doc_list:
                docs_by_doctype[doc.doctype].append(doc)

            message += f"<h4>{level_label}</h4>"

            for doctype, docs in docs_by_doctype.items():
                message += f"<b>{doctype}</b><br>"

                if doctype == 'Leave Application':
                    message += """<table border=1 cellpadding=5 cellspacing=0>
                    <tr><th>ID</th><th>Employee</th><th>Employee Name</th><th>From Date</th><th>To Date</th><th>Total Leave Days</th><th>Leave Type</th></tr>"""
                    for d in docs:
                        message += f"""
                        <tr>
                            <td>{d.name}</td><td>{d.employee}</td><td>{d.employee_name}</td>
                            <td>{formatdate(d.from_date, "dd-mm-yyyy") or ''}</td><td>{formatdate(d.to_date, "dd-mm-yyyy") or ''}</td><td>{d.total_leave_days or ''}</td><td>{d.leave_type or ''}</td>
                        </tr>"""
                    message += "</table><br>"

                elif doctype == 'On Duty Application':
                    message += """<table border=1 cellpadding=5 cellspacing=0>
                    <tr><th>ID</th><th>Employee</th><th>Employee Name</th><th>From Date</th><th>To Date</th><th>Total Days</th><th>Shift</th><th>Session</th><th>From Time</th><th>To Time</th></tr>"""
                    for d in docs:
                        message += f"""
                        <tr>
                            <td>{d.name}</td><td>{d.employee}</td><td>{d.employee_name}</td>
                            <td>{formatdate(d.from_date, "dd-mm-yyyy") or ''}</td><td>{formatdate(d.to_date, "dd-mm-yyyy") or ''}</td><td>{d.total_number_of_days or ''}</td>
                            <td>{d.shift or ''}</td><td>{d.session or ''}</td><td>{d.from_time or ''}</td><td>{d.to_time or ''}</td>
                        </tr>"""
                    message += "</table><br>"

                elif doctype == 'Miss Punch Application':
                    message += """<table border=1 cellpadding=5 cellspacing=0>
                    <tr><th>ID</th><th>Employee</th><th>Employee Name</th><th>Attendance Date</th><th>Shift</th><th>In Time</th><th>Out Time</th></tr>"""
                    for d in docs:
                        message += f"""
                        <tr>
                            <td>{d.name}</td><td>{d.employee}</td><td>{d.employee_name}</td>
                            <td>{formatdate(d.attendance_date, "dd-mm-yyyy") or ''}</td><td>{d.shift or ''}</td><td>{d.in_time or ''}</td><td>{d.out_time or ''}</td>
                        </tr>"""
                    message += "</table><br>"

                elif doctype == 'Attendance Permission':
                    message += """<table border=1 cellpadding=5 cellspacing=0>
                    <tr><th>ID</th><th>Employee</th><th>Employee Name</th><th>Permission Date</th><th>Shift</th><th>Session</th><th>Permission Hours</th><th>From Time</th><th>To Time</th></tr>"""
                    for d in docs:
                        message += f"""
                        <tr>
                            <td>{d.name}</td><td>{d.employee}</td><td>{d.employee_name}</td>
                            <td>{formatdate(d.permission_date, "dd-mm-yyyy") or ''}</td><td>{d.shift or ''}</td><td>{d.session or ''}</td>
                            <td>{d.permission_hours or ''}</td><td>{d.from_time or ''}</td><td>{d.to_time or ''}</td>
                        </tr>"""
                    message += "</table><br>"

                elif doctype == 'Over Time':
                    message += """<table border=1 cellpadding=5 cellspacing=0>
                    <tr><th>ID</th><th>Employee</th><th>Employee Name</th><th>OT Date</th><th>Shift</th><th>Overtime Hours</th></tr>"""
                    for d in docs:
                        message += f"""
                        <tr>
                            <td>{d.name}</td><td>{d.employee}</td><td>{d.employee_name}</td>
                            <td>{formatdate(d.ot_date, "dd-mm-yyyy") or ''}</td><td>{d.shift or ''}</td><td>{d.overtime_hours or ''}</td>
                        </tr>"""
                    message += "</table><br>"
                elif doctype == 'Compensatory Leave Request':
                    message += """<table border=1 cellpadding=5 cellspacing=0>
                    <tr><th>ID</th><th>Employee</th><th>Employee Name</th><th>From Date</th><th>To Date</th><th>Leave Type</th></tr>"""
                    for d in docs:
                        message += f"""
                        <tr>
                            <td>{d.name}</td><td>{d.employee}</td><td>{d.employee_name}</td>
                            <td>{formatdate(d.work_from_date, "dd-mm-yyyy") or ''}</td><td>{formatdate(d.work_end_date, "dd-mm-yyyy") or ''}</td><td>{d.leave_type or ''}</td>
                        </tr>"""
                    message += "</table><br>"

        message += "<br>Regards,<br>HR Department"

        # Uncomment below to send real email
        frappe.sendmail(
            recipients=[receiver],
            subject="Pending Applications Escalated for Your Approval",
            message=message
        )

        # frappe.sendmail(
        #     recipients=["jothi.m@groupteampro.com"],
        #     subject="Test: Escalated Applications",
        #     message=message
        # )

        print(receiver)
        print(message)

from frappe.utils import getdate, date_diff
from datetime import datetime, timedelta

@frappe.whitelist()
def salary_slip_alert_notify_for_hod(doc, method):
    doj = frappe.db.get_value("Employee", {'name': doc.employee}, 'date_of_joining')
    now_date = datetime.today()
    now_date = getdate(now_date)
    days_count = date_diff(now_date, doj)
    
    if days_count < 90:
        date_list = get_dates_between(doc.start_date, doc.end_date)
        holiday_count = 0
        holiday_date_list = []
        
        for date in date_list:
            check_holiday_result = check_holiday(date, doc.employee)
            if check_holiday_result == 'HH':
                holiday_count += 1
                fromdate = datetime.strptime(str(date), '%Y-%m-%d')
                doj = fromdate.strftime('%d-%m-%Y')
                holiday_date_list.append(date)  
        if holiday_count != 0:
            # hod = frappe.db.get_value("Employee", {'name': doc.employee}, 'reports_to')
            # if hod:
                # user_id = frappe.db.get_value("Employee", {'name': hod}, 'user_id')
            user_id = "kumaresan@gplast.com"
            holiday_dates = ", ".join(holiday_date_list)
            frappe.sendmail(
                recipients=user_id,
                subject="Alert Notification for Holiday Leave",
                message=f"""<p>Dear Sir/Madam,</p>
                    <p>The employee <b>{doc.employee}</b> is not eligible for the following holidays as the employee's 
                    <b>Date of Joining</b> exceeds the 90-day eligibility period.</p>
                    <p><b>Holiday Dates:</b> {holiday_dates}</p>
                    <p>Kindly review this matter and take necessary action if required.</p>
                    <p>Thank you.</p>
                """

            )

@frappe.whitelist()
def get_dates_between(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    dates = []
    current_date = start
    while current_date <= end:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    return dates

@frappe.whitelist()
def check_holiday(date, emp):
    # Get the holiday list for the employee
    holiday_list = frappe.db.get_value('Employee', emp, 'holiday_list')
    
    query = """
        SELECT `tabHoliday`.holiday_date, `tabHoliday`.weekly_off
        FROM `tabHoliday List`
        LEFT JOIN `tabHoliday` ON `tabHoliday`.parent = `tabHoliday List`.name
        WHERE `tabHoliday List`.name = %s AND holiday_date = %s
    """
    holiday = frappe.db.sql(query, (holiday_list, date), as_dict=True)
    if holiday:
        if holiday[0].weekly_off == 1:
            return "WW"  # Weekly off
        else:
            return "HH"  # Holiday
    return None

@frappe.whitelist()
def check_eligibility(applicant):
    employee = frappe.get_doc("Employee", applicant)

    # Get the date_of_joining from the Employee document
    date_of_joining = employee.date_of_joining

    # Calculate the experience in years
    experience_in_years = frappe.utils.data.getdate(frappe.utils.nowdate()) - date_of_joining
    experience_in_years = experience_in_years.days / 365

    if experience_in_years < 3:
        frappe.throw(_("You must have at least 3 years of experience to apply for a loan."))


def create_hooks_mark_ot():
    job = frappe.db.exists('Scheduled Job Type', 'create_notifications_based_on_the_pending')
    if not job:
        sjt = frappe.new_doc("Scheduled Job Type")
        sjt.update({
            "method": 'gplast.custom.create_notifications_based_on_the_pending',
            "frequency": 'Cron',
            "cron_format": '0 13 * * *'
        })
        sjt.save(ignore_permissions=True)

def send_holidays_reminder_in_advance_for_new_join_employees():
    def is_holiday(date,emp):
        if check_holiday(date,emp) == 'HH':
            return True
    date_to_check = getdate()
    date_to_check = add_days(date_to_check, 1)
    # today_date = getdate()

    # Calculate the date 90 days ago
    date_90_days_ago = add_days(date_to_check, -90)
    # date_of_joining_list = add_days(date_to_check,-90)
    employee_list = frappe.get_all(
        "Employee",
        filters={
            "status": "Active",
            "date_of_joining": [">=", date_90_days_ago]
        },
        fields=["name", "first_name", "user_id", "holiday_list", "date_of_joining"]
    )
    if employee_list:
        for emp in employee_list:
            if is_holiday(date_to_check,emp.name):
                # employee_doc = frappe.get_doc("Employee", employee)
                # if not holidays:
                #     return
                # doj = frappe.db.get_value("Employee", {'name': employee_doc.name}, 'date_of_joining')
                doj = emp.date_of_joining
                now_date = datetime.today()
                now_date = getdate(now_date)
                days_count = date_diff(now_date, doj)
                
                if days_count < 90:
                # employee_doc = frappe.get_doc("Employee", employee)
                    employee_email = get_employee_email(emp)
                    frappe.sendmail(
                recipients=[employee_email],
                subject=_("Upcoming Holidays Reminder"),
                message=_("This email is to remind you about the upcoming holidays. Tomorrow is a holiday for you, but you are not eligible for this holiday because your joining date is less than 90 days ago."),
                # holidays=holidays,
            )


def get_employee_email(employee_doc):
    return (
        employee_doc.get("user_id")
        or employee_doc.get("personal_email")
        or employee_doc.get("company_email")
    )

@frappe.whitelist()
def create_additional_salary(doc, method):
    for create_sal in doc.repayment_schedule:
        add_sal = frappe.new_doc("Additional Salary")
        add_sal.employee = doc.applicant
        add_sal.employee_name = doc.applicant_name
        add_sal.company = doc.company
        add_sal.salary_component = "Loan"
        add_sal.payroll_date = create_sal.payment_date
        add_sal.amount = create_sal.total_payment
        add_sal.save(ignore_permissions=True)



import frappe
from frappe.utils import add_to_date, add_days, get_time, get_datetime
import frappe
from frappe.utils import add_to_date, get_time, get_datetime

def set_permission_times(doc, method):
    if doc.shift and doc.session and doc.permission_hours:
        shift = frappe.get_doc("Shift Type", doc.shift)
        if shift:
            try:
                permission_hours = int(doc.permission_hours)
            except ValueError:
                frappe.throw("Invalid value for permission_hours. Please enter an integer value.")

            shift_start_time = get_time(shift.start_time)

            if doc.session == "First Half":
                from_time = get_datetime(shift_start_time)
            elif doc.session == "Second Half":
                from_time = add_to_date(get_datetime(shift_start_time), hours=shift.hours / 2)
            else:
                frappe.throw("Invalid session. Session should be either 'First Half' or 'Second Half'.")

            to_time = add_to_date(from_time, hours=permission_hours)

            doc.from_time = from_time.strftime("%H:%M:%S")
            doc.to_time = to_time.strftime("%H:%M:%S")
        else:
            frappe.throw("Shift Type '{}' not found.".format(doc.shift))


@frappe.whitelist()
def upadte_checkin_att():
    checkin = frappe.db.sql("""delete from `tabEmployee Checkin`""")
    print(checkin)
    att = frappe.db.sql("""delete from `tabAttendance`""")
    print(att)

@frappe.whitelist()
def get_end_date(start_date, frequency):
    start_date = getdate(start_date)
    frequency = frequency.lower() if frequency else "monthly"
    kwargs = (
        get_frequency_kwargs(frequency) if frequency != "bimonthly" else get_frequency_kwargs("monthly")
    )
    end_date = add_to_date(start_date, **kwargs) - relativedelta(days=1)
    if frequency == "monthly":
        return dict(end_date=end_date.strftime(DATE_FORMAT))

    else:
        return dict(end_date="")


def get_frequency_kwargs(frequency_name):
    frequency_dict = {
        "monthly": {"months": 1},
        "fortnightly": {"days": 14},
        "weekly": {"days": 7},
        "daily": {"days": 1},
    }
    return frequency_dict.get(frequency_name)

def get_dates(start_date, end_date):
    no_of_days = date_diff(add_days(end_date, 1), start_date)
    dates = [add_days(start_date, i) for i in range(0, no_of_days)]
    return dates


# @frappe.whitelist()
# def late_time_difference(end_time, start_time):
#     value = time_diff(end_time, start_time)
#     val = value.total_seconds()
#     hours = int(val // 3600)
#     val %= 3600
#     minutes = int(val // 60)
#     seconds = int(val % 60)
#     return f"{hours:02}:{minutes:02}:{seconds:02}"

@frappe.whitelist()
def get_conditions():
    condn = frappe.db.sql("""select * from `tabConditions` order by `order`""",as_dict=True)
    return condn


@frappe.whitelist()
def get_condition():
    condn = frappe.db.sql("""select * from `tabSkill` order by `order`""",as_dict=True)
    return condn

@frappe.whitelist()
def inactive_employee(doc,method):
    name =doc.name
    employee_aadhar_number=doc.employee_aadhar_number
    _uan_no=doc._uan_no
    esi_number=doc.esi_number
    pan_number  =doc.pan_number
    if doc.status=="Active":
        if doc.relieving_date:
            throw(_("Please remove the relieving date for the Active Employee."))
    # if pan_number and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan_number):
    #     frappe.throw("Please provide a valid PAN Number!")

    if esi_number and not re.match(r'^\d{12}$', esi_number):
        frappe.throw("ESI number should contain only 12 digits")
    if employee_aadhar_number and not re.match(r'^\d{12}$',employee_aadhar_number):
        frappe.throw("Aadhar number should contain only 12 digits")
    if _uan_no and not re.match(r'^\d{12}$',_uan_no):
        frappe.throw("UAN number should contain only 12 digits")
    if employee_aadhar_number and name:
        aadhar_number= frappe.db.get_value('Employee',{"employee_aadhar_number":employee_aadhar_number,'name':['!=',name]},'employee_aadhar_number')
        if aadhar_number:
            frappe.throw("Aadhar number alredy exists")

    if _uan_no and name:
        uan_no = frappe.db.get_value('Employee',{"_uan_no":_uan_no,'name':['!=',name]},'_uan_no')
        if uan_no:
            frappe.throw("UAN number alredy exists")
                
    if pan_number and name:
        pan_num = frappe.db.get_value('Employee',{"pan_number":pan_number,'name':['!=',name]},'pan_number')
        if pan_num:
            frappe.throw("PAN number alredy exists")
                
    if esi_number and name:
        esi_num = frappe.db.get_value('Employee',{"esi_number":esi_number,'name':['!=',name]},'esi_number')
        if esi_num:
            frappe.throw("ESI number alredy exists")

# from google.cloud import translate_v2
# @frappe.whitelist()
# def training_feedback(event_name,date,venue,feedback_result,employee,employee_name,department):
# 	data = '<div><table width=100%><tr><td style="text-align:center;font-size:25px;font-family:"Times New Roman", Times, serif"><u style="font-weight:bold;">பயிற்சி வகுப்பு  பற்றிய கருத்துக்கள்<br></u></td></tr><tr><td></td></tr>'
# 	event_name_tamil = translate_text(event_name)
# 	data += '<td style="font-size:17px;font-family:"Times New Roman", Times, serif">பயிற்சி தலைப்பு &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:%s</td></tr>'%(event_name_tamil)
# 	data += '</table></div>'
# 	return data


# def translate_text(text, target_language='ta'):
#     client = translate_v2.Client()
#     result = client.translate(text, target_language=target_language)
#     return result['input']

# @frappe.whitelist()
# def training_feedback(event_name, date, venue, feedback_result, employee, employee_name, department):
#     data = '<div><table width=100%><tr><td style="text-align:center;font-size:25px;font-family: \'Times New Roman\', Times, serif"><u style="font-weight:bold;">பயிற்சி வகுப்பு  பற்றிய கருத்துக்கள்<br></u></td></tr><tr><td></td></tr>'
#     event_name_tamil = translate_text(event_name)
#     data += '<td style="font-size:17px;font-family: \'Times New Roman\', Times, serif">பயிற்சி தலைப்பு &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:%s</td></tr>' % (event_name_tamil)
#     data += '</table></div>'
#     return data

# def translate_text(text, target_language='ta'):
#     client = translate_v2.Client()
#     result = client.translate(text, target_language=target_language)
#     return result['input']


@frappe.whitelist()
def get_language():
    print(frappe.db.get_single_value("System Settings","language"))
 
# Update submitted date
# @frappe.whitelist()
# def update_submitted_date(doc, method):
#     frappe.db.set_value("Training Result", doc.name, "submitted_on", today())
    
@frappe.whitelist()
def manpower_request_approved_date(doc, method):
    if doc.workflow_state == "Approved" and not doc.approved_date:
        frappe.db.set_value("Manpower Request", doc.name, "approved_date", today())
    
@frappe.whitelist()
def mail_trigger_for_training_result():
    job = frappe.db.exists('Scheduled Job Type', 'mail_training_result')
    if not job:
        sjt = frappe.new_doc("Scheduled Job Type")
        sjt.update({
            "method": 'gplast.custom.mail_training_result',
            "frequency": 'Cron',
            "cron_format": "0 8 * * *"
        })
        sjt.save(ignore_permissions=True)

@frappe.whitelist()
def mail_training_result():
    today_date = datetime.strptime(frappe.utils.today(), "%Y-%m-%d").date()
    training_results = frappe.get_all(
            "Training Result",
            filters={
                "docstatus": 1,
            },
            fields=["name", "submitted_on", "training_event"]
        )
    for doc in training_results:
        type = frappe.db.get_value("Training Event", doc.training_event, "type1") or None
        if type:
            months = frappe.db.get_value("Training Events Type", type, "month") or None
        if months:
            start_date = today_date - relativedelta(months=months)
        if start_date:
            training_result_doc = frappe.get_doc("Training Result", doc.name)
            if doc.submitted_on == start_date:
                for child in training_result_doc.employees:
                    user_id = frappe.get_value("Employee", {"name": child.employee}, "user_id")
                    department = frappe.get_value("Employee", {"name": child.employee}, "department")

                    hod_details = frappe.get_value(
                        "Department",
                        department,
                        ["hod", "hod_id", "hod_name"]
                    ) or [None, None, None]

                    hod_email = hod_details[0] or "kumaresan@gplast.com"
                    hod_id = hod_details[1] or "2328"
                    hod_name = hod_details[2] or "KUMARESAN S"

                    if user_id:
                        send_mail(child, doc, user_id, department)
                    if hod_email:
                        send_mail_to_hod(child, doc, department, hod_email, hod_id, hod_name)


@frappe.whitelist()
def send_mail(child, doc, user_id, department):
    data = f"""
        <html>
        <body>
        <p style="text-align: left; font-weight: 500">Dear {child.employee_name},</p>
        <p>Good Morning! {child.employee} - {child.employee_name}, find your Training Result below:</p>
        <div style="padding-left: 10px; line-height: 10px;">
            <p>Training Event: {doc.training_event}</p>
            <p>Department: {department}</p>
            <p>Date: {doc.submitted_on}</p>
            <p>Hours: {child.hours}</p>
            <p>Grade: {child.grade}</p>
            <p>Comments: {child.comments}</p>
        </div>
        </body>
        </html>
    """
    frappe.sendmail(
        recipients=[user_id],
        subject='Training Result',
        message=data
    )


@frappe.whitelist()
def send_mail_to_hod(child, doc, department, hod_email, hod_id, hod_name):
    data = f"""
        <html>
        <body>
        <p style="text-align: left; font-weight: 500">Dear {hod_name},</p>
        <p>Good Morning! Find the Training Results for employee {child.employee} - {child.employee_name}</p>
        <div style="padding-left: 10px; line-height: 10px;">
            <p>Training Event: {doc.training_event}</p>
            <p>Department: {department}</p>
            <p>Date: {doc.submitted_on}</p>
            <p>Hours: {child.hours}</p>
            <p>Grade: {child.grade}</p>
            <p>Comments: {child.comments}</p>
        </div>
        </body>
        </html>
    """
    frappe.sendmail(
        recipients=[hod_email],
        subject='Training Result',
        message=data
    )


@frappe.whitelist()
def get_now_date():
    print(now())       


import frappe
import re

# @frappe.whitelist()
# def validate_employee_doc(doc,method): 
    # name =doc.name
    # employee_aadhar_number=doc.employee_aadhar_number
    # _uan_no=doc._uan_no
    # esi_number=doc.esi_number
    # pan_number  =doc.pan_number
    # if pan_number and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan_number):
    #     frappe.throw("Please provide a valid PAN Number!")

    # if esi_number and not re.match(r'^\d{12}$', esi_number):
    #     frappe.throw("ESI number should contain only 12 digits")
    # if employee_aadhar_number and not re.match(r'^\d{12}$',employee_aadhar_number):
    #     frappe.throw("Aadhar number should contain only 12 digits")
    # if _uan_no and not re.match(r'^\d{12}$',_uan_no):
    #     frappe.throw("UAN number should contain only 12 digits")
    # if employee_aadhar_number and name:
    #     aadhar_number= frappe.db.get_value('Employee',{"employee_aadhar_number":employee_aadhar_number,'name':['!=',name]},'employee_aadhar_number')
    #     if aadhar_number:
    #         frappe.throw("Aadhar number alredy exists")

    # if _uan_no and name:
    #     uan_no = frappe.db.get_value('Employee',{"_uan_no":_uan_no,'name':['!=',name]},'_uan_no')
    #     if uan_no:
    #         frappe.throw("UAN number alredy exists")
                
    # if pan_number and name:
    #     pan_num = frappe.db.get_value('Employee',{"pan_number":pan_number,'name':['!=',name]},'pan_number')
    #     if pan_num:
    #         frappe.throw("PAN number alredy exists")
                
    # if esi_number and name:
    #     esi_num = frappe.db.get_value('Employee',{"esi_number":esi_number,'name':['!=',name]},'esi_number')
    #     if esi_num:
    #         frappe.throw("ESI number alredy exists")
    # return None
                
# @frappe.whitelist()
# def employee_attendance_status():
        
#         yesterday = add_days(today(), - 1)

#         days_count = add_days(yesterday, - 10)

#         absent = frappe.db.sql("""
#                         SELECT employee, count(attendance_date)
#                         FROM `tabAttendance`
#                         WHERE status = "Absent" AND attendance_date BETWEEN %s AND %s
#                         GROUP BY employee
#                       """, (days_count, yesterday), as_dict=True)
#         for abs in absent:
#             emp = abs["employee"]
#             leave_application = frappe.db.exists("Leave Application", 
#                                                 {"employee":emp, 
#                                                 "from_date": ["Between", [days_count, yesterday]],
#                                                 "docstatus": ["<", 2]})

#             if not leave_application:
#                 frappe.db.set_value("Employee", abs.employee, {"status": "Left"})
#                 send_absence_notification(user_id, yesterday)

#                 user_id = frappe.db.get_value("User", {"email": emp}, "name")
#                 if user_id:
#                     frappe.db.set_value("User", user_id, "enabled", 0)

# def send_absence_notification(user_id, last_working_day):
#     if user_id:
#         subject = "User Account Deactivated"
#         message = f"""
#             Dear Employee,
            
#             Your user account has been deactivated due to 10+ days of absent days.
#             Last Working Day: {last_working_day}.
#         """
#         frappe.sendmail(recipients=user_id, subject=subject, message=message)

@frappe.whitelist()
def designation_and_period_restriction(designation, from_date):
    if from_date:
        staffing_plan = frappe.db.sql("""
        SELECT parent 
        FROM `tabStaffing Plan Detail` 
        WHERE designation = %s
        AND parent IN (
            SELECT name FROM `tabStaffing Plan`
            WHERE from_date = %s 
        )
        """, (designation, from_date))

        if staffing_plan:
            return (f"Staffing Plan for {designation} is already created for the period {frappe.utils.formatdate(from_date)}.")

@frappe.whitelist()
def new_designation(doc, method):
    if not frappe.db.exists("Designation", {"designation_name": doc.designation}):
        design = frappe.new_doc("Designation")
        design.designation_name = doc.designation
        design.hod = doc.hod
        design.designation_code = doc.designation_code
        design.department = doc.department
        design.save(ignore_permissions = True)
        
    if not frappe.db.exists("Sub Designation",{"parent_designation":doc.designation,"designation_code":doc.designation_code}):
        sub_design = frappe.new_doc("Sub Designation")   
        sub_design.parent_designation = doc.designation
        sub_design.department = doc.department
        sub_design.designation_code = doc.designation_code
        sub_design.from_parent = 1
        sub_design.save(ignore_permissions = True) 
        
@frappe.whitelist()
def mail_for_forwarded(employee_id, reason, doc_name):
    employee = frappe.db.get_value("Employee", {"name": employee_id}, ["user_id"])
    if not employee:
        frappe.throw(f"No User ID found for employee.")
    manpower = frappe.db.get_value("Manpower Request", {"name": doc_name}, ["name"])
    url = frappe.utils.get_url()
    document_link = f"{url}/app/manpower-request/{doc_name}"   
    data = f"""
    Dear {employee},<br><br><br><br>
    You have received a forwarded request for the  Manpower Request - {manpower}.<br><br>
    <b>Reason: </b><br>{reason}<br><br>
    <a href="{document_link}" target="blank">Click here to view Manpower Request.</a>
    """
    frappe.sendmail(
        recipients=employee,
        subject="Manpower Request Forwarded",
        message=data
    )


@frappe.whitelist()
def existing_and_new_position_designation_code(employee, position_details):
    employee_data = frappe.db.get_value("Employee", {"name": employee}, ["designation_code", "department"], as_dict=True)

    if not employee_data:
        return {"designation_code": []}

    employee_designation_code = employee_data.get("designation_code")
    employee_department = employee_data.get("department")

    department_designations = frappe.db.get_all("Sub Designation", {"department": employee_department}, ["name"])
    department_designation_list = [d["name"] for d in department_designations]

    assigned_designations = frappe.db.get_all("Employee", ["designation_code"])
    assigned_designation_list = [d["designation_code"] for d in assigned_designations if d["designation_code"]]

    if position_details == "Existing Position":
        employee_designation_code = [d for d in department_designation_list if d in assigned_designation_list]
        return {"designation_code": employee_designation_code}

    if position_details == "New Position":
        new_position_designations = [d for d in department_designation_list if d not in assigned_designation_list]
        return {"designation_code": new_position_designations}


@frappe.whitelist()
def job_requisition_mail(employee_id, reason, doc_name):
    employee = frappe.db.get_value("Employee", {"name": employee_id}, ["user_id"])
    if not employee:
        frappe.throw("No User Id is found for Employee.")
    job = frappe.db.get_value("Job Requisition", {"name": doc_name}, ["name"])
    url = frappe.utils.get_url()
    document_link = f"{url}/app/job-requisition/{doc_name}"   
    data = f"""
    Dear {employee},<br><br><br><br>
    You have received a forwarded request for the  Job Requisition - {job}.<br><br>
    <b>Remarks: </b><br>{reason}<br><br>
    <a href="{document_link}" target="blank">Click here to view Job Requisition.</a>
    """
    frappe.sendmail(
        recipients=employee,
        subject="Job Requisition Forwarded",
        message=data
    )

@frappe.whitelist()
def permission_request(employee,attendance):
    sum=0
    month_start = get_first_day(attendance)
    month_end = get_last_day(attendance)
    total= frappe.db.sql("select * from `tabAttendance Permission` where employee = '%s' and permission_date between '%s' and '%s' and workflow_state != 'Rejected' and docstatus !=2 "%(employee,month_start,month_end),as_dict=True)
    for i in total:
        sum+=int(i.permission_hour)
    return sum
        
        

# @frappe.whitelist()
# def employee_restriction_relieving_date(doc, method):
#     employee = frappe.get_doc("Employee", doc.employee)
#     if employee["relieving_date"]:
#         frappe.throw(f"You cannot apply for leave as your relieving date is set to {employee.relieving_date}")

@frappe.whitelist()
def approved_on_set_value(doc, method):
    doc.approved_on = frappe.utils.today()

@frappe.whitelist()
def restriction_for_comp_off(doc, method):
    employee = frappe.db.exists("Employee", {"employee": doc.employee, "ot_eligibility": "Compensatory Off"})

    if not employee:
        frappe.throw("You are not eligible to apply for 'Compensatory Off'.")
    current_date=today()
    diff=date_diff(current_date,doc.work_end_date)
    # if diff>1:
    #     frappe.throw("Leave request should be raised on the next day itself. Old dates are not allowed.")


import frappe
from datetime import datetime

import frappe
from datetime import datetime

@frappe.whitelist()
def restriction_for_cl_leave_in_notice_period(doc, method):
    if not is_lwp(doc.leave_type):
        leave_balance = get_leave_balance_on(
                        doc.employee,
                        doc.leave_type,
                        doc.from_date,
                        doc.to_date,
                        consider_all_leaves_in_the_allocation_period=True,
                        for_consumption=True,
                    )
        leave_balance_for_consumption = leave_balance.get("leave_balance_for_consumption")
        if doc.status != "Rejected" and (
            leave_balance_for_consumption < doc.total_leave_days or not leave_balance_for_consumption
        ):
            if frappe.db.get_value("Leave Type", doc.leave_type, "allow_negative"):
                # frappe.errprint('Test by JM')
                hod_employee_id = frappe.db.get_value("Employee", doc.employee, "reports_to")
                if hod_employee_id:
                    hod_mail_id =frappe.db.get_value("Employee", hod_employee_id, "user_id")
                    hod_name = frappe.db.get_value("Employee", hod_employee_id, "first_name")
                    if hod_mail_id:
                        subject = "Warning: Insufficient Leave Balance for Privilege Leave Request - {}".format(doc.employee_name)
                        message = """
                        Dear {0} - {3},
                        <br>
                        <br>
                        I hope this message finds you well.
                        <br>
                        We wanted to bring to your attention that {1} has submitted a request for "Privilege Leave," 
                        but their current leave balance is insufficient to process the request.
                        <br> 
                        According to our records, 
                        {1} has {2} days remaining in their Privilege Leave balance, which is less than the requested leave 
                        duration.
                        <br>
                        We kindly request that you review the leave request and discuss any possible adjustments with the employee.
                        <br>
                        If there is a need for clarification or assistance, the HR team is available to support.
                        <br>
                        Thank you for your attention to this matter.
                        <br>
                        <br>
                        <br>
                        <b>Note:</b> This is an automated email notification. Please do not reply to this email.
                        """.format(hod_name, doc.employee_name, doc.leave_balance,hod_employee_id)

                        frappe.sendmail(
                            recipients=[hod_mail_id],  
                            subject=subject,
                            message=message
                        )

    
    if doc.leave_type == "Casual Leave":
        resignation = frappe.get_list(
            "Resignation Form",
            filters={
                "employee": doc.employee,
                "workflow_state": ["!=", "Rejected"],
                "docstatus": ["!=", 2]
            },
            fields=["posting_date"],
            order_by="posting_date desc",
            limit=1
        )

        relieving_date = resignation[0].posting_date if resignation else None

        if relieving_date:
            applied_date = datetime.strptime(doc.entry_applied_date, "%Y-%m-%d").date()
            from_date = datetime.strptime(doc.from_date, "%Y-%m-%d").date()
            to_date = datetime.strptime(doc.to_date, "%Y-%m-%d").date()
            if from_date < applied_date and to_date < applied_date:
                return
            elif applied_date >= relieving_date:
                frappe.throw("You have applied for a Resignation Form. You are not allowed to apply for 'Casual Leave' after your requested relieving date.")


@frappe.whitelist()
def resignation_form_mail(employee_id, reason, doc_name):
    employee = frappe.db.get_value("Employee", {"name": employee_id}, ["user_id"])
    if not employee:
        frappe.throw("No User Id is found for Employee.")
    resignation_form = frappe.db.get_value("Resignation Form", {"name": doc_name}, ["name"])
    url = frappe.utils.get_url()
    document_link = f"{url}/app/resignation-form/{doc_name}"   
    data = f"""
    Dear {employee},<br><br><br><br>
    You have received a forwarded request for the  Resignation Form - {resignation_form}.<br><br>
    <b>Reason: </b><br>{reason}<br><br>
    <a href="{document_link}" target="blank">Click here to view the Resignation Form.</a>
    """
    frappe.sendmail(
        recipients=employee,
        subject="Resignation Form Forwarded",
        message=data
    )
    return 'Okay'

from hrms.hr.utils import get_holiday_dates_for_employee

@frappe.whitelist()
def get_total_working_hours(doc, method):
    from_date = doc.work_from_date
    to_date = doc.work_end_date
    dates = get_dates(from_date ,to_date)
    for date in dates:
        holidays = get_holiday_dates_for_employee(doc.employee, date, date)
        if holidays:
            total_working_hours = frappe.db.get_value("Attendance", {'employee': doc.employee, 'attendance_date': date, 'status': ['!=', 'Absent'], 'docstatus': 1}, ['total_working_hours'])
            doc.total_working_hours = total_working_hours
        else:
            overtime_hours = frappe.db.get_value("Attendance", {'employee': doc.employee, 'attendance_date': date, 'status': ['!=', 'Absent'], 'docstatus': 1}, ['overtime_hours'])
            doc.total_working_hours = overtime_hours

# import frappe
# from frappe.model.document import Document
# from frappe.utils import now_datetime, get_datetime
# @frappe.whitelist()
# def validate_shift_request(doc, method):

#     shift_type_doc = frappe.get_doc("Shift Type", doc.shift_type)
#     shift_start_time = shift_type_doc.start_time

#     if not shift_start_time:
#         return

#     shift_start_datetime = get_datetime(f"{doc.from_date} {shift_start_time}")

#     current_datetime = now_datetime()

#     time_difference = (shift_start_datetime - current_datetime).total_seconds() / 3600

#     frappe.logger().info(f"Shift Start: {shift_start_datetime}, Current Time: {current_datetime}, Diff: {time_difference} hours")

#     if time_difference <= 12:
#         frappe.throw("You can only apply for a shift request if the shift start time is more than 12 hours from the current time.")

@frappe.whitelist()
def get_total_positions(designation):
    
    
    result = frappe.db.sql("""
        SELECT SUM(no_of_positions)
        FROM `tabJob Requisition`
        WHERE designation_code = %s AND workflow_state = 'Approved'
    """, (designation,))
    
    

    total_positions = result[0][0] if result and result[0][0] else 0

    manpower_request = frappe.db.sql("""
        SELECT SUM(vacancy_count)
        FROM `tabManpower Request`
        WHERE new_designation_code = %s AND docstatus != 2
    """, (designation,))
    

    vacancy = manpower_request[0][0] if manpower_request and manpower_request[0][0] else 0  # Ensure None is converted to 0

    return total_positions - vacancy


# @frappe.whitelist()
# def leave_deduction_for_attendance_permission():

#     first_day_of_month = datetime.now().replace(day=1)
#     last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

#     employees = frappe.db.sql("""
#         SELECT employee, employee_name 
#         FROM `tabAttendance Permission`
#         WHERE permission_date BETWEEN %s AND %s
#         GROUP BY employee
#     """, (first_day_of_month, last_day_of_month), as_dict=True)

#     leave_hours = {
#         (4, 5): 0.5, (6, 7): 1, (8, 9): 1.5,
#         (10, 11): 2, (12, 13): 2.5, (14, 15): 3,
#         (16, 17): 3.5, (18, 19): 4, (20, 21): 4.5,
#         (22, 23): 5
#     }

#     for emp in employees:
#         permission_hours = sum([
#             int(x.permission_hour) for x in frappe.get_all(
#                 "Attendance Permission",
#                 filters={"employee": emp.employee},
#                 fields=["permission_hour"]
#             )
#         ])
#         print(f"Total Permission Hours for {emp.employee}: {permission_hours}")

#         leave_days = 0
#         for hours, days in leave_hours.items():
#             if hours[0] <= permission_hours <= hours[1]:
#                 leave_days = days
#                 break

#         if leave_days > 0:
#             leave_types = frappe.get_all("Leave Type", fields=["name"], order_by="order_number ASC")

#             total_leave_deducted = 0
#             remaining_leave_days = leave_days

#             for leave in leave_types:
#                 if remaining_leave_days <= 0:
#                     break

#                 available_leave = frappe.db.sql("""
#                     SELECT COALESCE(SUM(leaves), 0) as total_leaves 
#                     FROM `tabLeave Ledger Entry`
#                     WHERE employee = %s AND leave_type = %s
#                 """, (emp.employee, leave["name"]), as_dict=True)

#                 total_balance_leave = available_leave[0]["total_leaves"] if available_leave else 0

#                 if total_balance_leave > 0:
#                     leave_to_deduct = min(remaining_leave_days, total_balance_leave)
#                     total_leave_deducted += leave_to_deduct
#                     remaining_leave_days -= leave_to_deduct

#                     leave_ledger_entries = frappe.get_all(
#                         "Leave Ledger Entry",
#                         filters={'employee': emp.employee},
#                         fields=["transaction_type", "transaction_name"],
#                         order_by="creation DESC",
#                         limit_page_length=1
#                     )

#                     transaction_type = leave_ledger_entries[0]["transaction_type"]
#                     transaction_name = leave_ledger_entries[0]["transaction_name"]

#                     leave_entry = frappe.new_doc('Leave Ledger Entry')
#                     leave_entry.employee = emp.employee
#                     leave_entry.employee_name = emp.employee_name
#                     leave_entry.from_date = first_day_of_month
#                     leave_entry.to_date = last_day_of_month
#                     leave_entry.leave_type = leave["name"]
#                     leave_entry.leaves = -leave_to_deduct
#                     leave_entry.transaction_type = transaction_type
#                     leave_entry.transaction_name = transaction_name

#                     print(f"Deducting {leave_to_deduct} days from {leave['name']} for {emp.employee}")

#                     leave_entry.submit()

#             if total_leave_deducted < leave_days:
#                 frappe.throw(f"Not enough leave balance available for {emp.employee}. Permission cannot be applied.")

#         frappe.db.commit()
    

# @frappe.whitelist()
# def create_attendance_permission(doc, method):
#     if doc.in_time and doc.late_entry_check == 0 and doc.shift:
#         shift_start_time = frappe.db.get_value("Shift Type", doc.shift, ["start_time"])
        
#         from_time = ""
#         to_time = ""
        
#         if not shift_start_time:
#             return
        
#         if isinstance(doc.in_time, str):
#             doc.in_time = datetime.strptime(doc.in_time, "%Y-%m-%d %H:%M:%S")

#         if isinstance(shift_start_time, timedelta):  
#             shift_start_time = (datetime.min + shift_start_time).time()

#         shift_start_datetime = datetime.combine(doc.in_time.date(), shift_start_time)

#         late_duration = (doc.in_time - shift_start_datetime).total_seconds() / 60

#         permission_hour = 0
        
#         if 15 < late_duration <= 60:
#             permission_hour = 1
            
#             if doc.shift == "A":
#                 from_time = "08:00:00"
#                 to_time = "09:00:00"
#             elif doc.shift == "B":
#                 from_time = "16:00:00"
#                 to_time = "17:00:00"
#             elif doc.shift == "C":
#                 from_time = "00:00:00"
#                 to_time = "01:00:00"
#             elif doc.shift == "G":
#                 from_time = "08:00:00"
#                 to_time = "09:00:00"
#             elif doc.shift == "G1":
#                 from_time = "09:00:00"
#                 to_time = "10:00:00"
#             elif doc.shift == "G2":
#                 from_time = "08:00:00"
#                 to_time = "09:00:00"
#             elif doc.shift == "PP1":
#                 from_time = "20:00:00"
#                 to_time = "21:00:00"
                
                
#         elif 15 < late_duration <= 120:
#             permission_hour = 2
            
#             if doc.shift == "A":
#                 from_time = "08:00:00"
#                 to_time = "10:00:00"
#             elif doc.shift == "B":
#                 from_time = "16:00:00"
#                 to_time = "18:00:00"
#             elif doc.shift == "C":
#                 from_time = "00:00:00"
#                 to_time = "02:00:00"
#             elif doc.shift == "G":
#                 from_time = "08:00:00"
#                 to_time = "10:00:00"
#             elif doc.shift == "G1":
#                 from_time = "09:00:00"
#                 to_time = "11:00:00"
#             elif doc.shift == "G2":
#                 from_time = "08:00:00"
#                 to_time = "10:00:00"
#             elif doc.shift == "PP1":
#                 from_time = "20:00:00"
#                 to_time = "22:00:00"
        
#         if permission_hour:
#             attendance_permission = frappe.new_doc("Attendance Permission")
#             attendance_permission.employee = doc.employee
#             attendance_permission.permission_date = doc.attendance_date
#             attendance_permission.shift = doc.shift
#             attendance_permission.permission_hour = permission_hour
#             attendance_permission.from_time = from_time
#             attendance_permission.to_time = to_time
#             attendance_permission.session = "First Half"
#             attendance_permission.reason = "Late Entry"
#             doc.late_entry_check = 1
            
#             attendance_permission.save()


@frappe.whitelist()
def yearly_el_leave_allocation():
    job = frappe.db.exists('Scheduled Job Type', 'el_leave_allocation')
    if not job:
        sjt = frappe.new_doc("Scheduled Job Type")
        sjt.update({
            "method": 'gplast.custom.el_leave_allocation',
            "frequency": 'Cron',
            "cron_format": "0 0 1 1 *"
        })
        sjt.save(ignore_permissions=True)


@frappe.whitelist()
def el_leave_allocation():
    import calendar
    
    today = datetime.today()
    
    # Current Year Date
    current_year = today.year
    current_year_start_date = date(current_year, 1, 1)
    current_year_end_date = date(current_year, 12, 31)
    
    # Previous Year Date
    previous_year = today.year - 1
    previous_year_start_date = date(previous_year, 1, 1)
    previous_year_end_date = date(previous_year, 12, 31)
    
    previous_year_total_days = 366 if calendar.isleap(previous_year) else 365
    
    employees = frappe.get_all("Employee", {'status': 'Active',"employment_type": ["!=", "Contract"]}, ["name", "holiday_list", "date_of_joining", "employee_grade"])

    def custom_round(value):
        decimal_part = value % 1

        if decimal_part < 0.5:  
            return int(value)
        elif decimal_part <= 0.59:  
            return int(value) + 0.5
        else:  
            return int(value) + 1

    holiday_count = absent_count = half_day = half_day_count= on_leave_count = total_leave = earned_leave = 0

    for emp in employees:
        if emp["date_of_joining"] < previous_year_start_date:
            if emp.holiday_list:
                holidays = frappe.get_all(
                    "Holiday",
                    {
                        "parent": emp.holiday_list,
                        "holiday_date": ["between", [previous_year_start_date, previous_year_end_date]],
                    },
                    ["holiday_date"]
                )
                holiday_count = len(holidays)
                
                absent_count = frappe.db.count("Attendance",
                                               {"employee": emp["name"], "status": "Absent",
                                                "attendance_date": ["BETWEEN", [previous_year_start_date, previous_year_end_date]],
                                                "docstatus": 1})
                
                half_day = frappe.db.count("Attendance",
                                           {"employee": emp["name"], "status": "Half Day",
                                            "attendance_date": ["BETWEEN", [previous_year_start_date, previous_year_end_date]],
                                            "docstatus": 1})
                
                half_day_count = half_day / 2
                
                on_leave_count = frappe.db.count("Attendance",
                                                 {"employee": emp["name"], "status": "On Leave",
                                                  "attendance_date": ["BETWEEN", [previous_year_start_date, previous_year_end_date]],
                                                  "docstatus": 1})
                
                total_leave = absent_count + half_day_count + on_leave_count
                
                earned_leave = previous_year_total_days - holiday_count - total_leave
                total_earned_leave = rounded = 0
                
                if earned_leave > 240:
                    if emp["employee_grade"] == "Grade 2":
                        total_earned_leave = earned_leave / 20
                    elif emp["employee_grade"] == "Grade 1":
                        total_earned_leave = earned_leave / 12.5
                    
                    rounded = custom_round(total_earned_leave)
                    
                    if rounded > 0:
                    
                        leave_allocation = frappe.new_doc("Leave Allocation")
                        leave_allocation.employee = emp["name"]
                        leave_allocation.leave_type = "Earned Leave"
                        leave_allocation.from_date = current_year_start_date
                        leave_allocation.to_date = current_year_end_date
                        leave_allocation.new_leaves_allocated = rounded
                        
                        leave_allocation.save()
                        leave_allocation.submit()
                        frappe.db.commit()

        diff = year_days = eligibility =  0

        if previous_year_start_date <= emp["date_of_joining"] <= previous_year_end_date:
            if emp.holiday_list:
                holidays = frappe.get_all(
                    "Holiday",
                    {
                        "parent": emp.holiday_list,
                        "holiday_date": ["BETWEEN", [emp["date_of_joining"], previous_year_end_date]],
                    },
                    ["holiday_date"]
                )
                holiday_count = len(holidays)
                
            absent_count = frappe.db.count("Attendance",
                                           {"employee": emp["name"], "status": "Absent",
                                            "attendance_date": ["BETWEEN", [emp["date_of_joining"], previous_year_end_date]],
                                            "docstatus": 1})
            
            half_day = frappe.db.count("Attendance",
                                       {"employee": emp["name"], "status": "Half Day",
                                        "attendance_date": ["BETWEEN", [emp["date_of_joining"], previous_year_end_date]],
                                        "docstatus": 1})
            
            half_day_count = half_day / 2
            
            on_leave_count = frappe.db.count("Attendance",
                                             {"employee": emp["name"], "status": "On Leave",
                                              "attendance_date": ["BETWEEN", [emp["date_of_joining"], previous_year_end_date]],
                                              "docstatus": 1})
            
            diff = (emp["date_of_joining"] - previous_year_start_date).days
            
            year_days = previous_year_total_days - diff
            
            total_leave = absent_count + half_day_count + on_leave_count
            
            earned_leave = year_days - holiday_count - total_leave
            
            eligibility = year_days - holiday_count

            eligi = (eligibility/3) * 2
            
            total_earned_leave = 0
            if earned_leave > eligi:
                if emp["employee_grade"] == "Grade 2":
                    total_earned_leave = earned_leave / 20
                elif emp["employee_grade"] == "Grade 1":
                    total_earned_leave = earned_leave / 12.5
                
                rounded = custom_round(total_earned_leave)
                
                if rounded > 0:
                
                    leave_allocation = frappe.new_doc("Leave Allocation")
                    leave_allocation.employee = emp["name"]
                    leave_allocation.leave_type = "Earned Leave"
                    leave_allocation.from_date = current_year_start_date
                    leave_allocation.to_date = current_year_end_date
                    leave_allocation.new_leaves_allocated = rounded
                    
                    leave_allocation.save()
                    leave_allocation.submit()
                    frappe.db.commit()
   
                    
@frappe.whitelist()
def yearly_cl_leave_allocation():
    job = frappe.db.exists('Scheduled Job Type', 'cl_leave_allocation')
    if not job:
        sjt = frappe.new_doc("Scheduled Job Type")
        sjt.update({
            "method": 'gplast.custom.cl_leave_allocation',
            "frequency": 'Cron',
            "cron_format": "0 0 * * *"
        })
        sjt.save(ignore_permissions=True)

@frappe.whitelist()
def cl_leave_allocation():
    current_date = datetime.today()
    current_year = current_date.year
    current_year_start_date = date(current_year, 1, 1)
    current_year_end_date = date(current_year, 12, 31)

    employees = frappe.db.get_all("Employee", 
        filters={"status": "Active","employment_type": ["!=", "Contract"]}, 
        fields=["employee", "date_of_joining", "employee_grade"]
    )

    for emp in employees:
        existing_allocation = frappe.get_all("Leave Allocation",
            filters={
                "employee": emp["employee"],
                "leave_type": "Casual Leave",
                "docstatus": ["!=", 2],
                "from_date": ["<=", current_year_end_date],
                "to_date": [">=", current_year_start_date],
            },
            fields=["name", "from_date", "to_date"]
        )

        if existing_allocation:
            continue

        leave_days = 9 if emp["employee_grade"] == "Grade 2" else 12 if emp["employee_grade"] == "Grade 1" else 0
        if leave_days == 0:
            continue
        
        joining_date = emp["date_of_joining"]
        new_leaves_allocated = 0
        from_date = current_year_start_date

        if joining_date < current_year_start_date:
            new_leaves_allocated = leave_days  

        elif current_year_start_date <= joining_date <= current_year_end_date:
            remaining_months = 12 - joining_date.month
            if joining_date.day <= 15:
                remaining_months += 1
                from_date = date(current_year, joining_date.month, 1)
            else:
                from_date = date(current_year, joining_date.month + 1, 1)

            new_leaves_allocated = round((leave_days / 12) * remaining_months)


        if new_leaves_allocated > 0:
            leave_allocation = frappe.new_doc("Leave Allocation")
            leave_allocation.employee = emp["employee"]
            leave_allocation.leave_type = "Casual Leave"
            leave_allocation.from_date = from_date
            leave_allocation.to_date = current_year_end_date
            leave_allocation.new_leaves_allocated = new_leaves_allocated

            leave_allocation.save()
            leave_allocation.submit()
            frappe.db.commit()
    
@frappe.whitelist()
def send_mail_leave(name, employee, from_date, to_date, leave,approver, emp_mail):
    table = f"""
    <table border="1" width="100%" style="border-collapse: collapse; text-align: left;">
        <tr>
            <td>ID</td><td>Employee</td><td>From Date</td><td>To Date</td><td>No of Days</td>
        </tr>
        <tr>
            <td>{name}</td><td>{employee}</td><td>{from_date}</td><td>{to_date}</td><td>{leave}</td>
        </tr>
    </table>
    """

    if approver:
        frappe.sendmail(
            recipients=[approver],
            subject=f"Leave Application {name} from {employee} is pending for your Approval",
            message=f"""
                Dear Sir/Madam,<br><br>
                The following leave application is pending for your approval.<br><br>
                {table}
                <br><br>
            """
        )
    # if emp_mail:
    #     frappe.sendmail(
    #         recipients=[emp_mail],
    #         subject=f"Leave Application {name} has been sent for Approval",
    #         message=f"""
    #             Dear Employee,<br><br>
    #             Your leave application has been sent for approval.<br><br>
    #             {table}
    #             <br><br>
    #         """
    #     )

# @frappe.whitelist()
# def create_attendance_permission_for_early_exit(doc, method):
#     if doc.out_time and doc.early_exit_check == 0 and doc.shift:
#         shift_end_time = frappe.db.get_value("Shift Type", doc.shift, ["end_time"])

#         from_time = ""
#         to_time = ""

#         if not shift_end_time:
#             return

#         if isinstance(doc.in_time, str):
#             doc.in_time = datetime.strptime(doc.in_time, "%Y-%m-%d %H:%M:%S")

#         if isinstance(shift_end_time, timedelta):
#             shift_end_time = (datetime.min + shift_end_time).time()

#         out_time_datetime = datetime.strptime(doc.out_time, "%Y-%m-%d %H:%M:%S")

#         shift_end_time_datetime = datetime.combine(out_time_datetime.date(), shift_end_time)

#         exit_duration = (shift_end_time_datetime - out_time_datetime).total_seconds() / 60
#         permission_hour = 0

#         if 15 < exit_duration <= 60:
#             permission_hour = 1

#             if doc.shift == "A":
#                 from_time = "15:00:00"
#                 to_time = "16:00:00"
#             elif doc.shift == "B":
#                 from_time = "23:00:00"
#                 to_time = "00:00:00"
#             elif doc.shift == "C":
#                 from_time = "07:00:00"
#                 to_time = "08:00:00"
#             elif doc.shift == "G":
#                 from_time = "11:00:00"
#                 to_time = "12:00:00"
#             elif doc.shift == "G1":
#                 from_time = "16:30:00"
#                 to_time = "17:30:00"
#             elif doc.shift == "G2":
#                 from_time = "15:30:00"
#                 to_time = "16:30:00"
#             elif doc.shift == "PP1":
#                 from_time = "03:00:00"
#                 to_time = "04:00:00"

#         elif 15 < exit_duration <= 120:
#             permission_hour = 2

#             if doc.shift == "A":
#                 from_time = "14:00:00"
#                 to_time = "16:00:00"
#             elif doc.shift == "B":
#                 from_time = "22:00:00"
#                 to_time = "00:00:00"
#             elif doc.shift == "C":
#                 from_time = "06:00:00"
#                 to_time = "08:00:00"
#             elif doc.shift == "G":
#                 from_time = "10:00:00"
#                 to_time = "12:00:00"
#             elif doc.shift == "G1":
#                 from_time = "15:30:00"
#                 to_time = "17:30:00"
#             elif doc.shift == "G2":
#                 from_time = "14:30:00"
#                 to_time = "16:30:00"
#             elif doc.shift == "PP1":
#                 from_time = "02:00:00"
#                 to_time = "04:00:00"

#         if permission_hour:
#             attendance_permission = frappe.new_doc("Attendance Permission")
#             attendance_permission.employee = doc.employee
#             attendance_permission.permission_date = doc.attendance_date
#             attendance_permission.shift = doc.shift
#             attendance_permission.permission_hour = permission_hour
#             attendance_permission.from_time = from_time
#             attendance_permission.to_time = to_time
#             attendance_permission.session = "Second Half"
#             attendance_permission.reason = "Early Exit"
#             doc.early_exit_check = 1

#             attendance_permission.save()

@frappe.whitelist()
def create_additional_salary_in_month_end():
    job = frappe.db.exists('Scheduled Job Type', 'additional_salary')
    if not job:
        sjt = frappe.new_doc("Scheduled Job Type")
        sjt.update({
            "method": 'gplast.custom.create_additional_salary_for_attendance_permission',
            "frequency": 'Cron',
            "cron_format": "59 23 28-31 * *"
        })
        sjt.save(ignore_permissions=True)

@frappe.whitelist()
def create_additional_salary_for_attendance_permission():
    from frappe.utils import getdate, add_to_date, date_diff

    today = getdate()
    start_date = today.replace(day=1)
    end_date = add_to_date(start_date, months=1, days=-1)

    if today != end_date:
        return

    query = """
        SELECT employee, employee_name, department
        FROM `tabAttendance Permission`
        WHERE permission_date BETWEEN %s AND %s
        AND docstatus != 2
        AND workflow_state != 'Rejected'
        GROUP BY employee
    """
    employees = frappe.db.sql(query, (start_date, end_date), as_dict=True)

    leave_hours = {
        (4, 5): 0.5, (6, 7): 1, (8, 9): 1.5,
        (10, 11): 2, (12, 13): 2.5, (14, 15): 3,
        (16, 17): 3.5, (18, 19): 4, (20, 21): 4.5,
        (22, 23): 5, (24, 25): 5.5, (26, 27): 6,
        (28, 29): 6.5, (30, 31): 7
    }

    for employee in employees:
        total_permission_count = 0
        approved_hours = 0
        unapproved_hours = 0

        permissions = frappe.db.get_all(
            "Attendance Permission",
            filters={
                "employee": employee["employee"],
                "docstatus": ["!=", 2],
                "workflow_state": ["!=", "Rejected"],
                "permission_date": ["between", [start_date, end_date]]
            },
            fields=["permission_hour", "workflow_state"]
        )

        for permission in permissions:
            permission_hours = int(permission["permission_hour"])
            total_permission_count += permission_hours

            if permission["workflow_state"] == "Approved":
                approved_hours += permission_hours
            else:
                unapproved_hours += permission_hours

        total_leave_days = 0
        approved_leave_days = 0
        month_days = date_diff(end_date, start_date) + 1

        salary_components = frappe.db.get_value(
                                                "Employee",
                                                {"employee": employee["employee"]},
                                                ["basic", "cca", "house_rent_allowance",
                                                "special_allowance", "shift_allowance",
                                                "other_allowance", "arrear", "arrear_hra", "ctc", "date_of_joining"],
                                                as_dict=True
                                            )

        if salary_components["ctc"]:
            penalty = salary_components["ctc"]
        else:
            penalty = (salary_components["basic"] + salary_components["cca"] +
                        salary_components["house_rent_allowance"] + salary_components["special_allowance"] +
                        salary_components["shift_allowance"] + salary_components["other_allowance"] +
                        salary_components["arrear"] + salary_components["arrear_hra"])


        if salary_components["date_of_joining"] > start_date:
            payroll_date = salary_components["date_of_joining"]
        else:
            payroll_date = start_date

        for hours, days in leave_hours.items():
            if total_permission_count in hours:
                total_leave_days = days
            if approved_hours in hours:
                approved_leave_days = days

        if total_permission_count > 3:
            leave_type = "Casual Leave"
            availiable_leave = frappe.db.sql("""
                    SELECT SUM(leaves) as total_leaves 
                    FROM `tabLeave Ledger Entry`
                    WHERE employee = %s AND leave_type = %s AND docstatus = 1
                """, (employee["employee"], leave_type), as_dict=True)

            total_balance_leave = (availiable_leave[0]["total_leaves"] or 0) if availiable_leave else 0
            if total_balance_leave > 0:
                if approved_hours > 0 and total_leave_days == approved_leave_days:
                    deducted_leave = min(approved_leave_days, total_balance_leave)
                    leave_ledger_entries = frappe.get_all(
                    "Leave Ledger Entry",
                    {'employee': employee["employee"], "transaction_type": "Leave Allocation", "docstatus": 1},
                    ["transaction_name"],
                    limit_page_length=1
                    )

                    transaction_name = leave_ledger_entries[0]["transaction_name"]

                    leave_entry = frappe.new_doc('Leave Ledger Entry')
                    leave_entry.employee = employee["employee"]
                    leave_entry.employee_name = employee["employee_name"]
                    leave_entry.from_date = start_date
                    leave_entry.to_date = end_date
                    leave_entry.leave_type = leave_type
                    leave_entry.leaves = -deducted_leave
                    leave_entry.transaction_type = "Leave Allocation"
                    leave_entry.transaction_name = transaction_name

                    leave_entry.submit()

                    balance_leave = approved_leave_days - deducted_leave
                else:
                    balance_leave = approved_leave_days

                if balance_leave > 0:
                    salary_assignment = frappe.db.exists("Salary Structure Assignment",
                                                        {"employee": employee["employee"], "docstatus": 1})
                    if salary_assignment:
                        additional_salary = frappe.new_doc("Additional Salary")
                        additional_salary.employee = employee["employee"]
                        additional_salary.employee_name = employee["employee_name"]
                        additional_salary.department = employee["department"]
                        additional_salary.payroll_date = payroll_date
                        additional_salary.salary_component = "Permission Penalty"
                        additional_salary.amount = (balance_leave * (int(penalty) / month_days))
                        additional_salary.save(ignore_permissions=True)
                        additional_salary.submit()

            else:
                salary_assignment = frappe.db.exists(
                    "Salary Structure Assignment",
                    {"employee": employee["employee"], "docstatus": 1})
                if salary_assignment:
                    additional_salary = frappe.new_doc("Additional Salary")
                    additional_salary.employee = employee["employee"]
                    additional_salary.employee_name = employee["employee_name"]
                    additional_salary.department = employee["department"]
                    additional_salary.payroll_date = payroll_date
                    additional_salary.salary_component = "Permission Penalty"
                    additional_salary.amount = (total_leave_days * (int(penalty) / month_days))
                    additional_salary.save(ignore_permissions=True)
                    additional_salary.submit()


# @frappe.whitelist()
# def restriction_for_shift_assignment_cancellation(doc, method):

#     if frappe.db.exists("Attendance",
#                         {"attendance_date": doc.start_date, "employee": doc.employee, "docstatus": ["!=", 2]}):
#         frappe.throw("Shift Assignment cannot be Cancelled. Attendance is created for the date.")

@frappe.whitelist()
def remove_shift_assignment(doc, method):
    attendance_name = frappe.db.exists("Attendance", {
        "attendance_date": doc.start_date,
        "employee": doc.employee,
        "assigned_shift": doc.shift_type
    })

    if attendance_name:
        attendance = frappe.get_doc("Attendance", attendance_name)
        attendance.assigned_shift = ""
        attendance.save(ignore_permissions=True)


@frappe.whitelist()
def get_count_designation(d_code):
    return frappe.db.count('Employee',{'designation_code' : d_code, 'status':'Active' })
 
    
@frappe.whitelist()
def validate_vacancy(doc,method):
        vacancy_count = int(doc.vacancy_count) if doc.vacancy_count else 0
        no_of_vacancy = int(doc.no_of_vacancy) if doc.no_of_vacancy else 0
        if(no_of_vacancy <= 0):
            frappe.throw("Vacancy count is not available for this designstion code from Job Requisition")
        if not doc.apply_for_left_employee:
            if (vacancy_count <=0):
                frappe.throw(f"Vacancy Count could not be {vacancy_count}")
      
            elif (vacancy_count > no_of_vacancy):
                        frappe.throw("Vacancy Count must less than 'No. of vacancy")




@frappe.whitelist()
def designation_check(doc,method):
         
        year1 = getdate().year
        
        date_1 = getdate()
        year2 = add_to_date(date_1, days=365).year
        
        year =f"""{year1}-{year2}"""
  
        # frappe.errprint(year or "Not received")

 
        s_date=  frappe.db.get_value("Fiscal Year",{"name":year},"year_start_date")
        s_date_obj=getdate(s_date)
        start_date=s_date_obj.strftime('%d-%m-%Y')
        
        
        e_date=  frappe.db.get_value("Fiscal Year",{"name":year},"year_end_date")
        e_date_obj=getdate(e_date)
        end_date=e_date_obj.strftime('%d-%m-%Y')
        
  
        # frappe.errprint(start_date)
        # frappe.errprint(end_date)
        # frappe.errprint(doc.designation_code)
        # frappe.errprint(doc.name)
  
        records =  frappe.db.get_all("Job Requisition", 
                               filters={"designation_code":doc.designation_code,"name":["!=",doc.name],"posting_date":["between",[start_date,end_date]],"status": ["!=","Cancelled"]},
                               fields=["name","count_of_designation","requested_by_designation","requested_by_dept","posting_date","designation_code"]
                               
                                   
          )
        
        
        # frappe.errprint(records[0]["name"])
        # frappe.errprint(records[0]["requested_by_designation"])
        # frappe.errprint(records[0]["requested_by_dept"])
        # frappe.errprint(records[0]["posting_date"])
        # frappe.errprint(records[0]["count_of_designation"] - employee_count)
        # frappe.errprint(doc.no_of_positions)
  
        if ( records and len(records)>0):
            
            
            employee_count = frappe.db.count("Employee", {
                    "designation_code": records[0]["designation_code"],
                    "department": records[0]["requested_by_dept"],
                    "creation": ["between", [start_date,records[0]["posting_date"]]],
                    "status": "Active"
                })
            
            if(employee_count<records[0]["count_of_designation"]):
                diff=records[0]["count_of_designation"] - employee_count
                if(doc.no_of_positions > diff):
                    frappe.throw(f"""No.Of Positions cannot exceeds{diff} for this designation""")
                    frappe.validated=False
                    
                
            
            elif(employee_count >= records[0]["count_of_designation"]):
                frappe.throw("Cannot able to made request for an already requested designation code")
                frappe.validated=False
                
# @frappe.whitelist()
# "gplast.custom.notify_hod_on_employee_left",
# def notify_hod_on_employee_left(doc, method):
#     # if (doc.cell_number =='+91'):
#     #     doc.cell_number =''
#     if (doc.emergency_phone_number =='+91'):
#         doc.emergency_phone_number =''
#     old_status = frappe.db.get_value("Employee", doc.name, "status")
    
#     if doc.status == "Left" and old_status != "Left":
#         department = doc.department
#         hod_user = frappe.db.get_value("Department", department, "hod")
        
#         if hod_user:
#             hod_email = frappe.db.get_value("User", hod_user, "email")
#             hod_full_name = frappe.utils.get_fullname(hod_user)
            
#             relieving_date = (
#                 formatdate(doc.relieving_date, "dd-mm-yyyy") if doc.relieving_date else "Not Specified"
#             )
#             subject = f"Notification: Employee {doc.employee_name} Marked as Left"
            
#             message = frappe.render_template("""
#                 <p>Dear {{ hod_name }},</p>
#                 <p>This is to inform you that the employee <strong>{{ employee_name }}</strong> 
#                 (<strong>{{ employee_id }}</strong>), holding the position of 
#                 <strong>{{ designation }}</strong>, has been marked as <strong>"Left"</strong> 
#                 effective from <strong>{{ relieving_date }}</strong>.</p>

#                 <p>Please take any further necessary action if required.</p>
#                 <p>Regards,<br>HR Department</p>
#             """, {
#                 "hod_name": hod_full_name,
#                 "employee_name": doc.employee_name,
#                 "employee_id": doc.name,
#                 "designation": doc.designation,
#                 "relieving_date": relieving_date
#             })
            
#             frappe.sendmail(
#                 recipients=[hod_email],
#                 subject=subject,
#                 message=message
#             )


@frappe.whitelist()
def status_update(doc, method):
    old_status = frappe.db.get_value("Job Requisition", doc.name, "workflow_state")
    if (old_status == 'Returned'):
        
        if doc.workflow_state == "Pending for GM-HR" and old_status != "Pending for GM-HR":
            doc.posting_date = date.today()



@frappe.whitelist()
def notify_retirement_date():
    now_year = frappe.utils.now_datetime().year

    start_date = f"{now_year}-01-01"
    end_date = f"{now_year}-12-31"

    employee_records = frappe.get_all("Employee",
        filters={
            'status': 'Active',
            'date_of_retirement': ['between', [start_date, end_date]]
        },
        fields=["name", "employee_name", "user_id", "date_of_retirement", "notice_number_of_days",'department']
    )
    
    today = getdate(nowdate())

    for emp in employee_records:
        if emp.date_of_retirement and emp.notice_number_of_days:
            notify_date = add_days(getdate(emp.date_of_retirement), -int(emp.notice_number_of_days))
            previos_day = add_days(getdate(emp.date_of_retirement),-1)
            if notify_date == today or previos_day == today:
                subject = f"Retirement Notice for {emp.employee_name}"
                message1 = f"""
                Dear {emp.employee_name},<br><br>
                This is a reminder that you are scheduled to retire on <strong>{formatdate(emp.date_of_retirement)}</strong>.<br>
                <br><br>
                Please begin the necessary formalities.
                """
                message2 = f"""
                    Dear Sir/Mam,<br><br>
                    This is a reminder that {emp.employee_name} is scheduled to retire on <strong>{formatdate(emp.date_of_retirement)}</strong>.<br>
                    <br><br>
                    Please begin the necessary formalities.
                    """
                recipient = []
                department = emp.department
                hod_user = frappe.db.get_value("Department", department, "hod")
                if hod_user:
                   recipient.append(hod_user) 

                if emp.user_id:
                    subject = f"Retirement Notice for {emp.employee_name}"
                frappe.sendmail(recipients=[emp.user_id], subject=subject, message=message1) 
                    # recipient.append(emp.user_id)
                recipient_users = frappe.db.get_list(
                    "Has Role",
                    filters={"role": ["in", ['HR Manager']], "parenttype": "User"},
                    fields=["parent as user_name"]
                )
                for user in recipient_users:
                    email =frappe.get_value("User", {'name': user['user_name'], 'enabled': 1}, "email")
                    if email and email not in recipient:
                        recipient.append(email)
               
                frappe.sendmail(recipients=recipient, subject=subject, message=message2)



@frappe.whitelist()
def update_lwf(employee, start_date):
    type,employer_amount,employee_amount = frappe.db.get_value("Employee", {"name": employee}, ["lwf_type","employer_amount","employee_amount"])
    if type == "Employee":
        lwf = employee_amount
    elif type == "Employer":
        lwf = employer_amount
    else:
        lwf = 0

    date_obj = getdate(start_date)

    if date_obj.month == 12:
        amount = lwf
    else:
        amount = 0

    return amount


# import frappe
# from frappe import _
# from frappe.utils import getdate
# import math
# @frappe.whitelist()
# def update_pt(employee, start_date, gross):
#     date_obj = getdate(start_date)
#     pt_amount = 0

#     # Get PT transaction parent (zone)
#     pt_parent = frappe.db.get_value("Employee", {"name": employee}, "zone_id")
#     if not pt_parent:
#         frappe.throw(_("ESI Zone ID not found for employee"))

#     # Get employee fixed components
#     allowances = frappe.db.get_value(
#         "Employee",
#         {"name": employee},
#         [
#             "basic",
#             "cca",
#             "house_rent_allowance",
#             "special_allowance",
#             "shift_allowance",
#             "other_allowance",
#         ],
#         as_dict=True
#     )

#     fixed = sum(allowances.values()) if allowances else 0

#     if date_obj.month == 8:
#         fiscal_year = date_obj.year
#         apr_01 = f"{fiscal_year}-04-01"
#         jul_31 = f"{fiscal_year}-07-31"

#         slips = frappe.get_all(
#             "Salary Slip",
#             filters={
#                 "employee": employee,
#                 "start_date": [">=", apr_01],
#                 "end_date": ["<=", jul_31],
#                 "docstatus": 1
#             },
#             fields=["gross_pay"]
#         )
#         total_apr_jul = sum(slip["gross_pay"] for slip in slips)
#         total_value = total_apr_jul + float(gross) + fixed

#     elif date_obj.month == 1:
#         fiscal_year = date_obj.year
#         oct_01 = f"{fiscal_year - 1}-10-01"
#         dec_31 = f"{fiscal_year - 1}-12-31"

#         slips = frappe.get_all(
#             "Salary Slip",
#             filters={
#                 "employee": employee,
#                 "start_date": [">=", oct_01],
#                 "end_date": ["<=", dec_31],
#                 "docstatus": 1
#             },
#             fields=["gross_pay"]
#         )
#         total_oct_dec = sum(slip["gross_pay"] for slip in slips)
#         total_value = total_oct_dec + float(gross) + (fixed * 2)

#     else:
#         return 0  # No PT deduction in other months

#     # Now fetch PT amount manually using range
#     pt_details = frappe.get_all(
#         "PT Transaction Details",
#         filters={
#             "parent": pt_parent
#         },
#         fields=["from_salary", "to_salary", "pt_amount"]
#     )

#     for row in pt_details:
#         if row["from_salary"] <= total_value <= row["to_salary"]:
#             pt_amount = row["pt_amount"]
#             break

#     return math.ceil(pt_amount)



@frappe.whitelist()
def update_total_experience(doc,method):
    total = 0
    for i in doc.external_work_history:
        if i.total_experience:
            total+=int(i.total_experience)
    doc.employee_previous_experience_ = total

@frappe.whitelist()
def autoname(doc,method):
    if doc.is_new():
        if(doc.employee_category == "Contractor"):
            if doc.employee_aadhar_number:
                doc.name= doc.employee_aadhar_number
                # contractor_emp = frappe.get_doc('Employee',{'name':doc.name})
                # frappe.rename_doc("Employee",doc.name,doc.employee_aadhar_number,force=1)
            else:
                frappe.throw("Aadhar Number not found. Kindly set a Aadhar Number")


@frappe.whitelist()
def validate_the_interview_feedback_document(doc,method):
    if doc.reason_for_designation_change and len(doc.reason_for_designation_change) > 20:
        frappe.throw("Reason for Designation Change cannot exceed 20 characters.")

import frappe
from collections import defaultdict
position_counters = defaultdict(int)
@frappe.whitelist()
def generate_designation_code(doc, method):
    if not doc.designation_code:
        title = (doc.designation_name or "").strip()
        if not title:
            frappe.throw("Designation Name is required to generate Designation Code.")

        parts = title.split()
        if len(parts) == 1:
            code = parts[0][:2].upper()
        else:
            code = "".join(part[0].upper() for part in parts[:3])
        # frappe.errprint(code)
        length = len (code)
        existing_count = frappe.db.count(
            doc.doctype,
            { "designation_code": ["like", f"{code}%"] }
        )
        seq = existing_count + 1
        # frappe.errprint(seq)
        if length == 2:
            doc.designation_code = f"{code}{seq:03}"
        elif length == 3:
            doc.designation_code = f"{code}{seq:02}"

# import frappe
# from frappe.utils import add_days, getdate
# from datetime import datetime

# @frappe.whitelist()
# def create_new_lop(doc, method):
#     if doc.leave_type == "Leave Without Pay" and doc.total_leave_days == 6:
#         from_date = getdate(doc.from_date)
#         if from_date.weekday() == 0:
#             new_from_date = add_days(doc.to_date, 1)
#             new_to_date = new_from_date  
#             new_leave = frappe.get_doc({
#                 "doctype": "Leave Application",
#                 "employee": doc.employee,
#                 "leave_type": "Leave Without Pay",
#                 "from_date": new_from_date,
#                 "to_date": new_to_date,
#                 "description": "Auto-created LOP leave after 6-day leave starting on Monday",
#             })
#             new_leave.insert()
#             new_leave.submit()

@frappe.whitelist()
def create_new_lop(doc, method):
    if doc.leave_type == "Leave Without Pay":
        from_date = getdate(doc.from_date)
        to_date = getdate(doc.to_date)
        next_day = add_days(to_date, 1)

        if is_weeklyoff(doc.employee, next_day):
            if doc.docstatus == 0 and doc.get("__islocal"):
                frappe.msgprint("You were not present this week, so the Weekly Off (WW) is not eligible for you")
            
            if doc.workflow_state == "Approved":
                create_lop_application(
                    doc.employee,
                    next_day,
                    next_day,
                    "Auto-created LOP for Weekly Off after continuous LWP"
                )

def create_lop_application(employee, from_date, to_date, description):
    new_leave = frappe.get_doc({
        "doctype": "Leave Application",
        "employee": employee,
        "leave_type": "Leave Without Pay",
        "from_date": from_date,
        "to_date": to_date,
        "description": description,
    })
    new_leave.insert()
    new_leave.submit()

def is_weeklyoff(employee, date):
    """Check if the given date is a Weekoff for the employee"""
    shift_type = frappe.db.get_value("Shift Assignment",{
                                    "employee" : employee,
                                    "start_date": ("<=",date),
                                    "end_date" : (">=",date)
                                    },
                                    "shift_type")
    return shift_type == "WW"

@frappe.whitelist()
#return the last execution time of attendance cron
def update_last_execution():
    doc=frappe.db.get_value("Scheduled Job Log",{"scheduled_job_type":"mark_attendance.mark_att","status":"Complete"},["creation"])
    if doc:
        return doc
    

@frappe.whitelist()
def validate_comp_off(doc, method):
        user_roles = frappe.get_roles(frappe.session.user)
        hr = "Miss Punch Role" in user_roles
        # admin = "Administrator" in user_roles
        if (not hr):
            allowed_days = 1
            current_date = today()
            if isinstance(current_date, str):
                current_date = datetime.strptime(current_date, "%Y-%m-%d").date()

            def is_working_day(check_date):
                return not check_holiday(check_date, doc.employee)

            days_count = 0
            earliest_allowed = current_date
            while days_count < allowed_days:
                earliest_allowed = add_days(earliest_allowed, -1)
                if is_working_day(earliest_allowed):
                    days_count += 1

            if not doc.work_from_date:
                return

            if isinstance(doc.work_from_date, str):
                miss_date = datetime.strptime(doc.work_from_date, "%Y-%m-%d").date()
            else:
                miss_date = doc.work_from_date

            if miss_date < earliest_allowed:
                frappe.throw(
                    _("Compensatory Leave Request applications are allowed only for up to the previous {0} working days.")
                    .format(allowed_days)
                )

@frappe.whitelist()
def validate_leave(doc, method):
    user_roles = frappe.get_roles(frappe.session.user)
    hr = "Miss Punch Role" in user_roles
    # admin = "Administrator" in user_roles
    if (not hr):
        allowed_days = 1
        current_date = today()
        if isinstance(current_date, str):
            current_date = datetime.strptime(current_date, "%Y-%m-%d").date()

        def is_working_day(check_date):
            return not check_holiday(check_date, doc.employee)

        days_count = 0
        earliest_allowed = current_date
        while days_count < allowed_days:
            earliest_allowed = add_days(earliest_allowed, -1)
            if is_working_day(earliest_allowed):
                days_count += 1

        if not doc.to_date:
            return

        if isinstance(doc.to_date, str):
            miss_date = datetime.strptime(doc.to_date, "%Y-%m-%d").date()
        else:
            miss_date = doc.to_date

        if miss_date < earliest_allowed:
            frappe.throw(
                _("Leave applications are allowed only for up to the previous {0} working days.")
                .format(allowed_days)
            )
            
        
@frappe.whitelist()
def leave_application_rejection_remark(doc,method):
    
    ws = ''
    if doc.workflow_state == "Rejected":
            current_user = frappe.session.user
            user_role = frappe.get_roles(current_user)
            if "Level Approver 4" in user_role:
                ws = "Pending for Manager 3"
            elif "Level Approver 3" in user_role:
                ws = "Pending for Manager 2"
            elif "Level Approver 2" in user_role:
                ws = "Pending for Manager 1"
            elif "Level Approver 1" in user_role:   
                ws = "Pending for Manager"    
            if not doc.rejection_remark:
                        frappe.db.sql("""
                                    UPDATE `tabLeave Application`
                                    SET docstatus = 0, workflow_state = %s
                                    WHERE name = %s
                            """,(ws, doc.name),as_dict=True)
                        doc.reload()
            if doc.rejection_remark:
                    frappe.db.sql("""
                                UPDATE `tabLeave Application`
                                   SET docstatus = 1, workflow_state = 'Rejected'
                                   WHERE name = %s
                                """, (doc.name), as_dict=True)

@frappe.whitelist()
def mpr_rejection_remark(doc,method):
    
    ws = ''
    if doc.workflow_state == "Rejected":
            current_user = frappe.session.user
            user_role = frappe.get_roles(current_user)
            if "GM-HR" in user_role and "COO" not in user_role:
                ws = "Pending for GM-HR"
            elif "COO" in user_role:
                ws = "Pending for COO"    
            if not doc.rejection_remark:
                frappe.db.sql("""
                    UPDATE `tabManpower Request`
                    SET docstatus = 0, workflow_state = %s
                    WHERE name = %s
                    """,(ws, doc.name),as_dict=True)
                doc.reload()
            if doc.rejection_remark:
                frappe.db.sql("""
                    UPDATE `tabManpower Request`
                        SET docstatus = 1, workflow_state = 'Rejected'
                        WHERE name = %s
                    """, (doc.name), as_dict=True)

@frappe.whitelist()
def jr_rejection_remark(doc,method):
    
    ws = ''
    if doc.workflow_state == "Rejected":
            current_user = frappe.session.user
            user_role = frappe.get_roles(current_user)
            if "GM-HR" in user_role and "COO" not in user_role:
                ws = "Pending for GM-HR"
            elif "COO" in user_role:
                ws = "Pending for COO"    
            if not doc.rejection_remark:
                frappe.db.sql("""
                    UPDATE `tabJob Requisition`
                    SET docstatus = 0, workflow_state = %s
                    WHERE name = %s
                    """,(ws, doc.name),as_dict=True)
                doc.reload()
            if doc.rejection_remark:
                frappe.db.sql("""
                    UPDATE `tabJob Requisition`
                        SET docstatus = 1, workflow_state = 'Rejected'
                        WHERE name = %s
                    """, (doc.name), as_dict=True)                
            
@frappe.whitelist()            
def on_duty_application_rejection_remark(doc,method):
        
        ws =" "
        if doc.workflow_state == "Rejected":
            current_user = frappe.session.user
            user_role = frappe.get_roles(current_user)
            if "Level Approver 4" in user_role:
                ws = "Pending for Manager 3"
            elif "Level Approver 3" in user_role:
                ws = "Pending for Manager 2"
            elif "Level Approver 2" in user_role:
                ws = "Pending for Manager 1"
            elif "Level Approver 1" in user_role:   
                ws = "Pending for Manager"     
            if not doc.rejection_remark:
                        frappe.db.sql("""
                                    UPDATE `tabOn Duty Application`
                                    SET docstatus = 0, workflow_state = %s
                                    WHERE name = %s
                            """,(ws, doc.name),as_dict=True)
                        doc.reload()
            if doc.rejection_remark:
                    frappe.db.sql("""
                                UPDATE `tabOn Duty Application`
                                   SET docstatus = 1, workflow_state = 'Rejected'
                                   WHERE name = %s
                                """, (doc.name), as_dict=True)
                    
                    
                    
                    
@frappe.whitelist()
def miss_punch_application_rejection_remark(doc,method):
        
        ws =""
        if doc.workflow_state == "Rejected":
            current_user = frappe.session.user
            user_role = frappe.get_roles(current_user)
            if "Level Approver 4" in user_role:
                ws = "Pending for Manager 3"
            elif "Level Approver 3" in user_role:
                ws = "Pending for Manager 2"
            elif "Level Approver 2" in user_role:
                ws = "Pending for Manager 1"
            elif "Level Approver 1" in user_role:   
                ws = "Pending for Manager"    
            if not doc.rejection_remark:
                        frappe.db.sql("""
                                    UPDATE `tabMiss Punch Application`
                                    SET docstatus = 0, workflow_state = %s
                                    WHERE name = %s
                            """,(ws, doc.name),as_dict=True)
                        doc.reload()
            if doc.rejection_remark:
                    frappe.db.sql("""
                                UPDATE `tabMiss Punch Application`
                                   SET docstatus = 1, workflow_state = 'Rejected'
                                   WHERE name = %s
                                """, (doc.name), as_dict=True)
                    
            
            
@frappe.whitelist()
def compensatory_leave_request_rejection_remark(doc,method):
        ws = ''
        if doc.workflow_state == "Rejected":
            current_user = frappe.session.user
            user_role = frappe.get_roles(current_user)
            if "Level Approver 4" in user_role:
                ws = "Pending for Manager 3"
            elif "Level Approver 3" in user_role:
                ws = "Pending for Manager 2"
            elif "Level Approver 2" in user_role:
                ws = "Pending for Manager 1"
            elif "Level Approver 1" in user_role:   
                ws = "Pending for Manager"     
            if not doc.rejection_remark:
                        frappe.db.sql("""
                                    UPDATE `tabCompensatory Leave Request`
                                    SET docstatus = 0, workflow_state = %s
                                    WHERE name = %s
                            """,(ws, doc.name),as_dict=True)
                        doc.reload()
            if doc.rejection_remark:
                    frappe.db.sql("""
                                UPDATE `tabCompensatory Leave Request`
                                   SET docstatus = 1, workflow_state = 'Rejected'
                                   WHERE name = %s
                                """, (doc.name), as_dict=True)
@frappe.whitelist()
def over_time_rejection_remark(doc,method):
        ws =""
        if doc.workflow_state == "Rejected":
            current_user = frappe.session.user
            user_role = frappe.get_roles(current_user)
            if "Supervisor" in user_role:
                        ws = "Pending for Manager"
            elif "HOD" in user_role:
                    ws = "Pending for Manager 1"
            if not doc.rejection_remark:
                        frappe.db.sql("""
                                    UPDATE `tabOver Time`
                                    SET docstatus = 0, workflow_state = %s
                                    WHERE name = %s
                            """,(ws, doc.name),as_dict=True)
                        doc.reload()
            if doc.rejection_remark:
                    frappe.db.sql("""
                                UPDATE `tabOver Time`
                                   SET docstatus = 1, workflow_state = 'Rejected'
                                   WHERE name = %s
                                """, (doc.name), as_dict=True)
@frappe.whitelist()
def shift_request_rejection_remark(doc,method):
    ws = ''
    if doc.workflow_state == "Rejected":
        current_user = frappe.session.user
        user_role = frappe.get_roles(current_user)
        if "Supervisor" in user_role:
                    ws = "Pending for Manager"
        elif "HOD" in user_role:
                ws = "Pending for Manager 1"
                
        if not doc.rejection_remark:
                    frappe.db.sql("""
                                UPDATE `tabShift Request`
                                SET docstatus = 0, workflow_state = %s
                                WHERE name = %s
                        """,(ws, doc.name),as_dict=True)
                    doc.reload()
        if doc.rejection_remark:
                frappe.db.sql("""
                            UPDATE `tabShift Request`
                                SET docstatus = 1, workflow_state = 'Rejected'
                                WHERE name = %s
                            """, (doc.name), as_dict=True)
                
                
                
@frappe.whitelist()
def resignation_form_rejection_remark(doc,method):
        
        ws = ""
        if doc.workflow_state == "Rejected":
            current_user = frappe.session.user
            user_role = frappe.get_roles(current_user)
            if "HOD" in user_role:
                        ws = "Pending for Manager"
            elif "HR" in user_role:
                    ws = "Pending for Manager 1"
            elif "COO" in user_role:
                    ws = "Pending for Manager 2"
                 
            if not doc.rejection_remark:
                        frappe.db.sql("""
                                    UPDATE `tabResignation Form`
                                    SET docstatus = 0, workflow_state = %s
                                    WHERE name = %s
                            """,(ws, doc.name),as_dict=True)
                        doc.reload()
            if doc.rejection_remark:
                    frappe.db.sql("""
                                UPDATE `tabResignation Form`
                                   SET docstatus = 1, workflow_state = 'Rejected'
                                   WHERE name = %s
                                """, (doc.name), as_dict=True)
                

@frappe.whitelist()
def expense_claim_rejection_remark(doc,method):
    ws = ""
    if doc.workflow_state == "Rejected":
        current_user = frappe.session.user
        user_role = frappe.get_roles(current_user)
        if "HR User" in user_role:
                    ws = "Pending for HR"
        elif "HR Manager" in user_role:
                ws = "Pending for HR Head"
        elif "Expense Approver" in user_role:
                ws = "Pending for Expense Approver"
        elif "COO" in user_role:   
                ws = "Pending for COO"     
        if not doc.rejection_remark:
                    frappe.db.sql("""
                                UPDATE `tabExpense Claim`
                                SET docstatus = 0, workflow_state = %s
                                WHERE name = %s
                        """,(ws, doc.name),as_dict=True)
                    doc.reload()
        if doc.rejection_remark:
                frappe.db.sql("""
                            UPDATE `tabExpense Claim`
                            SET docstatus = 1, workflow_state = 'Rejected'
                            WHERE name = %s
                            """, (doc.name), as_dict=True)
        

@frappe.whitelist()
def sending_mail(doc,method):
    if doc.status == "Accepted":
        frappe.sendmail(recipients=doc.job_applicant,subject="Offer Letter - reg",content=f"Dear {doc.applicant_name},<br>Please refer the above attached offer letter.",attachments = [frappe.attach_print("Job Offer", doc.name, file_name='Job  Offer', print_format="Job Offer Format")])

@frappe.whitelist()
def shift_overlap_update(doc, method):
    employee = doc.employee
    shift_to_check = doc.shift_type
    from_date = datetime.strptime(doc.from_date, "%Y-%m-%d").date()
    check_start_date = from_date - timedelta(days=15)

    shift_assignments = frappe.db.sql("""
        SELECT shift_type, start_date
        FROM `tabShift Assignment`
        WHERE docstatus != 2
        AND employee = %s
        AND start_date BETWEEN %s AND %s
        ORDER BY start_date
    """, (employee, check_start_date, from_date - timedelta(days=1)), as_dict=True)

    
    consecutive_days = 0
    expected_date = check_start_date

    for day in range(15):
        matching = next((s for s in shift_assignments if s['start_date'] == expected_date and s['shift_type'] == shift_to_check), None)
        if matching:
            consecutive_days += 1
        else:
            break  

        expected_date += timedelta(days=1)

    if consecutive_days == 15 and shift_to_check in ["B", "C"]:
        frappe.throw(f"Shift Request not allowed: Employee {employee} already has shift '{shift_to_check}' for 15 continuous days.")

@frappe.whitelist()
def create_job_fail():
    job = frappe.db.exists('Scheduled Job Type', 'cron_failed')
    if not job:
        emc = frappe.new_doc("Scheduled Job Type")
        emc.update({
            "method": 'gplast.custom.cron_failed_method',
            "frequency": 'Cron',
            "cron_format": '*/5 * * * *'
        })
        emc.save(ignore_permissions=True)

@frappe.whitelist()
def cron_failed_method():
    cutoff_time = datetime.now() - timedelta(minutes=5)
    failed_jobs = frappe.get_all(
        "Scheduled Job Log",
        filters={
            "status": "Failed",
            "creation": [">=", cutoff_time]
        },
        fields=["scheduled_job_type"]
    )
    unique_job_types = set()
    for job in failed_jobs:
        unique_job_types.add(job['scheduled_job_type'])

    for job_type in unique_job_types:
        frappe.sendmail(
            recipients = ["erp@groupteampro.com","jeniba.a@groupteampro.com","sivarenisha.m@groupteampro.com"],
            subject = 'Failed Cron List - GPLAST',
            message = 'Dear Sir / Mam <br> Kindly find the below failed Scheduled Job  %s'%(job_type)
        )

# import frappe

# def update_other_allowance(doc, method):
#     doc.other_allowance = (
#         (doc.conveyance_allowance or 0)
#         + (doc.medical_allowances or 0)
#         + (doc.ta_allowance or 0)
#         + (doc.education_allowance or 0)
#         + (doc.fvo_allowance or 0)
#         + (doc.help_allowance or 0)
#         + (doc.accommodation_allowance or 0)
#         + (doc.uniform_allowance or 0)
#         + (doc.magazine_allowances or 0)
#     )
#     doc.salary_total = (
#         (doc.basic or 0)
#         + (doc.cca or 0)
#         + (doc.house_rent_allowance or 0)
#         + (doc.special_allowance or 0)
#         + (doc.shift_allowance or 0)
#         + (doc.conveyance_allowance or 0)
#         + (doc.medical_allowances or 0)
#         + (doc.ta_allowance or 0)
#         + (doc.education_allowance or 0)
#         + (doc.fvo_allowance or 0)
#         + (doc.help_allowance or 0)
#         + (doc.accommodation_allowance or 0)
#         + (doc.uniform_allowance or 0)
#         + (doc.magazine_allowances or 0)
#     )

@frappe.whitelist()
def create_job_for_MPR():
    job = frappe.db.exists('Scheduled Job Type', 'update_employee_from_mpr')
    if not job:
        emc = frappe.new_doc("Scheduled Job Type")
        emc.update({
            "method": 'gplast.custom.update_employee_mis_from_mpr',
            "frequency": 'Cron',
            "cron_format": '*/5 * * * *'
        })
        emc.save(ignore_permissions=True)


@frappe.whitelist()
def update_employee_mis_from_mpr():
    mpr_list = frappe.get_all(
        "Manpower Request",
        filters={
            "workflow_state": "Approved",
            "filled_by": ["!=", "New Candidate"],
        },
        fields=["name", "employee_id", "effective_from", "approved_date",
                "new_department", "new_designation", "new_designation_code"]
    )

    today = getdate(nowdate())

    for mpr in mpr_list:
        eff_date = getdate(mpr.effective_from)
        app_date = getdate(mpr.approved_date)

        if eff_date > app_date:
            mis_update_date = eff_date

        elif eff_date < app_date:
            mis_update_date = today

        else:
            mis_update_date = app_date

        if mis_update_date == today:
            update_employee_mis(mpr)

    frappe.db.commit()


def update_employee_mis(mpr):
    if not frappe.db.exists("Employee", mpr.employee_id):
        frappe.log_error(f"Employee not found: {mpr.employee_id}", "MPR Scheduler Error")
        return

    frappe.db.set_value("Employee", mpr.employee_id, {
        "department": mpr.new_department,
        "designation": mpr.new_designation,
        "designation_code": mpr.new_designation_code
    })



import frappe
from frappe.utils import now_datetime, convert_utc_to_user_timezone
from datetime import datetime
import pytz
def store_workflow_stage_time(doc, event):

    # now = frappe.utils.now()
    # now = frappe.utils.now_datetime()
    now = now_datetime() - timedelta(minutes=24)
    current_state = doc.workflow_state

    user = frappe.session.user

    employee_id = frappe.db.get_value("Employee", {"user_id": user}, "name")

    if current_state == "Pending for Manager":
        doc.wf_for_preview = "Preview"
        doc.application_date_ = now
        doc.preview_approver = employee_id

    elif current_state == "Pending for Manager 1":
        doc.wf_for_pending_manager = "Pending for Manager"
        doc.approved_date_for_pending_manager = now
        doc.level_1_approver = employee_id

    elif current_state == "Pending for Manager 2":
        doc.wf_for_pending_manager_1 = "Pending for Manager 1"
        doc.approved_date_for_pending_manager_1 = now
        doc.level_2_approver = employee_id

    elif current_state == "Pending for Manager 3":
        doc.wf_for_pending_manager_2 = "Pending for Manager 2"
        doc.approved_date_for_pending_manager_2 = now
        doc.level_3_approver = employee_id

    elif current_state == "Approved":
        if doc.level_3_approver :
            doc.wf_for_pending_manager_3 = "Approved"
            doc.approved_date_for_pending_manager_3 = now
            doc.level_4_approver = employee_id
        elif doc.level_2_approver :
            doc.wf_for_pending_manager_2 = "Approved"
            doc.approved_date_for_pending_manager_2 = now
            doc.level_3_approver = employee_id
        elif doc.level_1_approver:
            doc.wf_for_pending_manager_1 = "Approved"
            doc.approved_date_for_pending_manager_1 = now
            doc.level_2_approver = employee_id
        elif doc.preview_approver:
            doc.wf_for_pending_manager = "Approved"
            doc.approved_date_for_pending_manager = now
            doc.level_1_approver = employee_id

    elif current_state == "Rejected":
        if doc.level_3_approver :
            doc.wf_for_pending_manager_3 = "Rejected"
            doc.approved_date_for_pending_manager_3 = now
            doc.level_4_approver = employee_id
        elif doc.level_2_approver :
            doc.wf_for_pending_manager_2 = "Rejected"
            doc.approved_date_for_pending_manager_2 = now
            doc.level_3_approver = employee_id
        elif doc.level_1_approver:
            doc.wf_for_pending_manager_1 = "Rejected"
            doc.approved_date_for_pending_manager_1 = now
            doc.level_2_approver = employee_id
        elif doc.preview_approver:
            doc.wf_for_pending_manager = "Rejected"
            doc.approved_date_for_pending_manager = now
            doc.level_1_approver = employee_id
    doc.db_update()


@frappe.whitelist()
def create_job_for_esi():
    job = frappe.db.exists('Scheduled Job Type', 'update_employee_for_esi')
    if not job:
        emc = frappe.new_doc("Scheduled Job Type")
        emc.update({
            "method": 'gplast.custom.send_esi_mail',
            "frequency": 'Cron',
            "cron_format": "0 10 21-31 4,10 *"
        })
        emc.save(ignore_permissions=True)

import frappe
from frappe.utils import getdate, today
from datetime import date
from calendar import monthrange


def send_esi_mail():
    today_date = getdate(today())
    month = today_date.month
    year = today_date.year
    day = today_date.day

    if month not in (4, 10):
        return
    if day < 21:
        return
    # if month not in (4, 12):
    #     return
    # if day < 15:
    #     return

    if month == 4:
        from_month = 10
        from_year = year - 1
        to_month = 3
        to_year = year
    else: 
        from_month = 4
        from_year = year
        to_month = 9
        to_year = year
    # else: 
    #     from_month = 4
    #     from_year = year
    #     to_month = 12
    #     to_year = year

    from_date = date(from_year, from_month, 1)
    to_date = date(to_year, to_month, monthrange(to_year, to_month)[1])

    employees = frappe.db.sql("""
        SELECT
            si.employee,
            si.employee_name,
            DATE(si.creation) AS increment_date
        FROM `tabSalary Increment` si
        INNER JOIN `tabEmployee` e ON e.name = si.employee
        WHERE
            si.docstatus = 1
            AND DATE(si.creation) BETWEEN %s AND %s
            AND e.esi_eligibility = 'Yes'
        ORDER BY si.creation
    """, (from_date, to_date), as_dict=True)

    if not employees:
        return

    rows = ""
    for i, emp in enumerate(employees, 1):
        increment_date = frappe.db.get_value('Salary Increment', 
                                     {'employee': emp.employee, 'docstatus': 1}, 
                                     'creation')
        rows += f"""
            <tr>
                <td>{i}</td>
                <td>{emp.employee}</td>
                <td>{emp.employee_name}</td>
                <td>{formatdate(increment_date)}</td>
            </tr>
        """

    message = f"""
        <p>Dear Team,</p>

        <p>
            Please find below the list of employees whose
            <b>salary increment was submitted between {formatdate(from_date)} and {formatdate(to_date)}</b>
            and who are <b>ESI eligible</b>.
        </p>

        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>S.No</th>
                <th>Employee</th>
                <th>Employee Name</th>
                <th>Increment Date</th>
            </tr>
            {rows}
        </table>

        
    """

    frappe.sendmail(
        # recipients=["jeniba.a@groupteampro.com","hrd@gplast.com","karthick.k@gplast.com","kumaresan@gplast.com"],  
        recipients=["sivarenisha.m@groupteampro.com"],
        subject="ESI Salary Increment Eligible Employees",
        message=message
    )

    frappe.db.commit()

@frappe.whitelist()
def set_esi_end_date(doc, method):
        """
        If ESI Eligibility changed to NO,
        set ESI End Date as current date
        """

        # Run only if document already exists (update case)
        if not doc.is_new():

            old_esi = frappe.db.get_value(
                "Employee",
                doc.name,
                "esi_eligibility"
            )

            # If changed from Yes → No
            if old_esi == "Yes" and doc.esi_eligibility == "No":

                # Set end date only if not already set
                if not doc.esi_end_date:
                    doc.esi_end_date = today()