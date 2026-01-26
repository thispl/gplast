# Copyright (c) 2023, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import time
from datetime import datetime, timedelta
from frappe.utils import date_diff,add_days,time_diff_in_hours,time_diff
from frappe.utils import formatdate
from datetime import datetime,timedelta,date
from gplast.mark_attendance import mark_att_with_employee
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,datetime,get_first_day,get_last_day,today)
from datetime import datetime
import datetime as dt
from frappe import _

class OnDutyApplication(Document):
    # pass
    
    
    
    
    
    
    def after_insert(self):
        self.previous_workflow_state ='Preview'

        user_roles = frappe.get_roles(frappe.session.user)
        hr = "Miss Punch Role" in user_roles
        admin = "Administrator" in user_roles
        if (not hr):
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

            if not self.to_date:
                return

            if isinstance(self.to_date, str):
                miss_date = datetime.strptime(self.to_date, "%Y-%m-%d").date()
            else:
                miss_date = self.to_date

            if miss_date < earliest_allowed:
                frappe.throw(
                    _("OD applications are allowed only for up to the previous {0} working days.")
                    .format(allowed_days)
                )
        # current_date=today()
        # diff=date_diff(current_date,self.to_date)
        # if diff>1:
            # frappe.throw("OD request should be raised within the next day itself. Old dates are not allowed.")

    def validate(self):
        doctype = self.doctype
        old_state = frappe.db.get_value(doctype, self.name, "workflow_state")

        if old_state and old_state != self.workflow_state:
            self.previous_approval_date = today()
        dublicate_docs =frappe.db.sql("""
                select name
                from `tabOn Duty Application`
                where docstatus != 2 and employee = %(employee)s and name != %(name)s
                    and (from_date between %(from_date)s and %(to_date)s
                        or to_date between %(from_date)s and %(to_date)s
                        or (from_date < %(from_date)s and to_date > %(to_date)s))
                """, {
                    "from_date": self.from_date,
                    "to_date": self.to_date,
                    "employee":self.employee,
                    'name':self.name
                },
            as_dict = True)
        # frappe.errprint(dublicate_docs)
        if len(dublicate_docs) > 0:
            formatted_date = formatdate(self.from_date, "dd-mm-yyyy")
            frappe.throw(f'On Duty Application for employee {self.employee} is already marked for the date {formatted_date}')
    
        # current_date=today()
        # diff=date_diff(current_date,self.to_date)
        # if diff>1:
        #     frappe.throw("OD request should be raised within the next day itself. Old dates are not allowed.")
        if self.shift:
            shift_type = frappe.get_doc("Shift Type", self.shift)
            if self.session == "First Half":
                self.from_time = shift_type.start_time
        if self.workflow_state == "Approved":
            dates= get_dates_between(self.from_date, self.to_date)
            for date in dates:
                frappe.db.set_value("Attendance", {"attendance_date": date, "employee": self.employee}, "on_duty_application", self.name)
    def before_submit(self):
        self.approved_on = frappe.utils.today()
        
    def on_submit(self):
        if self.workflow_state=="Approved":
            if self.shift and self.from_date and self.to_date and self.session:
                total_working_hours =0.0
                if isinstance(self.from_time, str):
                    try:
                        start_time = datetime.strptime(self.from_time, "%H:%M:%S")
                    except ValueError:
                        start_time = datetime.strptime(self.from_time, "%H:%M")
                else:
                    total_seconds = int(self.from_time.total_seconds())
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
                    start_time = datetime.strptime(time_str, "%H:%M:%S")
                frappe.errprint(self.to_time)
                if isinstance(self.to_time, str):
                    frappe.errprint(self.to_time)
                    try:
                        end_time = datetime.strptime(self.to_time, "%H:%M:%S")
                    except ValueError:
                        end_time = datetime.strptime(self.to_time, "%H:%M")
                else:
                    total_seconds = int(self.to_time.total_seconds())
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
                    end_time = datetime.strptime(time_str, "%H:%M:%S")

                time_difference = end_time - start_time
                frappe.errprint(time_difference)
                total_seconds = time_difference.total_seconds()
                formatted_total_hours =round((total_seconds/3600),1)
                frappe.errprint(total_seconds/3600)
                no_of_days = date_diff(add_days(self.to_date, 1),self.from_date )
                dates = [add_days(self.from_date, i) for i in range(0, no_of_days)]
                for date in dates:
                    attendance = frappe.db.exists("Attendance", {
                        "employee": self.employee,
                        "attendance_date": date
                    })
                    if attendance:
                        attendance_doc = frappe.get_doc("Attendance", attendance)
                        frappe.errprint(attendance_doc)
                        if self.session == 'Flexible':
                            frappe.errprint('Flexible')
                            if attendance_doc.total_working_hours:
                                total_working_hours = attendance_doc.total_working_hours 
                                total_working_hours += formatted_total_hours
                            else:
                                total_working_hours = formatted_total_hours
                            total_working_hours = float(total_working_hours)
                            frappe.errprint(total_working_hours)
                            if total_working_hours >= 8:
                                attendance_doc.status = "Present"
                            elif 4 <= total_working_hours <8:
                                attendance_doc.status = "Half Day"
                            else:
                                attendance_doc.status = "Absent"
                            frappe.errprint(attendance_doc.status)
                        if self.session == "Full Day":
                            frappe.errprint("Full day")
                            if attendance_doc.total_working_hours:
                                total_working_hours = attendance_doc.total_working_hours 
                                total_working_hours += formatted_total_hours
                            else:
                                total_working_hours = formatted_total_hours
                            attendance_doc.status = "Present"
                        if self.session == "First Half":
                            if attendance_doc.total_working_hours:
                                total_working_hours = attendance_doc.total_working_hours 
                                total_working_hours += formatted_total_hours
                            else:
                                total_working_hours = formatted_total_hours
                            total_working_hours = float(total_working_hours)
                            if total_working_hours >= 8:
                                attendance_doc.status = "Present"
                            elif 4 <= total_working_hours <8:
                                attendance_doc.status = "Half Day"
                            else:
                                attendance_doc.status = "Absent"
                        if self.session == "Second Half":
                            if attendance_doc.total_working_hours:
                                total_working_hours = attendance_doc.total_working_hours 
                                total_working_hours += formatted_total_hours
                            else:
                                total_working_hours = formatted_total_hours
                            total_working_hours = float(total_working_hours)
                            if total_working_hours >= 8:
                                attendance_doc.status = "Present"
                            elif 4 <= total_working_hours <8:
                                attendance_doc.status = "Half Day"
                            else:
                                attendance_doc.status = "Absent"
                        attendance_doc.on_duty_application = self.name
                        attendance_doc.session_from_time = self.from_time
                        attendance_doc.session_to_time = self.to_time
                        attendance_doc.shift = self.shift
                        attendance_doc.save(ignore_permissions=True)
                    else:
                        attendance_doc = frappe.new_doc("Attendance")
                        attendance_doc.employee = self.employee
                        attendance_doc.attendance_date = date
                        if self.session == 'Flexible':
                            total_working_hours = formatted_total_hours
                            total_working_hours = float(total_working_hours)
                            if total_working_hours >= 8:
                                attendance_doc.status = "Present"
                            elif 4 <= total_working_hours <8:
                                attendance_doc.status = "Half Day"
                            else:
                                attendance_doc.status = "Absent"
                        total_working_hours = formatted_total_hours
                        total_working_hours = float(total_working_hours)
                        if self.session == "Full Day":
                            attendance_doc.status = "Present"
                        if self.session == "First Half":
                            attendance_doc.status = "Half Day"
                        if self.session == "Second Half":
                            attendance_doc.status = "Half Day"
                        attendance_doc.on_duty_application = self.name
                        attendance_doc.session_from_time = self.from_time
                        attendance_doc.session_to_time = self.to_time
                        attendance_doc.shift = self.shift
                        attendance_doc.save(ignore_permissions=True)
                    mark_att_with_employee(date,date,self.employee) 
    def on_cancel(self):
        # Fetch the attendance document linked with the custom on duty application
        no_of_days = date_diff(add_days(self.to_date, 1),self.from_date )
        dates = [add_days(self.from_date, i) for i in range(0, no_of_days)]
        for date in dates:
            if frappe.db.exists("Attendance",{"attendance_date":date,'employee':self.employee,'docstatus':("!=",2)}):
                att=frappe.get_doc("Attendance",{"attendance_date":date,'employee':self.employee,'docstatus':("!=",2)})
                frappe.db.set_value("Attendance",att.name,"on_duty_application",'')
                frappe.db.set_value("Attendance",att.name,"shift",self.shift)
                frappe.db.set_value("Attendance",att.name,"session_from_time","00:00:00")
                frappe.db.set_value("Attendance",att.name,"session_to_time","00:00:00")
                if att.in_time and att.out_time:
                    mark_att_with_employee(date,date,self.employee)  
                else:
                    frappe.db.set_value("Attendance",att.name,"status",'Absent')
                    frappe.db.set_value('Attendance', att.name, 'total_working_hours', "0.0")
                    frappe.db.set_value('Attendance', att.name, 'overtime_hours', "0.0")
            
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
def get_time(shift,session):
    datalist = []
    data = {}
    if shift == 'A':
        get_session_st_time = frappe.db.get_value('Shift Type',{'name':shift},['start_time'])
        get_session_ed_time = frappe.db.get_value('Shift Type',{'name':shift},['end_time'])
        if session == 'Full Day':
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':get_session_ed_time    
            })
            datalist.append(data.copy())
        elif session == 'First Half' :
            gt = get_session_st_time + timedelta(hours=4)
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':gt
            })
            datalist.append(data.copy())
        elif session == 'Second Half' :
            gc =  get_session_ed_time - timedelta(hours=4)
            data.update({
                'get_session_st_time':gc,
                'get_session_ed_time':get_session_ed_time
            })
            datalist.append(data.copy()) 
    if shift == 'B':
        get_session_st_time = frappe.db.get_value('Shift Type',{'name':shift},['start_time'])
        get_session_ed_time = frappe.db.get_value('Shift Type',{'name':shift},['end_time'])
        if session == 'Full Day':
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':get_session_ed_time    
            })
            datalist.append(data.copy())
        elif session == 'First Half' :
            gt = get_session_st_time + timedelta(hours=4)
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':gt
            })
            datalist.append(data.copy())
        elif session == 'Second Half' :
            gc =  get_session_ed_time - timedelta(hours=4)
            data.update({
                'get_session_st_time':gc,
                'get_session_ed_time':get_session_ed_time
            })
            datalist.append(data.copy()) 
    

    if shift == 'C':
        get_session_st_time = frappe.db.get_value('Shift Type',{'name':shift},['start_time'])
        get_session_ed_time = frappe.db.get_value('Shift Type',{'name':shift},['end_time'])
        if session == 'Full Day':
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':get_session_ed_time    
            })
            datalist.append(data.copy())
        elif session == 'First Half' :
            gt = get_session_st_time + timedelta(hours=4)
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':gt
            })
            datalist.append(data.copy())
        elif session == 'Second Half' :
            gc =  get_session_ed_time - timedelta(hours=4)
            data.update({
                'get_session_st_time':gc,
                'get_session_ed_time':get_session_ed_time
            })
            datalist.append(data.copy()) 
   
    if shift == 'G':
        get_session_st_time = frappe.db.get_value('Shift Type',{'name':shift},['start_time'])
        get_session_ed_time = frappe.db.get_value('Shift Type',{'name':shift},['end_time'])
        if session == 'Full Day':
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':get_session_ed_time    
            })
            datalist.append(data.copy())
        elif session == 'First Half' :
            gt = get_session_st_time + timedelta(hours=4,minutes=25)
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':gt
            })
            datalist.append(data.copy())
        elif session == 'Second Half' :
            gc =  get_session_ed_time - timedelta(hours=4,minutes=25)
            data.update({
                'get_session_st_time':gc,
                'get_session_ed_time':get_session_ed_time
            })
            datalist.append(data.copy()) 
        frappe.errprint(f" Data {datalist}")

    if shift == 'G1':
        get_session_st_time = frappe.db.get_value('Shift Type',{'name':shift},['start_time'])
        get_session_ed_time = frappe.db.get_value('Shift Type',{'name':shift},['end_time'])
        if session == 'Full Day':
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':get_session_ed_time    
            })
            datalist.append(data.copy())
        elif session == 'First Half' :
            gt = get_session_st_time + timedelta(hours=4,minutes=25)
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':gt
            })
            datalist.append(data.copy())
        elif session == 'Second Half' :
            gc =  get_session_ed_time - timedelta(hours=4,minutes=25)
            data.update({
                'get_session_st_time':gc,
                'get_session_ed_time':get_session_ed_time
            })
            datalist.append(data.copy()) 
    
    if shift == 'GE':
        get_session_st_time = frappe.db.get_value('Shift Type',{'name':shift},['start_time'])
        get_session_ed_time = frappe.db.get_value('Shift Type',{'name':shift},['end_time'])
        if session == 'Full Day':
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':get_session_ed_time    
            })
            datalist.append(data.copy())
        elif session == 'First Half' :
            gt = get_session_st_time + timedelta(hours=4,minutes=25)
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':gt
            })
            datalist.append(data.copy())
        elif session == 'Second Half' :
            gc =  get_session_ed_time - timedelta(hours=4,minutes=25)
            data.update({
                'get_session_st_time':gc,
                'get_session_ed_time':get_session_ed_time
            })
            datalist.append(data.copy()) 
    else: 
        get_session_st_time = frappe.db.get_value('Shift Type',{'name':shift},['start_time'])
        get_session_ed_time = frappe.db.get_value('Shift Type',{'name':shift},['end_time'])
        if session == 'Full Day':
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':get_session_ed_time,    
            })
            datalist.append(data.copy())
        elif session == 'First Half' :
            gt = get_session_st_time + timedelta(hours=3,minutes=10) 
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':gt
            })
            datalist.append(data.copy())
        elif session == 'Second Half' :
            gc = get_session_ed_time - timedelta(hours=3,minutes=10)
            data.update({
                'get_session_st_time':gc,
                'get_session_ed_time':get_session_ed_time
            })
            datalist.append(data.copy())   
    return datalist

