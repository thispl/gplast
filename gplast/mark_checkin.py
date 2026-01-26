import json
import requests
import frappe
from frappe.utils import add_days,today
from datetime import datetime

@frappe.whitelist()
def mark_employee_checkin_manual():
    url = "http://115.244.98.52:86/api/v2/WebAPI/GetDeviceLogs"
    api_key = "162618022422" 
    from_date = '2026-01-25'  
    to_date = '2026-01-26'

    params = {
        "APIKey": api_key,
        "FromDate": from_date,
        "ToDate": to_date
    }

    response = requests.get(url, params=params)
    log_entries = response.json()

    for log_entry in log_entries:
        emp_id = log_entry["EmployeeCode"]
        log_date = log_entry["LogDate"]
        device_id = log_entry["SerialNumber"]
        log_type = log_entry['PunchDirection']
        if frappe.db.exists('Employee', {'name': emp_id}):
            if not frappe.db.exists('Employee Checkin', {'employee': emp_id, 'time': log_date}):
                ec = frappe.new_doc('Employee Checkin')
                ec.employee = emp_id
                ec.time = log_date
                ec.device_id = device_id
                ec.log_type = "IN"
                ec.save(ignore_permissions=True)
                print(log_date)
                print(emp_id)
                frappe.db.commit()
        else:
            if not frappe.db.exists('Unregistered Employee Checkin', {'employee_code': emp_id, 'time': log_date}):
                urec = frappe.new_doc('Unregistered Employee Checkin')
                urec.employee_code = emp_id
                urec.time = log_date
                urec.device_id = device_id
                urec.log_type = "IN"
                urec.save(ignore_permissions=True)
                print(emp_id)
                frappe.db.commit()

@frappe.whitelist()
def mark_employee_checkin():
    url = "http://115.244.98.52:86/api/v2/WebAPI/GetDeviceLogs"
    api_key = "162618022422" 
    from_date = add_days(today(),-1)  
    to_date = today()

    params = {
        "APIKey": api_key,
        "FromDate": from_date,
        "ToDate": to_date
    }

    response = requests.get(url, params=params)
    log_entries = response.json()

    for log_entry in log_entries:
        emp_id = log_entry["EmployeeCode"]
        log_date = log_entry["LogDate"]
        device_id = log_entry["SerialNumber"]
        log_type = log_entry['PunchDirection']
        # print(emp_id)
        # print(log_type)
        if frappe.db.exists('Employee', {'name': emp_id}):
            if not frappe.db.exists('Employee Checkin', {'employee': emp_id, 'time': log_date}):
                ec = frappe.new_doc('Employee Checkin')
                ec.employee = emp_id
                ec.time = log_date
                ec.device_id = device_id
                ec.log_type = "IN"
                ec.save(ignore_permissions=True)
                print(emp_id)
                frappe.db.commit()
        else:
            if not frappe.db.exists('Unregistered Employee Checkin', {'employee_code': emp_id, 'time': log_date}):
                urec = frappe.new_doc('Unregistered Employee Checkin')
                urec.employee_code = emp_id
                urec.time = log_date
                urec.device_id = device_id
                urec.log_type = "IN"
                urec.save(ignore_permissions=True)
                print(emp_id)
                frappe.db.commit()

@frappe.whitelist()
def mark_employee_checkin_new():
    url = "http://115.244.98.52:86/api/v2/WebAPI/GetDeviceLogs"
    api_key = "162618022422" 
    from_date = add_days(today(),-1)  
    to_date = today()

    params = {
        "APIKey": api_key,
        "FromDate": from_date,
        "ToDate": to_date
    }

    response = requests.get(url, params=params)
    log_entries = response.json()

    for log_entry in log_entries:
        emp_id = log_entry["EmployeeCode"]
        log_date = log_entry["LogDate"]
        device_id = log_entry["SerialNumber"]
        log_type = log_entry['PunchDirection']
        # print(emp_id)
        # print(log_type)
        if frappe.db.exists('Employee', {'name': emp_id}):
            if not frappe.db.exists('Employee Checkin', {'employee': emp_id, 'time': log_date}):
                ec = frappe.new_doc('Employee Checkin')
                ec.employee = emp_id
                ec.time = log_date
                ec.device_id = device_id
                ec.log_type = "IN"
                ec.save(ignore_permissions=True)
                print(emp_id)
                frappe.db.commit()
        else:
            if not frappe.db.exists('Unregistered Employee Checkin', {'employee_code': emp_id, 'time': log_date}):
                urec = frappe.new_doc('Unregistered Employee Checkin')
                urec.employee_code = emp_id
                urec.time = log_date
                urec.device_id = device_id
                urec.log_type = "IN"
                urec.save(ignore_permissions=True)
                print(emp_id)
                frappe.db.commit()


@frappe.whitelist()
def mark_employee_checkin_fontend_enqueue(from_date, to_date):
    frappe.errprint("Enqueueing mark_employee_checkin_fontend")
    frappe.enqueue(
        "gplast.mark_checkin.mark_employee_checkin_fontend",
        queue="long",
        timeout=36000,
        is_async=True,
        now=False,
        job_name="Mark Checkin",
        from_date=from_date,
        to_date=to_date
    )
    return "ok"

