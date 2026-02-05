import frappe
import requests
from datetime import datetime
from frappe.utils.data import today, add_days, add_years
from dateutil.relativedelta import relativedelta
from datetime import timedelta, time,date
from frappe.utils import time_diff_in_hours, formatdate, get_first_day,get_last_day, nowdate, now_datetime
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from collections import Counter
from datetime import datetime, time
@frappe.whitelist()
def mark_att_manual():
    from_date='2026-01-01'
    to_date='2026-01-03'
    checkins = frappe.db.sql(
        """select * from `tabEmployee Checkin` where date(time) between '%s' and '%s' order by time """%(from_date,to_date),as_dict=1)
    for c in checkins:
        employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
        left_emp = frappe.db.exists('Employee',{'status':'Left','date_of_joining':['<=',from_date],'relieving_date': ['>=',to_date], 'name':c.employee})

        if employee or left_emp: 
            mark_attendance_from_checkin_new(c.name,c.employee,c.time)
    mark_absent(from_date,to_date)
    assigned_shift(from_date, to_date)
    mark_wh(from_date,to_date)
    ot_calculation(from_date,to_date)   
    mark_late_entry_and_early_exit(from_date, to_date)
    mark_attendance_status_based_on_the_late_and_early_exit(from_date,to_date)
    create_attendance_permission_for_all_emp_late(from_date, to_date)    
    return "ok"   

# This code is used for manual testing
@frappe.whitelist()
def mark_att_with_employee_manual():
    from_date='2026-01-01'
    to_date='2026-02-01'
    employee='2502'
    checkins = frappe.db.sql(
        """select * from `tabEmployee Checkin` where date(time) between '%s' and '%s' and employee ='%s' order by time """%(from_date,to_date,employee),as_dict=1)
    for c in checkins:
        employee_data = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
        left_emp = frappe.db.exists('Employee',{'status':'Left','date_of_joining':['<=',from_date],'relieving_date': ['>=',to_date], 'name':c.employee})
        if employee_data or left_emp:
            mark_attendance_from_checkin_new(c.name,c.employee,c.time)
    
    mark_absent_with_employee(from_date,to_date,employee)
    assigned_shift_emp(from_date, to_date,employee)
    mark_wh_emp(from_date, to_date, employee)
    ot_calculation_with_employee(from_date,to_date,employee)
    mark_late_entry_and_early_exit_with_employee(from_date, to_date,employee)
    mark_attendance_status_based_on_the_late_and_early_exit_with_employee(from_date,to_date,employee)
    create_attendance_permission_late(from_date, to_date,employee)
    create_attendance_permission_early(from_date, to_date, employee)
    return "ok"  

# @frappe.whitelist()
# def mark_att_with_employee_enqueue(from_date, to_date, employee):
#     frappe.enqueue(
#         "gplast.mark_attendance.mark_att_with_employee",
#         queue="long",
#         timeout=36000,
#         is_async=True,
#         now=False,
#         job_name="Mark Attendance",
#         from_date=from_date,
#         to_date=to_date,
#         employee=employee
#     )
#     return "ok"

# This code is for running attendance automatically, not manually. If you want to run it manually, use the above method.
@frappe.whitelist()
def mark_att_with_employee(from_date, to_date, employee):
    checkins = frappe.db.sql(
        """select * from `tabEmployee Checkin` where date(time) between '%s' and '%s' and employee ='%s' order by time """%(from_date,to_date,employee),as_dict=1)
    for c in checkins:
        employee_data = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
        left_emp = frappe.db.exists('Employee',{'status':'Left','date_of_joining':['<=',from_date],'relieving_date': ['>=',to_date], 'name':c.employee})
        if employee_data or left_emp:
            mark_attendance_from_checkin_new(c.name,c.employee,c.time)
    mark_absent_with_employee(from_date,to_date,employee)
    assigned_shift_emp(from_date, to_date,employee)
    mark_wh_emp(from_date, to_date, employee)
    ot_calculation_with_employee(from_date,to_date,employee)
    mark_late_entry_and_early_exit_with_employee(from_date, to_date,employee)
    mark_attendance_status_based_on_the_late_and_early_exit_with_employee(from_date,to_date,employee)
    create_attendance_permission_late(from_date, to_date,employee) 
    create_attendance_permission_early(from_date, to_date, employee)
    return "ok"

@frappe.whitelist()
def mark_att():
    from_date = add_days(today(),-1)  
    to_date = today()
    # from_date='2025-05-31'
    # to_date='2025-05-31'
    checkins = frappe.db.sql(
        """select * from `tabEmployee Checkin` where date(time) between '%s' and '%s' and skip_auto_attendance = 0 order by time """%(from_date,to_date),as_dict=1)
    for c in checkins:
        employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
        left_emp = frappe.db.exists('Employee',{'status':'Left','date_of_joining':['<=',from_date],'relieving_date': ['>=',to_date], 'name':c.employee})
        if employee or left_emp:
            # mark_attendance_from_checkin(c.name,c.employee,c.time)
            mark_attendance_from_checkin_new(c.name,c.employee,c.time)
            # create_attendance_permission(from_date, to_date, c.employee)
            # create_attendance_permission_for_early_exit(from_date, to_date, c.employee)
    mark_absent(from_date,to_date)
    assigned_shift(from_date, to_date)
    mark_wh(from_date,to_date)
    # mark_late_in(from_date,to_date) 
    ot_eligible = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'ot_eligibility':'Over Time'})
    if ot_eligible:
        ot_calculation(from_date,to_date)   
    mark_late_entry_and_early_exit(from_date, to_date)
    mark_attendance_status_based_on_the_late_and_early_exit(from_date,to_date)  
    return "ok"

@frappe.whitelist()
def mark_att_frontend_enqueue(from_date, to_date):
    frappe.enqueue(
        "gplast.mark_attendance.mark_att_frontend",
        queue="long",
        timeout=36000,
        is_async=True,
        now=False,
        job_name="Mark Attendance",
        from_date=from_date,
        to_date=to_date
    )
    return "ok"

@frappe.whitelist()
def mark_att_frontend(from_date, to_date):
    checkins = frappe.db.sql(
        """select * from `tabEmployee Checkin` where date(time) between '%s' and '%s' order by time """%(from_date,to_date),as_dict=1)
    for c in checkins:
        employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
        left_emp = frappe.db.exists('Employee',{'status':'Left','date_of_joining':['<=',from_date],'relieving_date': ['>=',to_date], 'name':c.employee})
        if employee or left_emp:
            # mark_attendance_from_checkin(c.name,c.employee,c.time)
            mark_attendance_from_checkin_new(c.name,c.employee,c.time)
            # create_attendance_permission(from_date, to_date, c.employee)
            # create_attendance_permission_for_early_exit(from_date, to_date, c.employee)
    mark_absent(from_date,to_date)
    assigned_shift(from_date, to_date)
    mark_wh(from_date,to_date)
    # mark_late_in(from_date,to_date)
    ot_eligible = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'ot_eligibility':'Over Time'})
    if ot_eligible: 
        ot_calculation(from_date,to_date)
    mark_late_entry_and_early_exit(from_date, to_date)
    mark_attendance_status_based_on_the_late_and_early_exit(from_date,to_date) 
    mark_attendance_status_based_on_the_late_and_early_exit(from_date,to_date)    
    create_attendance_permission_for_all_emp_late(from_date, to_date)
    return "ok"               


def mark_wh(from_date, to_date):
    attendance = frappe.db.get_all(
        'Attendance',
        filters={'attendance_date': ('between', (from_date, to_date)), 'docstatus': ('!=', '2')},
        fields=['name', 'in_time', 'out_time', 'status','shift_status','on_duty_application','shift','attendance_date','late_entry',"employment_type"]
    )

    for att in attendance:

        in_time = att.get('in_time')
        out_time = att.get('out_time')
        if not in_time or not out_time or not att.shift:
            frappe.db.set_value('Attendance', att.name, 'wh', "0.000") 
            frappe.db.set_value('Attendance', att.name, 'total_working_hours', "0.000")
        if in_time and out_time:
            if isinstance(in_time, str):
                in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
            if isinstance(out_time, str):
                out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')

            wh = time_diff_in_hours(out_time, in_time)
            if att.on_duty_application:
                od_hours = frappe.db.get_value("On Duty Application",{'docstatus':1,"name":att.on_duty_application},['od_hours'])
                if od_hours:
                    wh= od_hours + wh 
            if wh:
                wh = round(wh, 1)
                frappe.db.set_value("Attendance", att.name, "total_working_hours", wh)
            if att.shift:
                shift_start = frappe.db.get_value('Shift Type',{'name':att.shift},['start_time'])
                shift_end = frappe.db.get_value('Shift Type',{'name':att.shift},['end_time'])
                if isinstance(shift_start, timedelta):
                    shift_start = (datetime.min + shift_start).time()
                if isinstance(shift_end, timedelta):
                    shift_end = (datetime.min + shift_end).time()
                # if att.shift != "C":
                shift_st = datetime.combine( att.attendance_date, shift_start)
                # else:
                #     tmr_att_s = att.attendance_date + timedelta(days=1)
                #     shift_st = datetime.combine( tmr_att_s, shift_start)
                if att.shift != "B" and att.shift != "C" and att.shift != "PP1":
                    shift_et = datetime.combine( att.attendance_date, shift_end)
                else:
                    tmr_att_e = att.attendance_date + timedelta(days=1)
                    shift_et = datetime.combine( tmr_att_e, shift_end)
                if in_time >= shift_st:
                    in_time = in_time
                else:
                    in_time = shift_st
                if out_time >  shift_et:
                    out_time = shift_et
                else:
                    out_time = out_time     
                if in_time and out_time :
                    wh_timedelta = out_time - in_time
                    wh_hours = wh_timedelta.total_seconds() / 3600  
                    if out_time < shift_st or ( wh_hours < 0.000):
                        wh_hours = 0.000 
                    frappe.db.set_value('Attendance', att.name, 'wh', wh_hours)  
                    if wh_hours < 4.000 :
                        frappe.db.set_value('Attendance', att.name, 'status', "Absent") 
                    if att.employment_type != "Contract":
                        if wh_hours >= 4.000 and wh_hours < 6.000:
                            if att.shift_status =="Matched":
                                frappe.db.set_value('Attendance', att.name, 'status', "Half Day")
                        if wh_hours >= 6.000 and wh_hours < 9.000:
                            if att.shift_status =="Matched":
                                frappe.db.set_value('Attendance', att.name, 'status', "Present")
                                doc = frappe.get_doc("Attendance", att.name)
                                doc.submit()   
                    if att.employment_type == "Contract": 
                        if wh_hours >= 4.000 and wh_hours < 7.750:
                            if att.shift_status =="Matched":
                                frappe.db.set_value('Attendance', att.name, 'status', "Half Day")
                        if wh_hours >= 7.750 and wh_hours < 9.000:
                            if att.shift_status =="Matched":
                                frappe.db.set_value('Attendance', att.name, 'status', "Present")
                                doc = frappe.get_doc("Attendance", att.name)
                                doc.submit()               
                    if att.shift_status =="Unmatched":      
                        frappe.db.set_value('Attendance', att.name, 'status', "Absent") 
                    
def mark_wh_emp(from_date, to_date, emp):
    attendance = frappe.db.get_all(
        'Attendance',
        filters={'attendance_date': ('between', (from_date, to_date)),'employee':emp, 'docstatus': ('!=', '2')},
        fields=['name', 'in_time', 'out_time', 'status','shift_status','on_duty_application','shift','attendance_date','late_entry','shift_status','employment_type']
    )
    print(attendance , "Attendance")

    for att in attendance:

        in_time = att.get('in_time')
        out_time = att.get('out_time')
        if not in_time or not out_time or not att.shift:
            frappe.db.set_value('Attendance', att.name, 'wh', "0.000") 
            frappe.db.set_value('Attendance', att.name, 'total_working_hours', "0.000")
        if in_time and out_time:
            if isinstance(in_time, str):
                in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
            if isinstance(out_time, str):
                out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')

            wh = time_diff_in_hours(out_time, in_time)
            if att.on_duty_application:
                od_hours = frappe.db.get_value("On Duty Application",{'docstatus':1,"name":att.on_duty_application},['od_hours'])
                if od_hours:
                    wh= od_hours + wh 
            if wh:
                wh = round(wh, 1)
                frappe.db.set_value("Attendance", att.name, "total_working_hours", wh)
            if att.shift:
                shift_start = frappe.db.get_value('Shift Type',{'name':att.shift},['start_time'])
                shift_end = frappe.db.get_value('Shift Type',{'name':att.shift},['end_time'])
                if isinstance(shift_start, timedelta):
                    shift_start = (datetime.min + shift_start).time()
                    # print(shift_start, "SHIFT START")
                if isinstance(shift_end, timedelta):
                    shift_end = (datetime.min + shift_end).time()
                    # print(shift_end, "SHIFT END")
                shift_st = datetime.combine( att.attendance_date, shift_start)
                # print(shift_st, "SHIFT ST 1 ")
                if att.shift != "B" and att.shift != "C" and att.shift != "PP1":
                    shift_et = datetime.combine( att.attendance_date, shift_end)
                    # print(shift_et, "SHIFT ET 1 ")
                else:
                    tmr_att_e = att.attendance_date + timedelta(days=1)
                    shift_et = datetime.combine( tmr_att_e, shift_end)
                    # print(shift_et, "SHIFT ET 2 ")
                if in_time >= shift_st:
                    in_time = in_time
                else:
                    in_time = shift_st
                if out_time >  shift_et:
                    out_time = shift_et
                else:
                    out_time = out_time     
                print(in_time , "IN TIME")
                print(out_time , "OUT TIME")
                if in_time and out_time :
                    wh_timedelta = out_time - in_time
                    wh_hours = wh_timedelta.total_seconds() / 3600 
                    if out_time < shift_st or ( wh_hours < 0.000):
                        wh_hours = 0.000 
                    frappe.db.set_value('Attendance', att.name, 'wh', wh_hours)  
                    print("IN")
                    if wh_hours < 4.000 :
                        frappe.db.set_value('Attendance', att.name, 'status', "Absent") 
                    if att.employment_type != "Contract":
                        if wh_hours >= 4.000 and wh_hours < 6.000:
                            if att.shift_status =="Matched":
                                frappe.db.set_value('Attendance', att.name, 'status', "Half Day")
                        if wh_hours >= 6.000 and wh_hours < 9.000:
                            if att.shift_status =="Matched":
                                frappe.db.set_value('Attendance', att.name, 'status', "Present")
                                doc = frappe.get_doc("Attendance", att.name)
                                doc.submit()   
                    if att.employment_type == "Contract": 
                        if wh_hours >= 4.000 and wh_hours < 7.750:
                            if att.shift_status =="Matched":
                                frappe.db.set_value('Attendance', att.name, 'status', "Half Day")
                        if wh_hours >= 7.750 and wh_hours < 9.000:
                            if att.shift_status =="Matched":
                                frappe.db.set_value('Attendance', att.name, 'status', "Present")
                                doc = frappe.get_doc("Attendance", att.name)
                                doc.submit()   
                    if att.shift_status =="Unmatched":      
                        frappe.db.set_value('Attendance', att.name, 'status', "Absent")  

            

from collections import Counter
from datetime import datetime

