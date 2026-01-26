import frappe
from datetime import datetime
from frappe.utils.data import today, add_days, add_years
from dateutil.relativedelta import relativedelta
from datetime import timedelta, time,date
from frappe.utils import time_diff_in_hours, formatdate, get_first_day,get_last_day, nowdate, now_datetime
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)

@frappe.whitelist()
# def mark_att_with_employee(attendance_dates,to_date,employee):
def mark_att_with_employee ():
    # frappe.errprint(employee)
    # from_date = attendance_dates
    # to_date =to_date
    from_date ='2024-12-12'
    to_date ='2024-12-12'
    employee = 'HR-EMP-00004'
    # from_date = add_days(today(),-1)
    # to_date = today()
    checkins = frappe.db.sql(
        """select * from `tabEmployee Checkin` where date(time) between '%s' and '%s' and employee ='%s' order by time """%(from_date,to_date,employee),as_dict=1)
#    if checkins:
#        # print(checkins)
    for c in checkins:
        frappe.errprint("employee")
        employee_data = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
        if employee_data:     
            frappe.errprint(c.employee)  
            frappe.errprint(checkins)
            mark_attendance_from_checkin(c.name,c.employee,c.log_type,c.time)
    mark_absent_with_employee(from_date,to_date,employee)

# @frappe.whitelist()
# def previous_mark_att():
#     from_date = '2022-01-01'
#     to_date = '2022-01-31'
#     nowday = add_days(nowdate(),-1)
#     from_date=get_first_day(nowday)
#     to_date=get_last_day(nowday)
#     frappe.errprint(from_date)
#     frappe.errprint(to_date)
#     checkins = frappe.db.sql(
#         """select * from `tabEmployee Checkin` where skip_auto_attendance = 0 and date(time) between '%s' and '%s' order by time """%(from_date,to_date),as_dict=1)
#     if checkins:
#         for c in checkins:
#             att = mark_attendance_from_checkin(c.name,c.employee,c.time)
#             if att:
#                 frappe.db.set_value("Employee Checkin",
#                                     c.name, "skip_auto_attendance", "1")

@frappe.whitelist()
def mark_att():
    from_date = '2023-07-15'
    to_date = '2023-07-17'
    # from_date = add_days(today(),-1)
    # to_date = today()
    checkins = frappe.db.sql(
        """select * from `tabEmployee Checkin` where skip_auto_attendance = 0 and date(time) between '%s' and '%s' order by time """%(from_date,to_date),as_dict=1)
#    if checkins:
#        # print(checkins)
    for c in checkins:
        employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
        if employee:       
            mark_attendance_from_checkin(c.name,c.employee,c.time)
    mark_absent(from_date,to_date)
    mark_overtime(from_date)
    mark_shift_status(from_date)                                

