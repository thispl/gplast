from . import __version__ as app_version

app_name = "gplast"
app_title = "GPLAST"
app_publisher = "Teampro"
app_description = "development"
app_email = "erp.teamproit.com"
app_license = "1234"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/gplast/css/gplast.css"
# app_include_js = "/assets/gplast/js/gplast.js"

# include js, css files in header of web template
# web_include_css = "/assets/gplast/css/gplast.css"
# web_include_js = "/assets/gplast/js/gplast.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "gplast/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
	"methods": [
		"gplast.gplast.doctype.salary_print.get_attendance",
		"gplast.gplast.doctype.salary_print.get_total_leaves_allocated",
		"gplast.gplast.doctype.salary_print.get_approved_leave_days",
		"gplast.gplast.doctype.salary_print.get_balance_leaves",
		"gplast.gplast.doctype.salary_print.get_approved_leave_days_except_current_month",
		"gplast.gplast.doctype.salary_print.get_weekly_off_count_shift",
		"gplast.gplast.doctype.salary_print.get_ww_shift_days_excluding_start_end_months",
		"gplast.gplast.doctype.salary_print.get_ww_shift_count_for_month",
		"gplast.gplast.doctype.salary_print.get_balance_weekoff",
        # "gplast.gplast.doctype.salary_print.get_weekly_off_count_for_this_nh",
        # "gplast.gplast.doctype.salary_print.get_weekly_off_count_for_this_fh",
        "gplast.gplast.doctype.salary_print.get_weekly_count_for_this_nh_fh",
        # "gplast.gplast.doctype.salary_print.get_weekly_off_count_for_other_nh",
        # "gplast.gplast.doctype.salary_print.get_weekly_off_count_for_other_fh",
        "gplast.gplast.doctype.salary_print.get_weekly_count_for_other_nh_fh",
        # "gplast.gplast.doctype.salary_print.get_weekly_off_count_nh",
        # "gplast.gplast.doctype.salary_print.get_weekly_off_count_fh",
        "gplast.gplast.doctype.salary_print.get_weekly_count_nh_fh",
        "gplast.gplast.doctype.salary_print.get_balance_nh_fh",
        "gplast.gplast.doctype.salary_print.inr_format",
        "gplast.gplast.doctype.salary_print.get_worked_days",
        "gplast.gplast.doctype.salary_print.get_interview_date",
        

	]
}


# Installation
# ------------

# before_install = "gplast.install.before_install"
# after_install = "gplast.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "gplast.uninstall.before_uninstall"
# after_uninstall = "gplast.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "gplast.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Shift Request": "gplast.overrides.CustomShiftRequest",
    "Salary Slip":"gplast.overrides.CustomSalarySlip",
    "Leave Application":"gplast.overrides.CustomLeaveApplication"
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"Job Offer": {
# 		"on_submit": "gplast.custom.sending_mail",
# 		# "on_cancel": "method",
# 		# "on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
    
    "cron": {
        "0 10 21-31 4,10 *": [
            "gplast.custom.send_esi_increment_mail"
        ],
        # "30 12 15-31 4,12 *": [
        #     "gplast.custom.send_esi_mail"
        # ],
		"0 */2 * * *"  : [
			"gplast.mark_checkin.mark_employee_checkin"
		],
        "0 */2 * * *"  : [
			"gplast.mark_attendance.mark_att"
		],
        "0 8 * * *" : [
			"gplast.custom.mail_training_result"
		],
        "0 0 1 1 *" : [
			"gplast.custom.el_leave_allocation"
		],
        "0 0 * * *" : [
			"glast.custom.cl_leave_allocation"
		],
        "59 23 28-31 * *": [
            "gplast.custom.create_additional_salary_for_attendance_permission"
        ]
        # "0 18 * * *" : [
        #     "gplast.custom.employee_attendance_status"
		# ],
  
        
	}
#	"all": [
#		"gplast.tasks.all"
#	],
#	"daily": [
#		"gplast.tasks.daily"
#	],
#	"hourly": [
#		"gplast.tasks.hourly"
#	],
#	"weekly": [
#		"gplast.tasks.weekly"
#	],
#	"monthly": [
#		"gplast.tasks.monthly"
#	],
}

# Testing
# -------

# before_tests = "gplast.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "gplast.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "gplast.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["gplast.utils.before_request"]
# after_request = ["gplast.utils.after_request"]