def mark_attendance_from_checkin(checkin,employee,time):
    att_time = time.time()
    att_date = time.date()
    in_time = ''
    out_time = ''
    checkins = frappe.db.sql("""select name,time from `tabEmployee Checkin` where employee = "%s" and date(time) = '%s' order by time """%(employee,att_date),as_dict=True)
    if checkins:
        if len(checkins) >= 2:
            in_time = checkins[0].time
            out_time = checkins[-1].time
        elif len(checkins) == 1:
            in_time = checkins[0].time
        
        a = frappe.db.get_value('Attendance',{'employee':employee,'attendance_date':att_date}, ['name'])
        
        shifta = frappe.db.get_value('Shift Type',{'name':'A'},['checkin_start_time','checkin_end_time'])
        shiftb = frappe.db.get_value('Shift Type',{'name':'B'},['checkin_start_time','checkin_end_time'])
        shiftc = frappe.db.get_value('Shift Type',{'name':'C'},['checkin_start_time','checkin_end_time'])
        # print("Shift C from DB:", shiftc)
        # print("Checkins:", checkins)
        shiftg = frappe.db.get_value('Shift Type',{'name':'G'},['checkin_start_time','checkin_end_time'])
        shiftg1 = frappe.db.get_value('Shift Type',{'name':'G1'},['checkin_start_time','checkin_end_time'])
        shiftge = frappe.db.get_value('Shift Type',{'name':'GE'},['checkin_start_time','checkin_end_time'])
        shift_assignment = frappe.db.get_value("Shift Assignment",{"employee":employee,"start_date":att_date, "docstatus": 1},["shift_type"])
        shift_start_time = frappe.db.get_value('Shift Type',{'name':shift_assignment},['checkin_start_time','checkin_end_time'])
        shift_type = frappe.db.get_all("Shift Type", ["checkin_start_time"])

        checkins_time = [shift["checkin_start_time"] for shift in shift_type if shift["checkin_start_time"]]

        checkins_count = Counter(checkins_time)

        shift_group = frappe.db.get_value("Employee", {"employee": employee}, "shift_group") or ""
        shift_type_ = None
        shift = ''
        checkin_datetime = checkins[0].time 
        shift_c_start = checkin_datetime.replace(hour=22, minute=0, second=0, microsecond=0) - timedelta(days=1)
        shift_c_end = shift_c_start + timedelta(hours=4)
        # print(shift_c_start)
        # print(shift_c_end)
        if (shift_assignment != "C") and shift_start_time:
            if (datetime.min + shift_start_time[0]).time() < checkins[0].time.time() < (datetime.min + shift_start_time[1]).time():
                shift = shift_assignment
            else:
                shift = ''
        elif shift_assignment == "C" :
            # if shift_c_start <= checkin_datetime <= shift_c_end:    
            shift = 'C'
        elif shift_group and not shift_assignment:
            # if shift_group.lower() != "rotational":
                if any(count > 1 for count in checkins_count.values()):
                    for shift_item in shift_type:
                        checkin_start_time = shift_item.get("checkin_start_time")
                        if checkin_start_time and (datetime.min + checkin_start_time).time() < checkins[0].time.time():
                            potential_shift = frappe.db.get_value(
                                "Shift Type",
                                {"shift_group": shift_group, "checkin_start_time": checkin_start_time},
                                "name",
                            )
                            if potential_shift:
                                shift_type_ = potential_shift
                                break

                if shift_type_:
                    shift = shift_type_
                else:
                    if (datetime.min + shifta[0]).time() < checkins[0].time.time() < (datetime.min + shifta[1]).time():
                        shift = 'A'
                    elif (datetime.min + shiftb[0]).time() < checkins[0].time.time() < (datetime.min + shiftb[1]).time():
                        shift = 'B'
                    # elif (datetime.min + shiftc[0]).time() < checkins[0].time.time() < (datetime.min + shiftc[1]).time():
                    #     shift ='C'
                    elif shift_c_start <= checkin_datetime <= shift_c_end:
                        shift = 'C'

                    elif (datetime.min + shiftg[0]).time() < checkins[0].time.time() < (datetime.min + shiftg[1]).time():
                        shift ='G'
                    elif (datetime.min + shiftg1[0]).time() < checkins[0].time.time() < (datetime.min + shiftg1[1]).time():
                        shift ='G1'
                    elif (datetime.min + shiftge[0]).time() < checkins[0].time.time() < (datetime.min + shiftge[1]).time():
                        shift ='GE'
                    else:
                        shift = ''
        elif (datetime.min + shifta[0]).time() < checkins[0].time.time() < (datetime.min + shifta[1]).time():
            shift = 'A'
        elif (datetime.min + shiftb[0]).time() < checkins[0].time.time() < (datetime.min + shiftb[1]).time():
            shift = 'B'
        # elif (datetime.min + shiftc[0]).time() < checkins[0].time.time() < (datetime.min + shiftc[1]).time():
        #     shift ='C'
        

        elif shift_c_start <= checkin_datetime <= shift_c_end:
            shift = 'C'

        elif (datetime.min + shiftg[0]).time() < checkins[0].time.time() < (datetime.min + shiftg[1]).time():
            shift ='G'
        elif (datetime.min + shiftg1[0]).time() < checkins[0].time.time() < (datetime.min + shiftg1[1]).time():
            shift ='G1'
        elif (datetime.min + shiftge[0]).time() < checkins[0].time.time() < (datetime.min + shiftge[1]).time():
            shift ='GE'
        # elif shift_group:
        #     if shift_group.lower() == "rotational":
        #         if any(count > 1 for count in checkins_count.values()):
        #             for shift_item in shift_type:
        #                 checkin_start_time = shift_item.get("checkin_start_time")
        #                 if checkin_start_time and (datetime.min + checkin_start_time).time() < checkins[0].time.time():
        #                     potential_shift = frappe.db.get_value(
        #                         "Shift Type",
        #                         {"shift_group": shift_group, "checkin_start_time": checkin_start_time},
        #                         "name",
        #                     )
        #                     if potential_shift:
        #                         shift_type_ = potential_shift
        #                         break

        #         if shift_type_:
        #             shift = shift_type_
        #         else:
        #             shift = ''
        #             print("shift Group not set")    
        else: 
            shift_value=frappe.db.get_value('Employee',{'name':employee},['default_shift'])
            if shift_value:
                shift = shift_value
            else:
                shift = ''
        att = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date})
        attended_shift = shift
        assigned_shift = ''
        if frappe.db.get_value("Shift Assignment",{"employee":employee,"start_date":att_date, "docstatus": 1},["shift_type"]):
            assigned_shift = frappe.db.get_value("Shift Assignment",{"employee":employee,"start_date":att_date, "docstatus": 1},["shift_type"])
        
        # elif shift_group:
        #     if any(count > 1 for count in checkins_count.values()):
        #         for shift_item in shift_type:
        #             checkin_start_time = shift_item.get("checkin_start_time")
        #             if checkin_start_time and (datetime.min + checkin_start_time).time() < checkins[0].time.time():
        #                 potential_shift = frappe.db.get_value(
        #                     "Shift Type",
        #                     {"shift_group": shift_group, "checkin_start_time": checkin_start_time},
        #                     "name",
        #                 )
        #                 if potential_shift:
        #                     shift_type_ = potential_shift
        #                     break

            # if shift_type_:
            #     assigned_shift = shift_type_
            # else:
            #     assigned_shift = frappe.db.get_value('Employee',{'name':employee},['default_shift'])

        elif shift_group:
            if shift_group.lower() == "rotational":
                # fetch all rotational shifts (A, B, C)
                rotational_shifts = frappe.db.get_all(
                    "Shift Type",
                    filters={"shift_group": "Rotational"},
                    fields=["name", "checkin_start_time", "checkin_end_time", "night_shift"]
                )
                punch_time = checkins[0].get("time").time()

                for s in rotational_shifts:
                    start_time = (datetime.min + s["checkin_start_time"]).time()
                    end_time   = (datetime.min + s["checkin_end_time"]).time()

                    if is_in_shift(punch_time, s["checkin_start_time"], s["checkin_end_time"], is_night=s.get("night_shift")):
                        assigned_shift = s["name"]
                        break

            else:
                shift_from_group = frappe.db.get_value(
                    "Shift Type",
                    {"shift_group": shift_group},
                    "name"
                )
                dshift = frappe.db.get_value("Employee", {"name": employee}, "default_shift")
                if shift_from_group:
                    assigned_shift = shift_from_group
                else:
                    if dshift :
                        shift = dshift
                    else:
                        shift=''
        else:
            assigned_shift = frappe.db.get_value('Employee',{'name':employee},['default_shift'])
        if assigned_shift == attended_shift:
            shift_status = "Matched"
        else:
            shift_status = "Unmatched"
        if not att and checkin:
            att = frappe.new_doc("Attendance")
            att.employee = employee
            att.attendance_date = att_date
            att.shift = shift
            att.status = "Absent"
            att.in_time = in_time
            att.out_time = out_time
            att.assigned_shift = assigned_shift
            att.attended_shift = shift
            att.shift_status = shift_status
            att.session_from_time = "00:00:00"
            att.session_to_time = "00:00:00"
            att.late_entry_time = "00:00:00"
            att.ot_hours = "00:00:00"
            if in_time and out_time:
                total_working_hours = (out_time-in_time).total_seconds() / 3600.0
                att.total_working_hours=total_working_hours
                if total_working_hours > 8:
                    att.save(ignore_permissions=True)
                    att.submit()
            att.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
            frappe.db.set_value('Employee Checkin',checkin,'attendance',att.name)
            return att.name
        else:
            if in_time:
                frappe.db.set_value("Attendance",att,'in_time',in_time)
            if out_time:
                frappe.db.set_value("Attendance",att,'out_time',out_time)
            if in_time and out_time:
                total_working_hours = (out_time-in_time).total_seconds() / 3600.0
                frappe.db.set_value("Attendance",att,'total_working_hours',total_working_hours)
            frappe.db.set_value("Attendance",att,'shift',shift)
            frappe.db.set_value("Attendance",att,'shift_status',shift_status)
            frappe.db.set_value("Attendance",att,'assigned_shift',assigned_shift)
            frappe.db.set_value("Attendance",att,'attended_shift',shift)
            
            frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
            frappe.db.set_value('Employee Checkin',checkin,'attendance',att)

# def mark_attendance_from_checkin(checkin,employee,time):
#     att_time = time.time()
#     att_date = time.date()
#     in_time = ''
#     out_time = ''
#     checkins = frappe.db.sql("""select name,time from `tabEmployee Checkin` where employee = "%s" and date(time) = '%s' order by time """%(employee,att_date),as_dict=True)
#     if checkins:
#         yesterday_date = att_date - timedelta(days=1)

#         # Step 1: Check if yesterday shift is C
#         yesterday_att = frappe.db.get_value(
#             "Attendance",
#             {"employee": employee, "attendance_date": yesterday_date, "shift": "C"},
#             ["name", "out_time", "in_time"]
#         )

#         # Step 2: Choose window based on yesterday shift
#         if yesterday_att:
#             # If yesterday shift is C => treat today's early punches as yesterday's
#             att_date = yesterday_date 
#             start_window = datetime.combine(yesterday_date, datetime.min.time()) + timedelta(hours=10)
#             end_window = datetime.combine(yesterday_date + timedelta(days=1), datetime.min.time()) + timedelta(hours=10)
#             checkins = frappe.db.sql("""
#             SELECT name, time 
#             FROM `tabEmployee Checkin`
#             WHERE employee = %s AND time BETWEEN %s AND %s
#             ORDER BY time
#         """, (employee, start_window, end_window), as_dict=True)

#         # else:
#         #     start_window = datetime.combine(att_date, datetime.min.time())
#         #     end_window = datetime.combine(att_date, datetime.max.time())

#         # Step 3: Fetch checkins
        
#         # if not checkins:
#         #     return
        
#     # Step 4: If yesterday_att exists, try closing yesterday out_time
#         if yesterday_att:
#             before_10 = [c for c in checkins if c.time.time() < datetime.strptime("10:00:00", "%H:%M:%S").time()]
#             after_10 = [c for c in checkins if c.time.time() >= datetime.strptime("10:00:00", "%H:%M:%S").time()]
#             att_name, y_out, y_in = yesterday_att
#             if before_10 and not y_out:
#                 first_punch = before_10[0]
#                 frappe.db.set_value("Attendance", att_name, "out_time", first_punch.time)
#                 total_working_hours = (first_punch.time - y_in).total_seconds() / 3600.0
#                 frappe.db.set_value("Attendance", att_name, "total_working_hours", total_working_hours)
#                 for c in before_10:   # ✅ Link all early punches
#                     frappe.db.set_value('Employee Checkin', c.name, 'attendance', att_name)
#                     frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', '1')
#                 frappe.db.commit()
#             checkins = after_10
#             # checkins = [c for c in checkins if c.time.date() == time.date()]
#             att_date = time.date()
            
#             # for c in checkins:   # ✅ Link all today punches
#             #     frappe.db.set_value('Employee Checkin', c.name, 'attendance', att.name if not isinstance(att, str) else att)
#             #     frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', '1')

#         if len(checkins) >= 2:
#             in_time = checkins[0].time
#             out_time = checkins[-1].time
#         elif len(checkins) == 1:
#             in_time = checkins[0].time
        
#         a = frappe.db.get_value('Attendance',{'employee':employee,'attendance_date':att_date}, ['name'])
        
#         shifta = frappe.db.get_value('Shift Type',{'name':'A'},['checkin_start_time','checkin_end_time'])
#         shiftb = frappe.db.get_value('Shift Type',{'name':'B'},['checkin_start_time','checkin_end_time'])
#         shiftc = frappe.db.get_value('Shift Type',{'name':'C'},['checkin_start_time','checkin_end_time'])
#         shiftg = frappe.db.get_value('Shift Type',{'name':'G'},['checkin_start_time','checkin_end_time'])
#         shiftg1 = frappe.db.get_value('Shift Type',{'name':'G1'},['checkin_start_time','checkin_end_time'])
#         shiftge = frappe.db.get_value('Shift Type',{'name':'GE'},['checkin_start_time','checkin_end_time'])
#         shift_assignment = frappe.db.get_value("Shift Assignment",{"employee":employee,"start_date":att_date, "docstatus": 1},["shift_type"])
#         shift_start_time = frappe.db.get_value('Shift Type',{'name':shift_assignment},['checkin_start_time','checkin_end_time'])
#         shift_type = frappe.db.get_all("Shift Type", ["checkin_start_time"])

#         checkins_time = [shift["checkin_start_time"] for shift in shift_type if shift["checkin_start_time"]]

#         checkins_count = Counter(checkins_time)

#         shift_group = frappe.db.get_value("Employee", {"employee": employee}, "shift_group") or ""
#         shift_type_ = None
#         shift = ''
#         # checkin_datetime = checkins[0].time 
#         if checkins:  
#             checkin_datetime = checkins[0].time
#             # use checkin_datetime safely
#         else:
#             checkin_datetime = None
#         shift_c_start = checkin_datetime.replace(hour=22, minute=0, second=0, microsecond=0) - timedelta(days=1)
#         shift_c_end = shift_c_start + timedelta(hours=4)
#         if (shift_assignment != "C") and shift_start_time:
#             if (datetime.min + shift_start_time[0]).time() < checkins[0].time.time() < (datetime.min + shift_start_time[1]).time():
#                 shift = shift_assignment
#             else:
#                 shift = ''
#         elif shift_assignment == "C" :
#             # if shift_c_start <= checkin_datetime <= shift_c_end:    
#             shift = 'C'
#         elif shift_group and not shift_assignment:
#             # if shift_group.lower() != "rotational":
#                 if any(count > 1 for count in checkins_count.values()):
#                     for shift_item in shift_type:
#                         checkin_start_time = shift_item.get("checkin_start_time")
#                         if checkin_start_time and (datetime.min + checkin_start_time).time() < checkins[0].time.time():
#                             potential_shift = frappe.db.get_value(
#                                 "Shift Type",
#                                 {"shift_group": shift_group, "checkin_start_time": checkin_start_time},
#                                 "name",
#                             )
#                             if potential_shift:
#                                 shift_type_ = potential_shift
#                                 break

#                 if shift_type_:
#                     shift = shift_type_
#                 else:
#                     if (datetime.min + shifta[0]).time() < checkins[0].time.time() < (datetime.min + shifta[1]).time():
#                         shift = 'A'
#                     elif (datetime.min + shiftb[0]).time() < checkins[0].time.time() < (datetime.min + shiftb[1]).time():
#                         shift = 'B'
#                     # elif (datetime.min + shiftc[0]).time() < checkins[0].time.time() < (datetime.min + shiftc[1]).time():
#                     #     shift ='C'
#                     elif shift_c_start <= checkin_datetime <= shift_c_end:
#                         shift = 'C'

#                     elif (datetime.min + shiftg[0]).time() < checkins[0].time.time() < (datetime.min + shiftg[1]).time():
#                         shift ='G'
#                     elif (datetime.min + shiftg1[0]).time() < checkins[0].time.time() < (datetime.min + shiftg1[1]).time():
#                         shift ='G1'
#                     elif (datetime.min + shiftge[0]).time() < checkins[0].time.time() < (datetime.min + shiftge[1]).time():
#                         shift ='GE'
#                     else:
#                         shift = ''
#         elif (datetime.min + shifta[0]).time() < checkins[0].time.time() < (datetime.min + shifta[1]).time():
#             shift = 'A'
#         elif (datetime.min + shiftb[0]).time() < checkins[0].time.time() < (datetime.min + shiftb[1]).time():
#             shift = 'B'
#         # elif (datetime.min + shiftc[0]).time() < checkins[0].time.time() < (datetime.min + shiftc[1]).time():
#         #     shift ='C'
        

#         elif shift_c_start <= checkin_datetime <= shift_c_end:
#             shift = 'C'

#         elif (datetime.min + shiftg[0]).time() < checkins[0].time.time() < (datetime.min + shiftg[1]).time():
#             shift ='G'
#         elif (datetime.min + shiftg1[0]).time() < checkins[0].time.time() < (datetime.min + shiftg1[1]).time():
#             shift ='G1'
#         elif (datetime.min + shiftge[0]).time() < checkins[0].time.time() < (datetime.min + shiftge[1]).time():
#             shift ='GE'
#         # elif shift_group:
#         #     if shift_group.lower() == "rotational":
#         #         if any(count > 1 for count in checkins_count.values()):
#         #             for shift_item in shift_type:
#         #                 checkin_start_time = shift_item.get("checkin_start_time")
#         #                 if checkin_start_time and (datetime.min + checkin_start_time).time() < checkins[0].time.time():
#         #                     potential_shift = frappe.db.get_value(
#         #                         "Shift Type",
#         #                         {"shift_group": shift_group, "checkin_start_time": checkin_start_time},
#         #                         "name",
#         #                     )
#         #                     if potential_shift:
#         #                         shift_type_ = potential_shift
#         #                         break

#         #         if shift_type_:
#         #             shift = shift_type_
#         #         else:
#         #             shift = ''
#         else: 
#             shift_value=frappe.db.get_value('Employee',{'name':employee},['default_shift'])
#             if shift_value:
#                 shift = shift_value
#             else:
#                 shift = ''
#         att = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date})
#         attended_shift = shift
#         assigned_shift = ''
#         if frappe.db.get_value("Shift Assignment",{"employee":employee,"start_date":att_date, "docstatus": 1},["shift_type"]):
#             assigned_shift = frappe.db.get_value("Shift Assignment",{"employee":employee,"start_date":att_date, "docstatus": 1},["shift_type"])
        
#         # elif shift_group:
#         #     if any(count > 1 for count in checkins_count.values()):
#         #         for shift_item in shift_type:
#         #             checkin_start_time = shift_item.get("checkin_start_time")
#         #             if checkin_start_time and (datetime.min + checkin_start_time).time() < checkins[0].time.time():
#         #                 potential_shift = frappe.db.get_value(
#         #                     "Shift Type",
#         #                     {"shift_group": shift_group, "checkin_start_time": checkin_start_time},
#         #                     "name",
#         #                 )
#         #                 if potential_shift:
#         #                     shift_type_ = potential_shift
#         #                     break

#             # if shift_type_:
#             #     assigned_shift = shift_type_
#             # else:
#             #     assigned_shift = frappe.db.get_value('Employee',{'name':employee},['default_shift'])

#         elif shift_group:
#             if shift_group.lower() == "rotational":
#                 # fetch all rotational shifts (A, B, C)
#                 rotational_shifts = frappe.db.get_all(
#                     "Shift Type",
#                     filters={"shift_group": "Rotational"},
#                     fields=["name", "checkin_start_time", "checkin_end_time", "night_shift"]
#                 )
#                 punch_time = checkins[0].get("time").time()

#                 for s in rotational_shifts:
#                     start_time = (datetime.min + s["checkin_start_time"]).time()
#                     end_time   = (datetime.min + s["checkin_end_time"]).time()

#                     if is_in_shift(punch_time, s["checkin_start_time"], s["checkin_end_time"], is_night=s.get("night_shift")):
#                         assigned_shift = s["name"]
#                         break

#             else:
#                 shift_from_group = frappe.db.get_value(
#                     "Shift Type",
#                     {"shift_group": shift_group},
#                     "name"
#                 )
#                 dshift = frappe.db.get_value("Employee", {"name": employee}, "default_shift")
#                 if shift_from_group:
#                     assigned_shift = shift_from_group
#                 else:
#                     if dshift :
#                         shift = dshift
#                     else:
#                         shift=''
#         else:
#             assigned_shift = frappe.db.get_value('Employee',{'name':employee},['default_shift'])
#         if assigned_shift == attended_shift:
#             shift_status = "Matched"
#         else:
#             shift_status = "Unmatched"
#         if not att and checkin:
#             att = frappe.new_doc("Attendance")
#             att.employee = employee
#             att.attendance_date = att_date
#             att.shift = shift
#             att.status = "Absent"
#             att.in_time = in_time
#             att.out_time = out_time
#             att.assigned_shift = assigned_shift
#             att.attended_shift = shift
#             att.shift_status = shift_status
#             att.session_from_time = "00:00:00"
#             att.session_to_time = "00:00:00"
#             att.late_entry_time = "00:00:00"
#             att.ot_hours = "00:00:00"
#             if in_time and out_time:
#                 total_working_hours = (out_time-in_time).total_seconds() / 3600.0
#                 att.total_working_hours=total_working_hours
#                 if total_working_hours > 8:
#                     att.save(ignore_permissions=True)
#                     att.submit()
#             att.save(ignore_permissions=True)
#             frappe.db.commit()
#             frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
#             frappe.db.set_value('Employee Checkin',checkin,'attendance',att.name)
#             return att.name
#         else:
#             if in_time:
#                 frappe.db.set_value("Attendance",att,'in_time',in_time)
#             if out_time:
#                 frappe.db.set_value("Attendance",att,'out_time',out_time)
#             if in_time and out_time:
#                 total_working_hours = (out_time-in_time).total_seconds() / 3600.0
#                 frappe.db.set_value("Attendance",att,'total_working_hours',total_working_hours)
#             frappe.db.set_value("Attendance",att,'shift',shift)
#             frappe.db.set_value("Attendance",att,'shift_status',shift_status)
#             frappe.db.set_value("Attendance",att,'assigned_shift',assigned_shift)
#             frappe.db.set_value("Attendance",att,'attended_shift',shift)
            
