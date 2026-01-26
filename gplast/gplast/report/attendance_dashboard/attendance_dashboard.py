from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, add_days, date_diff, formatdate

def execute(filters=None):
    if not filters:
        filters = {}

    filters = get_conditions(filters)  # Fix: Now filters remains a dictionary
    columns = get_columns()
    
    att_map = get_attendance_map(filters)
    if not att_map:
        return columns, [], None, None

    data = add_data(att_map, filters)
    chart_data = get_chart_data(data, filters)
    return columns, data, None, chart_data

def get_attendance_map(filters):
    att_map = {}
    att_filters = {
        "attendance_date": ["between", [filters["from_date"], filters["to_date"]]],
    }
    
    if filters.get("employee"):
        att_filters["employee"] = filters["employee"]
    if filters.get("shift"):
        att_filters["shift"] = filters["shift"]
    if filters.get("department"):
        att_filters["department"] = filters["department"]
    
    attendance_list = frappe.get_all(
        "Attendance",
        filters=att_filters,
        fields=["employee", "attendance_date", "status", "department", "shift"]
    )

    for record in attendance_list:
        if record.employee not in att_map:
            att_map[record.employee] = {}
        att_map[record.employee][record.attendance_date] = {
            "status": record.status,
            "department": record.department,
            "shift": record.shift
        }
    
    return att_map

def get_attendance_count(date, filters):
    att_filters = {"attendance_date": date, "status": "Present"}

    if filters.get("employee"):
        att_filters["employee"] = filters["employee"]
    if filters.get("shift"):
        att_filters["shift"] = filters["shift"]
    if filters.get("department"):
        att_filters["department"] = filters["department"]
    
    return frappe.db.count("Attendance", filters=att_filters)

def get_leave_count(date, filters):
    leave_filters = {"attendance_date": date, "status": "On Leave"}

    if filters.get("employee"):
        leave_filters["employee"] = filters["employee"]
    if filters.get("shift"):
        leave_filters["shift"] = filters["shift"]
    if filters.get("department"):
        leave_filters["department"] = filters["department"]

    return frappe.db.count("Attendance", filters=leave_filters)

def get_absent_count(date, filters):
    absent_filters = {"attendance_date": date, "status": "Absent"}

    if filters.get("employee"):
        absent_filters["employee"] = filters["employee"]
    if filters.get("shift"):
        absent_filters["shift"] = filters["shift"]
    if filters.get("department"):
        absent_filters["department"] = filters["department"]

    return frappe.db.count("Attendance", filters=absent_filters)

def get_columns():
    return [
        _("Date") + ":Date/:120",
        _("Present") + ":Int/:100",
        _("Absent") + ":Int/:100",
        _("Leave") + ":Int/:100"
    ]

def get_conditions(filters):
    if not (filters.get("from_date") and filters.get("to_date")):
        frappe.throw(_("Please select From Date and To Date"))

    return filters  # Fix: Return only the dictionary, not a tuple

def add_data(att_map, filters):
    records = []
    
    for date in get_dates(filters["from_date"], filters["to_date"]):
        total_present = get_attendance_count(date, filters)
        total_leave = get_leave_count(date, filters)
        total_absent = get_absent_count(date, filters)
        
        records.append([date, total_present, total_absent, total_leave])
    
    return records

def get_dates(from_date, to_date):
    no_of_days = date_diff(add_days(to_date, 1), from_date)
    return [add_days(from_date, i) for i in range(no_of_days)]

def get_chart_data(data, filters):
    labels = [str(record[0]) for record in data]
    date = [frappe.utils.formatdate(label, "dd-mm-yy") for label in labels]
    datasets = [
        {"name": "Present", "values": [record[1] for record in data]},
        {"name": "Absent", "values": [record[2] for record in data]},
        {"name": "Leave", "values": [record[3] for record in data]},
    ]

    return {
        "data": {"labels": date, "datasets": datasets},
        "type": "line", 
        "colors": ["#ED6396", "#39E4A5", "#29CD42"], 
    }
