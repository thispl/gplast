# # Copyright (c) 2025, Teampro and contributors
# # For license information, please see license.txt

# import frappe
# from frappe import _
# from datetime import timedelta, datetime

# status_map = {
#     'Half Day': 'HD', "Absent": "A", "Holiday": "HH",
#     "Weekly Off": "WO", "Present": "P", "On Leave": "On Leave"
# }

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data

# def get_columns():
#     return [
#         {"label": _("Attendance Date"), "fieldname": "attendance_date", "fieldtype": "Data", "width": 100, "align": "center"},
#         {"label": _("Shift"), "fieldname": "shift", "fieldtype": "Data", "width": 60, "align": "center"},
#         {"label": _("S.In Time"), "fieldname": "shift_in_time", "fieldtype": "Data", "width": 80, "align": "center"},
#         {"label": _("S.Out Time"), "fieldname": "shift_out_time", "fieldtype": "Data", "width": 80, "align": "center"},
#         {"label": _("Attended Shift"), "fieldname": "attended_shift", "fieldtype": "Data", "width": 80, "align": "center"},
#         {"label": _("A.In Time"), "fieldname": "attendance_in_time", "fieldtype": "Data", "width": 80, "align": "center"},
#         {"label": _("A.Out Time"), "fieldname": "attendance_out_time", "fieldtype": "Data", "width": 80, "align": "center"},
#         {"label": _("Work Duration"), "fieldname": "work_duration", "fieltype": "Data", "width": 100, "align": "center"},
#         {"label": _("OT"), "fieldname": "ot", "fieldtype": "Data", "width": 80, "align": "center"},
#         {"label": _("Total Duration"), "fieldname": "total_duration", "fieldtype": "Data", "width": 100, "align": "center"},
#         {"label": _("Late By"), "fieldname": "late_by", "fieldtype": "Data", "width": 80, "align": "center"},
#         {"label": _("Late Times"), "fieldname": "late_times", "fieldtype": "Data", "width": 80, "align": "right"},
#         {"label": _("Early Going By"), "fieldname": "early_going_by", "fieldtype": "Data", "width": 80, "align": "center"},
#         {"label": _("Permission"), "fieldname": "permission", "fieldtype": "Data", "width": 80, "align": "center"},
#         {"label": _("Permission in Hours"), "fieldname": "permission_in_hours", "fieldtype": "Data", "width": 80, "align": "right"},
#         {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 80, "align": "center"},
#         {"label": _("Permission/Late/Early"), "fieldname": "permission_late_early", "fieldtype": "Data", "width": 120, "align": "center"},
#         {"label": _("Punch Records"), "fieldname": "punch_records", "fieldtype": "Data", "width": 100}
#     ]

# def get_data(filters):
#     # from_date = filters.get("from_date")
#     # to_date = filters.get("to_date")
#     # employee = filters.get("employee")

#     # attendance = frappe.db.get_all("Attendance",
#     #                         {"attendance_date": ["BETWEEN", [from_date, to_date]],
#     #                         "employee": employee, "docstatus": ["!=", 2]},
#     #                         ["attendance_date", "shift", "in_time", "out_time", "status", "late_entry", "late_entry_time", "ot_hours", "total_working_hours"],
#     #                         order_by = "attendance_date ASC")
    
#     # result = []
#     # late = timedelta(hours=0, minutes=15, seconds=0)
#     # late_count = 0
#     # data = ""

#     # for att in attendance:
        
#     #     #Shift Assignment
#     #     shift_assignment = frappe.db.get_value("Shift Assignment",
#     #                                                {"employee": employee,
#     #                                                 "start_date": ["<=", att["attendance_date"]],
#     #                                                 "end_date": [">=", att["attendance_date"]],
#     #                                                 "docstatus": 1},
#     #                                                 ["shift_type"])
        
        
#     #     #Shift Assignemt Start Time
#     #     s_start_time = frappe.db.get_value("Shift Type", {"name": shift_assignment}, ["start_time"])
#     #     if s_start_time is None:
#     #             s_start_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
#     #     elif isinstance(s_start_time, timedelta):
#     #         s_start_time = (datetime.min + s_start_time).time()
#     #     else:
#     #         s_start_time = "-"


#     #     #Shift Assignment End Time
#     #     s_end_time = frappe.db.get_value("Shift Type", {"name": shift_assignment}, ["end_time"])
#     #     if s_end_time is None:
#     #         s_end_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
#     #     elif isinstance(s_end_time, timedelta):
#     #         s_end_time = (datetime.min + s_end_time).time()
#     #     else:
#     #         s_end_time = "-"