#             frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
#             frappe.db.set_value('Employee Checkin',checkin,'attendance',att)


def is_in_shift(punch_time, start, end, is_night=False):
    punch_seconds = punch_time.hour*3600 + punch_time.minute*60 + punch_time.second
    start_seconds = start.total_seconds()
    end_seconds = end.total_seconds()

    if is_night and start_seconds > end_seconds:
        # Example: 22:00 (79200) → 02:00 (7200 next day)
        return punch_seconds >= start_seconds or punch_seconds <= end_seconds
    else:
        return start_seconds <= punch_seconds <= end_seconds


def to_time(td):
    """Convert timedelta → datetime.time"""
    return (datetime.min + td).time() if td else None

@frappe.whitelist()
def assigned_shift(from_date, to_date):
    attendance = frappe.db.get_all(
        'Attendance',
        filters={'attendance_date': ('between', (from_date, to_date)),'docstatus': ('!=', '2'),"in_time": ["is", "not set"]},
        fields=['name', 'attendance_date', 'assigned_shift','employee']
    )

    for att in attendance:
        shift_group = frappe.db.get_value("Employee", {"employee": att.employee}, "shift_group")
        if shift_group:
            shift_list = frappe.db.get_all("Shift Type", {'shift_group':shift_group},'name')
            if shift_list:
                total = len(shift_list)
                if total == 1:
                    
                    assigned_shift = shift_list[0].get('name')
                else :
                    assigned_shift = frappe.db.get_value('Employee',{'name':att.employee},['default_shift']) or ""
            else :
                assigned_shift = frappe.db.get_value('Employee',{'name':att.employee},['default_shift']) or ""
        else:
            assigned_shift = frappe.db.get_value('Employee',{'name':att.employee},['default_shift'])        
        frappe.db.set_value("Attendance",att.name,'assigned_shift',assigned_shift)    

@frappe.whitelist()
def assigned_shift_emp(from_date, to_date,employee):
    attendance = frappe.db.get_all(
        'Attendance',
        filters={'attendance_date': ('between', (from_date, to_date)),'employee': employee, 'docstatus': ('!=', '2'),"in_time": ["is", "not set"]},
        fields=['name', 'attendance_date', 'assigned_shift','employee']
    )
    for att in attendance:
        shift_group = frappe.db.get_value("Employee", {"employee": att.employee}, "shift_group")
        if frappe.db.get_value("Shift Assignment",{"employee":att.employee,"start_date":att.attendance_date, "docstatus": 1},["shift_type"]):
            assigned_shift = frappe.db.get_value("Shift Assignment",{"employee":att.employee,"start_date":att.attendance_date, "docstatus": 1},["shift_type"])

        elif shift_group:
            shift_list = frappe.db.get_all("Shift Type", {'shift_group':shift_group},'name')
            if shift_list:
                total = len(shift_list)
                if total == 1:
                    
                    assigned_shift = shift_list[0].get('name')
                else :
                    assigned_shift = frappe.db.get_value('Employee',{'name':att.employee},['default_shift']) or ""
            else :
                assigned_shift = frappe.db.get_value('Employee',{'name':att.employee},['default_shift']) or ""
        else:
            assigned_shift = frappe.db.get_value('Employee',{'name':att.employee},['default_shift'])        
        frappe.db.set_value("Attendance",att.name,'assigned_shift',assigned_shift)    


