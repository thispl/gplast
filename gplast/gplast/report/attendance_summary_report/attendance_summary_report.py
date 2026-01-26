# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import timedelta, datetime

status_map = {
    'Half Day': 'HD', "Absent": "A", "Holiday": "HH",
    "Weekly Off": "WO", "Present": "P", "On Leave": "On Leave"
}

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Attendance Date"), "fieldname": "attendance_date", "fieldtype": "Data", "width": 100, "align": "center"},
        {"label": _("Shift"), "fieldname": "shift", "fieldtype": "Data", "width": 60, "align": "center"},
        {"label": _("S.In Time"), "fieldname": "shift_in_time", "fieldtype": "Data", "width": 80, "align": "center"},
        {"label": _("S.Out Time"), "fieldname": "shift_out_time", "fieldtype": "Data", "width": 80, "align": "center"},
        {"label": _("Attended Shift"), "fieldname": "attended_shift", "fieldtype": "Data", "width": 80, "align": "center"},
        {"label": _("A.In Time"), "fieldname": "attendance_in_time", "fieldtype": "Data", "width": 80, "align": "center"},
        {"label": _("A.Out Time"), "fieldname": "attendance_out_time", "fieldtype": "Data", "width": 80, "align": "center"},
        {"label": _("Work Duration"), "fieldname": "work_duration", "fieltype": "Data", "width": 100, "align": "center"},
        {"label": _("OT"), "fieldname": "ot", "fieldtype": "Data", "width": 80, "align": "center"},
        {"label": _("Total Duration"), "fieldname": "total_duration", "fieldtype": "Data", "width": 100, "align": "center"},
        {"label": _("Late By"), "fieldname": "late_by", "fieldtype": "Data", "width": 80, "align": "center"},
        {"label": _("Late Times"), "fieldname": "late_times", "fieldtype": "Data", "width": 80, "align": "right"},
        {"label": _("Early Going By"), "fieldname": "early_going_by", "fieldtype": "Data", "width": 80, "align": "center"},
        {"label": _("Permission"), "fieldname": "permission", "fieldtype": "Data", "width": 80, "align": "center"},
        {"label": _("Permission in Hours"), "fieldname": "permission_in_hours", "fieldtype": "Data", "width": 80, "align": "right"},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 80, "align": "center"},
        {"label": _("Permission/Late/Early"), "fieldname": "permission_late_early", "fieldtype": "Data", "width": 120, "align": "center"},
        {"label": _("Punch Records"), "fieldname": "punch_records", "fieldtype": "Data", "width": 100}
    ]