def mark_attendance_from_checkin(checkin,employee,log_type,time):
    frappe.errprint(checkin)
    att_time = time.time()
    att_date = time.date()
    month_start_date = get_first_day(att_date)
    month_end_date = get_last_day(att_date)
    shift = ''
    if log_type == 'IN':
        frappe.errprint(checkin)
        min_in_time = ''
        max_in_time = ''
        min_in_time1 = datetime.strptime('06:00', '%H:%M').time()
        max_in_time1 = datetime.strptime('13:00', '%H:%M').time()
        min_in_time2 = datetime.strptime('13:00', '%H:%M').time()
        max_in_time2 = datetime.strptime('18:30', '%H:%M').time()
        min_in_time3 = datetime.strptime('00:01', '%H:%M').time()
        max_in_time3 = datetime.strptime('03:00', '%H:%M').time()
        min_in_timepp1 = datetime.strptime('06:00', '%H:%M').time()
        max_in_timepp1 = datetime.strptime('10:00', '%H:%M').time()
        min_in_timepp2 = datetime.strptime('18:00', '%H:%M').time()
        max_in_timepp2 = datetime.strptime('23:00', '%H:%M').time()
        late = 0
        status = 'Absent'
        if max_in_time1 >= att_time >= min_in_time1:
            if frappe.db.get_value('Employee',employee,"default_shift") == 'PP1':
                shift = 'PP1'
            else:
                shift = 'A'
            min_in_time = datetime.strptime('06:00', '%H:%M').time()
            max_in_time = datetime.strptime('13:00', '%H:%M').time()
            if datetime.strptime('08:01', '%H:%M').time() < att_time:
                late = 1
        elif max_in_time2 >= att_time >= min_in_time2:
            shift = 'B'
            min_in_time = datetime.strptime('13:00', '%H:%M').time()
            max_in_time = datetime.strptime('18:30', '%H:%M').time()
            if datetime.strptime('16:31', '%H:%M').time() < att_time:
                late = 1
        elif max_in_time3 >= att_time >= min_in_time3:
            shift = 'C'
            att_date = add_days(att_date,-1)
            min_in_time = datetime.strptime('00:01', '%H:%M').time()
            max_in_time = datetime.strptime('03:00', '%H:%M').time()
            if datetime.strptime('01:01', '%H:%M').time() < att_time:
                late = 1
        elif max_in_timepp2 >= att_time >= min_in_timepp2:
            shift = 'PP2'
            min_in_time = datetime.strptime('18:30', '%H:%M').time()
            max_in_time = datetime.strptime('23:00', '%H:%M').time()
            if datetime.strptime('20:01', '%H:%M').time() < att_time:
                late = 1
        if min_in_time and max_in_time:
            att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':att_date,'docstatus': ['!=',2]})
            if not att:
                if shift != 'C':
                    checkins = frappe.db.sql("select name,time from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and time(time) between '%s' and '%s' order by time "%(employee,att_date,min_in_time,max_in_time),as_dict=True)
                else:
                    yesterday = add_days(att_date,1)
                    checkins = frappe.db.sql("select name,time from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and time(time) between '%s' and '%s' order by time "%(employee,yesterday,min_in_time,max_in_time),as_dict=True)
                if checkins:
                    # qr_checkin = frappe.db.sql("select name, employee,qr_shift,qr_scan_time,shift_date from `tabQR Checkin` where employee = '%s' and date(qr_scan_time) = '%s' order by qr_scan_time "%(employee,att_date),as_dict=True)
                    att = frappe.new_doc("Attendance")
                    att.employee = employee
                    att.attendance_date = att_date
                    att.shift = shift
                    att.status = status
                    if status == 'Half Day':
                        att.leave_type = 'Leave Without Pay'
                    att.late_entry = late
                    att.in_time = checkins[0].time
                    att.save(ignore_permissions=True)
                    frappe.db.commit()
                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                    return att
            else:
                if shift != 'C':
                    # checkins = []
                    checkins = frappe.db.sql("select name,time from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and time(time) between '%s' and '%s' order by time "%(employee,att_date,min_in_time,max_in_time),as_dict=True)
                else:
                    yesterday = add_days(att_date,1)
                    checkins = frappe.db.sql("select name,time from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and time(time) between '%s' and '%s' order by time "%(employee,yesterday,min_in_time,max_in_time),as_dict=True)
                if checkins:
                    att = frappe.get_doc("Attendance",att)
                    if att.docstatus == 0:
                        # att.employee = employee
                        # att.attendance_date = att_date
                        frappe.errprint(att_date)
                        att.shift = shift
                        att.status = status
                        frappe.errprint(status)
                        att.late_entry = late
                        att.in_time = checkins[0].time
                        frappe.errprint(checkins[0].time)
                        att.save(ignore_permissions=True)
                        frappe.db.commit()
                        frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                        frappe.errprint(checkins[0].time)
                        return att
                    

    if log_type == 'OUT':
        frappe.errprint(checkin)
        max_out = datetime.strptime('11:30', '%H:%M').time()
        if att_time < max_out:
            yesterday = add_days(att_date,-1)
            checkins = frappe.db.sql("select name,time from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and time(time) < '%s' order by time "%(employee,att_date,max_out),as_dict=True)
            att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':yesterday})
            if att:
                att = frappe.get_doc("Attendance",att)
                if att.docstatus == 0:
                    if not att.out_time:
                        if len(checkins) > 0:
                            att.out_time = checkins[-1].time
                        else:
                            att.out_time = checkins[-1].time
                        att.save(ignore_permissions=True)
                        frappe.db.commit()
                        frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                        return att
                    else:
                        return att
            else:
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = yesterday
                att.status = 'Absent'
                if len(checkins) > 0:
                    att.out_time = checkins[-1].time
                else:
                    att.out_time = checkins[-1].time
                att.save(ignore_permissions=True)
                frappe.db.commit()
                frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                return att
        else:
            checkins = frappe.db.sql("select name,time,docstatus from `tabEmployee Checkin` where employee ='%s' and log_type = 'OUT' and date(time) = '%s' order by time "%(employee,att_date),as_dict=True)
            att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':att_date})
            if att:
                att = frappe.get_doc("Attendance",att)
                if att.docstatus == 0:
                    if not att.out_time:
                        if len(checkins) > 0:
                            att.out_time = checkins[-1].time
                        else:
                            att.out_time = checkins[-1].time
                        att.save(ignore_permissions=True)
                        frappe.db.commit()
                        frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                        return att
                    else:
                        return att
            else:
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = att_date
                # att.shift_type = shift
                att.status = 'Absent'
                if len(checkins) > 0:
                    att.out_time = checkins[-1].time
                else:
                    att.out_time = checkins[-1].time
                att.save(ignore_permissions=True)
                frappe.db.commit()
                frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                return att