@frappe.whitelist()    
def mark_absent(from_date,to_date):
    dates = get_dates(from_date,to_date)
    for date in dates:
        employee = frappe.db.get_all('Employee',{'status':'Active','date_of_joining':['<=',from_date]},['*'])
        for emp in employee:
            hh = check_holiday(date,emp.name)
            if not hh:
                if not frappe.db.exists('Attendance',{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')}):
                    # if emp.employment_type =='None':
                    #     # att.employment_type =''
                    #     frappe.db.set_value('Employee', emp.name, 'employment_type', '')
                    att = frappe.new_doc('Attendance')
                    att.employee = emp.name
                    att.status = 'Absent'
                    att.attendance_date = date
                    att.session_from_time = "00:00:00"
                    att.session_to_time = "00:00:00"
                    att.late_entry_time = "00:00:00"
                    att.ot_hours = "00:00:00"
                    att.save(ignore_permissions=True)
                    frappe.db.commit()
                    # att.submit()   

def check_holiday(date,emp):
    holiday_list = frappe.db.get_value('Employee',emp,'holiday_list')
    sa = frappe.db.get_value("Shift Assignment",{"employee":emp,"start_date":date, "docstatus": 1},["shift_type"])
    holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
    left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
    if holiday:
        if holiday[0].weekly_off == 1:
            return "WW"
        else:
            return "HH"
    if sa == "WW":
        return "WW"
    

def check_holiday_new(date,emp):
    holiday_list = frappe.db.get_value('Employee',emp,'holiday_list')
    # sa = frappe.db.get_value("Shift Assignment",{"employee":emp,"start_date":date, "docstatus": 1},["shift_type"])
    # holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
    # left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
    holiday = frappe.db.sql(
        """
        SELECT
            `tabHoliday`.holiday_date,
            `tabHoliday`.weekly_off
        FROM `tabHoliday List`
        LEFT JOIN `tabHoliday`
            ON `tabHoliday`.parent = `tabHoliday List`.name
        WHERE
            `tabHoliday List`.name = %s
            AND `tabHoliday`.holiday_date = %s
        """,
        (holiday_list, date),
        as_dict=True
    )
    print(date)
    print(holiday , "HOLIDAYS")
    if holiday:
        if holiday[0].weekly_off == 1:
            return "WW"
        else:
            return "HH"
    else:
        return ""    
        
def get_dates(from_date,to_date):
    """get list of dates in between from date and to date"""
    no_of_days = date_diff(add_days(to_date, 1), from_date)
    dates = [add_days(from_date, i) for i in range(0, no_of_days)]
    return dates


@frappe.whitelist()
def unque_serial_number():

# API URL and parameters
    url = "http://115.244.98.52:86/api/v2/WebAPI/GetDeviceLogs"
    params = {
        "APIKey": "162618022422",
        "FromDate": "2024-12-02",
        "ToDate": "2024-12-02"
    }

    # Make the GET request
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        
        # Extract all SerialNumbers
        serial_numbers = {entry["SerialNumber"] for entry in data if "SerialNumber" in entry}

        print(f"Unique Serial Numbers: {serial_numbers}")
    else:
        print(f"Error: {response.status_code}, {response.text}")


@frappe.whitelist()    
def mark_absent_with_employee(from_date,to_date,employee):
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
                    att.session_from_time = "00:00:00"
                    att.session_to_time = "00:00:00"
                    att.late_entry_time = "00:00:00"
                    att.ot_hours = "00:00:00"
                    att.save(ignore_permissions=True)
                    frappe.db.commit()  

import datetime as dt
from datetime import datetime, timedelta

@frappe.whitelist()
def mark_late_in(from_date, to_date):
    attendance = frappe.db.get_all(
        'Attendance',
        {'attendance_date': ('between', (from_date, to_date)), 'docstatus': ('!=', '2')},
        ['*']
    )
    for att in attendance:
        if att.shift and att.in_time:
            shift_time = frappe.get_value(
                "Shift Type", {'name': att.shift}, ["start_time"]
            )
            shift_start_time = datetime.strptime(
                str(shift_time), '%H:%M:%S'
            ).time()
            start_time = dt.datetime.combine(att.attendance_date, shift_start_time)

            if att.in_time > start_time:
                late_entry_time = att.in_time - start_time
                if late_entry_time > timedelta(minutes=1):
                    frappe.db.set_value('Attendance', att.name, 'late_entry', 1)
                    late_entry_time_str = str(late_entry_time).split(",")[-1].strip() 
                    frappe.db.set_value('Attendance', att.name, 'late_entry_time', late_entry_time_str)
                else:
                    frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
                    frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
            else:
                frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
                frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")

            # Ensure status is updated correctly
            if timedelta(hours=0, minutes=0, seconds=0) < att.in_time - start_time < timedelta(hours=0, minutes=15, seconds=59):
                if att.status == "Half Day":
                    frappe.db.set_value("Attendance", att.name, "status", "Present")
                    doc = frappe.get_doc("Attendance", att.name)
                    doc.submit()
            elif att.in_time - start_time > timedelta(hours=2, minutes=00, seconds=00):
                if att.status == "Half Day":
                    frappe.db.set_value("Attendance", att.name, "status", "Absent")
                elif att.status == "Present":
                    frappe.db.set_value("Attendance", att.name, "status", "Half Day")


@frappe.whitelist()
def mark_late_in_with_employee(from_date, to_date,employee):
    attendance = frappe.db.get_all(
        'Attendance',
        {'attendance_date': ('between', (from_date, to_date)), 'docstatus': ('!=', '2'),'employee':employee},
        ['*']
    )
    for att in attendance:
        if att.shift and att.in_time:
            shift_time = frappe.get_value(
                "Shift Type", {'name': att.shift}, ["start_time"]
            )
            shift_start_time = datetime.strptime(
                str(shift_time), '%H:%M:%S'
            ).time()
            start_time = dt.datetime.combine(att.attendance_date, shift_start_time)

            if att.in_time > start_time:
                late_entry_time = att.in_time - start_time
                if late_entry_time > timedelta(minutes=1):
                    frappe.db.set_value('Attendance', att.name, 'late_entry', 1)
                    late_entry_time_str = str(late_entry_time).split(",")[-1].strip() 
                    frappe.db.set_value('Attendance', att.name, 'late_entry_time', late_entry_time_str)
                else:
                    frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
                    frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
            else:
                frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
                frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")

            # Ensure status is updated correctly
            if timedelta(hours=0, minutes=0, seconds=0) < att.in_time - start_time < timedelta(hours=0, minutes=15, seconds=59):
                if att.status == "Half Day" and att.shift_status =="Matched":
                    frappe.db.set_value("Attendance", att.name, "status", "Present")
                    doc = frappe.get_doc("Attendance", att.name)
                    doc.submit()
            elif att.in_time - start_time > timedelta(hours=2, minutes=00, seconds=00):
                if att.status == "Half Day":
                    frappe.db.set_value("Attendance", att.name, "status", "Absent")
                elif att.status == "Present":
                    frappe.db.set_value("Attendance", att.name, "status", "Half Day")
@frappe.whitelist()
def time_diff_in_timedelta_1(time1, time2):
    datetime1 = datetime.combine(datetime.min, time1)
    datetime2 = datetime.combine(datetime.min, time2)
    timedelta_seconds = (datetime2 - datetime1).total_seconds()
    diff_timedelta = timedelta(seconds=timedelta_seconds)
    return diff_timedelta
                
@frappe.whitelist()
def ot_calculation(from_date,to_date):
    dates = get_dates(from_date,to_date)
    for date in dates:
        attendance = frappe.db.sql("""select in_time,out_time,shift,attendance_date,employee,name from `tabAttendance` where attendance_date between '%s' and '%s' and docstatus IN (0, 1) """%(from_date,to_date),as_dict=True)
        for att in attendance:
            hh = check_holiday(date,att.employee)
            if not hh:
                ot_eligible = frappe.db.get_value('Employee', {"name": att.employee}, 'ot_eligibility')
                if ot_eligible == "Over Time":
                    ot_hours = '00:00:00'
                    # before_ot = timedelta()
                    after_ot = timedelta()
                    if att.shift and att.out_time and att.in_time :   
                        # shift_st = frappe.db.get_value("Shift Type",{'name':att.shift},['start_time'])
                        shift_et = frappe.db.get_value("Shift Type",{'name':att.shift},['end_time'])
                        # night_shift = frappe.db.get_value("Shift Type",{"name":att.shift},["night_shift"])
                        in_time = datetime.strptime(str(att.in_time),'%Y-%m-%d %H:%M:%S').time()
                        # shift_st_time = datetime.strptime(str(shift_st), '%H:%M:%S').time()
                        # if shift_st_time > in_time:
                        #     before_ot = time_diff_in_timedelta_1(in_time,shift_st_time)
                        #     frappe.db.set_value("Attendance",att.name,"before_ot",before_ot)
                        # if night_shift == 1:
                        #     if att.attendance_date != datetime.date(att.out_time):
                        #         out_time = datetime.strptime(str(att.out_time),'%Y-%m-%d %H:%M:%S').time()
                        #         shift_et = datetime.strptime(str(shift_et), '%H:%M:%S').time()
                        #         print()
                        #         if shift_et < out_time:
                        #             after_ot = time_diff_in_timedelta_1(shift_et,out_time)
                        #             frappe.db.set_value("Attendance",att.name,"after_ot",after_ot)
                                    
                        #             # difference = before_ot + after_ot 
                        #             difference = after_ot
                        #             print(before_ot , "Before  OT")
                        #             print(after_ot , "After OT")
                        #             diff_time = datetime.strptime(str(difference), '%H:%M:%S').time()
                        #             print(diff_time , "diff_time")
                        #             if difference > timedelta(hours=23, minutes=59, seconds=50):
                        #                 ot_hours = time(23, 0, 0) 
                        #             else:
                        #                 if diff_time.hour > 0:
                        #                     if diff_time.minute >= 30:
                        #                         ot_hours = time(diff_time.hour,30,0)
                        #                     else:
                        #                         ot_hours = time(diff_time.hour,0,0)
                        #                 else:
                        #                     ot_hours = "00:00:00"
                        #         else:
                        #             ot_hours = "00:00:00"
                        #     else:
                        #         ot_hours = "00:00:00"
                        #     print(att.name)
                        #     print('OT')
                        #     print(ot_hours)
                        #     frappe.db.set_value("Attendance",att.name,"ot_hours",ot_hours)
                        #     if ot_hours !='00:00:00':
                        #         ftr = [3600,60,1]
                        #         hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
                        #         ot_hr = round(hr/3600,1)
                        #     else:
                        #         ot_hr = '0.0'	
                        #     frappe.db.set_value("Attendance",att.name,"overtime_hours",ot_hr)
                        # else:
                        out_time = datetime.strptime(str(att.out_time),'%Y-%m-%d %H:%M:%S').time()
                        shift_et = datetime.strptime(str(shift_et), '%H:%M:%S').time()
                        if shift_et < out_time:
                            after_ot = time_diff_in_timedelta_1(shift_et,out_time)
                            frappe.db.set_value("Attendance",att.name,"after_ot",after_ot)
                            # difference = before_ot + after_ot
                            difference = after_ot
                            print(att.name , "Attendance Name")
                            # print(before_ot , "Before  OT")
                            print(after_ot , "After OT")
                            print(difference , "difference")
                            diff_time = datetime.strptime(str(difference), '%H:%M:%S').time()
                            print(diff_time , "diff_time")
                            if difference > timedelta(hours=23, minutes=59, seconds=50):
                                    ot_hours = time(23, 0, 0) 
                            else:
                                if diff_time.hour > 0:
                                    print("1")
                                    if diff_time.minute >= 30:
                                        print("2")
                                        ot_hours = time(diff_time.hour,30,0)
                                    else:
                                        print("3")
                                        ot_hours = time(diff_time.hour,0,0)
                                else:
                                    print("4")
                                    ot_hours = "00:00:00"
                        else:
                            print("5")
                            ot_hours = "00:00:00"
                        frappe.db.set_value("Attendance",att.name,"ot_hours",ot_hours)
                        print("6")
                        if ot_hours !='00:00:00':
                            print("7")
                            ftr = [3600,60,1]
                            hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
                            ot_hr = round(hr/3600,1)
                        else:
                            ot_hr = '0.0'	
                            print("8")
                        frappe.db.set_value("Attendance",att.name,"overtime_hours",ot_hr)    

                    else:    
                        ot_hr = '0.0'
                        frappe.db.set_value("Attendance",att.name,"ot_hours","00:00:00")
                        frappe.db.set_value("Attendance",att.name,"overtime_hours","0.0")
                        # create_update_delete_ot(att, ot_hr)        
                else:
                    ot_hr = '0.0'
                    frappe.db.set_value("Attendance",att.name,"ot_hours","00:00:00")
                    frappe.db.set_value("Attendance",att.name,"overtime_hours","0.0") 
                create_update_delete_ot(att, ot_hr)            
            else:
                print("HHI11")
                ot_eligible = frappe.db.get_value('Employee', {"name": att.employee}, 'ot_eligibility')
                if ot_eligible == "Over Time":
                    if att.shift and att.out_time and att.in_time :
                        shift_st = frappe.db.get_value("Shift Type",{'name':att.shift},['start_time'])
                        shift_st_time = datetime.strptime(str(shift_st), "%H:%M:%S").time()
                        print(shift_st_time , "shift_st_time")
                        shift_dt = datetime.combine(att.attendance_date, shift_st_time)
                        print(shift_dt,"shift_dt")
                        if att.shift == "C":
                            yes_att = att.attendance_date - timedelta(days=1)
                            shift_dt = datetime.combine(yes_att, shift_st_time)
                        if att.in_time > shift_dt :
                            in_time = att.in_time
                            out_time = att.out_time
                        else:
                            in_time = shift_dt 
                            if att.out_time >= shift_dt:
                                out_time = att.out_time
                            else:
                                out_time = shift_dt
                        # if att.out_time >= shift_dt :
                        #     out_time = att.out_time
                        # else:
                        #     if att.in_time >=
                        #     out_time = shift_dt
                        print(in_time , "IN time")
                        print(out_time , "OUT time")
                        print(att.employee)
                        print(att.shift)
                        print(att.attendance_date)
                        difference = out_time - in_time
                        print(difference)
                        diff_time = datetime.strptime(str(difference), '%H:%M:%S').time()
                        if difference > timedelta(hours=23, minutes=59, seconds=50):
                            ot_hours = time(23, 0, 0) 
                        else:
                            if diff_time.hour > 0:
                                print("1")
                                if diff_time.minute >= 30:
                                    print("2")
                                    ot_hours = time(diff_time.hour,30,0)
                                else:
                                    print("3")
                                    ot_hours = time(diff_time.hour,0,0)
                            else:
                                print("4")
                                ot_hours = "00:00:00"
                        frappe.db.set_value("Attendance",att.name,"ot_hours",ot_hours)
                        if ot_hours !='00:00:00':
                            ftr = [3600,60,1]
                            hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
                            ot_hr = round(hr/3600,1)
                        else:
                            ot_hr = '0.0'	
                        frappe.db.set_value("Attendance",att.name,"overtime_hours",ot_hr)  
                        # create_update_delete_ot(att, ot_hr) 
                    else:    
                        ot_hr = '0.0'
                        frappe.db.set_value("Attendance",att.name,"ot_hours","00:00:00")
                        frappe.db.set_value("Attendance",att.name,"overtime_hours","0.0")
                        # create_update_delete_ot(att, ot_hr)     
                else:
                    ot_hr = '0.0'
                    frappe.db.set_value("Attendance",att.name,"ot_hours","00:00:00")
                    frappe.db.set_value("Attendance",att.name,"overtime_hours","0.0") 
            create_update_delete_ot(att, ot_hr) 
# @frappe.whitelist()
# def ot_calculation_with_employee(from_date,to_date,employee):
#     dates = get_dates(from_date,to_date)
#     for date in dates:
#         print("1")
#         print("1st")
#         print("2st")
#         attendance = frappe.db.sql("""select * from `tabAttendance` where attendance_date ='%s'  and docstatus IN (0, 1) and employee ='%s'"""%(date,employee),as_dict=True)
#         for att in attendance:
#             print("2")
#             print("HHI")
#             hh = check_holiday(date,att.employee)
#             if not hh:
#                 print("HHI1")
#                 ot_eligible = frappe.db.get_value('Employee', {"name": att.employee}, 'ot_eligibility')
#                 if ot_eligible == "Over Time":
#                     ot_hours = '00:00:00'
#                     before_ot = timedelta()
#                     after_ot = timedelta()
#                     if att.shift and att.out_time and att.in_time :   
#                         shift_st = frappe.db.get_value("Shift Type",{'name':att.shift},['start_time'])
#                         shift_et = frappe.db.get_value("Shift Type",{'name':att.shift},['end_time'])
#                         night_shift = frappe.db.get_value("Shift Type",{"name":att.shift},["night_shift"])
#                         in_time = datetime.strptime(str(att.in_time),'%Y-%m-%d %H:%M:%S').time()
#                         shift_st_time = datetime.strptime(str(shift_st), '%H:%M:%S').time()
#                         if shift_st_time > in_time:
#                             before_ot = time_diff_in_timedelta_1(in_time,shift_st_time)
#                             frappe.db.set_value("Attendance",att.name,"before_ot",before_ot)
#                         if night_shift == 1:
#                             if att.attendance_date != datetime.date(att.out_time):
#                                 out_time = datetime.strptime(str(att.out_time),'%Y-%m-%d %H:%M:%S').time()
#                                 shift_et = datetime.strptime(str(shift_et), '%H:%M:%S').time()
#                                 print(out_time)
#                                 print(shift_et)
#                                 if shift_et < out_time:
#                                     # before_ot = time_diff_in_timedelta_1(in_time,shift_st_time)
#                                     after_ot = time_diff_in_timedelta_1(shift_et,out_time)
#                                     frappe.db.set_value("Attendance",att.name,"after_ot",after_ot)
#                                     # difference = before_ot + after_ot 
#                                     difference = after_ot
#                                     print(before_ot , "Before  OT")
#                                     print(after_ot , "After OT")
#                                     diff_time = datetime.strptime(str(difference), '%H:%M:%S').time()
#                                     # total_seconds = difference.total_seconds()
#                                     # hours = int(total_seconds // 3600)
#                                     # minutes = int((total_seconds % 3600) // 60)
#                                     # seconds = int(total_seconds % 60)
#                                     # diff_time = time(hours, minutes, seconds)
#                                     print(diff_time)
#                                     if difference > timedelta(hours=23, minutes=59, seconds=50):
#                                         ot_hours = time(23, 0, 0) 
#                                     else:
#                                         if diff_time.hour > 0:
#                                             if diff_time.minute >= 30:
#                                                 ot_hours = time(diff_time.hour,30,0)
#                                             else:
#                                                 ot_hours = time(diff_time.hour,0,0)
#                                         else:
#                                             ot_hours = "00:00:00"
#                                 else:
#                                     ot_hours = "00:00:00"
#                             else:
#                                 ot_hours = "00:00:00"
                            
#                             frappe.db.set_value("Attendance",att.name,"ot_hours",ot_hours)
#                             if ot_hours !='00:00:00':
#                                 ftr = [3600,60,1]
#                                 hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
#                                 ot_hr = round(hr/3600,1)
#                             else:
#                                 ot_hr = '0.0'	
#                             frappe.db.set_value("Attendance",att.name,"overtime_hours",ot_hr)
#                             create_update_delete_ot(att, ot_hr)
#                         else:
#                             out_time = datetime.strptime(str(att.out_time),'%Y-%m-%d %H:%M:%S').time()
#                             shift_et = datetime.strptime(str(shift_et), '%H:%M:%S').time()
#                             if shift_et < out_time:
#                                 after_ot = time_diff_in_timedelta_1(shift_et,out_time)
#                                 frappe.db.set_value("Attendance",att.name,"after_ot",after_ot)
#                                 # difference = before_ot + after_ot
#                                 difference = after_ot
#                                 print(before_ot , "Before  OT")
#                                 print(after_ot , "After OT")
#                                 diff_time = datetime.strptime(str(difference), '%H:%M:%S').time()
#                                 if diff_time.hour > 0:
#                                     if diff_time.minute >= 30:
#                                         ot_hours = time(diff_time.hour,30,0)
#                                     else:
#                                         ot_hours = time(diff_time.hour,0,0)
#                                 else:
#                                     ot_hours = "00:00:00"
#                             else:
#                                 ot_hours = "00:00:00"
                            
#                             frappe.db.set_value("Attendance",att.name,"ot_hours",ot_hours)
#                             if ot_hours !='00:00:00':
#                                 ftr = [3600,60,1]
#                                 hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
#                                 ot_hr = round(hr/3600,1)
#                             else:
#                                 ot_hr = '0.0'	
#                             frappe.db.set_value("Attendance",att.name,"overtime_hours",ot_hr) 
#                             create_update_delete_ot(att, ot_hr)
#                     else:    
#                         ot_hr = '0.0'
#                         frappe.db.set_value("Attendance",att.name,"ot_hours","00:00:00")
#                         frappe.db.set_value("Attendance",att.name,"overtime_hours","0.0")
#                         create_update_delete_ot(att, ot_hr)
#                 else:
#                     ot_hr = '0.0'
#                     frappe.db.set_value("Attendance",att.name,"ot_hours","00:00:00")
#                     frappe.db.set_value("Attendance",att.name,"overtime_hours","0.0") 
#                     create_update_delete_ot(att, ot_hr)
#             if hh:
#                 print("HHI11")
#                 ot_eligible = frappe.db.get_value('Employee', {"name": att.employee}, 'ot_eligibility')
#                 if ot_eligible == "Over Time":
#                     if att.shift and att.out_time and att.in_time :
#                         shift_st = frappe.db.get_value("Shift Type",{'name':att.shift},['start_time'])
#                         shift_st_time = datetime.strptime(str(shift_st), "%H:%M:%S").time()
#                         print(shift_st_time , "shift_st_time")
#                         shift_dt = datetime.combine(att.attendance_date, shift_st_time)
#                         print(shift_dt,"shift_dt")
#                         if att.shift == "C":
#                             yes_att = att.attendance_date - timedelta(days=1)
#                             shift_dt = datetime.combine(yes_att, shift_st_time)
#                         if att.in_time > shift_dt :
#                             in_time = att.in_time
#                         else:
#                             in_time = shift_dt   
#                         out_time = att.out_time
#                         print(in_time , "IN time")
#                         print(out_time , "OUT time")
#                         print(att.shift)
#                         print(att.attendance_date)
#                         difference = out_time - in_time
#                         print(difference)
#                         diff_time = datetime.strptime(str(difference), '%H:%M:%S').time()
#                         if diff_time.hour > 0:
#                             if diff_time.minute >= 30:
#                                 ot_hours = time(diff_time.hour,30,0)
#                             else:
#                                 ot_hours = time(diff_time.hour,0,0)
#                         else:
#                             ot_hours = "00:00:00"
#                         frappe.db.set_value("Attendance",att.name,"ot_hours",ot_hours)
#                         if ot_hours !='00:00:00':
#                             ftr = [3600,60,1]
#                             hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
#                             ot_hr = round(hr/3600,1)
#                         else:
#                             ot_hr = '0.0'	
#                         frappe.db.set_value("Attendance",att.name,"overtime_hours",ot_hr)  
#                         create_update_delete_ot(att, ot_hr) 
#                     else:    
#                         ot_hr = '0.0'
#                         frappe.db.set_value("Attendance",att.name,"ot_hours","00:00:00")
#                         frappe.db.set_value("Attendance",att.name,"overtime_hours","0.0")
#                         create_update_delete_ot(att, ot_hr)     
#                 else:
#                     ot_hr = '0.0'
#                     frappe.db.set_value("Attendance",att.name,"ot_hours","00:00:00")
#                     frappe.db.set_value("Attendance",att.name,"overtime_hours","0.0") 
#                     create_update_delete_ot(att, ot_hr)        

@frappe.whitelist()
def ot_calculation_with_employee(from_date,to_date,employee):
    dates = get_dates(from_date,to_date)
    for date in dates:
        print("1")
        print("1st")
        print("2st")
        attendance = frappe.db.sql("""select * from `tabAttendance` where attendance_date ='%s'  and docstatus IN (0, 1) and employee ='%s'"""%(date,employee),as_dict=True)
        for att in attendance:
            print("2")
            print("HHI")
            hh = check_holiday(date,att.employee)
            if not hh:
                print("HHI1")
                ot_eligible = frappe.db.get_value('Employee', {"name": att.employee}, 'ot_eligibility')
                if ot_eligible == "Over Time":
                    ot_hours = '00:00:00'
                    after_ot = timedelta()
                    if att.shift and att.out_time and att.in_time :   
                        shift_et = frappe.db.get_value("Shift Type",{'name':att.shift},['end_time'])
                        out_time = datetime.strptime(str(att.out_time),'%Y-%m-%d %H:%M:%S').time()
                        shift_et = datetime.strptime(str(shift_et), '%H:%M:%S').time()
                        if shift_et < out_time:
                            after_ot = time_diff_in_timedelta_1(shift_et,out_time)
                            frappe.db.set_value("Attendance",att.name,"after_ot",after_ot)
                            difference = after_ot
                            print(after_ot , "After OT")
                            diff_time = datetime.strptime(str(difference), '%H:%M:%S').time()
                            if difference > timedelta(hours=23, minutes=59, seconds=50):
                                ot_hours = time(23, 0, 0) 
                            else:
                                if diff_time.hour > 0:
                                    if diff_time.minute >= 30:
                                        ot_hours = time(diff_time.hour,30,0)
                                    else:
                                        ot_hours = time(diff_time.hour,0,0)
                                else:
                                    ot_hours = "00:00:00"                        
                            frappe.db.set_value("Attendance",att.name,"ot_hours",ot_hours)
                            if ot_hours !='00:00:00':
                                ftr = [3600,60,1]
                                hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
                                ot_hr = round(hr/3600,1)
                            else:
                                ot_hr = '0.0'	
                            frappe.db.set_value("Attendance",att.name,"overtime_hours",ot_hr) 
                    else:    
                        ot_hr = '0.0'
                        frappe.db.set_value("Attendance",att.name,"ot_hours","00:00:00")
                        frappe.db.set_value("Attendance",att.name,"overtime_hours","0.0")
                        # create_update_delete_ot(att, ot_hr)
                else:
                    ot_hr = '0.0'
                    frappe.db.set_value("Attendance",att.name,"ot_hours","00:00:00")
                    frappe.db.set_value("Attendance",att.name,"overtime_hours","0.0") 
                    # create_update_delete_ot(att, ot_hr)
            if hh:
                print("HHI11")
                ot_eligible = frappe.db.get_value('Employee', {"name": att.employee}, 'ot_eligibility')
                if ot_eligible == "Over Time":
                    if att.shift and att.out_time and att.in_time :
                        shift_st = frappe.db.get_value("Shift Type",{'name':att.shift},['start_time'])
                        shift_st_time = datetime.strptime(str(shift_st), "%H:%M:%S").time()
                        print(shift_st_time , "shift_st_time")
                        shift_dt = datetime.combine(att.attendance_date, shift_st_time)
                        print(shift_dt,"shift_dt")
                        if att.shift == "C":
                            yes_att = att.attendance_date - timedelta(days=1)
                            shift_dt = datetime.combine(yes_att, shift_st_time)
                        if att.in_time > shift_dt :
                            in_time = att.in_time
                        else:
                            in_time = shift_dt   
                        out_time = att.out_time
                        print(in_time , "IN time")
                        print(out_time , "OUT time")
                        print(att.shift)
                        print(att.attendance_date)
                        difference = out_time - in_time
                        print(difference)
                        diff_time = datetime.strptime(str(difference), '%H:%M:%S').time()
                        if diff_time.hour > 0:
                            if diff_time.minute >= 30:
                                ot_hours = time(diff_time.hour,30,0)
                            else:
                                ot_hours = time(diff_time.hour,0,0)
                        else:
                            ot_hours = "00:00:00"
                        frappe.db.set_value("Attendance",att.name,"ot_hours",ot_hours)
                        if ot_hours !='00:00:00':
                            ftr = [3600,60,1]
                            hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
                            ot_hr = round(hr/3600,1)
                        else:
                            ot_hr = '0.0'	
                        frappe.db.set_value("Attendance",att.name,"overtime_hours",ot_hr)  
                        # create_update_delete_ot(att, ot_hr) 
                    else:    
                        ot_hr = '0.0'
                        frappe.db.set_value("Attendance",att.name,"ot_hours","00:00:00")
                        frappe.db.set_value("Attendance",att.name,"overtime_hours","0.0")
                        # create_update_delete_ot(att, ot_hr)     
                else:
                    ot_hr = '0.0'
                    frappe.db.set_value("Attendance",att.name,"ot_hours","00:00:00")
                    frappe.db.set_value("Attendance",att.name,"overtime_hours","0.0") 
                    # create_update_delete_ot(att, ot_hr) z       
            create_update_delete_ot(att, ot_hr)


@frappe.whitelist()
def create_attendance_permission_for_all_emp_late(from_date, to_date):
    attedance = frappe.db.get_all("Attendance",
                                  {"attendance_date": ["BETWEEN", [from_date, to_date]]},
                                  ['in_time','out_time','shift','assigned_shift','late_entry_check','leave_application','employee','attendance_date','name','employment_type'])
    for att in attedance:
        if att.employment_type != "Contract":
            print(att.employee)
            print(att.name)
            if att.leave_application:
                break
            if att.in_time and att.shift and att.assigned_shift:
                print("HI HI 1")
                shift_start_time = frappe.db.get_value("Shift Type", att.shift, ["start_time"])
                if not shift_start_time:
                    return
                if isinstance(att.in_time, str):
                    att.in_time = datetime.strptime(att.in_time, "%Y-%m-%d %H:%M:%S")
                if isinstance(shift_start_time, timedelta):  
                    shift_start_time = (datetime.min + shift_start_time).time()
                shift_start_datetime = datetime.combine(att.in_time.date(), shift_start_time)
                late_duration = (att.in_time - shift_start_datetime).total_seconds() / 60
                print("HI HI 2")
                if not frappe.db.exists("Attendance Permission",{"employee":att.employee,"permission_date":att.attendance_date,"docstatus":("!=",2)}):
                    print("HI HI 3")
                    permission_hour = 0
                    if 16 < late_duration <= 60:
                        permission_hour = 1
                    elif 16 < late_duration <= 120:
                        permission_hour = 2
                    else:
                        permission_hour = 0
                    if permission_hour and not att.leave_application:
                        perm_data = get_from_time_and_to_time(att.shift,'First Half',permission_hour,att.attendance_date)
                        if perm_data:
                            from_time = perm_data[0].get('permission_from_time')
                            to_time = perm_data[0].get('permission_to_time')
                            attendance_permission_doc = frappe.new_doc("Attendance Permission")
                            attendance_permission_doc.employee = att.employee
                            attendance_permission_doc.permission_date = att.attendance_date
                            attendance_permission_doc.shift = att.shift
                            attendance_permission_doc.permission_hour = permission_hour
                            attendance_permission_doc.from_time = from_time
                            attendance_permission_doc.to_time = to_time
                            attendance_permission_doc.session = "First Half"
                            attendance_permission_doc.reason = "Late Entry"
                            attendance_permission_doc.save()


@frappe.whitelist()
def create_attendance_permission_late(from_date, to_date, employee):
    attedance = frappe.db.get_all("Attendance",
                                  {"employee": employee, "attendance_date": ["BETWEEN", [from_date, to_date]]},
                                  ['in_time','out_time','shift','assigned_shift','late_entry_check','leave_application','employee','attendance_date','name','employment_type'])
    for att in attedance:
        if att.employment_type != "Contract":
            print(att.shift)
            print(att.employee)
            print(att.name)
            if att.leave_application:
                break
            if att.in_time and att.shift and att.assigned_shift:
                print("1")
                shift_start_time = frappe.db.get_value("Shift Type", att.shift, ["start_time"])
                if not shift_start_time:
                    return
                if isinstance(att.in_time, str):
                    att.in_time = datetime.strptime(att.in_time, "%Y-%m-%d %H:%M:%S")
                if isinstance(shift_start_time, timedelta):  
                    shift_start_time = (datetime.min + shift_start_time).time()
                shift_start_datetime = datetime.combine(att.in_time.date(), shift_start_time)
                late_duration = (att.in_time - shift_start_datetime).total_seconds() / 60
                if not frappe.db.exists("Attendance Permission",{"employee":att.employee,"permission_date":att.attendance_date,"docstatus":("!=",2)}):
                    permission_hour = 0
                    if 16 < late_duration <= 60:
                        permission_hour = 1
                    elif 16 < late_duration <= 120:
                        permission_hour = 2
                    else:
                        permission_hour = 0
                    print(permission_hour)    
                    if permission_hour and not att.leave_application:
                        print("2 2")
                        perm_data = get_from_time_and_to_time(att.shift,'First Half',permission_hour,att.attendance_date)
                        print("33 ")
                        if perm_data:
                            print("33 ")
                            from_time = perm_data[0].get('permission_from_time')
                            to_time = perm_data[0].get('permission_to_time')
                            attendance_permission_doc = frappe.new_doc("Attendance Permission")
                            attendance_permission_doc.employee = att.employee
                            attendance_permission_doc.permission_date = att.attendance_date
                            attendance_permission_doc.shift = att.shift
                            attendance_permission_doc.permission_hour = permission_hour
                            attendance_permission_doc.from_time = from_time
                            attendance_permission_doc.to_time = to_time
                            attendance_permission_doc.session = "First Half"
                            attendance_permission_doc.reason = "Late Entry"
                            attendance_permission_doc.save()

@frappe.whitelist()
def create_attendance_permission_early(from_date, to_date, employee):
    attedance = frappe.db.get_all("Attendance",
                                  {"employee": employee, "attendance_date": ["BETWEEN", [from_date, to_date]]},
                              ['in_time','out_time','shift','assigned_shift','leave_application','employee','attendance_date','name','employment_type'])
    exit_duration = 0
    
    for att in attedance:
        if att.employment_type != "Contract":
            print(att.employee)
            print(att.name)
            if att.out_time and att.shift and att.assigned_shift:
                shift_end_time = frappe.db.get_value("Shift Type", att.shift, ["end_time"])
                if not shift_end_time:
                    return
                print("2")
                print(att.out_time)
                if isinstance(att.out_time, str):
                    att.out_time = datetime.strptime(att.out_time, "%Y-%m-%d %H:%M:%S")
                    print(att.out_time)
                if isinstance(shift_end_time, timedelta):  
                    shift_end_time = (datetime.min + shift_end_time).time()
                    print(shift_end_time)
                shift_end_datetime = datetime.combine(att.out_time.date(), shift_end_time)
                if shift_end_datetime > att.out_time:
                    exit_duration = (shift_end_datetime - att.out_time).total_seconds() / 60
            
                
                if not frappe.db.exists("Attendance Permission",{"employee":att.employee,"permission_date":att.attendance_date,"docstatus":("!=",2)}):
                    print("HI")
                    permission_hour = 0
                    if 16 < exit_duration <= 60:
                        permission_hour = 1
                    elif 16 < exit_duration <= 120:
                        permission_hour = 2
                    print(permission_hour)    
                    if permission_hour and not att.leave_application:
                        perm_data = get_from_time_and_to_time(att.shift,'Second Half',permission_hour,att.attendance_date)
                        if perm_data:
                            from_time = perm_data[0].get('permission_from_time')
                            to_time = perm_data[0].get('permission_to_time')
                            attendance_permission = frappe.new_doc("Attendance Permission")
                            attendance_permission.employee = att.employee
                            attendance_permission.permission_date = att.attendance_date
                            attendance_permission.shift = att.shift
                            attendance_permission.permission_hour = permission_hour
                            attendance_permission.from_time = from_time
                            attendance_permission.to_time = to_time
                            attendance_permission.session = "Second Half"
                            attendance_permission.reason = "Early Exit"
                            attendance_permission.save()
                else:
                    existing_permission = frappe.db.get_all("Attendance Permission",filters={"employee": employee, "permission_date": att.attendance_date, "reason": "Early Exit"},pluck="name")
                    if exit_duration <= 15 and existing_permission:
                        for permission_name in existing_permission:
                            frappe.delete_doc("Attendance Permission", permission_name, force=True)
                        frappe.db.commit()

@frappe.whitelist()
def get_from_time_and_to_time(shift,session,permission_hour,permission_date):
    datalist = []
    data = {}
    if session == 'First Half':
        get_shift_time = frappe.db.get_value('Shift Type', {'name': shift}, 'start_time')
        if isinstance(permission_date, str):
            permission_date = dt.datetime.strptime(permission_date, "%Y-%m-%d").date()  
        if isinstance(get_shift_time, dt.timedelta):  
            shift_start_time = (dt.datetime.min + get_shift_time).time()
        elif isinstance(get_shift_time, str):
            try:
                start_time = dt.datetime.strptime(get_shift_time, '%H:%M:%S').time()
            except ValueError:
                start_time = dt.datetime.strptime(get_shift_time, '%H:%M').time()
        start_time = dt.datetime.combine(permission_date, shift_start_time)
        permission_to_time = timedelta(hours=int(permission_hour)) + start_time  
        if isinstance(permission_to_time, str):
            try:
                permission_to_time = datetime.strptime(permission_to_time, '%Y-%m-%d %H:%M:%S') 
            except ValueError:
                return {"error": "Invalid datetime format in permission_to_time"}

        permission_to_time = permission_to_time.strftime('%H:%M:%S') 
        data.update({
            'permission_from_time':get_shift_time,
            'permission_to_time':permission_to_time
        })
        datalist.append(data.copy())   
  
    elif session == 'Second Half':
        get_shift_time = frappe.db.get_value('Shift Type',{'name':shift},['end_time'])
        if isinstance(permission_date, str):
            permission_date = dt.datetime.strptime(permission_date, "%Y-%m-%d").date()  
        if isinstance(get_shift_time, dt.timedelta):  
            shift_end_time = (dt.datetime.min + get_shift_time).time()
        elif isinstance(get_shift_time, str):
            try:
                shift_end_time = dt.datetime.strptime(get_shift_time, '%H:%M:%S').time()
            except ValueError:
                shift_end_time = dt.datetime.strptime(get_shift_time, '%H:%M').time()

        end_time = dt.datetime.combine(permission_date, shift_end_time)
        permission_from_time = end_time - timedelta(hours=int(permission_hour))
        if isinstance(permission_from_time, str):
            try:
                permission_from_time = datetime.strptime(permission_from_time, '%Y-%m-%d %H:%M:%S') 
            except ValueError:
                return {"error": "Invalid datetime format in permission_from_time"}

        permission_from_time = permission_from_time.strftime('%H:%M:%S')
        data.update({
            'permission_from_time':permission_from_time,
            'permission_to_time':get_shift_time
        })
        datalist.append(data.copy())

               
    return datalist        


@frappe.whitelist()
def mark_attendance_status_based_on_the_late_and_early_exit(from_date, to_date):
    attendance_list = frappe.db.get_all("Attendance",filters={"docstatus":["!=",2],"attendance_date": ["between", [from_date, to_date]],'shift':['!=',''],'assigned_shift':['!=','']},fields=['in_time', 'out_time', 'shift', 'assigned_shift', 'leave_application', 'employee', 'attendance_date', 'name', 'late_entry_time', 'early_exit_time'])
    for att in attendance_list:
        if att.in_time and att.out_time and att.shift and att.assigned_shift:
            grace_time = timedelta(minutes=15)
            if frappe.db.exists("Attendance Permission", {"employee": att.employee,"permission_date": att.attendance_date,"docstatus": ("!=", 2)}):
                session = frappe.db.get_value("Attendance Permission",{"employee": att.employee,"permission_date": att.attendance_date,"docstatus": ("!=", 2)},"session")
                if session == 'First Half' and att.early_exit_time:
                    if isinstance(att.early_exit_time, str):
                        early_exit = frappe.utils.to_timedelta(att.early_exit_time)
                    else:
                        early_exit = att.early_exit_time
                    if early_exit < grace_time:
                        if att.shift_status =="Matched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Present')
                            doc = frappe.get_doc("Attendance", att.name)
                            doc.submit()
                        if att.shift_status =="Unmatched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Absent')    
                    elif early_exit > grace_time:
                        if att.shift_status =="Matched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Half Day')
                        if att.shift_status =="Unmatched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Absent')    
                    else:
                        pass
                elif session == 'Second Half' and att.late_entry_time:
                    if isinstance(att.late_entry_time, str):
                        late_entry = frappe.utils.to_timedelta(att.late_entry_time)
                    else:
                        late_entry = att.late_entry_time
                    if late_entry < grace_time:
                        if att.shift_status =="Matched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Present')
                            doc = frappe.get_doc("Attendance", att.name)
                            doc.submit()
                        if att.shift_status =="Unmatched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Absent')    
                    elif late_entry > grace_time:
                        if att.shift_status =="Matched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Half Day')
                        if att.shift_status =="Unmatched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Absent')    
                    else:
                        pass
            else:
                if att.late_entry_time or att.early_exit_time:
                    late_entry = timedelta(minutes=0)
                    early_exit = timedelta(minutes=0)
                    if att.late_entry_time:
                        if isinstance(att.late_entry_time, str):
                            late_entry = frappe.utils.to_timedelta(att.late_entry_time)
                        else:
                            late_entry = att.late_entry_time
                    if att.early_exit_time:
                        if isinstance(att.early_exit_time, str):
                            early_exit = frappe.utils.to_timedelta(att.early_exit_time)
                        else:
                            early_exit = att.early_exit_time
                    if early_exit < grace_time and late_entry < grace_time:
                        if att.shift_status =="Matched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Present')
                            doc = frappe.get_doc("Attendance", att.name)
                            doc.submit()
                        if att.shift_status =="Unmatched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Absent')    
                    else:
                        pass


def mark_attendance_status_based_on_the_late_and_early_exit_with_employee(from_date,to_date,employee):
    attendance_list = frappe.db.get_all("Attendance",filters={"docstatus":["!=",2],"employee":employee,"attendance_date": ["between", [from_date, to_date]],'shift':['!=',''],'assigned_shift':['!=','']},fields=['in_time', 'out_time', 'shift', 'assigned_shift', 'leave_application', 'employee', 'attendance_date', 'name', 'late_entry_time', 'early_exit_time'])
    for att in attendance_list:
        if (att.in_time or att.out_time) and att.shift and att.assigned_shift:
            grace_time = timedelta(minutes=15)
            if frappe.db.exists("Attendance Permission", {"employee": att.employee,"permission_date": att.attendance_date,"docstatus": ("!=", 2)}):
                session = frappe.db.get_value("Attendance Permission",{"employee": att.employee,"permission_date": att.attendance_date,"docstatus": ("!=", 2)},"session")
                if session == 'First Half' and att.early_exit_time:
                    if isinstance(att.early_exit_time, str):
                        early_exit = frappe.utils.to_timedelta(att.early_exit_time)
                    else:
                        early_exit = att.early_exit_time
                    if early_exit < grace_time:
                        if att.shift_status =="Matched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Present')
                            doc = frappe.get_doc("Attendance", att.name)
                            doc.submit()
                    elif early_exit > grace_time:
                        if att.shift_status =="Matched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Half Day')
                        if att.shift_status =="Unmatched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Absent')
                    else:
                        pass
                elif session == 'Second Half' and att.late_entry_time:
                    if isinstance(att.late_entry_time, str):
                        late_entry = frappe.utils.to_timedelta(att.late_entry_time)
                    else:
                        late_entry = att.late_entry_time
                    if late_entry < grace_time:
                        if att.shift_status =="Matched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Present')
                            doc = frappe.get_doc("Attendance", att.name)
                            doc.submit()
                    elif late_entry > grace_time:
                        if att.shift_status =="Matched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Half Day')
                        if att.shift_status =="Unmatched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Absent')
                    else:
                        pass
            else:
                if att.late_entry_time or att.early_exit_time:
                    late_entry = timedelta(minutes=0)
                    early_exit = timedelta(minutes=0)
                    if att.late_entry_time:
                        if isinstance(att.late_entry_time, str):
                            late_entry = frappe.utils.to_timedelta(att.late_entry_time)
                        else:
                            late_entry = att.late_entry_time
                    if att.early_exit_time:
                        if isinstance(att.early_exit_time, str):
                            early_exit = frappe.utils.to_timedelta(att.early_exit_time)
                        else:
                            early_exit = att.early_exit_time
                    if early_exit < grace_time and late_entry < grace_time:
                        print('GRACE')
                        if att.shift_status =="Matched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Present')
                            doc = frappe.get_doc("Attendance", att.name)
                            doc.submit()
                        if att.shift_status =="Unmatched":
                            frappe.db.set_value('Attendance',{'name':att.name},'status','Absent')    
                    else:
                        pass

@frappe.whitelist()
def mark_late_entry_and_early_exit_with_employee(from_date, to_date,employee):
    attendance = frappe.db.get_all('Attendance',{'employee':employee,'attendance_date':('between',(from_date,to_date)),'docstatus':('!=',2)},['on_duty_application','session_from_time','session_to_time','name','shift','in_time','out_time',
        'shift_status','total_working_hours','attendance_date','employee','leave_type','leave_application','status','late_entry','early_exit','assigned_shift'],order_by='attendance_date')
    for att in attendance:
        od_from_time =''
        od_to_time =''
        if att.shift and att.shift != 'WW':
            start_time = frappe.db.get_value('Shift Type', {'name': att.shift}, 'start_time')
            end_time = frappe.db.get_value('Shift Type', {'name': att.shift}, 'end_time')
            # total_hours = frappe.db.get_value('Shift Type',{'name':att.shift},'total_hours')
            shift_start_time = datetime.strptime(str(start_time), '%H:%M:%S').time()
            shift_end_time = datetime.strptime(str(end_time), '%H:%M:%S').time()
            shift_start_datetime = dt.datetime.combine(att.attendance_date, shift_start_time)
            shift_end_datetime = dt.datetime.combine(att.attendance_date, shift_end_time)
            total_hours =shift_end_datetime -shift_start_datetime
            shift_start_datetime +=dt.timedelta(seconds=59)
            print(shift_start_datetime , "shift_start_datetime")
            print(shift_end_datetime , "shift_end_datetime")
            
            if att.leave_type:
                if frappe.db.exists(
                    "Leave Application",{'docstatus': 1, "name": att.leave_application, 'half_day': 1, 'from_date': att.attendance_date,'to_date': att.attendance_date}):
                    hd_leave_session = frappe.db.get_value(
                    "Leave Application",
                    {'docstatus': 1, "name": att.leave_application, 'half_day': 1, 'from_date': att.attendance_date,'to_date': att.attendance_date},
                    'session')
                else:
                    hd_leave_session = frappe.db.get_value(
                        "Leave Application",
                        {'docstatus': 1, "name": att.leave_application, 'half_day': 1, 'half_day_date': att.attendance_date},
                        'session'
                    )
                if hd_leave_session:
                    # half_shift_hours = float(total_hours) / 2
                    half_shift_hours = total_hours.total_seconds() / 3600 / 2
                    if hd_leave_session == 'First Half':
                        leave_start_time = shift_start_datetime 
                        leave_end_time = shift_start_datetime + timedelta(hours=half_shift_hours) 
                        shift_start_datetime = leave_end_time 
                        shift_start_datetime += dt.timedelta(seconds=59)
                    elif hd_leave_session == 'Second Half':
                        leave_start_time = shift_end_datetime - timedelta(hours=half_shift_hours) 
                        leave_end_time = shift_end_datetime 
                        shift_end_datetime = leave_start_time 
                        # shift_end_datetime -= dt.timedelta(seconds=59)
                    if att.total_working_hours:
                        att.total_working_hours += half_shift_hours
                    
            if att.on_duty_application:
                od_session = frappe.db.get_value("On Duty Application",{'name':att.on_duty_application,'session':['in',['First Half','Second Half']]},["session"])
                if od_session:
                    if isinstance(att.session_from_time, dt.timedelta) and isinstance(att.session_to_time, dt.timedelta):
                        od_from_time = (dt.datetime.min + att.session_from_time).time()
                        od_to_time = (dt.datetime.min + att.session_to_time).time()
                    print(att.session_from_time )
                    half_shift_hours = total_hours.total_seconds() / 3600 / 2
                    att.total_working_hours = (att.total_working_hours or 0) + half_shift_hours
                    if od_session == 'First Half': 
                        if isinstance(od_to_time, dt.time):
                            shift_start_datetime = dt.datetime.combine(att.attendance_date, od_to_time)
                        shift_start_datetime += dt.timedelta(seconds=59)
                    if od_session == 'Second Half': 
                        if isinstance(od_from_time, dt.time):
                            shift_end_datetime = dt.datetime.combine(att.attendance_date, od_from_time)
                        # shift_end_datetime -= dt.timedelta(seconds=59)
            if att.status not in ['On Leave', 'Work From Home']:
                if att.in_time:
                    print(att.in_time)
                    if att.in_time > shift_start_datetime: 
                        frappe.db.set_value('Attendance', att.name, 'late_entry', 1)
                        frappe.db.set_value('Attendance', att.name, 'late_entry_time', att.in_time - shift_start_datetime)
                        late_entry_from = timedelta(hours=15, minutes=59) 
                        late_entry_to = timedelta(hours=2)  
                        if late_entry_from < att.in_time - shift_start_datetime < late_entry_to:
                            if att.assigned_shift and att.shift:
                                create_attendance_permission_for_late_entry(att.attendance_date,att.employee)
                        elif att.in_time - shift_start_datetime > late_entry_from:
                            existing_permission = frappe.db.get_value("Attendance Permission",{"employee": att.employee, "permission_date": att.attendance_date, "session": "First Half",'docstatus':0},["name"])
                            if existing_permission:
                                frappe.delete_doc("Attendance Permission", existing_permission, force=True)
                                frappe.db.commit()                                    
                    else:
                        frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
                        frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00") 
                        existing_permission = frappe.db.get_value("Attendance Permission",{"employee": att.employee, "permission_date": att.attendance_date, "session": "First Half",'docstatus':0},["name"])
                        if existing_permission:
                            frappe.delete_doc("Attendance Permission", existing_permission, force=True)
                            frappe.db.commit()   

                if att.out_time:
                    if att.out_time < shift_end_datetime:
                        frappe.db.set_value('Attendance', att.name, 'early_exit', 1)
                        frappe.db.set_value('Attendance', att.name, 'early_exit_time', shift_end_datetime - att.out_time)
                        if not att.on_duty_application and not att.leave_application:
                            late_entry_from = timedelta(hours=15, minutes=59) 
                            late_entry_to = timedelta(hours=2)  
                            if late_entry_from < shift_end_datetime - att.out_time < late_entry_to:
                                if att.assigned_shift and att.shift:                         
                                    create_attendance_permission_for_early_exit(att.attendance_date,att.employee)
                            elif shift_end_datetime - att.out_time > late_entry_from:
                                existing_permission = frappe.db.get_value("Attendance Permission",{"employee": att.employee, "permission_date": att.attendance_date, "session": "Second Half",'docstatus':0},["name"])
                                if existing_permission:
                                    frappe.delete_doc("Attendance Permission", existing_permission, force=True)
                                    frappe.db.commit()
                    else:
                        frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
                        frappe.db.set_value('Attendance', att.name, 'early_exit_time', "00:00:00")
                        existing_permission = frappe.db.get_value("Attendance Permission",{"employee": att.employee, "permission_date": att.attendance_date, "session": "Second Half",'docstatus':0},["name"])
                        if existing_permission:
                            frappe.delete_doc("Attendance Permission", existing_permission, force=True)
                            frappe.db.commit()
            else:
                frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
                frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
                frappe.db.set_value('Attendance', att.name, 'early_exit_time', "00:00:00")
        else:
            frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
            frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
            frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
            frappe.db.set_value('Attendance', att.name, 'early_exit_time', "00:00:00")    
    # for att in attendance:
        

@frappe.whitelist()
def create_attendance_permission_for_late_entry(att_date,employee):
    late_entry_from = timedelta(hours=2)       
    late_entry_to = timedelta(hours=15, minutes=59) 
    attedance = frappe.db.get_all("Attendance",
                                  {"employee": employee, "attendance_date": att_date,'early_exit':1,'early_exit_time':["between", late_entry_from, late_entry_to],'assigned_shift':['is','set'],'shift':['is','set']},
                              ['in_time','shift','assigned_shift','leave_application','employee','attendance_date','name'])
    att =attedance[0]
    if att:
    # for att in attedance:
        if att.in_time and att.shift and att.assigned_shift:
            shift_start_time = frappe.db.get_value("Shift Type", att.shift, ["start_time"])
            if not shift_start_time:
                return
            if isinstance(att.in_time, str):
                att.in_time = datetime.strptime(att.in_time, "%Y-%m-%d %H:%M:%S")
            if isinstance(shift_start_time, timedelta):  
                shift_start_time = (datetime.min + shift_start_time).time()
            shift_start_datetime = datetime.combine(att.in_time.date(), shift_start_time)
            late_duration = (att.in_time - shift_start_datetime).total_seconds() / 60
            if not frappe.db.exists("Attendance Permission",{"employee":att.employee,"permission_date":att.attendance_date,"docstatus":("!=",2)}):
                permission_hour = 0
                if 16 < late_duration <= 60:
                    permission_hour = 1
                elif 16 < late_duration <= 120:
                    permission_hour = 2
                else:
                    permission_hour = 0
                if permission_hour and not att.leave_application:
                    perm_data = get_from_time_and_to_time(att.shift,'First Half',permission_hour,att.attendance_date)
                    if perm_data:
                        from_time = perm_data[0].get('permission_from_time')
                        to_time = perm_data[0].get('permission_to_time')
                        attendance_permission_doc = frappe.new_doc("Attendance Permission")
                        attendance_permission_doc.employee = att.employee
                        attendance_permission_doc.permission_date = att.attendance_date
                        attendance_permission_doc.shift = att.shift
                        attendance_permission_doc.permission_hour = permission_hour
                        attendance_permission_doc.from_time = from_time
                        attendance_permission_doc.to_time = to_time
                        attendance_permission_doc.session = "First Half"
                        attendance_permission_doc.reason = "Late Entry"
                        attendance_permission_doc.save()

@frappe.whitelist()
def create_attendance_permission_for_early_exit(att_date,employee):
    early_exit_from = timedelta(hours=2)         
    early_exit_to = timedelta(hours=15, minutes=59) 
    attedance = frappe.db.get_all("Attendance",
                                  {"employee": employee, "attendance_date": att_date,'early_exit':1,'early_exit_time':["between", early_exit_from, early_exit_to],'assigned_shift':['is','set'],'shift':['is','set']},
                              ['out_time','shift','assigned_shift','leave_application','employee','attendance_date','name'])
    exit_duration = 0
    att =attedance[0]
    if att:
        if att.out_time and att.shift and att.assigned_shift:
            shift_end_time = frappe.db.get_value("Shift Type", att.shift, ["end_time"])

            
            if not shift_end_time:
                return
            
            if isinstance(att.out_time, str):
                att.out_time = datetime.strptime(att.out_time, "%Y-%m-%d %H:%M:%S")

            if isinstance(shift_end_time, timedelta):  
                shift_end_time = (datetime.min + shift_end_time).time()
            
            shift_end_datetime = datetime.combine(att.out_time.date(), shift_end_time)
            if shift_end_datetime > att.out_time:
                exit_duration = (shift_end_datetime - att.out_time).total_seconds() / 60
        
            
            if not frappe.db.exists("Attendance Permission",{"employee":att.employee,"permission_date":att.attendance_date,"docstatus":("!=",2)}):
                permission_hour = 0
                if 16 < exit_duration <= 60:
                    permission_hour = 1
                elif 16 < exit_duration <= 120:
                    permission_hour = 2
                if permission_hour and not att.leave_application:
                    perm_data = get_from_time_and_to_time(att.shift,'Second Half',permission_hour,att.attendance_date)
                    if perm_data:
                        from_time = perm_data[0].get('permission_from_time')
                        to_time = perm_data[0].get('permission_to_time')
                        attendance_permission = frappe.new_doc("Attendance Permission")
                        attendance_permission.employee = att.employee
                        attendance_permission.permission_date = att.attendance_date
                        attendance_permission.shift = att.shift
                        attendance_permission.permission_hour = permission_hour
                        attendance_permission.from_time = from_time
                        attendance_permission.to_time = to_time
                        attendance_permission.session = "Second Half"
                        attendance_permission.reason = "Early Exit"
                        attendance_permission.save()
            else:
                existing_permission = frappe.db.get_all("Attendance Permission",filters={"employee": employee, "permission_date": att.attendance_date, "session": "Second Half"},pluck="name")
                if exit_duration <= 15 and existing_permission:
                    for permission_name in existing_permission:
                        frappe.delete_doc("Attendance Permission", permission_name, force=True)
                    frappe.db.commit()

@frappe.whitelist()
def mark_late_entry_and_early_exit(from_date, to_date):
    attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'docstatus':('!=',2)},['on_duty_application','session_from_time','session_to_time','name','shift','in_time','out_time',
        'total_working_hours','attendance_date','employee','leave_type','leave_application','status','late_entry','early_exit','assigned_shift'],order_by='attendance_date')
    for att in attendance:
        od_from_time =''
        od_to_time =''
        if att.shift and att.shift != 'WW':
            start_time = frappe.db.get_value('Shift Type', {'name': att.shift}, 'start_time')
            end_time = frappe.db.get_value('Shift Type', {'name': att.shift}, 'end_time')
            # total_hours = frappe.db.get_value('Shift Type',{'name':att.shift},'total_hours')
            shift_start_time = datetime.strptime(str(start_time), '%H:%M:%S').time()
            shift_end_time = datetime.strptime(str(end_time), '%H:%M:%S').time()
            shift_start_datetime = dt.datetime.combine(att.attendance_date, shift_start_time)
            shift_end_datetime = dt.datetime.combine(att.attendance_date, shift_end_time)
            total_hours =shift_end_datetime -shift_start_datetime
            shift_start_datetime +=dt.timedelta(seconds=59)
            print(shift_start_datetime , "shift_start_datetime")
            print(shift_end_datetime , "shift_end_datetime")
            
            if att.leave_type:
                if frappe.db.exists(
                    "Leave Application",{'docstatus': 1, "name": att.leave_application, 'half_day': 1, 'from_date': att.attendance_date,'to_date': att.attendance_date}):
                    hd_leave_session = frappe.db.get_value(
                    "Leave Application",
                    {'docstatus': 1, "name": att.leave_application, 'half_day': 1, 'from_date': att.attendance_date,'to_date': att.attendance_date},
                    'session')
                else:
                    hd_leave_session = frappe.db.get_value(
                        "Leave Application",
                        {'docstatus': 1, "name": att.leave_application, 'half_day': 1, 'half_day_date': att.attendance_date},
                        'session'
                    )
                if hd_leave_session:
                    # half_shift_hours = float(total_hours) / 2
                    half_shift_hours = total_hours.total_seconds() / 3600 / 2
                    if hd_leave_session == 'First Half':
                        leave_start_time = shift_start_datetime 
                        leave_end_time = shift_start_datetime + timedelta(hours=half_shift_hours) 
                        shift_start_datetime = leave_end_time 
                        shift_start_datetime += dt.timedelta(seconds=59)
                    elif hd_leave_session == 'Second Half':
                        leave_start_time = shift_end_datetime - timedelta(hours=half_shift_hours) 
                        leave_end_time = shift_end_datetime 
                        shift_end_datetime = leave_start_time 
                    if att.total_working_hours:
                        att.total_working_hours += half_shift_hours
                    
            if att.on_duty_application:
                od_session = frappe.db.get_value("On Duty Application",{'name':att.on_duty_application,'session':['in',['First Half','Second Half']]},["session"])
                if od_session:
                    if isinstance(att.session_from_time, dt.timedelta) and isinstance(att.session_to_time, dt.timedelta):
                        od_from_time = (dt.datetime.min + att.session_from_time).time()
                        od_to_time = (dt.datetime.min + att.session_to_time).time()
                    half_shift_hours = total_hours.total_seconds() / 3600 / 2
                    att.total_working_hours = (att.total_working_hours or 0) + half_shift_hours
                    if od_session == 'First Half': 
                        if isinstance(od_to_time, dt.time):
                            shift_start_datetime = dt.datetime.combine(att.attendance_date, od_to_time)
                        shift_start_datetime += dt.timedelta(seconds=59)
                    if od_session == 'Second Half': 
                        if isinstance(od_from_time, dt.time):
                            shift_end_datetime = dt.datetime.combine(att.attendance_date, od_from_time)
                        # shift_end_datetime -= dt.timedelta(seconds=59)
                        # shift_end_datetime -= dt.timedelta(minutes=59)
            if att.status not in ['On Leave', 'Work From Home']:
                if att.in_time:
                    if att.in_time > shift_start_datetime: 
                        frappe.db.set_value('Attendance', att.name, 'late_entry', 1)
                        frappe.db.set_value('Attendance', att.name, 'late_entry_time', att.in_time - shift_start_datetime)
                        late_entry_from = timedelta(hours=15, minutes=59) 
                        late_entry_to = timedelta(hours=2)  
                        if late_entry_from < att.in_time - shift_start_datetime < late_entry_to:
                            if att.assigned_shift and att.shift:
                                create_attendance_permission_for_late_entry(att.attendance_date,att.employee)
                        elif att.in_time - shift_start_datetime > late_entry_from:
                            existing_permission = frappe.db.get_value("Attendance Permission",{"employee": att.employee, "permission_date": att.attendance_date, "session": "First Half",'docstatus':0},["name"])
                            if existing_permission:
                                frappe.delete_doc("Attendance Permission", existing_permission, force=True)
                                frappe.db.commit()
                    else:
                        frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
                        frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00") 
                        existing_permission = frappe.db.get_value("Attendance Permission",{"employee": att.employee, "permission_date": att.attendance_date, "session": "First Half",'docstatus':0},["name"])
                        if existing_permission:
                            frappe.delete_doc("Attendance Permission", existing_permission, force=True)
                            frappe.db.commit()      
                if att.out_time:
                    if att.out_time < shift_end_datetime:
                        frappe.db.set_value('Attendance', att.name, 'early_exit', 1)
                        frappe.db.set_value('Attendance', att.name, 'early_exit_time', shift_end_datetime - att.out_time)
                        if not att.on_duty_application and not att.leave_application:
                            late_entry_from = timedelta(hours=15, minutes=59) 
                            late_entry_to = timedelta(hours=2)  
                            if late_entry_from < shift_end_datetime - att.out_time < late_entry_to:
                                if att.assigned_shift and att.shift:                         
                                    _for_early_exit(att.attendance_date,att.employee)
                            elif shift_end_datetime - att.out_time > late_entry_from:
                                existing_permission = frappe.db.get_value("Attendance Permission",{"employee": att.employee, "permission_date": att.attendance_date, "session": "Second Half",'docstatus':0},["name"])
                                if existing_permission:
                                    frappe.delete_doc("Attendance Permission", existing_permission, force=True)
                                    frappe.db.commit()
                    else:
                        frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
                        frappe.db.set_value('Attendance', att.name, 'early_exit_time', "00:00:00")
                        existing_permission = frappe.db.get_value("Attendance Permission",{"employee": att.employee, "permission_date": att.attendance_date, "session": "Second Half",'docstatus':0},["name"])
                        if existing_permission:
                            frappe.delete_doc("Attendance Permission", existing_permission, force=True)
                            frappe.db.commit()
            else:
                frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
                frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
                frappe.db.set_value('Attendance', att.name, 'early_exit_time', "00:00:00")
        else:
            frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
            frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
            frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
            frappe.db.set_value('Attendance', att.name, 'early_exit_time', "00:00:00")    
    # for att in attendance:
        