@frappe.whitelist()
def get_time_diff(from_time,to_time):
    total_hours = time_diff_in_hours(to_time,from_time)
    return total_hours



@frappe.whitelist()
def get_from_time_and_to_time(shift, session, from_date, to_date):
    
    if isinstance(from_date, str):
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
    if isinstance(to_date, str):
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
    start_time = frappe.db.get_value('Shift Type', {'name': shift}, ['start_time'])
    end_time = frappe.db.get_value('Shift Type', {'name': shift}, ['end_time'])
    shift_start_time = datetime.strptime(str(start_time), '%H:%M:%S').time()
    shift_start_datetime = dt.datetime.combine(from_date, shift_start_time)

    shift_end_time = datetime.strptime(str(end_time), '%H:%M:%S').time()
    shift_end_datetime = dt.datetime.combine(to_date, shift_end_time)

    datalist = []

    if session == 'Full Day':
        total_hours = time_diff_in_hours(shift_end_datetime, shift_start_datetime)
        total_hours_in_time = shift_end_datetime - shift_start_datetime
        frappe.errprint(f"total_hours_in_time {total_hours_in_time}")
        if total_hours_in_time > timedelta(hours=23, minutes=59, seconds=59):
            total_hours_in_time = timedelta(hours=23, minutes=59, seconds=59)
        data = {
            'shift_start_time': shift_start_datetime.strftime('%H:%M:%S'),
            'shift_end_time': shift_end_datetime.strftime('%H:%M:%S'),
            'od_hours': total_hours,
            'total_od_hours': total_hours_in_time
        }
        datalist.append(data)

    elif session == 'First Half':
        total_duration = shift_end_datetime - shift_start_datetime
        first_half_duration = total_duration / 2
        first_half_end = shift_start_datetime + first_half_duration
        
        total_hours = time_diff_in_hours(first_half_end, shift_start_datetime)
        total_hours_in_time = first_half_end - shift_start_datetime
        
        if total_hours_in_time > timedelta(hours=23, minutes=59, seconds=59):
            total_hours_in_time = timedelta(hours=23, minutes=59, seconds=59)
        data = {
            'shift_start_time': shift_start_datetime.strftime('%H:%M:%S'),
            'shift_end_time': first_half_end.strftime('%H:%M:%S'),
            'od_hours': total_hours,
            'total_od_hours':total_hours_in_time
        }
        datalist.append(data)

    elif session == 'Second Half':
        total_duration = shift_end_datetime - shift_start_datetime
        first_half_duration = total_duration / 2
        second_half_start = shift_start_datetime + first_half_duration
        
        total_hours = time_diff_in_hours(second_half_start, shift_start_datetime)
        total_hours_in_time = second_half_start - shift_start_datetime
        if total_hours_in_time > timedelta(hours=23, minutes=59, seconds=59):
            total_hours_in_time = timedelta(hours=23, minutes=59, seconds=59)
        data = {
            'shift_start_time': second_half_start.strftime('%H:%M:%S'),
            'shift_end_time': shift_end_datetime.strftime('%H:%M:%S'),
            'od_hours': total_hours,
            'total_od_hours':total_hours_in_time
        }
        datalist.append(data)

    return datalist


@frappe.whitelist()
def calculate_total_hours(from_time, to_time, from_date, to_date):
    
    if isinstance(from_date, str):
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
    if isinstance(to_date, str):
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
    shift_start_time = datetime.strptime(str(from_time), '%H:%M:%S').time()
    shift_start_datetime = dt.datetime.combine(from_date, shift_start_time)

    shift_end_time = datetime.strptime(str(to_time), '%H:%M:%S').time()
    shift_end_datetime = dt.datetime.combine(to_date, shift_end_time)

    datalist = []
    if shift_end_datetime < shift_start_datetime:
        frappe.throw('To Time cannot be earlier than the From Time')
    total_hours = time_diff_in_hours(shift_end_datetime, shift_start_datetime)
    total_hours_in_time = shift_end_datetime - shift_start_datetime
    frappe.errprint(f"total_hours_in_time {total_hours_in_time}")
    if total_hours_in_time > timedelta(hours=23, minutes=59, seconds=59):
        total_hours_in_time = timedelta(hours=23, minutes=59, seconds=59)
    data = {
        'od_hours': total_hours,
        'total_od_hours': total_hours_in_time
    }
    datalist.append(data)

   
    return datalist

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
        
