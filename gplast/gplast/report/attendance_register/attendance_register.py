from __future__ import unicode_literals
from functools import total_ordering
from itertools import count
import frappe
from frappe import permissions
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days,date_diff
from math import floor
from frappe import msgprint, _
from calendar import month, monthrange
from datetime import date, timedelta, datetime,time
import datetime as dt

status_map = {
    'On Duty': 'OD', 'Half Day': 'HD', "Absent": "A", "Holiday": "HH",
    "Weekly Off": "WW", "Present": "P", "On Leave": "On Leave", "Work From Home": "WFH", 
    "Leave Without Pay": "LOP", "Casual Leave": "CL", "Earned Leave": "EL", "Sick Leave": "SL", 
    "Privilege Leave": "PVL", "Compensatory Off": "C-OFF"
}

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        _("Employee ID") + ":Data/:150", _("Employee Name") + ":Data/:200", _("Department") + ":Data/:150",
        _("Designation") + ":Data/:150", _("DOJ") + ":Date/:100", _("") + ":Data/:100"
    ]
    
    dates = get_dates(filters.from_date, filters.to_date)
    for date in dates:
        date = datetime.strptime(date,'%Y-%m-%d')
        day = datetime.date(date).strftime('%d')
        month = datetime.date(date).strftime('%b')
        columns.append(_(day + '/' + month) + ":Data/:70")
        
    columns += [_("Present") + ":Data/:100", _('Half Day') + ':Data/:100', _("Absent") + ":Data/:100", _("Casual Leave") + ':Data/:100',
    _("Sick Leave") + ':Data/:100',_("Leave Without Pay") + ':Data/:100',_("Compensatory Off") + ':Data/:100',_("On Duty in Days") + ':Data/:100',_("Holiday") + ':Data/:100',
    _("Weekly Off")]
    
    return columns

def get_dates(from_date,to_date):
    no_of_days = date_diff(add_days(to_date, 1), from_date)
    dates = [add_days(from_date, i) for i in range(0, no_of_days)]
    return dates

def get_data(filters):
    data = []
    employees = get_employees(filters)
    date_range = get_dates(filters.from_date, filters.to_date)
    attendance_data = fetch_attendance_data(filters, employees, date_range)
    holiday_data_new = fetch_holiday_data(employees)
    for emp in employees:
        emp_data = process_employee_data(emp, date_range, attendance_data, holiday_data_new)
        data.extend(emp_data)
       
    return data

def fetch_attendance_data(filters, employees, date_range):
    employee_ids = [emp.name for emp in employees]
    
    
    attendance = frappe.db.sql("""
                                SELECT employee, 
                                attendance_date, status, late_entry, late_entry, late_entry_time,
                                in_time, out_time, shift, 
                                ot_hours, total_working_hours, 
                                leave_type, shift_status, 
                                on_duty_application, leave_application
                                FROM `tabAttendance`
                                WHERE attendance_date BETWEEN %s AND %s 
                                AND employee IN %s AND docstatus != 2
                            """, (filters.from_date, filters.to_date, tuple(employee_ids)), as_dict=True)
    
    attendance_map = {(att['employee'], att['attendance_date']): att for att in attendance}
    
    return attendance_map

def fetch_holiday_data(employees):
    holiday_data = {}
    for emp in employees:
        holiday_list = frappe.db.get_value('Employee', {'name': emp.name}, 'holiday_list')
        holidays = frappe.db.sql("""
                                SELECT h.holiday_date, h.weekly_off, h.national_holiday, h.festival_holiday
                                FROM `tabHoliday` h 
                                JOIN `tabHoliday List` hl ON hl.name = h.parent 
                                WHERE hl.name = %s
                            """, holiday_list, as_dict=True)
        holiday_data[emp.name] = {holiday['holiday_date']: holiday for holiday in holidays}
        # for holiday in holidays:
        #     holiday_data[emp.name][holiday['weekly_off']] = holiday	
        for holiday in holidays:
            if holiday.weekly_off:
                holiday_data[emp.name][holiday['weekly_off']] = holiday
            if holiday.national_holiday:
                holiday_data[emp.name][holiday['national_holiday']] = holiday
            if holiday.festival_holiday:
                holiday_data[emp.name][holiday['festival_holiday']] = holiday	
        
    return holiday_data