# def mark_attendance_from_checkin_new(checkin,employee,time):
#     att_time = time.time()
#     att_date = time.date()
#     in_time = ''
#     out_time = ''
#     print(employee)
#     checkins = frappe.db.sql("""select name,time from `tabEmployee Checkin` where employee = "%s" and date(time) = '%s' order by time """%(employee,att_date),as_dict=True)
#     if checkins:
#         start_midnight = datetime.strptime("00:00:00", "%H:%M:%S").time()
#         end_early = datetime.strptime("02:00:00", "%H:%M:%S").time()
#         late_start = datetime.strptime("22:00:00", "%H:%M:%S").time()
#         late_end = datetime.strptime("23:59:59", "%H:%M:%S").time()
#         yesterday_date = att_date - timedelta(days=1)
#         if not frappe.db.exists("Attendance",{"employee": employee, "attendance_date": yesterday_date, "docstatus":["!=",2]}):
#             create_att=frappe.new_doc('Attendance')
#             create_att.employee=employee
#             create_att.attendance_date=yesterday_date
#             create_att.status='Absent'
#             create_att.save(ignore_permissions=True)
#         att_name, y_out, y_in,y_wh = frappe.db.get_value(
#                 "Attendance",
#                 {"employee": employee, "attendance_date": yesterday_date, "docstatus":["!=",2]},
#                 ["name", "out_time", "in_time","total_working_hours"]
#                 )
#         yesterday_att_check = frappe.db.exists("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]})
#         print(att_name)
#         if start_midnight <= att_time <= end_early:  
#             yesterday_att = frappe.db.exists(
#                 "Attendance",{"employee": employee, "attendance_date": yesterday_date, "docstatus": ["!=", 2]})
#             if not y_in:
#                 in_datetime = datetime.combine(att_date, att_time)
#                 if y_out:
                    
