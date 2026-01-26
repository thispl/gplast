# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr, add_days, date_diff,format_datetime,format_time
from datetime import date, timedelta, datetime, time
class AttendanceSummary(Document):
	pass




@frappe.whitelist()
def get_data_system(emp, from_date, to_date):
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	dates = [add_days(from_date, i) for i in range(no_of_days)]
	emp_details = frappe.db.get_value('Employee', emp, ['employee_name', 'department'])
	data = """<table class='table table-bordered=1'>"""
	data += f"""<tr>
			<td style='border: 1px solid black;background-color:#FFA500'><b><center>ID</b></center></b></td>
			<td style='border: 1px solid black;background-color:#FFA500;' colspan=3><b><center>{emp}</b></center></b></td>
			<td style='border: 1px solid black;background-color:#FFA500;'><b><center>Name</b></center></b></td>
			<td style='border: 1px solid black;background-color:#FFA500;' colspan=3><b><center>{emp_details[0]}</b></center></b></td>
			<td style='border: 1px solid black;background-color:#FFA500;'><b><center>Dept</b></center></b></td>
			<td style='border: 1px solid black;background-color:#FFA500;' colspan=3><b><center>{emp_details[1]}</b></center></b></td>
		</tr>"""
	data += """<tr><td style='border: 1px solid black;' colspan=12><b><center>Attendance</b></center></td><tr>"""
	data += """<tr><td style='border: 1px solid black;background-color:#FFA500'><b><center>Date</b></center></b></td>
		<td style='border: 1px solid black;background-color:#FFA500;'><b><center>Day</b></center></b></td>
		<td style='border: 1px solid black;background-color:#FFA500;'><b><center>Working</b></center></b></td>
		<td style='border: 1px solid black;background-color:#FFA500;'><b><center>In Time</b></center></b></td>
		<td style='border: 1px solid black;background-color:#FFA500;'><b><center>Out Time</b></center></b></td>
		<td style='border: 1px solid black;background-color:#FFA500;'><b><center>Shift</b></center></b></td>
		<td style='border: 1px solid black;background-color:#FFA500;'><b><center>Status</b></center></b></td>
		<td style='border: 1px solid black;background-color:#FFA500;'><b><center>Working Hours</b></center></b></td>
		<td style='border: 1px solid black;background-color:#FFA500;'><b><center>OT Hours</b></center></b></td>
		<td style='border: 1px solid black;background-color:#FFA500;'><b><center>Late Entry Time</b></center></b></td>
		<td style='border: 1px solid black;background-color:#FFA500;'><b><center>Early Exit Time</b></center></b></td>
	</tr>"""
	for date in dates:
		dt = datetime.strptime(date, '%Y-%m-%d')
		d = dt.strftime('%d-%b')
		day = datetime.date(dt).strftime('%a')
		if frappe.db.exists('Attendance', {'employee': emp, "attendance_date": date, 'docstatus': ('!=', '2')}):
			att = frappe.get_doc("Attendance",{'attendance_date':date,'employee':emp,'docstatus':('!=','2')})
			
			in_time = att.in_time 
			out_time = att.out_time 
			shift = att.shift 
			status = att.status
			leave_type= att.leave_type
			leave_type = att.leave_type
			twh=round(att.total_working_hours,2) 
			late = att.late_entry_time
			early = att.early_exit_time
			if att.leave_type :
				leave = frappe.db.get_value('Leave Type',{'name':att.leave_type},['short_code'])
			else:
				leave = "LWP"
			overtime_hours = att.overtime_hours 
			overtime_hours = round(att.overtime_hours,2)
			holiday = check_holiday(date ,emp)
			if holiday[0]:
				if in_time or out_time:
					data += f"""<tr>
						<td style='border: 1px solid black;'><center>{d}</center></td>
						<td style='border: 1px solid black;'><center>{day}</center></td>
						<td style='border: 1px solid black;'><center>{'W'}</center></td>
						<td style='border: 1px solid black;'><center>{format_datetime(in_time) or ''}</center></td>
						<td style='border: 1px solid black;'><center>{format_datetime(out_time) or ''}</center></td>
						<td style='border: 1px solid black;'><center>{shift or ''}</center></td>
						<td style='border: 1px solid black;color:#ECE418'><center>{status}</center></td>
						<td style='border: 1px solid black;'><center>{twh or ''}</center></td>
						<td style='border: 1px solid black;'><center>{overtime_hours or''}</center></td>
						<td style='border: 1px solid black;'><center>{format_time(late) or ''}</center></td>
						<td style='border: 1px solid black;'><center>{format_time(early) or ''}</center></td>
					</tr>"""
				else:
					data += f"""<tr>
						<td style='border: 1px solid black;'><center>{d}</center></td>
						<td style='border: 1px solid black;'><center>{day}</center></td>
						<td style='border: 1px solid black;'><center>{holiday}</center></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;color:#BD2A0F'><center>{holiday[1]}</center></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;'></td>
					</tr>"""
			else:
				if status == "On Leave":
					data += f"""<tr>
						<td style='border: 1px solid black;'><center>{d}</center></td>
						<td style='border: 1px solid black;'><center>{day}</center></td>
						<td style='border: 1px solid black;'><center>L</center></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;color:#b9597f'><center>{leave}</center></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;'></td>
					</tr>"""
				elif status == "Half Day" and att.leave_application:
					ltype=frappe.db.get_value("Leave Type",{"name":att.leave_type},['is_lwp'])
					if ltype==1:
						data += f"""<tr>
							<td style='border: 1px solid black;'><center>{d}</center></td>
							<td style='border: 1px solid black;'><center>{day}</center></td>
							<td style='border: 1px solid black;'><center>{'W'}</center></td>
							<td style='border: 1px solid black;'><center>{format_datetime(in_time) or ''}</center></td>
							<td style='border: 1px solid black;'><center>{format_datetime(out_time) or ''}</center></td>
							<td style='border: 1px solid black;'><center>{shift or ''}</center></td>
							<td style='border: 1px solid black;color:#d57b64'><center>HD/{leave}</center></td>
							<td style='border: 1px solid black;'><center>{twh or ''}</center></td>
							<td style='border: 1px solid black;'><center>{overtime_hours or ''}</center></td>
							<td style='border: 1px solid black;'><center>{format_time(late) or ''}</center></td>
							<td style='border: 1px solid black;'><center>{format_time(early) or ''}</center></td>
						</tr>"""
					else:
						if twh>=4:
							data += f"""<tr>
								<td style='border: 1px solid black;'><center>{d}</center></td>
								<td style='border: 1px solid black;'><center>{day}</center></td>
								<td style='border: 1px solid black;'><center>{'W'}</center></td>
								<td style='border: 1px solid black;'><center>{format_datetime(in_time) or ''}</center></td>
								<td style='border: 1px solid black;'><center>{format_datetime(out_time) or ''}</center></td>
								<td style='border: 1px solid black;'><center>{shift or ''}</center></td>
								<td style='border: 1px solid black;color:#d57b64'><center>Present/{leave}</center></td>
								<td style='border: 1px solid black;'><center>{twh or ''}</center></td>
								<td style='border: 1px solid black;'><center>{overtime_hours or ''}</center></td>
								<td style='border: 1px solid black;'><center>{format_time(late) or ''}</center></td>
								<td style='border: 1px solid black;'><center>{format_time(early) or ''}</center></td>
							</tr>"""
						else:
							data += f"""<tr>
									<td style='border: 1px solid black;'><center>{d}</center></td>
									<td style='border: 1px solid black;'><center>{day}</center></td>
									<td style='border: 1px solid black;'><center>{'W'}</center></td>
									<td style='border: 1px solid black;'><center>{format_datetime(in_time) or ''}</center></td>
									<td style='border: 1px solid black;'><center>{format_datetime(out_time) or ''}</center></td>
									<td style='border: 1px solid black;'><center>{shift or ''}</center></td>
									<td style='border: 1px solid black;color:#d57b64'><center>HD/{leave}</center></td>
									<td style='border: 1px solid black;'><center>{twh or ''}</center></td>
									<td style='border: 1px solid black;'><center>{overtime_hours or ''}</center></td>
									<td style='border: 1px solid black;'><center>{format_time(late) or ''}</center></td>
									<td style='border: 1px solid black;'><center>{format_time(early) or ''}</center></td>
								</tr>"""
				elif status == "Present" and att.on_duty_application:
					data += f"""<tr>
						<td style='border: 1px solid black;'><center>{d}</center></td>
						<td style='border: 1px solid black;'><center>{day}</center></td>
						<td style='border: 1px solid black;'><center>{'W'}</center></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;color:#82EB31'><center>On Duty</center></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;'></td>
						<td style='border: 1px solid black;'></td>
					</tr>"""
					# % (d, day, "W" , '', '', '',"On Duty", '',' ',' ','')
				elif status == "Half Day" and att.on_duty_application:
					data += f"""<tr>
						<td style='border: 1px solid black;'><center>{d}</center></td>
						<td style='border: 1px solid black;'><center>{day}</center></td>
						<td style='border: 1px solid black;'><center>{'W'}</center></td>
						<td style='border: 1px solid black;'><center>{format_datetime(in_time) or ''}</center></td>
						<td style='border: 1px solid black;'><center>{format_datetime(out_time) or ''}</center></td>
						<td style='border: 1px solid black;'><center>{shift or ''}</center></td>
						<td style='border: 1px solid black;color:#d57b64'><center>HD/On Duty</center></td>
						<td style='border: 1px solid black;'><center>{twh or ''}</center></td>
						<td style='border: 1px solid black;'><center>{overtime_hours or ''}</center></td>
						<td style='border: 1px solid black;'><center>{format_time(late) or ''}</center></td>
						<td style='border: 1px solid black;'><center>{format_time(early) or ''}</center></td>
					</tr>"""
				else:
					if att.attendance_permission :
						data += f"""<tr>
							<td style='border: 1px solid black;'><center>{d}</center></td>
							<td style='border: 1px solid black;'><center>{day}</center></td>
							<td style='border: 1px solid black;'><center>{'W'}</center></td>
							<td style='border: 1px solid black;'><center>{format_datetime(in_time) or ''}</center></td>
							<td style='border: 1px solid black;'><center>{format_datetime(out_time) or ''}</center></td>
							<td style='border: 1px solid black;'><center>{shift or ''}</center></td>
							<td style='border: 1px solid black;color:#9FF60E'><center>{status}/PR</center></td>
							<td style='border: 1px solid black;'><center>{twh or ''}</center></td>
							<td style='border: 1px solid black;'><center>{overtime_hours or ''}</center></td>
							<td style='border: 1px solid black;'><center>{format_time(late) or ''}</center></td>
							<td style='border: 1px solid black;'><center>{format_time(early) or ''}</center></td>
					</tr>"""
					else:
						if status == "Absent":
							data += f"""<tr>
								<td style='border: 1px solid black;'><center>{d}</center></td>
								<td style='border: 1px solid black;'><center>{day}</center></td>
								<td style='border: 1px solid black;'><center>{'W'}</center></td>
								<td style='border: 1px solid black;'><center>{format_datetime(in_time) or ''}</center></td>
								<td style='border: 1px solid black;'><center>{format_datetime(out_time) or ''}</center></td>
								<td style='border: 1px solid black;'><center>{shift or ''}</center></td>
								<td style='border: 1px solid black;color:#FF0000'><center>{status}</center></td>
								<td style='border: 1px solid black;'><center>{twh or ''}</center></td>
								<td style='border: 1px solid black;'><center>{overtime_hours or ''}</center></td>
								<td style='border: 1px solid black;'><center>{format_time(late) or ''}</center></td>
								<td style='border: 1px solid black;'><center>{format_time(early) or ''}</center></td>
							</tr>"""
						else:
							data += f"""<tr>
								<td style='border: 1px solid black;'><center>{d}</center></td>
								<td style='border: 1px solid black;'><center>{day}</center></td>
								<td style='border: 1px solid black;'><center>{'W'}</center></td>
								<td style='border: 1px solid black;'><center>{format_datetime(in_time) or ''}</center></td>
								<td style='border: 1px solid black;'><center>{format_datetime(out_time) or ''}</center></td>
								<td style='border: 1px solid black;'><center>{shift or ''}</center></td>
								<td style='border: 1px solid black;color:#6b8855'><center>{status}</center></td>
								<td style='border: 1px solid black;'><center>{twh or ''}</center></td>
								<td style='border: 1px solid black;'><center>{overtime_hours or ''}</center></td>
								<td style='border: 1px solid black;'><center>{format_time(late) or ''}</center></td>
								<td style='border: 1px solid black;'><center>{format_time(early) or ''}</center></td>
							</tr>"""
		else:
			holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
			holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off, `tabHoliday`.description from `tabHoliday List` 
			left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
			doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
			status = ''
			desc = ''
			if holiday :
				if doj <= holiday[0].holiday_date:
					if holiday[0].weekly_off == 1:
						status = "WO"
						desc = "Weekly Off"
					else:
						status = "NH"
						desc = holiday[0].description
				else:
					status = 'NJ'
					desc = "Not Joined"
			if holiday:
				data += f"""<tr>
					<td style='border: 1px solid black;'><center>{d}</center></td>
					<td style='border: 1px solid black;'><center>{day}</center></td>
					<td style='border: 1px solid black;'><center>{status}</center></td>
					<td style = 'border: 1px solid black;'></td>
					<td style = 'border: 1px solid black;'></td>
					<td style = 'border: 1px solid black;'></td>
					<td style = 'border: 1px solid black;color:#DB2CE3'><center>{desc}</center></td>
					<td style = 'border: 1px solid black;'></td>
					<td style = 'border: 1px solid black;'></td>
					<td style='border: 1px solid black;'></td>
					<td style='border: 1px solid black;'></td>
				</tr>"""
			else:
				data += f"""<tr>
				<td style = 'border: 1px solid black;'><center>{d}</center></td>
				<td style = 'border: 1px solid black;'><center>{day}</center></td>
				<td style = 'border: 1px solid black;'>{status}</td>
				<td style = 'border: 1px solid black;'></td>
				<td style = 'border: 1px solid black;'></td>
				<td style = 'border: 1px solid black;'></td>
				<td style = 'border: 1px solid black;'color:#DB2CE3'><center>{desc}</center></td>
				<td style = 'border: 1px solid black;'></td>
				<td style = 'border: 1px solid black;'></td>
				<td style='border: 1px solid black;'></td>
				<td style='border: 1px solid black;'></td>
				</tr>"""
				
	data += """</table>"""
	return data

def check_holiday(date,emp):
	holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off, `tabHoliday`.description from `tabHoliday List` 
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
	status = ''
	desc = ''
	if holiday :
		if doj <= holiday[0].holiday_date:
			if holiday[0].weekly_off == 1:
				status = "WO"
				desc = "Weekly Off"
			else:
				status = "NH"
				desc = holiday[0].description
		else:
			status = 'NJ'
			desc = "Not Joined"
	return status, desc
		

from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days,date_diff
@frappe.whitelist()
def get_from_to_dates(month,year):
	if month == 'January':
		month1 = "01"
	if month == 'February':
		month1 = "02"
	if month == 'March':
		month1 = "03"
	if month == 'April':
		month1 = "04"
	if month == 'May':
		month1 = "05"
	if month == 'June':
		month1 = "06"
	if month == 'July':
		month1 = "07"
	if month == 'August':
		month1 = "08"
	if month == 'September':
		month1 = "09"
	if month == 'October':
		month1 = "10"
	if month == 'November':
		month1 = "11"
	if month == 'December':
		month1 = "12"
	formatted_start_date = year + '-' + month1 + '-01'
	formatted_end_date = get_last_day(formatted_start_date)
	return formatted_start_date,formatted_end_date