def process_employee_data(emp, date_range, attendance_data, holiday_data_new):
    row1, row2, row3, row4, row5, row6, row7, row8, row9, row10, row11, row12, row13, row14 = initialize_rows(emp)
    total_present = total_half_day = total_absent = total_sick_leave = total_casual_leave = 0
    total_earned_leave = total_od = total_lwp = total_coff_leave = shift_start_time = shift_end_time = on_duty_time = attendance_permission = 0
    total_holiday = weekly_off = on_duty_hours = 0
    work_hours = miss_in = miss_out = work_duration = early_out = sh_start_time = sh_end_time = 0
    
    for date in date_range:
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")
        
        att = attendance_data.get((emp.name, date.date()))
        holiday = holiday_data_new.get(emp.name, {}).get(date.date())
        
        
        if att:
            if holiday:
                if holiday.get('weekly_off'):
                    weekly_off += 1
                # else:
                #     total_holiday += 1
                if holiday.get('national_holiday') or holiday.get('festival_holiday'):
                    total_holiday += 1
            shift_assignment = frappe.db.get_value("Shift Assignment",
                                                   {"employee": att["employee"],
                                                    "start_date": ["<=", date],
                                                    "end_date": [">=", date],
                                                    "docstatus": 1},
                                                    ["shift_type"])
            
            if shift_assignment:
                row1.append(shift_assignment)
            else:
                row1.append("-")
            
            shift_start_time = frappe.db.get_value("Shift Type", {"name": shift_assignment}, ["start_time"])
            if shift_start_time is None:
                shift_start_time = datetime.strptime("00:00:00", "%H:%M:%S").time()

            elif isinstance(shift_start_time, timedelta):
                shift_start_time = (datetime.min + shift_start_time).time()

            sh_start_time = frappe.db.get_value("Shift Type", {"name": att["shift"]}, ["start_time"])
            if sh_start_time is None:
                sh_start_time = datetime.strptime("00:00:00", "%H:%M:%S").time()

            elif isinstance(sh_start_time, timedelta):
                sh_start_time = (datetime.min + sh_start_time).time()
                
            shift_end_time = frappe.db.get_value("Shift Type", {"name": shift_assignment}, ["end_time"])
            if shift_end_time is None:
                shift_end_time = datetime.strptime("00:00:00", "%H:%M:%S").time()

            elif isinstance(shift_end_time, timedelta):
                shift_end_time = (datetime.min + shift_end_time).time()

            sh_end_time = frappe.db.get_value("Shift Type", {"name": att["shift"]}, ["end_time"])
            if sh_end_time is None:
                sh_end_time = datetime.strptime("00:00:00", "%H:%M:%S").time()

            elif isinstance(sh_end_time, timedelta):
                sh_end_time = (datetime.min + sh_end_time).time()
            
            on_duty_time = frappe.db.get_value(
                                                "On Duty Application",
                                                {"employee": att["employee"], "from_date": date.date(), "docstatus": ["!=", 2], "workflow_state": ["!=", "Rejected"]},
                                                ["from_time", "to_time"]
                                            )
            

            attendance_permission = frappe.db.sql("""
                                                SELECT SUM(permission_hour)
                                                FROM `tabAttendance Permission`
                                                WHERE employee = %s
                                                AND permission_date = %s
                                                AND workflow_state != "Rejected"
                                                AND docstatus != 2
                                                """, (att["employee"], date.date()))
            
            attendance_permission = attendance_permission[0][0] if attendance_permission else 0
            
            if att["late_entry"] == 1:
                total_seconds = att["late_entry_time"].total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)

                row11.append(f"{hours:02d}:{minutes:02d}")
            else:
                row11.append("-")
            
            if attendance_permission:
                row13.append(attendance_permission)
            else:
                row13.append("-")
            
            if on_duty_time:
                from_time, to_time = on_duty_time
            else:
                from_time, to_time = None, None

            def format_timedelta(td):
                if td is not None:
                    hours, remainder = divmod(td.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    return f"{hours:02}:{minutes:02}"
                return None

            if from_time is not None and to_time is not None:
                row14.append(f"{format_timedelta(from_time)}(IN), {format_timedelta(to_time)}(OUT)")
            else:
                row14.append("-")

            
            if shift_assignment:
                shift_time = datetime.strptime(
                str(shift_start_time), '%H:%M:%S'
                ).time()
                start_time = dt.datetime.combine(att.attendance_date, shift_time)
                row2.append(start_time.strftime("%H:%M"))
            else:
                row2.append('-')
            
            if shift_assignment:
                shift_time = datetime.strptime(
                str(shift_end_time), '%H:%M:%S'
                ).time()
                end_time = dt.datetime.combine(att.attendance_date, shift_time)
                row3.append(end_time.strftime("%H:%M"))
            else:
                row3.append('-')
                
            status = process_attendance_status(att, holiday, row4)
            
            if att['status'] == 'Present' and not holiday:
                total_present += 1

            if att['status'] == 'Half Day' and not holiday and not att['on_duty_application']:
                if att['leave_type']:
                    if att['total_working_hours'] >= 4:
                        total_present += 0.5
                    else:  
                        total_absent += 0.5 
                    leave = status_map.get(att['leave_type'], "")
                    if leave == 'CL':
                        total_casual_leave += 0.5
                    if leave == 'EL':
                        total_earned_leave += 0.5
                    if leave == 'LOP':
                        total_lwp += 0.5
                    if leave == 'SL':
                        total_sick_leave += 0.5
                    if leave == 'C-OFF':
                        total_coff_leave += 0.5
                else:
                    total_half_day += 0.5
            elif att['status'] == 'Half Day' and holiday and not att['on_duty_application']:
                if att['leave_type']:
                    leave = status_map.get(att['leave_type'], "")
                    if leave == 'CL':
                        total_casual_leave += 0.5
                    if leave == 'EL':
                        total_earned_leave += 0.5
                    if leave == 'LOP':
                        total_lwp += 0.5
                    if leave == 'SL':
                        total_sick_leave += 0.5
                    if leave == 'C-OFF':
                        total_coff_leave += 0.5
            if att['status'] == 'Absent' and not holiday and not att['on_duty_application']:
                total_absent += 1
                
            if att['status'] == 'On Leave' and not holiday and not att['on_duty_application']:
                # Fetch the leave count and leave type from the database
                leave_data = frappe.db.sql("""
                    select COUNT(name) as leave_count, leave_type
                    from `tabLeave Application`
                    where workflow_state = "Approved" 
                    and docstatus = 1 
                    and employee = %(employee)s and name != %(leave_application)s
                    and (from_date between %(from_date)s and %(to_date)s
                        or to_date between %(from_date)s and %(to_date)s
                        or (from_date < %(from_date)s and to_date > %(to_date)s))
                """, {
                    "from_date": att['attendance_date'],
                    "to_date": att['attendance_date'],
                    "employee": att['employee'],
                    "leave_application": att['leave_application'],
                })
                if leave_data:
                    leave_count = leave_data[0][0] 
                    leave_type = leave_data[0][1]
                else:
                    leave_count = 0
                    leave_type = None
                if leave_count == 1:
                    leave_type = status_map.get(leave_type, "")
                    leave = status_map.get(att['leave_type'], "")
                    if leave_type:
                        if leave_type == 'CL':
                            total_casual_leave += 0.5
                        if leave_type == 'EL':
                            total_earned_leave += 0.5
                        if leave_type == 'LOP':
                            total_lwp += 0.5
                        if leave_type == 'SL':
                            total_sick_leave += 0.5
                        if leave_type == 'C-OFF':
                            total_coff_leave += 0.5
                    if att['leave_type']:
                        if leave == 'CL':
                            total_casual_leave += 0.5
                        if leave == 'EL':
                            total_earned_leave += 0.5
                        if leave == 'LOP':
                            total_lwp += 0.5
                        if leave == 'SL':
                            total_sick_leave += 0.5
                        if leave == 'C-OFF':
                            total_coff_leave += 0.5
                else:
                    leave = status_map.get(att['leave_type'], "")
                    if leave == 'CL':
                        total_casual_leave += 1
                    if leave == 'EL':
                        total_earned_leave += 1
                    if leave == 'LOP':
                        total_lwp += 1
                    if leave == 'SL':
                        total_sick_leave += 1
                    if leave == 'C-OFF':
                        total_coff_leave += 1
            elif att['status'] == 'On Leave' and holiday and not att['on_duty_application']:
                    # Fetch the leave count and leave type from the database
                leave_data = frappe.db.sql("""
                    select COUNT(name) as leave_count, leave_type
                    from `tabLeave Application`
                    where workflow_state = "Approved" 
                    and docstatus = 1 
                    and employee = %(employee)s and name != %(leave_application)s
                    and (from_date between %(from_date)s and %(to_date)s
                        or to_date between %(from_date)s and %(to_date)s
                        or (from_date < %(from_date)s and to_date > %(to_date)s))
                """, {
                    "from_date": att['attendance_date'],
                    "to_date": att['attendance_date'],
                    "employee": att['employee'],
                    "leave_application": att['leave_application'],
                })

                # Get the first result (if any)
                if leave_data:
                    leave_count = leave_data[0][0] 
                    leave_type = leave_data[0][1]
                else:
                    leave_count = 0
                    leave_type = None
                if leave_count == 1:
                    leave_type = status_map.get(leave_type, "")
                    leave = status_map.get(att['leave_type'], "")
                    if leave_type:
                        if leave_type == 'CL':
                            total_casual_leave += 0.5
                        if leave_type == 'EL':
                            total_earned_leave += 0.5
                        if leave_type == 'LOP':
                            total_lwp += 0.5
                        if leave_type == 'SL':
                            total_sick_leave += 0.5
                        if leave_type == 'C-OFF':
                            total_coff_leave += 0.5
                    if att['leave_type']:
                        if leave == 'CL':
                            total_casual_leave += 0.5
                        if leave == 'EL':
                            total_earned_leave += 0.5
                        if leave == 'LOP':
                            total_lwp += 0.5
                        if leave == 'SL':
                            total_sick_leave += 0.5
                        if leave == 'C-OFF':
                            total_coff_leave += 0.5
                else:
                    leave = status_map.get(att['leave_type'], "")
                    if leave == 'CL':
                        total_casual_leave += 1
                    if leave == 'PVL':
                        total_earned_leave += 1
                    if leave == 'LOP':
                        total_lwp += 1
                    if leave == 'SL':
                        total_sick_leave += 1
                    if leave == 'C-OFF':
                        total_coff_leave += 1
            if att['in_time'] and att['out_time']:
                if att["in_time"]:
                    row6.append(att["in_time"].strftime("%H:%M"))
                else:
                    row6.append("-")
                if att['out_time']:
                    row7.append(att["out_time"].strftime("%H:%M"))
                else:
                    row7.append("-")
            elif not att['in_time'] and att['out_time']:
                row6.append('M')
                row7.append(att['out_time'].strftime('%H:%M'))
                miss_in += 1
            elif not att['out_time'] and att['in_time']:
                row6.append(att['in_time'].strftime('%H:%M'))
                row7.append('M')
                miss_out += 1
            else:
                row6.append('-')
                row7.append('-')
            if att["shift"] and att["ot_hours"]:
                total_seconds = att["ot_hours"].total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                row9.append(f"{hours:02d}:{minutes:02d}" if att['ot_hours'] else '-')
            else:
                row9.append('-')
            
            if att["in_time"] and att["out_time"]:
                if att["in_time"].time() <= sh_start_time and att["out_time"].time() >= sh_end_time:
                    work_duration = datetime.combine(datetime.min, sh_end_time) - datetime.combine(datetime.min, sh_start_time)
                elif att["in_time"].time() <= sh_start_time and att["out_time"].time() <= sh_end_time:
                    work_duration = datetime.combine(datetime.min, att["out_time"].time()) - datetime.combine(datetime.min, sh_start_time)
                elif att["in_time"].time() >= sh_start_time and att["out_time"].time() >= sh_end_time:
                    work_duration = datetime.combine(datetime.min, sh_end_time) - datetime.combine(datetime.min, att["in_time"].time())
                elif att["in_time"].time() >= sh_start_time and att["out_time"].time() <= sh_end_time:
                    work_duration = datetime.combine(datetime.min, att["out_time"].time()) - datetime.combine(datetime.min, att["in_time"].time())
                else:
                    work_duration = timedelta(0)

                work_hours = work_duration.total_seconds() / 3600

                row8.append(f"{work_hours:.2f}" if work_hours > 0 else '-')
            else:
                row8.append("-")
                
            if att["in_time"] and att["out_time"]:
                total_hours = att["total_working_hours"]
                row10.append(f"{total_hours:.2f}")
            else:
                row10.append('-')
            
            if att["shift"] and att["out_time"]:
                if att["out_time"].time() < sh_end_time:
                    early_out = datetime.combine(datetime.min, sh_end_time) - datetime.combine(datetime.min, att["out_time"].time())
                    
                    # Convert timedelta to total seconds
                    early_out_seconds = early_out.total_seconds()

                    # Calculate hours and minutes
                    total_hours = int(early_out_seconds // 3600)
                    total_minutes = int((early_out_seconds % 3600) // 60)

                    # Format as HH:MM
                    row12.append(f"{total_hours:02d}:{total_minutes:02d}")
                else:
                    row12.append("-")
            else:
                row12.append("-")

            if att["shift"]:
                row5.append(att["shift"])
            else:
                row5.append("-")


        else:
            if holiday:
                if holiday.get('weekly_off'):
                    weekly_off += 1
                # else:
                #     total_holiday += 1
                if holiday.get('national_holiday') or holiday.get('festival_holiday'):
                    total_holiday += 1
            print(total_holiday)
                    # frappe.errprint(total_holiday,"2")
            append_holiday_or_default(holiday, row1, row2, row3, row4, row5, row6, row7, row8, row9, row10, row11, row12, row13, row14)
    # weekly_off = "2"
    # finalize_row_data(row1, row2, row3, row4, row5, row6, row7, row8, row9, row10, row11, row12, row13, row14, total_present, total_half_day, total_absent,total_casual_leave,
    # total_earned_leave,total_lwp, total_sick_leave,total_coff_leave,total_od,on_duty_hours, miss_in, miss_out,total_holiday,weekly_off)
    finalize_row_data(row1, row2, row3, row4, row5, row6, row7, row8, row9, row10, row11, row12, row13, row14, total_present, total_half_day, total_absent,total_casual_leave,
    total_earned_leave,total_lwp, total_sick_leave,total_coff_leave,total_holiday, weekly_off, total_od,on_duty_hours, miss_in, miss_out)
    print(total_holiday)
    return [row1, row2, row3, row4, row5, row6, row7, row8, row9, row10,  row11, row12, row13, row14]

def initialize_rows(emp):
    return (
        [emp.name, emp.employee_name, emp.department, emp.designation, emp.date_of_joining, "Shift"],
        ["", "", "", "", "", "Shift In"],
        ["", "", "", "", "", "Shift Out"],
        ["", "", "", "", "", "Status"],
        ["", "", "", "", "", "Att Shift"],
        ["", "", "", "", "", "In Time"],
        ["", "", "", "", "", "Out Time"],
        ["", "", "", "", "", "Work Duration"],
        ["", "", "", "", "", "OT"],
        ["", "", "", "", "", "Total Duration"],
        ["", "", "", "", "", "Late"],
        ["", "", "", "", "", "Early"],
        ["", "", "", "", "", "Permission"],
        ["", "", "", "", "", "On Duty"]
    )

def process_attendance_status(att, holiday, row4):
    status = status_map.get(att['status'], "")
    leave = status_map.get(att['leave_type'], "")
    if status == "On Leave" and not att['on_duty_application']:
        leave_data = frappe.db.sql("""
            select COUNT(name) as leave_count, leave_type
            from `tabLeave Application`
            where workflow_state = "Approved" 
            and docstatus = 1 
            and employee = %(employee)s and name != %(leave_application)s
            and (from_date between %(from_date)s and %(to_date)s
                or to_date between %(from_date)s and %(to_date)s
                or (from_date < %(from_date)s and to_date > %(to_date)s))
        """, {
            "from_date": att['attendance_date'],
            "to_date": att['attendance_date'],
            "employee": att['employee'],
            "leave_application": att['leave_application'],
        })

        # Get the first result (if any)
        if leave_data:
            leave_count = leave_data[0][0] 
            leave_type = leave_data[0][1]
            leave_type = status_map.get(leave_type, "")
            if leave_count == 1:
                row4.append(f'{leave_type}-{leave}' or status)
            else:
                row4.append(leave or status)
        else:
            row4.append(leave or status)
    elif att['status'] == 'Absent' and not holiday and not att['on_duty_application']:
        if att['in_time'] and att['out_time']:  
            row4.append(status or '-')
        elif not att['in_time'] and att['out_time']:
            row4.append(status or '-')  
        elif att['in_time'] and not att['out_time']: 
            row4.append(status or '-')
        else:
            row4.append(status or '-')
    elif att['status'] == 'Absent' and holiday and not  att['on_duty_application']:
        
        if att['in_time'] and att['out_time']:  
            row4.append(status or '-')
        elif not att['in_time'] and att['out_time']:
            row4.append(status or '-')  
        elif att['in_time'] and not att['out_time']: 
            row4.append(status or '-')
        else:
            weekly_off = 0
            weekly_off = append_holiday_or_default_new(holiday, row4, weekly_off) 
    elif att['status'] == "Half Day" and att['leave_type'] and not att['on_duty_application']:
        if att['total_working_hours']:
            if att['total_working_hours'] < 4:
                row4.append(f"A-{leave}")
            else:
                row4.append(f"P-{leave}")
    elif att['leave_type'] and not att['on_duty_application']:
        row4.append(f"{status}- P")
    else:
        row4.append(status or '-')

    return status

def append_holiday_or_default(holiday, row1, row2, row3, row4, row5, row6, row7, row8, row9, row10, row11, row12, row13, row14):
    # if holiday:
    #     row4.append(holiday['weekly_off'] and 'WW')
    if holiday:
        if holiday.get('weekly_off'):
            row4.append('WW')
        elif holiday.get('national_holiday'):
            row4.append('NH')
        elif holiday.get('festival_holiday'):
            row4.append('FH')
        else:
            row4.append('-')
    else:
        row4.append('-')
    row5.append('-')
    row6.append('-')
    row1.append('-')
    row8.append('-')
    row7.append('-')
    row2.append('-')
    row3.append('-')
    row9.append('-')
    row10.append('-')
    row11.append('-')
    row12.append('-')
    row13.append('-')
    row14.append('-')
    
def finalize_row_data(row1, row2, row3, row4, row5, row6, row7, row8, row9, row10, row11, row12, row13, row14, total_present, total_half_day, total_absent,total_casual_leave,total_earned_leave,total_lwp, total_sick_leave,total_coff_leave,total_holiday,weekly_off,total_od,on_duty_hours, miss_in, miss_out):
# def finalize_row_data(row1, row2, row3, row4, row5, row6, row7, row8, row9, row10, row11, row12, row13, row14, total_present, total_half_day, total_absent,total_casual_leave,total_earned_leave,total_lwp, total_sick_leave,total_coff_leave,total_od,total_holiday,weekly_off,on_duty_hours, miss_in, miss_out):
    row4.extend([total_present, total_half_day, total_absent,total_casual_leave, total_sick_leave,total_earned_leave,total_lwp,total_coff_leave,total_holiday,weekly_off,total_od,on_duty_hours, miss_in, miss_out])
    row5.extend(['-', '-', '-', '-', '-', '-', '-', '-','-', '-', '-', '-', '-', '-', '-','-'])
    row6.extend(['-', '-', '-', '-', '-', '-', '-', '-','-', '-', '-', '-', '-', '-', '-','-'])
    row1.extend(['-', '-', '-', '-', '-', '-', '-', '-','-', '-', '-', '-', '-', '-', '-','-'])
    row8.extend(['-', '-', '-', '-', '-', '-', '-', '-','-', '-', '-', '-', '-', '-', '-','-'])
    row7.extend(['-', '-', '-', '-', '-', '-', '-', '-','-', '-', '-', '-', '-', '-', '-','-'])
    row2.extend(['-', '-', '-', '-', '-', '-', '-', '-','-', '-', '-', '-', '-', '-', '-','-'])
    row3.extend(['-', '-', '-', '-', '-', '-', '-', '-','-', '-', '-', '-', '-', '-', '-','-'])
    row9.extend(['-', '-', '-', '-', '-', '-', '-', '-','-', '-', '-', '-', '-', '-', '-','-'])
    row10.extend(['-', '-', '-', '-', '-', '-', '-', '-','-', '-', '-', '-', '-', '-', '-','-'])
    row11.extend(['-', '-', '-', '-', '-', '-', '-', '-','-', '-', '-', '-', '-', '-', '-','-'])
    row12.extend(['-', '-', '-', '-', '-', '-', '-', '-','-', '-', '-', '-', '-', '-', '-','-'])
    row13.extend(['-', '-', '-', '-', '-', '-', '-', '-','-', '-', '-', '-', '-', '-', '-','-'])
    row14.extend(['-', '-', '-', '-', '-', '-', '-', '-','-', '-', '-', '-', '-', '-', '-','-'])
    
def get_employees(filters):
    conditions = []
    if filters.employee:
        conditions.append(f"employee = '{filters.employee}'")
    if filters.designation:
        conditions.append(f"designation = '{filters.designation}'")
    if filters.department:
        conditions.append(f"department = '{filters.department}'")
    
    query_conditions = " AND ".join(conditions) if conditions else '1=1'
    
    employees = frappe.db.sql(f"""
        SELECT name, employee_name, department, designation, date_of_joining, holiday_list 
        FROM `tabEmployee` 
        WHERE status = 'Active' AND {query_conditions}
    """, as_dict=True)
    
    left_employees = frappe.db.sql(f"""
        SELECT name, employee_name, department, designation, date_of_joining, holiday_list 
        FROM `tabEmployee` 
        WHERE status = 'Left' AND relieving_date >= '{filters.from_date}' AND {query_conditions}
    """, as_dict=True)
    
    employees.extend(left_employees)
    return employees

def append_holiday_or_default_new(holiday, row4,weekly_off):
    # weekly_off = 0
    # total_holiday = 0
    # if holiday:
    #     row4.append(holiday['weekly_off'] and 'WW')
    if holiday:
        if holiday.get('weekly_off'):
            row4.append('WW')
            # weekly_off += 1
        elif holiday.get('national_holiday'):
            row4.append('NH')
            # total_holiday += 1
        elif holiday.get('festival_holiday'):
            row4.append('FH')
            # total_holiday += 1
        else:
            row4.append('-')
    else:
        row4.append('-')