@frappe.whitelist()
def mark_employee_checkin_fontend(from_date, to_date):
    url = "http://115.244.98.52:86/api/v2/WebAPI/GetDeviceLogs"
    api_key = "162618022422" 
    # from_date = add_days(today(),-1)  
    # to_date = today()

    params = {
        "APIKey": api_key,
        "FromDate": from_date,
        "ToDate": to_date
    }

    response = requests.get(url, params=params)
    log_entries = response.json()

    for log_entry in log_entries:
        emp_id = log_entry["EmployeeCode"]
        log_date = log_entry["LogDate"]
        device_id = log_entry["SerialNumber"]
        log_type = log_entry['PunchDirection']
        # print(emp_id)
        # print(log_type)
        if frappe.db.exists('Employee', {'name': emp_id}):
            if not frappe.db.exists('Employee Checkin', {'employee': emp_id, 'time': log_date}):
                ec = frappe.new_doc('Employee Checkin')
                ec.employee = emp_id
                ec.time = log_date
                ec.device_id = device_id
                ec.log_type = "IN"
                ec.save(ignore_permissions=True)
                print(emp_id)
                frappe.db.commit()
        else:
            if not frappe.db.exists('Unregistered Employee Checkin', {'employee_code': emp_id, 'time': log_date}):
                urec = frappe.new_doc('Unregistered Employee Checkin')
                urec.employee_code = emp_id
                urec.time = log_date
                urec.device_id = device_id
                urec.log_type = "IN"
                urec.save(ignore_permissions=True)
                print(emp_id)
                frappe.db.commit()

# def create_employee_checkin():
#     job = frappe.db.exists('Scheduled Job Type', 'mark_employee_checkin')
#     if not job:
#         sjt = frappe.new_doc("Scheduled Job Type")
#         sjt.update({
#             "method": 'gplast.mark_checkin.mark_employee_checkin',
#             "frequency": 'Cron',
#             "cron_format": '*/30 * * * *'
#         })
#         sjt.save(ignore_permissions=True)

def create_employee_checkin_new():
    job = frappe.db.exists('Scheduled Job Type', 'mark_employee_checkin_new')
    if not job:
        sjt = frappe.new_doc("Scheduled Job Type")
        sjt.update({
            "method": 'gplast.mark_checkin.mark_employee_checkin_new',
            "frequency": 'Cron',
            "cron_format": '*/30 * * * *'
        })
        sjt.save(ignore_permissions=True)

@frappe.whitelist()
def mark_unregistered_emp_enqueue(from_date, to_date, employee):
    frappe.enqueue(
        "gplast.mark_checkin.mark_unregistered_emp",
        queue="long",
        timeout=36000,
        is_async=True,
        now=False,
        job_name="Mark Unregistered Checkin",
        from_date=from_date,
        to_date=to_date,
        employee=employee
    )
    return "ok"

@frappe.whitelist()
def mark_unregistered_emp(from_date,to_date,employee):
    checkins = frappe.db.sql(
        """SELECT time, device_id, log_type 
           FROM `tabUnregistered Employee Checkin` 
           WHERE employee_code = %s 
           AND DATE(time) BETWEEN %s AND %s""",
        (employee, from_date, to_date),
        as_dict=True
    )
    count=0
    for c in checkins:
        if frappe.db.exists('Employee', {'name': employee}):
            if not frappe.db.exists("Employee Checkin",{"employee": employee, "time": c.time, "log_type": c.log_type}):
                count+=1
                checkin=frappe.new_doc("Employee Checkin")
                checkin.employee=employee
                checkin.time=c.time
                checkin.log_type=c.log_type
                checkin.device_id=c.device_id
                checkin.insert()
                checkin.save(ignore_permissions=True)
    if count>0:
        return 'ok'
    else:
        return 'no'

@frappe.whitelist()
def mark_unregistered_enqueue(from_date, to_date):
    frappe.enqueue(
        "gplast.mark_checkin.mark_unregistered",
        queue="long",
        timeout=36000,
        is_async=True,
        now=False,
        job_name="Mark Unregistered Checkin",
        from_date=from_date,
        to_date=to_date
    )
    return "ok"

@frappe.whitelist()
def mark_unregistered(from_date,to_date):
    checkins = frappe.db.sql(
        """SELECT time, employee_code, device_id, log_type 
           FROM `tabUnregistered Employee Checkin` 
           WHERE DATE(time) BETWEEN %s AND %s""",
        (from_date, to_date),
        as_dict=True
    )
    count=0
    for c in checkins:
            if frappe.db.exists('Employee', {'name': c.employee_code}):
                if not frappe.db.exists("Employee Checkin",{"employee": c.employee_code, "time": c.time, "log_type": c.log_type}):
                    count+=1
                    checkin=frappe.new_doc("Employee Checkin")
                    checkin.employee=c.employee_code
                    checkin.time=c.time
                    checkin.log_type=c.log_type
                    checkin.device_id=c.device_id
                    checkin.insert()
                    checkin.save(ignore_permissions=True)
    if count>0:
        return 'ok'
    else:
        return 'no'