#                     if y_out > in_datetime:
#                         frappe.db.set_value("Attendance", yesterday_att, "in_time", in_datetime)
#                         frappe.db.set_value("Attendance", yesterday_att, "shift", "C")
#                         frappe.db.set_value("Attendance", yesterday_att, "attended_shift", "C")
#                         y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                     else:
#                         frappe.db.set_value("Attendance", yesterday_att, "in_time", y_in)
#                         y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                 else:
#                     frappe.db.set_value("Attendance", yesterday_att, "in_time", in_datetime)
#                     frappe.db.set_value("Attendance", yesterday_att, "shift", "C")
#                     frappe.db.set_value("Attendance", yesterday_att, "attended_shift", "C")
#                     y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
                
#                 frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
#                 frappe.db.set_value('Employee Checkin',checkin,'attendance',yesterday_att)
#                 y_shift=frappe.db.get_value("Attendance", yesterday_att, "shift")
#                 if y_shift == "A" and y_wh >= 12.000:
#                     later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                     checkins = later_punches
#             else:
#                     late_start1 = datetime.combine(yesterday_date, datetime.strptime("22:00:00", "%H:%M:%S").time())
#                     late_end1 = datetime.combine(yesterday_date, datetime.strptime("23:59:59", "%H:%M:%S").time())
#                     if late_start1 <= y_in <= late_end1:
#                         frappe.db.set_value("Attendance", yesterday_att, "shift", "C")
#                         y_shift=frappe.db.get_value("Attendance", yesterday_att, "shift")
#                         if y_shift == "A" and y_wh >= 12.000:
#                             later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                             checkins = later_punches
#                         pass
#                     else:
#                         in_datetime = datetime.combine(att_date, att_time)
#                         if y_out:
#                             if y_out > in_datetime:
#                                 frappe.db.set_value("Attendance", yesterday_att, "in_time", in_datetime)
#                                 frappe.db.set_value("Attendance", yesterday_att, "shift", "C")
#                                 frappe.db.set_value("Attendance", yesterday_att, "attended_shift", "C")
#                                 y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                             else:
#                                 frappe.db.set_value("Attendance", yesterday_att, "in_time", y_in)
#                                 if y_in and y_out and (y_in == y_out ):
#                                     frappe.db.set_value("Attendance", yesterday_att, "in_time",None)
#                                 y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                                 if y_shift == "A" and y_wh >= 12.000:
#                                     later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                                     checkins = later_punches
#                         else:
#                             frappe.db.set_value("Attendance", yesterday_att, "out_time", in_datetime)
#                             later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                             checkins =later_punches
#                         y_shift=frappe.db.get_value("Attendance", yesterday_att, "shift")
#                         if y_shift == "A" and y_wh >= 12.000:
#                             later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                             checkins = later_punches
#                         frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
#                         frappe.db.set_value('Employee Checkin',checkin,'attendance',yesterday_att)
#         elif datetime.strptime("06:00:00", "%H:%M:%S").time() <= att_time <= datetime.strptime("10:00:00", "%H:%M:%S").time():
#             yesterday_date = att_date - timedelta(days=1)
#             yesterday_att = frappe.db.exists(
#                 "Attendance",
#                 {"employee": employee, "attendance_date": yesterday_date, "shift": "C","docstatus":["!=",2]}
#             )
#             early_punches = [c for c in checkins if c["time"].time() < datetime.strptime("10:00:00", "%H:%M:%S").time()]
#             later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("10:00:00", "%H:%M:%S").time()]
            
#             if yesterday_att:
#                 att_name, y_out, y_in = frappe.db.get_value(
#                 "Attendance",
#                 {"employee": employee, "attendance_date": yesterday_date, "shift": "C","docstatus":["!=",2]},
#                 ["name", "out_time", "in_time"]
#                 )     
#                 if early_punches:
#                     frappe.db.set_value("Attendance", att_name, "out_time", early_punches[-1]["time"])
#                     y_shift=frappe.db.get_value("Attendance", yesterday_att, "shift")
#                 checkins = later_punches
#                 y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                 if y_shift == "A" and y_wh >= 12.000:
#                     later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                     checkins = later_punches
#             else:
#                 yesterday_att_check = frappe.db.exists("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]})
#                 y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                 if y_shift == "PP1":
#                     if early_punches :
#                         frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches[-1]["time"])
#                     checkins = later_punches
#                 if y_shift == "B":
#                     early_punches = [c for c in checkins if c["time"].time() < datetime.strptime("09:00:00", "%H:%M:%S").time()]
#                     if early_punches :
#                         frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches[-1]["time"])
#                     later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("09:00:00", "%H:%M:%S").time()]
#                     checkins = later_punches    
#                 if y_shift == "A" and y_wh >= 12.000:
#                     later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                     checkins = later_punches
#         elif datetime.strptime("06:00:00", "%H:%M:%S").time() >= att_time:
#             yesterday_date = att_date - timedelta(days=1)
#             yesterday_att_pp1 = frappe.db.get_value("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]},[ "shift"])
#             if yesterday_att_pp1:
#                 if yesterday_att_pp1 == "PP1":
#                     later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                     early_punches = [c for c in checkins if c["time"].time() <= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                     if later_punches:
#                         checkins = later_punches
#                         yesterday_att_check = frappe.db.exists("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]})
#                         y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                     if early_punches:   
#                         if not y_out: 
#                             in_datetime = datetime.combine(att_date, att_time)
#                             frappe.db.set_value("Attendance", yesterday_att_check, "out_time", in_datetime)
#                             frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
#                             frappe.db.set_value('Employee Checkin',checkin,'attendance',yesterday_att_check)
#                             y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                         else:
#                             in_datetime = datetime.combine(att_date, att_time)
#                             y_att_out = frappe.db.get_value("Attendance", yesterday_att_check, "out_time")
#                             if y_att_out > in_datetime :
#                                 out = y_att_out
#                             else:
#                                 out = in_datetime
#                             frappe.db.set_value("Attendance", yesterday_att_check, "out_time", out)
#                             frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
#                             frappe.db.set_value('Employee Checkin',checkin,'attendance',yesterday_att_check)
#                             y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                 elif yesterday_att_pp1 == "C":
#                     yesterday_date = att_date - timedelta(days=1)
#                     yesterday_att1 = frappe.db.exists(
#                         "Attendance",
#                         {"employee": employee, "attendance_date": yesterday_date, "shift": "C","docstatus":["!=",2]}
#                     )
#                     if yesterday_att1:
#                         later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("10:00:00", "%H:%M:%S").time()]
#                         early_punches = [c for c in checkins if c["time"].time() <= datetime.strptime("10:00:00", "%H:%M:%S").time()]
#                         if later_punches:
#                             checkins = later_punches
#                             yesterday_att_check = frappe.db.exists("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]})
#                             y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                             if y_shift == "A" and y_wh >= 12.000:
#                                 later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                                 checkins = later_punches
#                         if early_punches:     
#                             yesterday_att_check = frappe.db.exists("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]})
#                             y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                             if y_shift == "A" and y_wh >= 12.000:
#                                 later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                                 checkins = later_punches
#                     else:
#                         yesterday_att_check = frappe.db.exists("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]})
#                         y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                         if y_shift == "A" and y_wh >= 12.000:
#                             later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                             checkins = later_punches

