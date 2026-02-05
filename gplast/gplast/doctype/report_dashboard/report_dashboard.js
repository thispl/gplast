// Copyright (c) 2023, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Report Dashboard', {
    from_date: function(frm) {
        if (frm.doc.report == 'Bonus Report' && frm.doc.from_date) {
            var from_dt = new Date(frm.doc.from_date);

            // March 31 of next year
            var to_year = from_dt.getFullYear() + 1;
            var to_dt = new Date(to_year, 2, 31); // 2 = March

            // Format as yyyy-mm-dd (ERPNext standard)
            var yyyy = to_dt.getFullYear();
            var mm = String(to_dt.getMonth() + 1).padStart(2, '0');
            var dd = String(to_dt.getDate()).padStart(2, '0');
            frm.set_value('to_date', yyyy + '-' + mm + '-' + dd);
        }
    },
	download: function (frm) {
        if(frm.doc.report == 'Department Wise OT Report') {
            var path = "gplast.gplast.doctype.report_dashboard.dept_wise_ot_report.download";
            var args = $.param({
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                unit:frm.doc.unit,
                // company:doc.frm.company1
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }
        if(frm.doc.report == 'Daily Strength Report') {
            var path = "gplast.gplast.doctype.report_dashboard.dept_wise_strength.download_daily_strength";
            var args = $.param({
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                unit:frm.doc.unit,
                // company:doc.frm.company1
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }
		if (frm.doc.report == 'Monthly Salary Register') {
			var path = "gplast.gplast.doctype.report_dashboard.monthly_salary_register.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s'
		}
        if(frm.doc.report == 'Monthly Salary Register - Contractor') {
            var path = "gplast.gplast.doctype.report_dashboard.cl_register.download";
            var args = $.param({
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                contractor_name: frm.doc.contractor_name,
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }
        // if (frm.doc.report == 'Monthly Salary Register - Contractor') {
		// 	var path = "gplast.gplast.doctype.report_dashboard.cl_register.download"
		// 	let args =
        //         "from_date=" + frm.doc.from_date +
        //         "&to_date=" + frm.doc.to_date +
        //         "&contractor_name=" + frm.doc.contractor_name;
		// }
        if (frm.doc.report == 'PF Report') {
			var path = "gplast.gplast.doctype.report_dashboard.pf_report.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s'
		}
		if(path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s',{
				cmd: path,
				args: args,
				from_date : frm.doc.from_date,
				to_date : frm.doc.to_date,
			});
		}
        if (frm.doc.report == 'Bonus Report') {
			var path = "gplast.gplast.doctype.report_dashboard.bonus_report.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s'
		}
		if(path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s',{
				cmd: path,
				args: args,
				from_date : frm.doc.from_date,
				to_date : frm.doc.to_date,
			});
		}
		// if (frm.doc.report == 'Muster Roll Report') {
		// 	var path = "gplast.gplast.doctype.report_dashboard.muster_roll.download_form25_excel"
		// 	var args = 'from_date=%(from_date)s&to_date=%(to_date)s'
		// }
		// if(path) {
		// 	window.location.href = repl(frappe.request.url +
		// 		'?cmd=%(cmd)s&%(args)s',{
		// 		cmd: path,
		// 		args: args,
		// 		from_date : frm.doc.from_date,
		// 		to_date : frm.doc.to_date,
		// 		company : frm.doc.company1,
		// 		company_address : frm.doc.company_address
		// 	});
		// }

		if(frm.doc.report == 'Muster Roll Report') {
            var path = "gplast.gplast.doctype.report_dashboard.muster_roll.download_form25_excel";
            var args = $.param({
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                company: frm.doc.company1,
                company_address: frm.doc.company_address,
				employee:frm.doc.employee
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }
        if(frm.doc.report == 'Form 25') {
            var path = "gplast.gplast.doctype.report_dashboard.form_25.download_form25_excel";
            var args = $.param({
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                company: frm.doc.company1,
                company_address: frm.doc.company_address,
				employee:frm.doc.employee
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }
		if(frm.doc.report == 'Shift Register Report 1') {
            var path = "gplast.gplast.doctype.report_dashboard.shift_register1.download_form25_excel";
            var args = $.param({
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                company: frm.doc.company1,
                company_address: frm.doc.company_address,
				employee:frm.doc.employee
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }
		if(frm.doc.report == 'Shift Register Report 2') {
            var path = "gplast.gplast.doctype.report_dashboard.shift_register2.download_form25_excel";
            var args = $.param({
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                company: frm.doc.company1,
                company_address: frm.doc.company_address,
				employee:frm.doc.employee
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }

		if(frm.doc.report == 'Form 12') {
            var path = "gplast.gplast.doctype.report_dashboard.form_12.download_form12_excel";
            var args = $.param({
                
                company: frm.doc.company1
                
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }


        if(frm.doc.report == 'Leave Credit Report') {
            var path = "gplast.gplast.doctype.report_dashboard.leave_credit_report.download_leave_credit_excel";
            var args = $.param({
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                company: frm.doc.company1,
                employee:frm.doc.employee
                
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }

        if(frm.doc.report == 'Leave Wages') {
            var path = "gplast.gplast.doctype.report_dashboard.leave_wages.download_leave_wages_excel";
            var args = $.param({
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                company: frm.doc.company1,
                employee:frm.doc.employee,
                department:frm.doc.department,
                
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }
        if(frm.doc.report == 'Leave Encashment' && frm.doc.employment_type !='Apprentice' ) {
            var path = "gplast.gplast.doctype.report_dashboard.leave_encashment_format1.download_leave_encashment_format1_excel";
            var args = $.param({
                employment_type:frm.doc.employment_type,
                
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }
        if(frm.doc.report == 'Leave Encashment' && frm.doc.employment_type =='Apprentice') {
            var path = "gplast.gplast.doctype.report_dashboard.leave_encashment_format2.download_leave_encashment_format2_excel";
            var args = $.param({
                employment_type:frm.doc.employment_type,
                
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }
        if(frm.doc.report == 'Shift Wise Present Count Report') {
            var path = "gplast.gplast.doctype.report_dashboard.shift_wise_present.download";
            var args = $.param({
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }
        if(frm.doc.report == 'Department & Shift Wise Present') {
            var path = "gplast.gplast.doctype.report_dashboard.department_wise_present.generate_shift_excel";
            var args = $.param({
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                department: frm.doc.department
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }

        if(frm.doc.report == 'Overall CTC Report') {
            var path = "gplast.gplast.doctype.report_dashboard.overall_ctc_report.download";
            var args = $.param({
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                contractor_name: frm.doc.contractor_name,
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }
        if(frm.doc.report == 'ESI Report') {
            var path = "gplast.gplast.doctype.report_dashboard.esi_report.download_esi_excel";
            var args = $.param({
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date
            });
            window.location.href = frappe.request.url + 
                                    '?cmd=' + encodeURIComponent(path) + '&' + args;
        }


	}
    
	});