#     #     #Attendance Shift Start Time  
#     #     shift_start_time = frappe.db.get_value("Shift Type", {"name": att["shift"]}, ["start_time"])
#     #     if shift_start_time is None:
#     #             shift_start_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
#     #     elif isinstance(shift_start_time, timedelta):
#     #         shift_start_time = (datetime.min + shift_start_time).time()
#     #     else:
#     #         shift_start_time = "-"


#     #     #Attendance Shift End Time
#     #     shift_end_time = frappe.db.get_value("Shift Type", {"name": att["shift"]}, ["end_time"])
#     #     if shift_end_time is None:
#     #         shift_end_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
#     #     elif isinstance(shift_end_time, timedelta):
#     #         shift_end_time = (datetime.min + shift_end_time).time()
#     #     else:
#     #         shift_end_time = "-":

#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")
#     employee = filters.get("employee")   # ✅ FIX 1 (ONLY ADD)

#     attendance_filters = {
#         "attendance_date": ["BETWEEN", [from_date, to_date]],
#         "docstatus": ["!=", 2]
#     }

#     if employee:
#         attendance_filters["employee"] = employee   # ✅ FIX 2

#     attendance = frappe.db.get_all(
#         "Attendance",
#         attendance_filters,
#         ["attendance_date", "shift", "in_time", "out_time", "status",
#          "late_entry", "late_entry_time", "ot_hours", "total_working_hours"],
#         order_by="attendance_date ASC"
#     )

#     result = []
#     late = timedelta(hours=0, minutes=15, seconds=0)
#     late_count = 0
#     data = ""

#     for att in attendance:

#         # Shift Assignment
#         shift_assignment = frappe.db.get_value(
#             "Shift Assignment",
#             {
#                 "employee": employee,
#                 "start_date": ["<=", att["attendance_date"]],
#                 "end_date": [">=", att["attendance_date"]],
#                 "docstatus": 1
#             },
#             "shift_type"
#         )

#         # Shift Start Time
#         s_start_time = frappe.db.get_value("Shift Type", shift_assignment, "start_time")
#         if s_start_time is None:
#             s_start_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
#         elif isinstance(s_start_time, timedelta):
#             s_start_time = (datetime.min + s_start_time).time()
#         else:
#             s_start_time = "-"

#         # Shift End Time
#         s_end_time = frappe.db.get_value("Shift Type", shift_assignment, "end_time")
#         if s_end_time is None:
#             s_end_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
#         elif isinstance(s_end_time, timedelta):
#             s_end_time = (datetime.min + s_end_time).time()
#         else:
#             s_end_time = "-"

#         # Attendance Shift Start Time
#         shift_start_time = frappe.db.get_value("Shift Type", att["shift"], "start_time")
#         if shift_start_time is None:
#             shift_start_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
#         elif isinstance(shift_start_time, timedelta):
#             shift_start_time = (datetime.min + shift_start_time).time()
#         else:
#             shift_start_time = "-"

#         # Attendance Shift End Time
#         shift_end_time = frappe.db.get_value("Shift Type", att["shift"], "end_time")
#         if shift_end_time is None:
#             shift_end_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
#         elif isinstance(shift_end_time, timedelta):
#             shift_end_time = (datetime.min + shift_end_time).time()
#         else:
#             shift_end_time = "-"

#         #Work Duration
#         if att["in_time"] and att["out_time"]:
#             if att["in_time"].time() <= shift_start_time and att["out_time"].time() >= shift_end_time:
#                 work_duration = datetime.combine(datetime.min, shift_end_time) - datetime.combine(datetime.min, shift_start_time)
#             elif att["in_time"].time() <= shift_start_time and att["out_time"].time() <= shift_end_time:
#                 work_duration = datetime.combine(datetime.min, att["out_time"].time()) - datetime.combine(datetime.min, shift_start_time)
#             elif att["in_time"].time() >= shift_start_time and att["out_time"].time() >= shift_end_time:
#                 work_duration = datetime.combine(datetime.min, shift_end_time) - datetime.combine(datetime.min, att["in_time"].time())
#             elif att["in_time"].time() >= shift_start_time and att["out_time"].time() <= shift_end_time:
#                 work_duration = datetime.combine(datetime.min, att["out_time"].time()) - datetime.combine(datetime.min, att["in_time"].time())
#             else:
#                 work_duration = timedelta(0)

#             work_hours = work_duration.total_seconds() / 3600

#             wd = (f"{work_hours:.2f}" if work_hours > 0 else '-')
#         else:
#             wd = "-"

        
#         #OT
#         if att["ot_hours"]:
#             total_seconds = att["ot_hours"].total_seconds()
#             hours = int(total_seconds // 3600)
#             minutes = int((total_seconds % 3600) // 60)