# Job Events
# ----------
# before_job = ["gplast.utils.before_job"]
# after_job = ["gplast.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"gplast.auth.validate"
# ]
doc_events = {
	'Loan':{
		'on_submit':'gplast.custom.create_additional_salary'
	},
	'Attendance Permission':{
		'validate':'gplast.custom.set_permission_times',
        "on_update": ["gplast.custom.store_workflow_stage_time",
                         ],
	},
	"Employee":{
		# "validate": "gplast.custom.inactive_employee",
        "before_save":[ "gplast.custom.autoname","gplast.custom.set_esi_end_date"],
        "validate":["gplast.custom.update_total_experience"]
        # "before_insert":"gplast.custom.autoname"
	},
    "Designation":{
        "before_save": "gplast.custom.generate_designation_code"
	},
	# "Training Result": {
	# 	"on_submit": "gplast.custom.update_submitted_date"
	# },
    "Leave Application":{
        "after_insert": ["gplast.custom.check_eligibility_for_privilege_leave",
                         "gplast.custom.validate_leave",
                         ],
        # "before_submit": "gplast.custom.approved_on_set_value",
        "validate": ["gplast.custom.restriction_for_cl_leave_in_notice_period",
                     "gplast.custom.update_previous_approval_date_on_validation",
                     "gplast.custom.create_new_lop",
                     ],
        "on_update":["gplast.custom.leave_application_rejection_remark",
                     "gplast.custom.store_workflow_stage_time",
                     ]
        # "onload": "gplast.custom.employee_restriction_relieving_date"
        # "on_submit":"gplast.custom.create_new_lop"
	},
    "Salary Slip":{
        "after_insert":"gplast.custom.salary_slip_alert_notify_for_hod",

	},
    "Designation Approval": {
		"on_submit": "gplast.custom.new_designation"
	},
    "Manpower Request": {
        "on_update":"gplast.custom.mpr_rejection_remark" ,
		"on_submit": ["gplast.custom.manpower_request_approved_date"],
        "validate":"gplast.custom.validate_vacancy"
	},
    "Compensatory Leave Request": {
        "after_insert":"gplast.custom.validate_comp_off",
		"validate": ["gplast.custom.restriction_for_comp_off",
                "gplast.custom.get_total_working_hours",
                "gplast.custom.update_previous_approval_date_on_validation"
                ],
        "on_update":"gplast.custom.compensatory_leave_request_rejection_remark"
	},
    # "Expense Claim": {
        # "after_insert":"gplast.custom.update_previous_workflow_state_on_creation",
		# "validate": "gplast.custom.update_previous_workflow_state_on_validation"
	# },
    # "Shift Request": {
	# 	"validate": "gplast.custom.validate_shift_request"
	# },
	# "Attendance": {
	# 	"validate": ["gplast.custom.create_attendance_permission", "gplast.custom.create_attendance_permission_for_early_exit"],
    #     "on_update": ["gplast.custom.create_attendance_permission", "gplast.custom.create_attendance_permission_for_early_exit"]
	# },
    "Shift Assignment": {
        "on_cancel": "gplast.custom.remove_shift_assignment"
	},
    
    "Job Requisition":{
		"before_save":["gplast.custom.designation_check","gplast.custom.status_update"],
        "on_update":["gplast.custom.jr_rejection_remark",]
	},
    "Interview Feedback":{
        "validate":['gplast.custom.validate_the_interview_feedback_document'],
        
	},
    "On Duty Application":{
		"on_update":["gplast.custom.on_duty_application_rejection_remark",
                        "gplast.custom.store_workflow_stage_time",]
	},
    
    "Miss Punch Application":{
        
        "on_update":["gplast.custom.miss_punch_application_rejection_remark" ,
                    "gplast.custom.store_workflow_stage_time",]
		
	},
    # "Compensatory Leave Request":{
    #      "on_update":"gplast.custom.compensatory_leave_request_rejection_remark"
    #     },
    
    "Over Time":{
        "on_update":"gplast.custom.over_time_rejection_remark"
        },
    
    "Shift Request":{
        "on_update":["gplast.custom.shift_request_rejection_remark"],
        "validate":["gplast.custom.shift_overlap_update"]
        },
    "Resignation Form":{
        "on_update":"gplast.custom.resignation_form_rejection_remark"
        },
    
    "Expense Claim":{
        "on_update":"gplast.custom.expense_claim_rejection_remark"
        },
    "Job Offer": {
		"on_submit": "gplast.custom.sending_mail",
	},
    
    'Scheduled Job Log':{
        "on_update":"gplast.custom.schedule_log_fail" 
    },

    
    
}