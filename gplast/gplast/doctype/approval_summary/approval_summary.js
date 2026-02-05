// Copyright (c) 2026, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Approval Summary', {
	refresh: function(frm) {
			frm.disable_save()
			frm.get_field('la_approval').grid.cannot_add_rows = true;
			frm.get_field('od_approval').grid.cannot_add_rows = true;
			frm.get_field('mp_approval').grid.cannot_add_rows = true;
			frm.get_field('pr_approval').grid.cannot_add_rows = true;
			frm.get_field('ot_approval').grid.cannot_add_rows = true;
			// LA Table-FM
			if (frappe.user.has_role(['Level Approver 1'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Leave Application",
						"filters": [
							['workflow_state', '=', 'Pending for Manager'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Leave Application",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('la_approval', {
										'leave_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'request_date': r.message.request_date,
										'department': r.message.department,
										'leave_type': r.message.leave_type,
										// 'leave_balance': r.message.leave_balance,
										'from_date': r.message.from_date,
										'half_day': r.message.half_day,
										'half_day_date': r.message.half_day_date,
										'total_leave_days': r.message.total_leave_days,
										'session': r.message.session,
										'to_date': r.message.to_date,
										'leave_approver': r.message.leave_approver,
										// 'leave_approver_name': r.message.leave_approver_name,
										// 'posting_date': r.message.posting_date,
										'leave_approver_2':r.message.leave_approver_2,
										'leave_approver_3':r.message.leave_approver_3,
										'leave_approver_4':r.message.leave_approver_4,
									})
									frm.refresh_field('la_approval')
								}
							})

						})
					}
				})
			}
			// LA Table-SM
			if (frappe.user.has_role(['Level Approver 2'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Leave Application",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 1'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Leave Application",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('la_approval', {
										'leave_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'request_date': r.message.request_date,
										'department': r.message.department,
										'leave_type': r.message.leave_type,
										'leave_balance': r.message.leave_balance,
										'from_date': r.message.from_date,
										'half_day': r.message.half_day,
										'half_day_date': r.message.half_day_date,
										'total_leave_days': r.message.total_leave_days,
										'session': r.message.session,
										'description': r.message.to_time,
										'leave_approver': r.message.leave_approver,
										'leave_approver_name': r.message.leave_approver_name,
										'posting_date': r.message.posting_date,
										'approver_name':r.message.custom_second_manager_name
									})
									frm.refresh_field('la_approval')
								}
							})

						})
					}
				})
			}
			// LA Table- Pending for Manager 2
			if (frappe.user.has_role(['Level Approver 3'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Leave Application",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 2'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Leave Application",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('la_approval', {
										'leave_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'request_date': r.message.request_date,
										'department': r.message.department,
										'leave_type': r.message.leave_type,
										'leave_balance': r.message.leave_balance,
										'from_date': r.message.from_date,
										'half_day': r.message.half_day,
										'half_day_date': r.message.half_day_date,
										'total_leave_days': r.message.total_leave_days,
										'session': r.message.session,
										'description': r.message.to_time,
										'leave_approver': r.message.leave_approver,
										'leave_approver_name': r.message.leave_approver_name,
										'posting_date': r.message.posting_date
									})
									frm.refresh_field('la_approval')
								}
							})

						})
					}
				})
			}

			// LA Table- Pending for Manager 3
			if (frappe.user.has_role(['Level Approver 4'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Leave Application",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 3'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Leave Application",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('la_approval', {
										'leave_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'request_date': r.message.request_date,
										'department': r.message.department,
										'leave_type': r.message.leave_type,
										'leave_balance': r.message.leave_balance,
										'from_date': r.message.from_date,
										'half_day': r.message.half_day,
										'half_day_date': r.message.half_day_date,
										'total_leave_days': r.message.total_leave_days,
										'session': r.message.session,
										'description': r.message.to_time,
										'leave_approver': r.message.leave_approver,
										'leave_approver_name': r.message.leave_approver_name,
										'posting_date': r.message.posting_date
									})
									frm.refresh_field('la_approval')
								}
							})

						})
					}
				})
			}


			// LA Approval
			frm.fields_dict["la_approval"].grid.add_custom_button(__('Reject'),
				function () {
					$.each(frm.doc.la_approval, function (i, d) {
						if (d.__checked == 1) {
							frm.call('submit_leave_doc', {
								doctype: "Leave Application",
								name: d.leave_application,
								workflow_state: 'Rejected'
							}).then(r => {
								frm.get_field("la_approval").grid.grid_rows[d.idx - 1].remove();
							})
						}
						frm.refresh_field('la_approval')
					})
				}).addClass('btn-danger')

			frm.fields_dict["la_approval"].grid.add_custom_button(__('Approve'),
				function () {
					$.each(frm.doc.la_approval, function (i, d) {
						if (d.__checked == 1) {
							if (d.workflow_state == 'Pending for Manager') {
								frm.call('submit_leave_doc', {
								doctype: "Leave Application",
								name: d.leave_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Leave Application {0} moved to <b>{1}</b>",
									[d.leave_application, next_state]
								));

								frm.get_field("la_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('la_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 1') {
								frm.call('submit_leave_doc', {
								doctype: "Leave Application",
								name: d.leave_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Leave Application {0} moved to <b>{1}</b>",
									[d.leave_application, next_state]
								));

								frm.get_field("la_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('la_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 2') {
								frm.call('submit_leave_doc', {
								doctype: "Leave Application",
								name: d.leave_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Leave Application {0} moved to <b>{1}</b>",
									[d.leave_application, next_state]
								));

								frm.get_field("la_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('la_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 3') {
								frm.call('submit_leave_doc', {
								doctype: "Leave Application",
								name: d.leave_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Leave Application {0} moved to <b>{1}</b>",
									[d.leave_application, next_state]
								));

								frm.get_field("la_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('la_approval');
							});
							}							
						}
					})
				}).addClass('btn-primary').css({ "margin-left": "10px", "margin-right": "10px" })


				//----------OD-----------

			if (frappe.user.has_role(['Level Approver 1'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "On Duty Application",
						"filters": [
							['workflow_state', '=', 'Pending for Manager'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "On Duty Application",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('od_approval', {
										'od_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'od_hours': r.message.od_hours,
										'from_date': r.message.from_date,
										'from_time': r.message.from_time,
										'to_time': r.message.to_time,
										'total_number_of_days': r.message.total_number_of_days,
										'session': r.message.session,
										'to_date': r.message.to_date,
										'leave_approver_1': r.message.leave_approver_1,
										'leave_approver_2':r.message.leave_approver_2,
										'leave_approver_3':r.message.leave_approver_3,
										'leave_approver_4':r.message.leave_approver_4,
									})
									frm.refresh_field('od_approval')
								}
							})

						})
					}
				})
			}
			// LA Table-SM
			if (frappe.user.has_role(['Level Approver 2'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "On Duty Application",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 1'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "On Duty Application",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('od_approval', {
										'od_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'od_hours': r.message.od_hours,
										'from_date': r.message.from_date,
										'from_time': r.message.from_time,
										'to_time': r.message.to_time,
										'total_number_of_days': r.message.total_number_of_days,
										'session': r.message.session,
										'to_date': r.message.to_date,
										'leave_approver_1': r.message.leave_approver_1,
										'leave_approver_2':r.message.leave_approver_2,
										'leave_approver_3':r.message.leave_approver_3,
										'leave_approver_4':r.message.leave_approver_4,
									})
									frm.refresh_field('od_approval')
								}
							})

						})
					}
				})
			}
			// LA Table- Pending for Manager 2
			if (frappe.user.has_role(['Level Approver 3'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "On Duty Application",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 2'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "On Duty Application",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('od_approval', {
										'od_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'od_hours': r.message.od_hours,
										'from_date': r.message.from_date,
										'from_time': r.message.from_time,
										'to_time': r.message.to_time,
										'total_number_of_days': r.message.total_number_of_days,
										'session': r.message.session,
										'to_date': r.message.to_date,
										'leave_approver_1': r.message.leave_approver_1,
										'leave_approver_2':r.message.leave_approver_2,
										'leave_approver_3':r.message.leave_approver_3,
										'leave_approver_4':r.message.leave_approver_4,
									})
									frm.refresh_field('od_approval')
								}
							})

						})
					}
				})
			}

			// LA Table- Pending for Manager 3
			if (frappe.user.has_role(['Level Approver 4'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "On Duty Application",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 3'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "On Duty Application",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('od_approval', {
										'od_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'od_hours': r.message.od_hours,
										'from_date': r.message.from_date,
										'from_time': r.message.from_time,
										'to_time': r.message.to_time,
										'total_number_of_days': r.message.total_number_of_days,
										'session': r.message.session,
										'to_date': r.message.to_date,
										'leave_approver_1': r.message.leave_approver_1,
										'leave_approver_2':r.message.leave_approver_2,
										'leave_approver_3':r.message.leave_approver_3,
										'leave_approver_4':r.message.leave_approver_4,
									})
									frm.refresh_field('od_approval')
								}
							})

						})
					}
				})
			}

			// LA Approval
			frm.fields_dict["od_approval"].grid.add_custom_button(__('Reject'),
				function () {
					$.each(frm.doc.od_approval, function (i, d) {
						if (d.__checked == 1) {
							frm.call('submit_od', {
								doctype: "On Duty Application",
								name: d.od_application,
								workflow_state: 'Rejected'
							}).then(r => {
								frm.get_field("od_approval").grid.grid_rows[d.idx - 1].remove();
							})
						}
						frm.refresh_field('od_approval')
					})
				}).addClass('btn-danger')

			frm.fields_dict["od_approval"].grid.add_custom_button(__('Approve'),
				function () {
					$.each(frm.doc.od_approval, function (i, d) {
						if (d.__checked == 1) {
							if (d.workflow_state == 'Pending for Manager') {
								frm.call('submit_od', {
								doctype: "On Duty Application",
								name: d.od_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The On Duty Application {0} moved to <b>{1}</b>",
									[d.od_application, next_state]
								));

								frm.get_field("od_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('od_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 1') {
								frm.call('submit_od', {
								doctype: "On Duty Application",
								name: d.od_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The On Duty Application {0} moved to <b>{1}</b>",
									[d.od_application, next_state]
								));

								frm.get_field("od_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('od_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 2') {
								frm.call('submit_od', {
								doctype: "On Duty Application",
								name: d.od_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The On Duty Application {0} moved to <b>{1}</b>",
									[d.od_application, next_state]
								));

								frm.get_field("od_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('od_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 3') {			
								frm.call('submit_od', {
								doctype: "On Duty Application",
								name: d.od_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The On Duty Application {0} moved to <b>{1}</b>",
									[d.od_application, next_state]
								));

								frm.get_field("od_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('od_approval');
							});
							}
							
						}
					})
				}).addClass('btn-primary').css({ "margin-left": "10px", "margin-right": "10px" })


			//---------- Miss Punch-----------

			if (frappe.user.has_role(['Level Approver 1'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Miss Punch Application",
						"filters": [
							['workflow_state', '=', 'Pending for Manager'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Miss Punch Application",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('mp_approval', {
										'mp_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'attendance_date': r.message.attendance_date,
										'in_time': r.message.in_time,
										'out_time': r.message.out_time,
										'leave_approver_1': r.message.level_approver_1,
										'leave_approver_2':r.message.level_approver_2,
										'leave_approver_3':r.message.level_approver_3,
										'leave_approver_4':r.message.level_approver_4,
									})
									frm.refresh_field('mp_approval')
								}
							})

						})
					}
				})
			}
			// LA Table-SM
			if (frappe.user.has_role(['Level Approver 2'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Miss Punch Application",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 1'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Miss Punch Application",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('mp_approval', {
										'mp_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'attendance_date': r.message.attendance_date,
										'in_time': r.message.in_time,
										'out_time': r.message.out_time,
										'leave_approver_1': r.message.level_approver_1,
										'leave_approver_2':r.message.level_approver_2,
										'leave_approver_3':r.message.level_approver_3,
										'leave_approver_4':r.message.level_approver_4,
									})
									frm.refresh_field('mp_approval')
								}
							})

						})
					}
				})
			}
			// LA Table- Pending for Manager 2
			if (frappe.user.has_role(['Level Approver 3'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Miss Punch Application",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 2'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Miss Punch Application",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('mp_approval', {
										'mp_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'attendance_date': r.message.attendance_date,
										'in_time': r.message.in_time,
										'out_time': r.message.out_time,
										'leave_approver_1': r.message.level_approver_1,
										'leave_approver_2':r.message.level_approver_2,
										'leave_approver_3':r.message.level_approver_3,
										'leave_approver_4':r.message.level_approver_4,
									})
									frm.refresh_field('mp_approval')
								}
							})

						})
					}
				})
			}

			// LA Table- Pending for Manager 3
			if (frappe.user.has_role(['Level Approver 4'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Miss Punch Application",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 3'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Miss Punch Application",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('mp_approval', {
										'mp_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'attendance_date': r.message.attendance_date,
										'in_time': r.message.in_time,
										'out_time': r.message.out_time,
										'leave_approver_1': r.message.level_approver_1,
										'leave_approver_2':r.message.level_approver_2,
										'leave_approver_3':r.message.level_approver_3,
										'leave_approver_4':r.message.level_approver_4,
									})
									frm.refresh_field('mp_approval')
								}
							})

						})
					}
				})
			}


			// LA Approval
			frm.fields_dict["mp_approval"].grid.add_custom_button(__('Reject'),
				function () {
					$.each(frm.doc.mp_approval, function (i, d) {
						if (d.__checked == 1) {
							frm.call('submit_miss_punch', {
								doctype: "Miss Punch Application",
								name: d.mp_application,
								workflow_state: 'Rejected'
							}).then(r => {
								frm.get_field("mp_approval").grid.grid_rows[d.idx - 1].remove();
							})
						}
						frm.refresh_field('mp_approval')
					})
				}).addClass('btn-danger')

			frm.fields_dict["mp_approval"].grid.add_custom_button(__('Approve'),
				function () {
					$.each(frm.doc.mp_approval, function (i, d) {
						if (d.__checked == 1) {
							if (d.workflow_state == 'Pending for Manager') {
								frm.call('submit_miss_punch', {
								doctype: "Miss Punch Application",
								name: d.mp_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Miss Punch Application {0} moved to <b>{1}</b>",
									[d.mp_application, next_state]
								));

								frm.get_field("mp_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('mp_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 1') {
								frm.call('submit_miss_punch', {
								doctype: "Miss Punch Application",
								name: d.mp_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Miss Punch Application {0} moved to <b>{1}</b>",
									[d.mp_application, next_state]
								));

								frm.get_field("mp_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('mp_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 2') {
								frm.call('submit_miss_punch', {
								doctype: "Miss Punch Application",
								name: d.mp_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Miss Punch Application {0} moved to <b>{1}</b>",
									[d.mp_application, next_state]
								));

								frm.get_field("mp_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('mp_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 3') {			
								frm.call('submit_miss_punch', {
								doctype: "Miss Punch Application",
								name: d.mp_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Miss Punch Application {0} moved to <b>{1}</b>",
									[d.mp_application, next_state]
								));

								frm.get_field("mp_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('mp_approval');
							});
							}
							
						}
					})
				}).addClass('btn-primary').css({ "margin-left": "10px", "margin-right": "10px" })

			
			//---------- Permision-----------

			if (frappe.user.has_role(['Level Approver 1'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Attendance Permission",
						"filters": [
							['workflow_state', '=', 'Pending for Manager'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Attendance Permission",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('pr_approval', {
										'pr_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'permission_date': r.message.permission_date,
										'in_time': r.message.from_time,
										'out_time': r.message.to_time,
										'leave_approver_1': r.message.level_approver_1,
										'leave_approver_2':r.message.level_approver_2,
										'leave_approver_3':r.message.level_approver_3,
										'leave_approver_4':r.message.level_approver_4,
									})
									frm.refresh_field('pr_approval')
								}
							})

						})
					}
				})
			}
			// LA Table-SM
			if (frappe.user.has_role(['Level Approver 2'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Attendance Permission",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 1'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Attendance Permission",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('pr_approval', {
										'pr_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'permission_date': r.message.permission_date,
										'in_time': r.message.from_time,
										'out_time': r.message.to_time,
										'leave_approver_1': r.message.level_approver_1,
										'leave_approver_2':r.message.level_approver_2,
										'leave_approver_3':r.message.level_approver_3,
										'leave_approver_4':r.message.level_approver_4,
									})
									frm.refresh_field('pr_approval')
								}
							})

						})
					}
				})
			}
			// LA Table- Pending for Manager 2
			if (frappe.user.has_role(['Level Approver 3'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Attendance Permission",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 2'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Attendance Permission",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('pr_approval', {
										'pr_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'permission_date': r.message.permission_date,
										'in_time': r.message.from_time,
										'out_time': r.message.to_time,
										'leave_approver_1': r.message.level_approver_1,
										'leave_approver_2':r.message.level_approver_2,
										'leave_approver_3':r.message.level_approver_3,
										'leave_approver_4':r.message.level_approver_4,
									})
									frm.refresh_field('pr_approval')
								}
							})

						})
					}
				})
			}

			// LA Table- Pending for Manager 3
			if (frappe.user.has_role(['Level Approver 4'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Attendance Permission",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 3'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Attendance Permission",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('pr_approval', {
										'pr_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'permission_date': r.message.permission_date,
										'in_time': r.message.from_time,
										'out_time': r.message.to_time,
										'leave_approver_1': r.message.level_approver_1,
										'leave_approver_2':r.message.level_approver_2,
										'leave_approver_3':r.message.level_approver_3,
										'leave_approver_4':r.message.level_approver_4,
									})
									frm.refresh_field('pr_approval')
								}
							})

						})
					}
				})
			}


			// LA Approval
			frm.fields_dict["pr_approval"].grid.add_custom_button(__('Reject'),
				function () {
					$.each(frm.doc.pr_approval, function (i, d) {
						if (d.__checked == 1) {
							frm.call('submit_permission', {
								doctype: "Attendance Permission",
								name: d.pr_application,
								workflow_state: 'Rejected'
							}).then(r => {
								frm.get_field("pr_approval").grid.grid_rows[d.idx - 1].remove();
							})
						}
						frm.refresh_field('pr_approval')
					})
				}).addClass('btn-danger')

			frm.fields_dict["pr_approval"].grid.add_custom_button(__('Approve'),
				function () {
					$.each(frm.doc.pr_approval, function (i, d) {
						if (d.__checked == 1) {
							if (d.workflow_state == 'Pending for Manager') {
								frm.call('submit_permission', {
								doctype: "Attendance Permission",
								name: d.pr_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Attendance Permission {0} moved to <b>{1}</b>",
									[d.pr_application, next_state]
								));

								frm.get_field("pr_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('pr_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 1') {
								frm.call('submit_permission', {
								doctype: "Attendance Permission",
								name: d.pr_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Attendance Permission {0} moved to <b>{1}</b>",
									[d.pr_application, next_state]
								));

								frm.get_field("pr_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('pr_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 2') {
								frm.call('submit_permission', {
								doctype: "Attendance Permission",
								name: d.pr_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Attendance Permission {0} moved to <b>{1}</b>",
									[d.pr_application, next_state]
								));

								frm.get_field("pr_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('pr_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 3') {			
								frm.call('submit_permission', {
								doctype: "Attendance Permission",
								name: d.pr_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Attendance Permission {0} moved to <b>{1}</b>",
									[d.pr_application, next_state]
								));

								frm.get_field("pr_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('pr_approval');
							});
							}
							
						}
					})
				}).addClass('btn-primary').css({ "margin-left": "10px", "margin-right": "10px" })


			
			//---------- Overtime-----------

			if (frappe.user.has_role(['Level Approver 1'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Over Time",
						"filters": [
							['workflow_state', '=', 'Pending for Manager'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Over Time",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('ot_approval', {
										'ot_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'ot_date': r.message.ot_date,
										'ot_hours': r.message.overtime_hours,
										'leave_approver_1': r.message.level_approver_1,
										'leave_approver_2':r.message.level_approver_2,
										'leave_approver_3':r.message.level_approver_3,
										'leave_approver_4':r.message.level_approver_4,
									})
									frm.refresh_field('ot_approval')
								}
							})

						})
					}
				})
			}
			// LA Table-SM
			if (frappe.user.has_role(['Level Approver 2'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Over Time",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 1'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Over Time",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('ot_approval', {
										'ot_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'permission_date': r.message.permission_date,
										'in_time': r.message.from_time,
										'out_time': r.message.to_time,
										'leave_approver_1': r.message.level_approver_1,
										'leave_approver_2':r.message.level_approver_2,
										'leave_approver_3':r.message.level_approver_3,
										'leave_approver_4':r.message.level_approver_4,
									})
									frm.refresh_field('ot_approval')
								}
							})

						})
					}
				})
			}
			// LA Table- Pending for Manager 2
			if (frappe.user.has_role(['Level Approver 3'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Over Time",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 2'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Over Time",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('ot_approval', {
										'pr_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'permission_date': r.message.permission_date,
										'in_time': r.message.from_time,
										'out_time': r.message.to_time,
										'leave_approver_1': r.message.level_approver_1,
										'leave_approver_2':r.message.level_approver_2,
										'leave_approver_3':r.message.level_approver_3,
										'leave_approver_4':r.message.level_approver_4,
									})
									frm.refresh_field('ot_approval')
								}
							})

						})
					}
				})
			}

			// LA Table- Pending for Manager 3
			if (frappe.user.has_role(['Level Approver 4'])) {
				frappe.call({
					"method": "frappe.client.get_list",
					"args": {
						"doctype": "Over Time",
						"filters": [
							['workflow_state', '=', 'Pending for Manager 3'],
						],
						'field':['*'],
						limit_page_length: 500
					},
					callback(r) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								"args": {
									"doctype": "Over Time",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Loading...",
								callback(r) {
									frm.add_child('ot_approval', {
										'pr_application': r.message.name,
										'employee': r.message.employee,
										'employee_name': r.message.employee_name,
										'workflow_state': r.message.workflow_state,
										'shift': r.message.shift,
										'department': r.message.department,
										'permission_date': r.message.permission_date,
										'in_time': r.message.from_time,
										'out_time': r.message.to_time,
										'leave_approver_1': r.message.level_approver_1,
										'leave_approver_2':r.message.level_approver_2,
										'leave_approver_3':r.message.level_approver_3,
										'leave_approver_4':r.message.level_approver_4,
									})
									frm.refresh_field('ot_approval')
								}
							})

						})
					}
				})
			}


			// LA Approval
			frm.fields_dict["ot_approval"].grid.add_custom_button(__('Reject'),
				function () {
					$.each(frm.doc.ot_approval, function (i, d) {
						if (d.__checked == 1) {
							frm.call('submit_overtime', {
								doctype: "Over Time",
								name: d.ot_application,
								workflow_state: 'Rejected'
							}).then(r => {
								frm.get_field("ot_approval").grid.grid_rows[d.idx - 1].remove();
							})
						}
						frm.refresh_field('ot_approval')
					})
				}).addClass('btn-danger')

			frm.fields_dict["ot_approval"].grid.add_custom_button(__('Approve'),
				function () {
					$.each(frm.doc.ot_approval, function (i, d) {
						if (d.__checked == 1) {
							if (d.workflow_state == 'Pending for Manager') {
								frm.call('submit_overtime', {
								doctype: "Over Time",
								name: d.ot_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Over Time {0} moved to <b>{1}</b>",
									[d.ot_application, next_state]
								));

								frm.get_field("ot_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('ot_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 1') {
								frm.call('submit_overtime', {
								doctype: "Over Time",
								name: d.ot_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Over Time {0} moved to <b>{1}</b>",
									[d.ot_application, next_state]
								));

								frm.get_field("ot_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('ot_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 2') {
								frm.call('submit_overtime', {
								doctype: "Over Time",
								name: d.ot_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Over Time {0} moved to <b>{1}</b>",
									[d.ot_application, next_state]
								));

								frm.get_field("ot_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('ot_approval');
							});
							}
							if (d.workflow_state == 'Pending for Manager 3') {			
								frm.call('submit_overtime', {
								doctype: "Over Time",
								name: d.ot_application,
								workflow_state: d.workflow_state
							}).then(r => {

								let next_state = r.message.workflow_state;

								frappe.msgprint(__(
									"The Over Time {0} moved to <b>{1}</b>",
									[d.ot_application, next_state]
								));

								frm.get_field("ot_approval").grid.grid_rows[d.idx - 1].remove();
								frm.refresh_field('ot_approval');
							});
							}
							
						}
					})
				}).addClass('btn-primary').css({ "margin-left": "10px", "margin-right": "10px" })

	}
});