#             ot = (f"{hours:02d}:{minutes:02d}")
#         else:
#             ot = "-"

        
#         #Late By
#         if att["late_entry"] == 1 and att["late_entry_time"] <= late:
#             total_seconds = att["late_entry_time"].total_seconds()
#             hours = int(total_seconds // 3600)
#             minutes = int((total_seconds % 3600) // 60)

#             late_entry = (f"{hours:02d}:{minutes:02d}")
#         else:
#             late_entry = "-"
        

#         #Late Times
#         if att["late_entry"] and att["late_entry_time"] <= late:
#             late_count += 1


#         #Early Going By
#         if isinstance(shift_end_time, timedelta):
#             shift_end_time = (datetime.min + shift_end_time).time()

#         if att["out_time"]:
#             shift_end_time_datetime = datetime.combine(att["out_time"].date(), shift_end_time)
#             exit_duration = (shift_end_time_datetime - att["out_time"]).total_seconds() / 60

#             hours = int(exit_duration // 60)
#             minutes = int(exit_duration % 60)
#             exit_duration_display = f"{hours:02d}:{minutes:02d}" if (0 < exit_duration <= 15) else "-"

#             #Permission(Early)
#             exit_duration = f"{hours:02}:{minutes:02d}" if (15 < exit_duration < 120) else "-"
#         else:
#             exit_duration_display = "-"
#             exit_duration = "-"


#         #Permission(Late)
#         if att["late_entry"] == 1 and att["late_entry_time"] > late:
#             total_seconds = att["late_entry_time"].total_seconds()
#             hours = int(total_seconds // 3600)
#             minutes = int((total_seconds % 3600) // 60)

#             formatted_time = (f"{hours:02d}:{minutes:02d}")
#         else:
#             formatted_time = "-"


#         #Permission
#         permissions = frappe.db.sql("""
#             SELECT reason, permission_hour 
#             FROM `tabAttendance Permission`
#             WHERE employee = %s 
#             AND permission_date = %s
#             AND workflow_state != "Rejected" 
#             AND docstatus != 2
#             AND reason IN ("Late Entry", "Early Exit")
#         """, (employee, att["attendance_date"]))

#         permission_list = []
#         total_permission_hours = 0

#         for reason, permission_hour in permissions:
#             if reason == "Early Exit" and exit_duration != "-":
#                 permission_list.append(exit_duration)
#             if reason == "Late Entry" and formatted_time != "-":
#                 permission_list.append(formatted_time)

#             #Permission in hours
#             if permission_hour:
#                 total_permission_hours += int(permission_hour)

#         attendance_permission = ", ".join(permission_list) if permission_list else "-"

        
#         #Status
#         holiday_list = frappe.db.get_value("Employee", {"employee": employee}, "holiday_list")

#         if not holiday_list:
#             company = frappe.db.get_value("Employee", {"employee": employee}, "company")
#             holiday_list = frappe.db.get_value("Company", {"name": company}, "default_holiday_list")

#         weekly_off = frappe.db.get_value(
#             "Holiday", 
#             {"parent": holiday_list, "holiday_date": att["attendance_date"], "weekly_off": 1}, 
#             "name"
#         )
        
#         status = status_map.get(att["status"], att["status"])

#         if weekly_off:
#             status = "WO"

#         if status == "P" and late_entry != "-":
#             status = "P(Late)"

#         if status == "P" and exit_duration_display != "-":
#             status = "P(Early)"

#         if status == "HD" and late_entry != "-":
#             status = "HD(Late)"
        
#         if status == "HD" and exit_duration_display != "-":
#             status = "HD(Early)"


#         # Permission/Late/Early
#         status_list = []

#         if late_entry and late_entry != "-":
#             status_list.append("Late")

#         if exit_duration_display and exit_duration_display != "-":
#             status_list.append("Early")

#         if attendance_permission and attendance_permission != "-":
#             status_list.append("Permission")

#         data = "/".join(status_list).strip() if status_list else "-"

        
#         #Punch Records
#         checkin_data = frappe.db.sql(f"""
#             SELECT 
#                 GROUP_CONCAT(CONCAT(TIME_FORMAT(ec.time, '%H:%i')) ORDER BY ec.time SEPARATOR ', ') AS checkin_times
#             FROM `tabEmployee Checkin` ec
#             JOIN `tabAttendance` att ON ec.attendance = att.name
#             WHERE ec.employee = '{employee}' 
#             AND DATE(ec.time) = '{att["attendance_date"]}'
#             AND att.name = ec.attendance
#         """, as_dict=True)

