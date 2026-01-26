# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe import _, msgprint
from urllib.request import ftpwrapper
from frappe.model.document import Document
from frappe.utils import get_first_day, get_last_day, format_datetime,get_url_to_form,today
import frappe
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import calendar
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,datetime,get_first_day,get_last_day,today)
from datetime import datetime
from frappe.utils import formatdate
from gplast.mark_attendance import mark_att_with_employee,mark_wh_emp
import datetime as dt

class AttendancePermission(Document):
    def before_submit(self):
        self.approved_on = frappe.utils.today()
    def validate(self):
        doctype = self.doctype
        old_state = frappe.db.get_value(doctype, self.name, "workflow_state")

        if old_state and old_state != self.workflow_state:
            self.previous_approval_date = today()
        if self.is_new():
            formatted_date = formatdate(self.permission_date, "dd-mm-yyyy")
            if frappe.db.exists("Attendance Permission",{"name":["!=",self.name],"employee":self.employee,"permission_date":self.permission_date,"docstatus":("!=",2)}):
                existing_request=frappe.db.get_value("Attendance Permission",{"name":["!=",self.name],"employee":self.employee,"permission_date":self.permission_date,"docstatus":("!=",2)},['name'])
                if existing_request:
                    msgcontent = """ <b><a href="/app/Form/Attendance Permission/{0}">{0}</a></b>""".format(existing_request)
                    msg = _('Attendance Permission {0} for the employee {1} is already created for the date {2}').format(
                        msgcontent, self.employee, formatted_date
                    )
                    frappe.throw(msg)
            # if frappe.db.exists("Attendance Permission",{"name":["!=",self.name],"employee":self.employee,"permission_date":self.permission_date,"docstatus":("!=",2)}):
            #     frappe.throw("You are already applied Permission for Same day")

            # elif frappe.db.exists("Attendance Permission",{"employee":self.employee,"permission_date":self.permission_date,"docstatus":("!=",2)}):
            #     frappe.throw("You are already applied Permission for Same day")
            current_date=today()
            diff=date_diff(current_date,self.permission_date)
            # if diff>1:
            #     frappe.throw("Permission should be requested within the next day itself. Old dates are not allowed.")
        leave_application = frappe.db.get_all(
            "Leave Application", 
            filters={"employee": self.employee,'docstatus':1,"from_date": ["<=", self.permission_date],"to_date": [">=", self.permission_date]}, 
            fields=["from_date", "to_date"]
        )
        print(leave_application)
        for leave in leave_application:
            print(leave)
            if frappe.db.exists(
                "Attendance Permission", 
                {
                    "employee": self.employee,
                    "permission_date": ["between", [leave["from_date"], leave["to_date"]]]
                }
            ):
                frappe.throw(f"Leave Application exists for {self.permission_date}. So Permission can't apply for the same day.")


    # @frappe.whitelist()
    # def hour_res(self):
    # 	# data = []
        # total = 0
        # month_start = get_first_day(today())
        # month_end = get_last_day(today())
        # permission = frappe.db.get_all('Permission',{'employee':self.employee,"permission_date": ('between',(month_start,month_end))},['*'])    
        # for per in permission:
        # 	total_per_time = frappe.db.get_value('Permission',{'name':per.name},['total_time'])
        # 	data.append(total_per_time)
        # total = sum(map(int, [i for i in data if i.isdigit()]))
        # total_hours = total + self.total_time
        # frappe.errprint(total_hours)
        # if total_hours > int(4):
        # 	frappe.throw(_("Only 4 Hours permissions are allowed for a month"))
    
    # Saturday Restriction Code
    @frappe.whitelist()
    def sat_res(self):
        dates = frappe.db.get_value('permission',{'employee':self.employee,},['permission_date'])
        day = self.permission_date
        date_obj = datetime.strptime(day, '%Y-%m-%d')
        if date_obj.weekday() == 5:
            frappe.throw(_("Permission not allowed in Saturday"))


    def on_cancel(self):
        if frappe.db.exists("Attendance",{"attendance_permission":self.name,'docstatus':['!=',2]}):
            att=frappe.get_doc("Attendance",{"attendance_permission":self.name,'docstatus':['!=',2]})
            frappe.db.set_value("Attendance",att.name,'attendance_permission','')
            frappe.db.set_value("Attendance",att.name,'permission_hour',0)
            if att.in_time and att.out_time and att.shift:
                mark_att_with_employee(self.permission_date,self.permission_date,self.employee)
            else:
                frappe.db.set_value("Attendance",att.name,'status','Absent')
    
    def on_submit(self):
        if self.workflow_state == "Approved":
            att = frappe.db.get_value("Attendance", {"attendance_date": self.permission_date, "employee": self.employee}, ["name"])
            if att:
                att_doc = frappe.get_doc("Attendance", att)
                
                frappe.db.set_value("Attendance", att, "permission_hour", self.permission_hour)
                frappe.db.set_value("Attendance", att, "attendance_permission", self.name)
                if self.permission_hour:
                    if att_doc.in_time and att_doc.out_time:
                        diff = 0
                        # wh = att_doc.total_working_hours
                        wh = att_doc.wh
                        diff = self.permission_hour
                        totwh = float(wh) + float(diff)
                        
                        if totwh >= 8:
                            frappe.db.set_value("Attendance", att, "status", "Present")
                        elif 4 <= totwh < 8:
                            frappe.db.set_value("Attendance", att, "status", "Half Day")
                        else:
                            frappe.db.set_value("Attendance", att, "status", "Absent")

    # def validate(self):
    #     leave_application = frappe.db.get_all(
    #         "Leave Application", 
    #         filters={"employee": self.employee,'docstatus':1}, 
    #         fields=["from_date", "to_date"]
    #     )
        
    #     for leave in leave_application:
    #         if frappe.db.exists(
    #             "Attendance Permission", 
    #             {
    #                 "employee": self.employee,
    #                 "permission_date": ["between", [leave["from_date"], leave["to_date"]]]
    #             }
    #         ):
    #             frappe.throw(f"Leave Application exists for {self.permission_date}. So Permission can't apply for the same day.")

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