#                 else:
#                     yesterday_att_check = frappe.db.exists("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]})
#                     y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                     if y_shift == "A" and y_wh >= 12.000:
#                         later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                         checkins = later_punches
#             else:
#                 yesterday_att_check = frappe.db.exists("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]})
#                 y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")  
#                 if y_shift == "A" and y_wh >= 12.000:
#                     later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                     checkins = later_punches  
#         else :
#             yesterday_date = att_date - timedelta(days=1)
#             yesterday_att1 = frappe.db.exists(
#                 "Attendance",
#                 {"employee": employee, "attendance_date": yesterday_date, "shift": "C","docstatus":["!=",2]}
#             )
#             if yesterday_att1:
#                 later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("10:00:00", "%H:%M:%S").time()]
#                 if later_punches:
#                     checkins = later_punches
#                     yesterday_att_check = frappe.db.exists("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]})
#                     y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                     if y_shift == "A" and y_wh >= 12.000:
#                         later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                         checkins = later_punches
#                 else:     
#                     yesterday_att_check = frappe.db.exists("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]})
#                     y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
                    
#                     early_punches = [c for c in checkins if c["time"].time() < datetime.strptime("10:00:00", "%H:%M:%S").time()]
                    
#                     if y_shift == "PP1" or y_shift == "C":
#                         if early_punches :
#                             frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches[-1]["time"])
#                         checkins = later_punches
#                     if y_shift == "B":
#                         early_punches_b = [c for c in checkins if c["time"].time() < datetime.strptime("09:00:00", "%H:%M:%S").time()]
#                         if early_punches_b :
#                             frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches_b[-1]["time"])
#                             if y_in == y_out:
#                                 frappe.db.set_value("Attendance", yesterday_att_check, "out_time", None)
#                         later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("09:00:00", "%H:%M:%S").time()]
#                         checkins = later_punches
#                     if y_shift == "A" and y_wh >= 12.000:
#                         later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                         checkins = later_punches    
#             else:
#                 yesterday_att_check = frappe.db.exists("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]})
#                 y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")
#                 early_punches = [c for c in checkins if c["time"].time() < datetime.strptime("10:00:00", "%H:%M:%S").time()]
#                 later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("10:00:00", "%H:%M:%S").time()]
#                 if y_shift == "PP1":
#                     if early_punches :
#                         frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches[-1]["time"])
#                     checkins = later_punches
#                 if y_shift == "B":
#                     early_punches_b = [c for c in checkins if c["time"].time() < datetime.strptime("09:00:00", "%H:%M:%S").time()]
#                     if early_punches_b :
#                         frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches_b[-1]["time"])
#                         if y_in == y_out:
#                             frappe.db.set_value("Attendance", yesterday_att_check, "out_time", None)
#                     later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("09:00:00", "%H:%M:%S").time()]
#                     checkins = later_punches
#                 if y_shift == "A" and y_wh >= 12.000:
#                     later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
#                     checkins = later_punches
#         if y_shift:
#             if (y_shift == "C" or y_shift == 'PP1'): 
#                 later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("10:00:00", "%H:%M:%S").time()]
#                 checkins = later_punches
#             if (y_shift == "B" ): 
#                 later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("09:00:00", "%H:%M:%S").time()]
#                 checkins = later_punches    
#         else:
#             pass        
#         if len(checkins) >= 2:
#             in_time = checkins[0].time
#             out_time = checkins[-1].time

#         elif len(checkins) == 1:
#             if start_midnight <= att_time <= end_early:
#                 in_time = ''
#             in_time = checkins[0].time
#         if len(checkins) > 0:
#             print("Inside") 
#             a = frappe.db.get_value('Attendance',{'employee':employee,'attendance_date':att_date}, ['name'])
            
#             shifta = frappe.db.get_value('Shift Type',{'name':'A'},['checkin_start_time','checkin_end_time'])
#             shiftb = frappe.db.get_value('Shift Type',{'name':'B'},['checkin_start_time','checkin_end_time'])
#             shiftc = frappe.db.get_value('Shift Type',{'name':'C'},['checkin_start_time','checkin_end_time'])
#             shiftg = frappe.db.get_value('Shift Type',{'name':'G'},['checkin_start_time','checkin_end_time'])
#             shiftg1 = frappe.db.get_value('Shift Type',{'name':'G1'},['checkin_start_time','checkin_end_time'])
#             shiftge = frappe.db.get_value('Shift Type',{'name':'GE'},['checkin_start_time','checkin_end_time'])
#             shiftpp1 = frappe.db.get_value('Shift Type',{'name':'PP1'},['checkin_start_time','checkin_end_time'])
#             shift_assignment = frappe.db.get_value("Shift Assignment",{"employee":employee,"start_date":att_date, "docstatus": 1},["shift_type"])
#             shift_start_time = frappe.db.get_value('Shift Type',{'name':shift_assignment},['checkin_start_time','checkin_end_time'])
#             shift_type = frappe.db.get_all("Shift Type", ["checkin_start_time"])

#             checkins_time = [shift["checkin_start_time"] for shift in shift_type if shift["checkin_start_time"]]

#             checkins_count = Counter(checkins_time)

#             shift_group = frappe.db.get_value("Employee", {"employee": employee}, "shift_group") or ""
#             shift_type_ = None
#             shift = ''
#             if checkins :
#                 checkin_datetime = checkins[0].time 
#             common_shift = []
#             if (datetime.min + shifta[0]).time() < checkins[0].time.time() < (datetime.min + shifta[1]).time():
#                 shift = 'A'
#                 common_shift.append('A')
#             if (datetime.min + shiftb[0]).time() < checkins[0].time.time() < (datetime.min + shiftb[1]).time():
#                 shift = 'B'
#                 common_shift.append('B')
#             if (datetime.min + shiftg[0]).time() < checkins[0].time.time() < (datetime.min + shiftg[1]).time():
#                 shift ='G'
#                 common_shift.append('G')
#             if (datetime.min + shiftg1[0]).time() < checkins[0].time.time() < (datetime.min + shiftg1[1]).time():
#                 shift ='G1'
#                 common_shift.append('G1')
#             if (datetime.min + shiftge[0]).time() < checkins[0].time.time() < (datetime.min + shiftge[1]).time():
#                 shift ='GE'
#                 common_shift.append('GE')
#             if (datetime.min + shiftpp1[0]).time() < checkins[0].time.time() < (datetime.min + shiftpp1[1]).time():
#                 shift ='PP1'
#                 common_shift.append('PP1')    
            
#             if late_start <= att_time <= late_end:
#                 shift_c_start = checkin_datetime.replace(hour=22, minute=0, second=0, microsecond=0) 
#                 shift_c_end = shift_c_start + timedelta(hours=4)
#                 if shift_c_start <= checkin_datetime <= shift_c_end:
#                     shift = 'C'
#                     common_shift.append('C')
#             if start_midnight <= att_time <= end_early:
#                 shift_c_start = checkin_datetime.replace(hour=22, minute=0, second=0, microsecond=0) - timedelta(days=1)
#                 shift_c_end = shift_c_start + timedelta(hours=4)
#                 if shift_c_start <= checkin_datetime <= shift_c_end:
#                     shift = 'C'
#                     common_shift.append('C')
#             if common_shift == []:
#                 shift = ''  
#             if shift_assignment:
#                 if shift_assignment in common_shift:
#                     shift = shift_assignment
#             elif shift_group and shift not in ('C','B','PP1'):
#                 rotational_shift = []
#                 rotational_shift = frappe.db.get_all("Shift Type",{"shift_group": shift_group},pluck="name")
#                 for i in rotational_shift:
#                     if i in common_shift:
#                         shift = i
#                         break
#                 else :    
#                     shift = ''
#             else:
#                 if common_shift:             
#                     shift = common_shift[0]
#                 else:
#                     shift = '' 
#             print(common_shift , "Common")
#             print(shift)
#             att = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date})
#             attended_shift = shift
#             assigned_shift = ''
#             default_shift = frappe.db.get_value('Employee',{'name':employee},['default_shift'])
#             if frappe.db.exists("Shift Assignment",{"employee":employee,"start_date":att_date, "docstatus": 1}):
#                 assigned_shift = frappe.db.get_value("Shift Assignment",{"employee":employee,"start_date":att_date, "docstatus": 1},["shift_type"])
#             elif default_shift:
#                 assigned_shift = default_shift
#             elif shift_group:
#                 if shift_group.lower() == "rotational":
#                     rotational_shifts = frappe.db.get_all(
#                         "Shift Type",
#                         filters={"shift_group": "Rotational"},
#                         fields=["name", "checkin_start_time", "checkin_end_time", "night_shift"]
#                     )
#                     punch_time = checkins[0].get("time").time()

#                     for s in rotational_shifts:
#                         start_time = (datetime.min + s["checkin_start_time"]).time()
#                         end_time   = (datetime.min + s["checkin_end_time"]).time()

#                         if is_in_shift(punch_time, s["checkin_start_time"], s["checkin_end_time"], is_night=s.get("night_shift")):
#                             assigned_shift = s["name"]
#                             break

#                 else:
#                     shift_from_group = frappe.db.get_value(
#                         "Shift Type",
#                         {"shift_group": shift_group},
#                         "name"
#                     )
#                     dshift = frappe.db.get_value("Employee", {"name": employee}, "default_shift")
#                     if shift_from_group:
#                         assigned_shift = shift_from_group
#                     else:
#                         if dshift :
#                             shift = dshift
#                         else:
#                             shift=''  
#             print(assigned_shift , "Ass")  
#             print(shift, "SHIFT")                
#             if assigned_shift and attended_shift and assigned_shift == attended_shift:
#                 shift_status = "Matched"
#             else:
#                 shift_status = "Unmatched"
#             if not att and checkin:
#                 att = frappe.new_doc("Attendance")
#                 att.employee = employee
#                 att.attendance_date = att_date
#                 att.shift = shift
#                 att.status = "Absent"
#                 att.in_time = in_time
#                 att.out_time = out_time
#                 att.assigned_shift = assigned_shift
#                 att.attended_shift = shift
#                 att.shift_status = shift_status
#                 att.session_from_time = "00:00:00"
#                 att.session_to_time = "00:00:00"
#                 att.late_entry_time = "00:00:00"
#                 att.ot_hours = "00:00:00"
#                 hh = check_holiday_new(att_date,att.employee)
#                 if hh == "WW":
#                     att.weekly_off = 1   
#                 else:
#                     att.weekly_off = 0   
#                 att.save(ignore_permissions=True)
#                 if not shift:
#                     if assigned_shift:
#                         n_shift = frappe.db.get_value('Shift Type',{'name': assigned_shift},['night_shift'])
#                         shift_end_time = frappe.db.get_value('Shift Type',{'name': assigned_shift},['end_time'])
#                         shift_st_time = datetime.strptime(str(shift_end_time), "%H:%M:%S").time()
#                         tmr_att = att_date + timedelta(days=1)
#                         if n_shift :
#                             shift_dt = datetime.combine( tmr_att, shift_st_time)
#                         else:
#                             shift_dt = datetime.combine( att_date, shift_st_time)
#                         get_att = frappe.get_all(
#                             "Attendance",
#                             filters={"employee": employee,"attendance_date": att_date,"docstatus": ["!=", 2]},fields=["in_time", "shift"],limit=1)

#                         if get_att:
#                             att_in = get_att[0].in_time
#                             shift = get_att[0].shift
#                             if att_in <= shift_dt:
#                                 att.shift = assigned_shift
#                                 att.attended_shift = assigned_shift
#                                 if assigned_shift and att.attended_shift and assigned_shift == att.attended_shift:
#                                     shift_status = "Matched"
#                                 att.save(ignore_permissions=True)   
#                 if in_time and out_time:
#                     total_working_hours = (out_time-in_time).total_seconds() / 3600.0
#                     att.total_working_hours=total_working_hours
#                     if total_working_hours >= 8:
#                         if att.shift_status == "Matched" :
#                             att.status = "Present"
#                             att.save(ignore_permissions=True)
#                         else:
#                             att.status = "Absent"
#                             att.save(ignore_permissions=True)
#                     elif total_working_hours >= 4:
#                         if att.shift_status == "Matched" :
#                             att.status = "Half Day"
#                             att.save(ignore_permissions=True)
#                         else:
#                             att.status = "Absent"
#                             att.save(ignore_permissions=True)
#                     else:
#                         att.status = "Absent"
#                         att.save(ignore_permissions=True)        
#                 if in_time == out_time:
#                     att.out_time == " "
#                     att.save(ignore_permissions=True)
#                 frappe.db.commit()
#                 frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
#                 frappe.db.set_value('Employee Checkin',checkin,'attendance',att.name)
#                 return att.name
#             else:
#                 att = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date})
#                 hh = check_holiday_new(att_date,employee)
#                 print(att, "Att")
#                 print(hh , "HH")
#                 if hh == "WW":
#                     frappe.db.set_value("Attendance",att,'weekly_off',1)
#                 else:
#                     frappe.db.set_value("Attendance",att,'weekly_off',0)
#                 if not in_time:
#                     frappe.db.set_value("Attendance",att,'in_time',None)
#                     frappe.db.set_value('Attendance', att, 'late_entry', 0)
#                     frappe.db.set_value('Attendance', att, 'late_entry_time', "00:00:00")
#                 if not out_time:
#                     frappe.db.set_value("Attendance",att,'out_time',None)    
#                     frappe.db.set_value('Attendance', att, 'early_exit', 0)
#                     frappe.db.set_value('Attendance', att, 'early_exit_time', "00:00:00")
#                 if in_time:
#                     frappe.db.set_value("Attendance",att,'in_time',in_time)
#                 if out_time:
#                     frappe.db.set_value("Attendance",att,'out_time',out_time)
#                 if not shift:
#                     if assigned_shift:
#                         n_shift = frappe.db.get_value('Shift Type',{'name': assigned_shift},['night_shift'])
#                         shift_end_time = frappe.db.get_value('Shift Type',{'name': assigned_shift},['end_time'])
#                         shift_st_time = datetime.strptime(str(shift_end_time), "%H:%M:%S").time()
#                         tmr_att = att_date + timedelta(days=1)
#                         if n_shift :
#                             shift_dt = datetime.combine( tmr_att, shift_st_time)
#                         else:
#                             shift_dt = datetime.combine( att_date, shift_st_time)
#                         get_att = frappe.get_all(
#                             "Attendance",
#                             filters={"employee": employee,"attendance_date": att_date,"docstatus": ["!=", 2]},fields=["in_time", "shift"],limit=1)

#                         if get_att:
#                             att_in = get_att[0].in_time
#                             shift = get_att[0].shift
                        
#                             if att_in <= shift_dt:
#                                 shift = assigned_shift
#                                 attended_shift = assigned_shift
#                                 if assigned_shift and attended_shift and assigned_shift == attended_shift:
#                                     shift_status = "Matched"
#                     frappe.db.set_value("Attendance",att,'shift',shift)
#                     frappe.db.set_value("Attendance",att,'attended_shift',shift)            
#                 if in_time and out_time:
#                     total_working_hours = (out_time-in_time).total_seconds() / 3600.0
#                     frappe.db.set_value("Attendance",att,'total_working_hours',total_working_hours)
#                     if total_working_hours > 8:
#                         if shift_status == "Matched" :
#                             frappe.db.set_value("Attendance",att,'status',"Present")
#                             doc = frappe.get_doc("Attendance", att)
#                         else:
#                             frappe.db.set_value("Attendance",att,'status',"Absent")
#                     else:   
#                         frappe.db.set_value("Attendance",att,'status',"Absent")
#                 if (in_time and not out_time ) or ( not in_time and out_time) or (not in_time and not out_time):
#                     att = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date})
#                     frappe.db.set_value("Attendance",att,'status',"Absent")
#                 if in_time == out_time:
#                     out_time = None   
#                     frappe.db.set_value("Attendance",att,'out_time',out_time)     
#                 frappe.db.set_value("Attendance",att,'shift',shift)
#                 frappe.db.set_value("Attendance",att,'attended_shift',shift) 
#                 frappe.db.set_value("Attendance",att,'shift_status',shift_status)
#                 frappe.db.set_value("Attendance",att,'assigned_shift',assigned_shift)
                
#                 if start_midnight <= att_time <= end_early:
#                     frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
#                     frappe.db.set_value('Employee Checkin',checkin,'attendance',yesterday_att)
#                 else:    
#                     frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
#                     frappe.db.set_value('Employee Checkin',checkin,'attendance',att)
                   