#         checkin_times = checkin_data[0]["checkin_times"] if checkin_data and checkin_data[0]["checkin_times"] else ""


#         result.append([
#             att["attendance_date"].strftime("%d-%b-%Y"),
#             shift_assignment if shift_assignment else "-",
#             s_start_time.strftime("%H:%M") if shift_assignment else "-",
#             s_end_time.strftime("%H:%M") if shift_assignment else "-",
#             att["shift"] if att["shift"] else "-",
#             att["in_time"].strftime("%H:%M") if att["in_time"] else "-",
#             att["out_time"].strftime("%H:%M") if att["out_time"] else "-",
#             wd,
#             ot,
#             f"{att['total_working_hours']:.2f}" if att["total_working_hours"] else "-",
#             late_entry,
#             late_count if att["late_entry"] and att["late_entry_time"] <= late else "-",
#             exit_duration_display,
#             attendance_permission,
#             total_permission_hours if total_permission_hours > 0 else "-",
#             status if status else "-",
#             data,
#             checkin_times
#         ])
        
#     return result

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
        {"label": _("Employee ID"), "fieldname": "employee", "fieldtype": "Link","options": "Employee", "width": 120},
        {"label": _("Employee Name"), "fieldname": "employee_name","fieldtype": "Data", "width": 150},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Data", "width": 120},
        {"label": _("Unit"), "fieldname": "company", "fieldtype": "Data", "width": 140},
        {"label": _("Cost Center"), "fieldname": "cost_center", "fieldtype": "Data", "width": 120},
        {"label": _("Attendance Date"), "fieldname": "attendance_date", "fieldtype": "Data", "width": 100, "align": "center"},
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



from datetime import datetime, timedelta
import frappe

