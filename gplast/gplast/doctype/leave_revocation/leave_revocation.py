# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.document import Document
import frappe
from frappe.model.document import Document
from frappe.utils import now
from frappe.utils import now, getdate,date_diff,add_days
from datetime import timedelta
import datetime
from frappe.utils.data import ceil, get_time, get_year_start
from datetime import date, timedelta,time
from frappe import _
from gplast.mark_attendance import get_dates,mark_att_with_employee_enqueue
from hrms.hr.doctype.leave_application.leave_application import get_number_of_leave_days
class LeaveRevocation(Document):
    def validate(self):
        dates=get_dates(self.from_date,self.to_date)
        for date in dates:
            hh=check_holiday(self.employee,date)
            if not hh:
                checkins = frappe.db.sql("""
                    SELECT * FROM `tabEmployee Checkin` 
                    WHERE employee = %s 
                    AND date(time) BETWEEN %s AND %s
                """, (self.employee, date, date), as_dict=1)
                if not checkins:
                    frappe.throw(_(f"Checkins are not available for {date}"))
        rev_from = self.from_date
        rev_to = self.to_date
        employee_id = self.employee
        overlapping_leaves = frappe.db.sql("""
            SELECT
                name, from_date, to_date, leave_type
            FROM
                `tabLeave Application`
            WHERE
                employee = %s AND docstatus = 1 AND workflow_state = 'Approved'
                AND (
                    (from_date <= %s AND to_date >= %s)
                    OR (from_date BETWEEN %s AND %s)
                    OR (to_date BETWEEN %s AND %s)
                    OR (%s BETWEEN from_date AND to_date)
                    OR (%s BETWEEN from_date AND to_date)
                )
        """, (
            employee_id, getdate(self.from_date), getdate(self.to_date),
            getdate(self.from_date), getdate(self.to_date),
            getdate(self.from_date), getdate(self.to_date),
            getdate(self.from_date), getdate(self.to_date)
        ), as_dict=True)

        for leave in overlapping_leaves:
            if (getdate(leave.from_date) < getdate(self.from_date) and getdate(leave.to_date) > getdate(self.to_date)):
                frappe.throw(_("Revocation cannot be applied for mid-days. Please revoke from the start or end of a leave period."))
            if getdate(self.from_date) < (getdate(leave.from_date) ):
                frappe.throw(_(f"From date must be greater than or equal to the {leave.from_date}"))
            if getdate(self.to_date) > getdate(leave.to_date)  :
                frappe.throw(_(f"To date must be less than or equal to the {leave.to_date}"))
            
        if not overlapping_leaves:
            frappe.throw(_(f"Leave application not available between {self.from_date} and {self.to_date}"))
    def on_submit(self):
        rev_from = getdate(self.from_date)
        rev_to = getdate(self.to_date)
        employee_id = self.employee

        dates=get_dates(self.from_date,self.to_date)
        for date in dates:
            hh=check_holiday(self.employee,date)
            if not hh:
                checkins = frappe.db.sql("""
                    SELECT * FROM `tabEmployee Checkin` 
                    WHERE employee = %s 
                    AND date(time) BETWEEN %s AND %s
                """, (self.employee, date, date), as_dict=1)
                if not checkins:
                    frappe.throw(_(f"Checkins are not available for {date}"))

        overlapping_leaves = frappe.db.sql("""
            SELECT name, from_date, to_date, leave_type
            FROM `tabLeave Application`
            WHERE employee = %s AND docstatus = 1 AND workflow_state='Approved'
            AND (
                (from_date BETWEEN %s AND %s)
                OR (to_date BETWEEN %s AND %s)
                OR (%s BETWEEN from_date AND to_date)
                OR (%s BETWEEN from_date AND to_date)
            )
        """, (employee_id, rev_from, rev_to, rev_from, rev_to, rev_from, rev_to), as_dict=True)

        if not overlapping_leaves:
            frappe.throw(_("No approved leave applications found in the revocation period."))
        for leave in overlapping_leaves:
            original_from = getdate(leave.from_date)
            original_to = getdate(leave.to_date)
            if rev_from > original_from and rev_to < original_to:
                frappe.throw(_("Revocation period lies inside a leave. Manual adjustment required."))
            if rev_to < original_from or rev_from > original_to:
                continue 
            if rev_from <= original_from and rev_to >= original_to:
                frappe.throw(_("Revocation period completely overlaps the leave. Cannot fully revoke. Please cancel manually."))            
            if rev_from <= original_from:
                new_from = add_days(rev_to, 1)
                new_to = original_to
            elif rev_to >= original_to:
                new_from = original_from
                new_to = add_days(rev_from, -1)
            else:
                frappe.throw(_("Unsupported case: Revocation in the middle. Please split manually."))
            if new_from > new_to:
                frappe.throw(_("Invalid date range after revocation. Nothing to update."))

            #Update leave application
            leave_doc = frappe.get_doc("Leave Application", leave.name)
            leave_days = get_number_of_leave_days(leave_doc.employee, leave_doc.leave_type,new_from, new_to, leave_doc.half_day,leave_doc.half_day_date)
            leave_doc.from_date = new_from
            leave_doc.to_date = new_to
            leave_doc.total_leave_days = leave_days
            leave_doc.leave_revocation=self.name
            leave_doc.db_update()

            # Update ledger 
            ledger_entries = frappe.get_all("Leave Ledger Entry", filters={
                "transaction_name": leave.name,
                "transaction_type": "Leave Application"
            })

            for entry in ledger_entries:
                frappe.db.set_value("Leave Ledger Entry", entry.name, {
                    "from_date": new_from,
                    "to_date": new_to,
                    "leaves": -leave_doc.total_leave_days
                })

            dates=get_dates(self.from_date,self.to_date)
            for date in dates:
                hh=check_holiday(self.employee,date)
                if not hh:
                    if frappe.db.exists("Attendance",{'attendance_date':getdate(date),'docstatus':['!=',2],'leave_application':leave.name}):
                        attendance=frappe.db.get_value("Attendance",{'attendance_date':getdate(date),'docstatus':['!=',2],'leave_application':leave.name},['name'])
                        att=frappe.get_doc("Attendance",attendance)
                        att.leave_application=''
                        att.leave_type=''
                        att.status='Absent'
                        att.leave_revocation=self.name
                        att.save(ignore_permissions=True)
                        mark_att_with_employee_enqueue(date,date,self.employee)

@frappe.whitelist()
def check_holiday(emp,date):
    holiday_list = frappe.db.get_value('Employee',emp,'holiday_list')
    holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
    left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
    if holiday:
        if holiday[0].weekly_off == 1:
            return "WW"
        else:
            return "HH"
    else:
        if frappe.db.exists("Shift Assignment",{'employee':emp,'start_date':getdate(date),'shift_type':'WW','docstatus':1}):
            return "WW" 
        