@frappe.whitelist()    
def mark_absent(from_date,to_date):
    # if to_date == today():
    #     to_date = add_days(to_date,-1)
    #     print(to_date)
    # no_of_days = date_diff(add_days(to_date, 1),from_date )
    # dates = [add_days(from_date, i) for i in range(0, no_of_days)]
    dates = [from_date,to_date]
    for date in dates:
        employee = frappe.db.get_all('Employee',{'status':'Active','date_of_joining':['<=',from_date]},['*'])
        for emp in employee:
            hh = check_holiday(date,emp.name)
            if not hh:
                if not frappe.db.exists('Attendance',{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')}):
                    att = frappe.new_doc('Attendance')
                    att.employee = emp.name
                    att.status = 'Absent'
                    att.attendance_date = date
                    att.save(ignore_permissions=True)
                    frappe.db.commit()   
@frappe.whitelist()    
def mark_absent_with_employee(from_date,to_date,employee):
    # if to_date == today():
    #     to_date = add_days(to_date,-1)
    #     print(to_date)
    # no_of_days = date_diff(add_days(to_date, 1),from_date )
    # dates = [add_days(from_date, i) for i in range(0, no_of_days)]
    dates = [from_date,to_date]
    for date in dates:
        employee_data = frappe.db.get_all('Employee',{'employee':employee,'status':'Active','date_of_joining':['<=',from_date]},['*'])
        for emp in employee_data:
            hh = check_holiday(date,emp.name)
            if not hh:
                if not frappe.db.exists('Attendance',{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')}):
                    att = frappe.new_doc('Attendance')
                    att.employee = emp.name
                    att.status = 'Absent'
                    att.attendance_date = date
                    att.save(ignore_permissions=True)
                    frappe.db.commit()  

def check_holiday(date,emp):
    holiday_list = frappe.db.get_value('Employee',emp,'holiday_list')
    holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
    left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
    if holiday:
        if holiday[0].weekly_off == 1:
            return "WW"
        else:
            return "HH"
    return None
        