def get_data(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    employee_filter = filters.get("employee")

    if employee_filter:
        employees = [employee_filter]
    else:
        employees = [e.name for e in frappe.get_all(
            "Employee",
            filters={"status": "Active"},
            fields=["name"]
        )]

    if not employees:
        return []

    emp_details = {
        e.name: e for e in frappe.get_all(
            "Employee",
            filters={"name": ["in", employees]},
            fields=[
                "name", "employee_name", "department",
                "unit", "payroll_cost_center", "holiday_list"
            ]
        )
    }

    attendance_list = frappe.get_all(
        "Attendance",
        filters={
            "attendance_date": ["between", [from_date, to_date]],
            "docstatus": ["!=", 2],
            "employee": ["in", employees]
        },
        fields=[
            "employee", "attendance_date", "shift",
            "in_time", "out_time", "status",
            "late_entry", "late_entry_time",
            "ot_hours", "total_working_hours", "overtime_hours","wh"
        ],
        order_by="employee, attendance_date"
    )

    if not attendance_list:
        return []

    shift_assignments = frappe.get_all(
        "Shift Assignment",
        filters={
            "employee": ["in", employees],
            "start_date": ["<=", to_date],
            "end_date": [">=", from_date],
            "docstatus": 1
        },
        fields=["employee", "shift_type", "start_date", "end_date"]
    )

    shift_map = {}
    for sa in shift_assignments:
        shift_map.setdefault(sa.employee, []).append(sa)

    shift_types = {}
    for sa in shift_assignments:
        if sa.shift_type not in shift_types:
            shift_types[sa.shift_type] = frappe.db.get_value(
                "Shift Type", sa.shift_type, ["start_time", "end_time"]
            )

    permissions = frappe.get_all(
        "Attendance Permission",
        filters={
            "employee": ["in", employees],
            "permission_date": ["between", [from_date, to_date]],
            "workflow_state": ["!=", "Rejected"],
            "docstatus": ["!=", 2]
        },
        fields=["employee", "permission_date", "reason", "permission_hour"]
    )

    permission_map = {}
    for p in permissions:
        permission_map.setdefault((p.employee, p.permission_date), []).append(p)

    checkins = frappe.get_all(
        "Employee Checkin",
        filters={
            "employee": ["in", employees],
            "time": ["between", [from_date + " 00:00:00", to_date + " 23:59:59"]]
        },
        fields=["employee", "time"]
    )

    checkin_map = {}
    for c in checkins:
        checkin_map.setdefault((c.employee, c.time.date()), []).append(
            c.time.strftime("%H:%M")
        )

    result = []
    late_threshold = timedelta(minutes=15)
    late_counter = {}

    for att in attendance_list:
        emp = emp_details.get(att.employee)
        att_date = att.attendance_date

        # Shift
        shift_name = "-"
        shift_start = shift_end = None
        for sa in shift_map.get(att.employee, []):
            if sa.start_date <= att_date <= sa.end_date:
                shift_name = sa.shift_type
                shift_start, shift_end = shift_types.get(shift_name, (None, None))
                break
        # Attendance Shift Start Time
        shift_start_time = frappe.db.get_value("Shift Type", att["shift"], "start_time")
        if shift_start_time is None:
            shift_start_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
        elif isinstance(shift_start_time, timedelta):
            shift_start_time = (datetime.min + shift_start_time).time()
        else:
            shift_start_time = "-"

        # Attendance Shift End Time
        shift_end_time = frappe.db.get_value("Shift Type", att["shift"], "end_time")
        if shift_end_time is None:
            shift_end_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
        elif isinstance(shift_end_time, timedelta):
            shift_end_time = (datetime.min + shift_end_time).time()
        else:
            shift_end_time = "-"

        # Work Duration
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

        # OT
        ot = "-"
        if att.overtime_hours:
            hours = int(att.overtime_hours)
            minutes = int((att.overtime_hours - hours) * 60)
            ot = f"{hours:02d}:{minutes:02d}"



        # Late By
        late_by = "-"
        if att.late_entry and att.late_entry_time:
            mins = int(att.late_entry_time.total_seconds() / 60)
            late_by = f"{mins//60:02d}:{mins%60:02d}"

        # Late Times (COUNT)
        late_counter.setdefault(att.employee, 0)
        late_times = "-"
        if att.late_entry and att.late_entry_time <= late_threshold:
            late_counter[att.employee] += 1
            late_times = late_counter[att.employee]

        # Early Going By
        early_going = "-"
        if att.out_time and shift_end:
            shift_end_dt = datetime.combine(att.out_time.date(), shift_end)
            mins = int((shift_end_dt - att.out_time).total_seconds() / 60)
            if 0 < mins <= 15:
                early_going = f"{mins//60:02d}:{mins%60:02d}"

        # Permission
        perm_key = (att.employee, att_date)
        perms = permission_map.get(perm_key, [])
        perm_list = []
        perm_hours = 0

        for p in perms:
            perm_hours += int(p.permission_hour or 0)
            if p.reason == "Late Entry" and late_by != "-":
                perm_list.append(late_by)
            if p.reason == "Early Exit" and early_going != "-":
                perm_list.append(early_going)

        permission = ", ".join(perm_list) if perm_list else "-"
        perm_hours = perm_hours if perm_hours > 0 else "-"

        # Permission / Late / Early column
        ple = []
        if late_by != "-":
            ple.append("Late")
        if early_going != "-":
            ple.append("Early")
        if permission != "-":
            ple.append("Permission")
        ple_data = "/".join(ple) if ple else "-"

        punches = ", ".join(checkin_map.get((att.employee, att_date), []))

        result.append([
            emp.name,
            emp.employee_name,
            emp.department,
            emp.unit,
            emp.payroll_cost_center,
            att_date.strftime("%d-%b-%Y"),
            att["shift"] if att["shift"] else "-",
            att.in_time.strftime("%H:%M") if att.in_time else "-",
            att.out_time.strftime("%H:%M") if att.out_time else "-",
            # wd,
            f"{att.wh:.2f}" if att.wh else "-",
            ot,
            f"{att.total_working_hours:.2f}" if att.total_working_hours else "-",
            late_by,
            late_times,
            early_going,
            permission,
            perm_hours,
            att.status,
            ple_data,
            punches
        ])

    return result



@frappe.whitelist()
def get_employees_by_user_department(doctype, txt, searchfield, start, page_len, filters):
	user = frappe.session.user

	emp = frappe.db.get_value(
		"Employee",
		{"user_id": user, "status": "Active"},
		["department"],
		as_dict=True
	)

	if not emp or not emp.department:
		return []

	return frappe.db.sql("""
		SELECT name, employee_name
		FROM tabEmployee
		WHERE status = 'Active'
		  AND department = %s
		  AND (name LIKE %s OR employee_name LIKE %s)
		LIMIT %s OFFSET %s
	""", (
		emp.department,
		f"%{txt}%", f"%{txt}%",
		page_len, start
	))

@frappe.whitelist()
def get_all_active_employees(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""
		SELECT name, employee_name
		FROM tabEmployee
		WHERE status = 'Active'
		  AND (name LIKE %s OR employee_name LIKE %s)
		LIMIT %s OFFSET %s
	""", (
		f"%{txt}%", f"%{txt}%",
		page_len, start
	))