def get_data(filters):

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    employee = filters.get("employee")

    attendance = frappe.db.get_all("Attendance",
                            {"attendance_date": ["BETWEEN", [from_date, to_date]],
                            "employee": employee, "docstatus": ["!=", 2]},
                            ["attendance_date", "shift", "in_time", "out_time", "status", "late_entry", "late_entry_time", "ot_hours", "total_working_hours"],
                            order_by = "attendance_date ASC")
    
    result = []
    late = timedelta(hours=0, minutes=15, seconds=0)
    late_count = 0
    data = ""

    for att in attendance:
        
        #Shift Assignment
        shift_assignment = frappe.db.get_value("Shift Assignment",
                                                   {"employee": employee,
                                                    "start_date": ["<=", att["attendance_date"]],
                                                    "end_date": [">=", att["attendance_date"]],
                                                    "docstatus": 1},
                                                    ["shift_type"])
        
        
        #Shift Assignemt Start Time
        s_start_time = frappe.db.get_value("Shift Type", {"name": shift_assignment}, ["start_time"])
        if s_start_time is None:
                s_start_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
        elif isinstance(s_start_time, timedelta):
            s_start_time = (datetime.min + s_start_time).time()
        else:
            s_start_time = "-"


        #Shift Assignment End Time
        s_end_time = frappe.db.get_value("Shift Type", {"name": shift_assignment}, ["end_time"])
        if s_end_time is None:
            s_end_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
        elif isinstance(s_end_time, timedelta):
            s_end_time = (datetime.min + s_end_time).time()
        else:
            s_end_time = "-"


        #Attendance Shift Start Time  
        shift_start_time = frappe.db.get_value("Shift Type", {"name": att["shift"]}, ["start_time"])
        if shift_start_time is None:
                shift_start_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
        elif isinstance(shift_start_time, timedelta):
            shift_start_time = (datetime.min + shift_start_time).time()
        else:
            shift_start_time = "-"


        #Attendance Shift End Time
        shift_end_time = frappe.db.get_value("Shift Type", {"name": att["shift"]}, ["end_time"])
        if shift_end_time is None:
            shift_end_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
        elif isinstance(shift_end_time, timedelta):
            shift_end_time = (datetime.min + shift_end_time).time()
        else:
            shift_end_time = "-"


        #Work Duration
        if att["in_time"] and att["out_time"]:
            if att["in_time"].time() <= shift_start_time and att["out_time"].time() >= shift_end_time:
                work_duration = datetime.combine(datetime.min, shift_end_time) - datetime.combine(datetime.min, shift_start_time)
            elif att["in_time"].time() <= shift_start_time and att["out_time"].time() <= shift_end_time:
                work_duration = datetime.combine(datetime.min, att["out_time"].time()) - datetime.combine(datetime.min, shift_start_time)
            elif att["in_time"].time() >= shift_start_time and att["out_time"].time() >= shift_end_time:
                work_duration = datetime.combine(datetime.min, shift_end_time) - datetime.combine(datetime.min, att["in_time"].time())
            elif att["in_time"].time() >= shift_start_time and att["out_time"].time() <= shift_end_time:
                work_duration = datetime.combine(datetime.min, att["out_time"].time()) - datetime.combine(datetime.min, att["in_time"].time())
            else:
                work_duration = timedelta(0)

            work_hours = work_duration.total_seconds() / 3600

            wd = (f"{work_hours:.2f}" if work_hours > 0 else '-')
        else:
            wd = "-"

        
        #OT
        if att["ot_hours"]:
            total_seconds = att["ot_hours"].total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)

            ot = (f"{hours:02d}:{minutes:02d}")
        else:
            ot = "-"

        
        #Late By
        if att["late_entry"] == 1 and att["late_entry_time"] <= late:
            total_seconds = att["late_entry_time"].total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)

            late_entry = (f"{hours:02d}:{minutes:02d}")
        else:
            late_entry = "-"
        

        #Late Times
        if att["late_entry"] and att["late_entry_time"] <= late:
            late_count += 1


        #Early Going By
        if isinstance(shift_end_time, timedelta):
            shift_end_time = (datetime.min + shift_end_time).time()

        if att["out_time"]:
            shift_end_time_datetime = datetime.combine(att["out_time"].date(), shift_end_time)
            exit_duration = (shift_end_time_datetime - att["out_time"]).total_seconds() / 60

            hours = int(exit_duration // 60)
            minutes = int(exit_duration % 60)
            exit_duration_display = f"{hours:02d}:{minutes:02d}" if (0 < exit_duration <= 15) else "-"

            #Permission(Early)
            exit_duration = f"{hours:02}:{minutes:02d}" if (15 < exit_duration < 120) else "-"
        else:
            exit_duration_display = "-"
            exit_duration = "-"


        #Permission(Late)
        if att["late_entry"] == 1 and att["late_entry_time"] > late:
            total_seconds = att["late_entry_time"].total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)

            formatted_time = (f"{hours:02d}:{minutes:02d}")
        else:
            formatted_time = "-"


        #Permission
        permissions = frappe.db.sql("""
            SELECT reason, permission_hour 
            FROM `tabAttendance Permission`
            WHERE employee = %s 
            AND permission_date = %s
            AND workflow_state != "Rejected" 
            AND docstatus != 2
            AND reason IN ("Late Entry", "Early Exit")
        """, (employee, att["attendance_date"]))

        permission_list = []
        total_permission_hours = 0

        for reason, permission_hour in permissions:
            if reason == "Early Exit" and exit_duration != "-":
                permission_list.append(exit_duration)
            if reason == "Late Entry" and formatted_time != "-":
                permission_list.append(formatted_time)

            #Permission in hours
            if permission_hour:
                total_permission_hours += int(permission_hour)

        attendance_permission = ", ".join(permission_list) if permission_list else "-"

        
        #Status
        holiday_list = frappe.db.get_value("Employee", {"employee": employee}, "holiday_list")

        if not holiday_list:
            company = frappe.db.get_value("Employee", {"employee": employee}, "company")
            holiday_list = frappe.db.get_value("Company", {"name": company}, "default_holiday_list")

        weekly_off = frappe.db.get_value(
            "Holiday", 
            {"parent": holiday_list, "holiday_date": att["attendance_date"], "weekly_off": 1}, 
            "name"
        )
        
        status = status_map.get(att["status"], att["status"])

        if weekly_off:
            status = "WO"

        if status == "P" and late_entry != "-":
            status = "P(Late)"

        if status == "P" and exit_duration_display != "-":
            status = "P(Early)"

        if status == "HD" and late_entry != "-":
            status = "HD(Late)"
        
        if status == "HD" and exit_duration_display != "-":
            status = "HD(Early)"


        # Permission/Late/Early
        status_list = []

        if late_entry and late_entry != "-":
            status_list.append("Late")

        if exit_duration_display and exit_duration_display != "-":
            status_list.append("Early")

        if attendance_permission and attendance_permission != "-":
            status_list.append("Permission")

        data = "/".join(status_list).strip() if status_list else "-"

        
        #Punch Records
        checkin_data = frappe.db.sql(f"""
            SELECT 
                GROUP_CONCAT(CONCAT(TIME_FORMAT(ec.time, '%H:%i')) ORDER BY ec.time SEPARATOR ', ') AS checkin_times
            FROM `tabEmployee Checkin` ec
            JOIN `tabAttendance` att ON ec.attendance = att.name
            WHERE ec.employee = '{employee}' 
            AND DATE(ec.time) = '{att["attendance_date"]}'
            AND att.name = ec.attendance
        """, as_dict=True)

        checkin_times = checkin_data[0]["checkin_times"] if checkin_data and checkin_data[0]["checkin_times"] else ""


        result.append([
            att["attendance_date"].strftime("%d-%b-%Y"),
            shift_assignment if shift_assignment else "-",
            s_start_time.strftime("%H:%M") if shift_assignment else "-",
            s_end_time.strftime("%H:%M") if shift_assignment else "-",
            att["shift"] if att["shift"] else "-",
            att["in_time"].strftime("%H:%M") if att["in_time"] else "-",
            att["out_time"].strftime("%H:%M") if att["out_time"] else "-",
            wd,
            ot,
            f"{att['total_working_hours']:.2f}" if att["total_working_hours"] else "-",
            late_entry,
            late_count if att["late_entry"] and att["late_entry_time"] <= late else "-",
            exit_duration_display,
            attendance_permission,
            total_permission_hours if total_permission_hours > 0 else "-",
            status if status else "-",
            data,
            checkin_times
        ])
        
    return result