def mark_attendance_from_checkin_new(checkin,employee,time):
    att_time = time.time()
    att_date = time.date()
    in_time = ''
    out_time = ''
    print(employee)
    checkins = frappe.db.sql("""select name,time from `tabEmployee Checkin` where employee = "%s" and date(time) = '%s' order by time """%(employee,att_date),as_dict=True)
    if checkins:
        start_midnight = datetime.strptime("00:00:00", "%H:%M:%S").time()
        end_early = datetime.strptime("02:00:00", "%H:%M:%S").time()
        mrg_time = datetime.strptime("06:00:00", "%H:%M:%S").time()
        late_start = datetime.strptime("22:00:00", "%H:%M:%S").time()
        late_end = datetime.strptime("23:59:59", "%H:%M:%S").time()
        yesterday_date = att_date - timedelta(days=1)            
        yesterday_att_check = frappe.db.exists("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]})
        if yesterday_att_check:
            att_name, y_out, y_in,y_wh = frappe.db.get_value("Attendance",
                {"employee": employee, "attendance_date": yesterday_date, "docstatus":["!=",2]},
                ["name", "out_time", "in_time","total_working_hours"])
        else:
            create_att=frappe.new_doc('Attendance')
            create_att.employee=employee
            create_att.attendance_date=yesterday_date
            create_att.status='Absent'
            create_att.save(ignore_permissions=True)
            att_name, y_out, y_in,y_wh = frappe.db.get_value("Attendance",
                {"employee": employee, "attendance_date": yesterday_date, "docstatus":["!=",2]},
                ["name", "out_time", "in_time","total_working_hours"])
        print(att_name)
        if start_midnight <= att_time <= end_early:  
            print(" HI A")
            early_punches = [c for c in checkins if c["time"].time() < datetime.strptime("10:00:00", "%H:%M:%S").time()]
            later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("10:00:00", "%H:%M:%S").time()]
            y_shift = frappe.db.get_value("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]},[ "shift"])
            if y_shift == "PP1" or y_shift == "C":
                if early_punches :
                    frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches[-1]["time"])
                checkins = later_punches
            elif y_shift == "B":
                print(" HI A1")
                early_punches = [c for c in checkins if c["time"].time() < datetime.strptime("06:00:00", "%H:%M:%S").time()]
                if early_punches :
                    frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches[-1]["time"])
                
                later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
                checkins = later_punches
            else:
                early_punches = [c for c in checkins if c["time"].time() < datetime.strptime("06:00:00", "%H:%M:%S").time()]
                if early_punches :
                    frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches[-1]["time"])   
                    later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
                    checkins = later_punches
            if not y_in:
                in_datetime = datetime.combine(att_date, att_time)
                if y_out:
                    if y_out > in_datetime:
                        frappe.db.set_value("Attendance", yesterday_att_check, "in_time", in_datetime)
                        frappe.db.set_value("Attendance", yesterday_att_check, "shift", "C")
                        frappe.db.set_value("Attendance", yesterday_att_check, "attended_shift", "C")
                else:
                    frappe.db.set_value("Attendance", yesterday_att_check, "in_time", in_datetime)
                    frappe.db.set_value("Attendance", yesterday_att_check, "shift", "C")
                    frappe.db.set_value("Attendance", yesterday_att_check, "attended_shift", "C")
                
                frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
                frappe.db.set_value('Employee Checkin',checkin,'attendance',yesterday_att_check)
            else:
                late_start1 = datetime.combine(yesterday_date, datetime.strptime("22:00:00", "%H:%M:%S").time())
                late_end1 = datetime.combine(yesterday_date, datetime.strptime("23:59:59", "%H:%M:%S").time())
                if late_start1 <= y_in <= late_end1:
                    frappe.db.set_value("Attendance", yesterday_att_check, "shift", "C")
                else:
                    in_datetime = datetime.combine(att_date, att_time)
                    if y_out:
                        if y_out > in_datetime:
                            frappe.db.set_value("Attendance", yesterday_att_check, "in_time", in_datetime)
                            frappe.db.set_value("Attendance", yesterday_att_check, "shift", "C")
                            frappe.db.set_value("Attendance", yesterday_att_check, "attended_shift", "C")
                        else:
                            frappe.db.set_value("Attendance", yesterday_att_check, "in_time", y_in)
                            if y_in and y_out and (y_in == y_out ):
                                frappe.db.set_value("Attendance", yesterday_att_check, "in_time",None)
                    else:
                        frappe.db.set_value("Attendance", yesterday_att_check, "out_time", in_datetime)
                        later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
                        checkins =later_punches
                    frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
                    frappe.db.set_value('Employee Checkin',checkin,'attendance',yesterday_att_check)
            if yesterday_att_check:
                early_punches = [c for c in checkins if c["time"].time() < datetime.strptime("06:00:00", "%H:%M:%S").time()]
                if early_punches:
                    frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches[-1]["time"])
                    later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
                    checkins = later_punches
            y_shift=frappe.db.get_value("Attendance", yesterday_att_check, "shift")    
        elif datetime.strptime("06:00:00", "%H:%M:%S").time() <= att_time <= datetime.strptime("10:00:00", "%H:%M:%S").time():
            print("HI B")
            early_punches = [c for c in checkins if c["time"].time() < datetime.strptime("10:00:00", "%H:%M:%S").time()]
            later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("10:00:00", "%H:%M:%S").time()]
            y_shift = frappe.db.get_value("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]},[ "shift"])
            if y_shift == "PP1" or y_shift == "C":
                if early_punches :
                    frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches[-1]["time"])
                checkins = later_punches
            elif y_shift == "B":
                early_punches = [c for c in checkins if c["time"].time() < datetime.strptime("06:00:00", "%H:%M:%S").time()]
                if early_punches :
                    frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches[-1]["time"])
                later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
                checkins = later_punches 
            else:
                print("HI J1")
                early_punches = [c for c in checkins if c["time"].time() < datetime.strptime("06:00:00", "%H:%M:%S").time()]
                print(early_punches , "Early")
                if early_punches:
                    frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches[-1]["time"])
                    later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
                    checkins = later_punches     
        else :
            y_shift = frappe.db.get_value("Attendance",{"employee": employee, "attendance_date": yesterday_date,"docstatus":["!=",2]},[ "shift"])
            if y_shift == "C":
                later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("10:00:00", "%H:%M:%S").time()]
                if later_punches:
                    checkins = later_punches
                else:
                    early_punches = [c for c in checkins if c["time"].time() < datetime.strptime("10:00:00", "%H:%M:%S").time()]
                    if early_punches :
                        frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches[-1]["time"])
            elif y_shift == "PP1":
                later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
                if later_punches:
                    checkins = later_punches
                else:
                    early_punches = [c for c in checkins if c["time"].time() < datetime.strptime("06:00:00", "%H:%M:%S").time()]
                    if early_punches :
                        frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches[-1]["time"])
            elif y_shift == "B":
                later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
                early_punches_b = [c for c in checkins if c["time"].time() < datetime.strptime("06:00:00", "%H:%M:%S").time()]
                if later_punches:
                    checkins = later_punches
                else :
                    frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches_b[-1]["time"])
                    if y_in == y_out:
                        frappe.db.set_value("Attendance", yesterday_att_check, "out_time", None)
            else:
                early_punches = [c for c in checkins if c["time"].time() < datetime.strptime("06:00:00", "%H:%M:%S").time()]
                if early_punches:
                    frappe.db.set_value("Attendance", yesterday_att_check, "out_time", early_punches[-1]["time"])
                    later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
                    checkins = later_punches
        if y_shift:
            if (y_shift == "C" or y_shift == 'PP1'): 
                later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("10:00:00", "%H:%M:%S").time()]
                checkins = later_punches
            elif (y_shift == "B" ): 
                later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
                checkins = later_punches   
            elif (y_shift == "A" or y_shift =="G1") and y_wh >= 12.000:
                later_punches = [c for c in checkins if c["time"].time() >= datetime.strptime("06:00:00", "%H:%M:%S").time()]
                checkins = later_punches     
        else:
            pass        
        print(checkins)
        if len(checkins) >= 2:
            in_time = checkins[0].time
            out_time = checkins[-1].time

        elif len(checkins) == 1:
            if start_midnight <= att_time <= end_early:
                in_time = ''
            in_time = checkins[0].time
        if len(checkins) > 0:
            print("Inside") 
            a = frappe.db.get_value('Attendance',{'employee':employee,'attendance_date':att_date}, ['name'])
            
            shifta = frappe.db.get_value('Shift Type',{'name':'A'},['checkin_start_time','checkin_end_time'])
            shiftb = frappe.db.get_value('Shift Type',{'name':'B'},['checkin_start_time','checkin_end_time'])
            shiftc = frappe.db.get_value('Shift Type',{'name':'C'},['checkin_start_time','checkin_end_time'])
            shiftg = frappe.db.get_value('Shift Type',{'name':'G'},['checkin_start_time','checkin_end_time'])
            shiftg1 = frappe.db.get_value('Shift Type',{'name':'G1'},['checkin_start_time','checkin_end_time'])
            shiftge = frappe.db.get_value('Shift Type',{'name':'GE'},['checkin_start_time','checkin_end_time'])
            shiftpp1 = frappe.db.get_value('Shift Type',{'name':'PP1'},['checkin_start_time','checkin_end_time'])
            shift_type = frappe.db.get_all("Shift Type", ["checkin_start_time"])

            checkins_time = [shift["checkin_start_time"] for shift in shift_type if shift["checkin_start_time"]]

            checkins_count = Counter(checkins_time)

            shift_group = frappe.db.get_value("Employee", {"employee": employee}, "shift_group") or ""
            shift_type_ = None
            shift = ''
            if checkins :
                checkin_datetime = checkins[0].time 
            common_shift = []
            if (datetime.min + shifta[0]).time() < checkins[0].time.time() < (datetime.min + shifta[1]).time():
                shift = 'A'
                common_shift.append('A')
            if (datetime.min + shiftg[0]).time() < checkins[0].time.time() < (datetime.min + shiftg[1]).time():
                shift ='G'
                common_shift.append('G')
            if (datetime.min + shiftg1[0]).time() < checkins[0].time.time() < (datetime.min + shiftg1[1]).time():
                shift ='G1'
                common_shift.append('G1')
            if (datetime.min + shiftge[0]).time() < checkins[0].time.time() < (datetime.min + shiftge[1]).time():
                shift ='GE'
                common_shift.append('GE')
            if (datetime.min + shiftpp1[0]).time() < checkins[0].time.time() < (datetime.min + shiftpp1[1]).time():
                shift ='PP1'
                common_shift.append('PP1')  
            if (datetime.min + shiftb[0]).time() < checkins[0].time.time() < (datetime.min + shiftb[1]).time():
                shift = 'B'
                common_shift.append('B')      
            
            if late_start <= att_time <= late_end:
                shift_c_start = checkin_datetime.replace(hour=22, minute=0, second=0, microsecond=0) 
                shift_c_end = shift_c_start + timedelta(hours=4)
                if shift_c_start <= checkin_datetime <= shift_c_end:
                    shift = 'C'
                    common_shift.append('C')
            if start_midnight <= att_time <= end_early:
                shift_c_start = checkin_datetime.replace(hour=22, minute=0, second=0, microsecond=0) - timedelta(days=1)
                shift_c_end = shift_c_start + timedelta(hours=4)
                if shift_c_start <= checkin_datetime <= shift_c_end:
                    shift = 'C'
                    common_shift.append('C')
            if common_shift == []:
                shift = ''  
            if shift_group and shift not in ('C','B','PP1'):
                rotational_shift = []
                rotational_shift = frappe.db.get_all("Shift Type",{"shift_group": shift_group},pluck="name")
                for i in rotational_shift:
                    if i in common_shift:
                        shift = i
                        break
                else :    
                    shift = ''
            else:
                if common_shift:             
                    shift = common_shift[0]
                else:
                    shift = '' 
            att = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date})
            attended_shift = shift
            assigned_shift = ''
            default_shift = frappe.db.get_value('Employee',{'name':employee},['default_shift'])
            if default_shift:
                assigned_shift = default_shift
            elif shift_group:
                if shift_group.lower() == "rotational":
                    rotational_shifts = frappe.db.get_all(
                        "Shift Type",
                        filters={"shift_group": "Rotational"},
                        fields=["name", "checkin_start_time", "checkin_end_time", "night_shift"]
                    )
                    punch_time = checkins[0].get("time").time()

                    for s in rotational_shifts:
                        start_time = (datetime.min + s["checkin_start_time"]).time()
                        end_time   = (datetime.min + s["checkin_end_time"]).time()

                        if is_in_shift(punch_time, s["checkin_start_time"], s["checkin_end_time"], is_night=s.get("night_shift")):
                            assigned_shift = s["name"]
                            break

                else:
                    shift_from_group = frappe.db.get_value(
                        "Shift Type",
                        {"shift_group": shift_group},
                        "name"
                    )
                    dshift = frappe.db.get_value("Employee", {"name": employee}, "default_shift")
                    if shift_from_group:
                        assigned_shift = shift_from_group
                    else:
                        if dshift :
                            shift = dshift
                        else:
                            shift=''  
            print("Assigned Shift ", assigned_shift)
            if assigned_shift and attended_shift and assigned_shift == attended_shift:
                shift_status = "Matched"
            else:
                shift_status = "Unmatched"
            if not att and checkin:
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = att_date
                att.shift = shift
                att.status = "Absent"
                att.in_time = in_time
                att.out_time = out_time
                att.assigned_shift = assigned_shift
                att.attended_shift = shift
                att.shift_status = shift_status
                att.session_from_time = "00:00:00"
                att.session_to_time = "00:00:00"
                att.late_entry_time = "00:00:00"
                att.ot_hours = "00:00:00"
                hh = check_holiday_new(att_date,att.employee)
                if hh == "WW":
                    att.weekly_off = 1   
                else:
                    att.weekly_off = 0   
                if not shift:
                    if assigned_shift:
                        n_shift = frappe.db.get_value('Shift Type',{'name': assigned_shift},['night_shift'])
                        shift_end_time = frappe.db.get_value('Shift Type',{'name': assigned_shift},['end_time'])
                        shift_st_time = datetime.strptime(str(shift_end_time), "%H:%M:%S").time()
                        tmr_att = att_date + timedelta(days=1)
                        if n_shift :
                            shift_dt = datetime.combine( tmr_att, shift_st_time)
                        else:
                            shift_dt = datetime.combine( att_date, shift_st_time)
                        get_att = frappe.get_all(
                            "Attendance",
                            filters={"employee": employee,"attendance_date": att_date,"docstatus": ["!=", 2]},fields=["in_time", "shift"],limit=1)
                        if get_att:
                            att_in = get_att[0].in_time
                            shift = get_att[0].shift
                            if att_in <= shift_dt:
                                att.shift = assigned_shift
                                att.attended_shift = assigned_shift
                                if assigned_shift and att.attended_shift and assigned_shift == att.attended_shift:
                                    shift_status = "Matched"  
                if in_time and out_time:
                    total_working_hours = (out_time-in_time).total_seconds() / 3600.0
                    att.total_working_hours=total_working_hours     
                if in_time == out_time:
                    att.out_time == " "
                att.save(ignore_permissions=True)
                frappe.db.commit()
                frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
                frappe.db.set_value('Employee Checkin',checkin,'attendance',att.name)
                return att.name
            else:
                att = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date})
                hh = check_holiday_new(att_date,employee)
                if hh == "WW":
                    frappe.db.set_value("Attendance",att,'weekly_off',1)
                else:
                    frappe.db.set_value("Attendance",att,'weekly_off',0)
                if not in_time:
                    frappe.db.set_value("Attendance",att,'in_time',None)
                    frappe.db.set_value('Attendance', att, 'late_entry', 0)
                    frappe.db.set_value('Attendance', att, 'late_entry_time', "00:00:00")
                    frappe.db.set_value('Attendance', att, 'ot_hours', "00:00:00")
                else:
                    frappe.db.set_value("Attendance",att,'in_time',in_time)
                if not out_time:
                    frappe.db.set_value("Attendance",att,'out_time',None)    
                    frappe.db.set_value('Attendance', att, 'early_exit', 0)
                else:
                    frappe.db.set_value("Attendance",att,'out_time',out_time)
                if not shift:
                    if assigned_shift:
                        n_shift = frappe.db.get_value('Shift Type',{'name': assigned_shift},['night_shift'])
                        shift_end_time = frappe.db.get_value('Shift Type',{'name': assigned_shift},['end_time'])
                        shift_st_time = datetime.strptime(str(shift_end_time), "%H:%M:%S").time()
                        tmr_att = att_date + timedelta(days=1)
                        if n_shift :
                            shift_dt = datetime.combine( tmr_att, shift_st_time)
                        else:
                            shift_dt = datetime.combine( att_date, shift_st_time)
                        get_att = frappe.get_all(
                            "Attendance",
                            filters={"employee": employee,"attendance_date": att_date,"docstatus": ["!=", 2]},fields=["in_time", "shift"],limit=1)

                        if get_att:
                            att_in = get_att[0].in_time
                            shift = get_att[0].shift
                        
                            if att_in <= shift_dt:
                                shift = assigned_shift
                                attended_shift = assigned_shift
                                if assigned_shift and attended_shift and assigned_shift == attended_shift:
                                    shift_status = "Matched"
                    frappe.db.set_value("Attendance",att,'shift',shift)
                    frappe.db.set_value("Attendance",att,'attended_shift',shift)            
                if in_time and out_time:
                    total_working_hours = (out_time-in_time).total_seconds() / 3600.0
                    frappe.db.set_value("Attendance",att,'total_working_hours',total_working_hours)
                if (in_time and not out_time ) or ( not in_time and out_time) or (not in_time and not out_time):
                    att = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date})
                    frappe.db.set_value("Attendance",att,'status',"Absent")
                if in_time == out_time:
                    out_time = None   
                    frappe.db.set_value("Attendance",att,'out_time',out_time)     
                frappe.db.set_value("Attendance",att,'shift',shift)
                frappe.db.set_value("Attendance",att,'attended_shift',shift) 
                frappe.db.set_value("Attendance",att,'shift_status',shift_status)
                frappe.db.set_value("Attendance",att,'assigned_shift',assigned_shift)
                frappe.db.set_value('Attendance', att, 'ot_hours', "00:00:00")
                if start_midnight <= att_time <= end_early:
                    frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
                    frappe.db.set_value('Employee Checkin',checkin,'attendance',yesterday_att_check)
                else:    
                    frappe.db.set_value('Employee Checkin',checkin,'skip_auto_attendance','1')
                    frappe.db.set_value('Employee Checkin',checkin,'attendance',att)
                   

        
            

# def create_update_delete_ot(att, ot_hr):
#     print("1a")
#     existing_ot = frappe.db.get_value("Over Time",{"employee": att.employee,"ot_date": att.attendance_date},"name")
#     if ot_hr and float(ot_hr) > 0.5:
#         print("2a")
#         if existing_ot:
#             print(att)
#             print(att.employee)
#             print("3a")
#             frappe.db.set_value("Over Time",existing_ot,"overtime_hours",ot_hr)
#         else:
#             print(att)
#             print(att.employee)
#             print("4a")
#             print(ot_hr , "ot_hr")
            
#             ot_doc = frappe.get_doc({
#                 "doctype": "Over Time",
#                 "employee": att.employee,
#                 "ot_date": att.attendance_date,
#                 "shift": att.shift,
#                 "overtime_hours": ot_hr,
#                 "reason": "Automatic Creation"
#             })
#             ot_doc.insert(ignore_permissions=True)
#     else:
#         if existing_ot:
#             frappe.delete_doc("Over Time",existing_ot,force=1)

def create_update_delete_ot(att, ot_hr):
    print("1a")

    employee = att.employee if hasattr(att, "employee") else att.get("employee")
    attendance_date = att.attendance_date if hasattr(att, "attendance_date") else att.get("attendance_date")
    shift = att.shift if hasattr(att, "shift") else att.get("shift")

    existing_ot = frappe.db.get_value(
        "Over Time",
        {"employee": employee, "ot_date": attendance_date},
        "name"
    )

    if ot_hr and float(ot_hr) > 0.5:
        print("2a")
        if existing_ot:
            print("3a")
            frappe.db.set_value(
                "Over Time",
                existing_ot,
                "overtime_hours",
                ot_hr
            )
        else:
            print("4a", ot_hr)

            ot_doc = frappe.get_doc({
                "doctype": "Over Time",
                "employee": employee,
                "ot_date": attendance_date,
                "shift": shift,
                "overtime_hours": ot_hr,
                "reason": "Automatic Creation"
            })
            ot_doc.insert(ignore_permissions=True)
    else:
        if existing_ot:
            frappe.delete_doc("Over Time", existing_ot, force=1)


@frappe.whitelist()
def mark_att_with_employee_ww_submit(from_date, to_date, employee):

    attendances = frappe.get_all("Attendance",filters={"employee": employee,"attendance_date": ["between", [from_date, to_date]],"weekly_off": 1,"docstatus": 0},pluck="name")

    for att_name in attendances:
        att_doc = frappe.get_doc("Attendance", att_name)
        att_doc.submit()
    return "ok"       

@frappe.whitelist()
def mark_att_for_all_ww_submit(from_date, to_date):

    attendances = frappe.get_all("Attendance",filters={"attendance_date": ["between", [from_date, to_date]],"weekly_off": 1,"docstatus": 0},pluck="name")

    for att_name in attendances:
        att_doc = frappe.get_doc("Attendance", att_name)
        att_doc.submit()        
    return "ok"       