// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Revision Summary', {
	refresh: function(frm) {
		frm.fields_dict['salary_details'].grid.wrapper.find('.edit-grid-row').hide();
		$('*[data-fieldname="salary_details"]').find('.grid-remove-all-rows').hide();
	},
	onload: function(frm) {
        let currentLength = (frm.doc.salary_details || []).length;

        if (frm.doc.employee) {
            frappe.call({
                method: "gplast.gplast.doctype.revision_summary.revision_summary.get_salary_details",
                args: { employee: frm.doc.employee },
                callback(r) {
                    if (r.message && Array.isArray(r.message)) {
                        if (r.message.length !== currentLength) {
                            frm.clear_table("salary_details");

                            $.each(r.message, function(i, v) {
                                frm.add_child("salary_details", v);
                            });

                            frm.refresh_field("salary_details");

                            if (!frm.is_new()) {
                                frm.save();
                            }
                        }
                    }
                }
            });
        } 
        else {
            if (frm.is_new()) {
                frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
                    .then(r => {
                        if (r.message && r.message.name) {
                            console.log(r.message)
							frappe.db.get_value('Revision Summary', { name: r.message.name }, 'name')
							.then(res => {
                                console.log(res.message)
								if (res.message && !res.message.name) {
                                    frm.set_value('employee', r.message.name);
                                    frappe.call({
                                        method: "gplast.gplast.doctype.revision_summary.revision_summary.get_salary_details",
                                        args: { employee: r.message.name },
                                        callback(r) {
                                            if (r.message && Array.isArray(r.message)) {
                                                if (r.message.length !== currentLength) {
                                                    frm.clear_table("salary_details");

                                                    $.each(r.message, function(i, v) {
                                                        frm.add_child("salary_details", v);
                                                    });

                                                    frm.refresh_field("salary_details");
                                                    frm.save();
                                                    
                                                }
                                            }
                                        }
                                    });
                                }
                            });
                        }
                    });
            } 
            else {
                frm.clear_table("salary_details");
                frm.refresh_field("salary_details");
            }
        }
    },


	
	setup(frm){
		frm.get_docfield('salary_details').allow_bulk_edit = 1
	},
	employee: function(frm) {
		if (frm.doc.employee) {
			frm.trigger('get_salary_details');
		}
		else{
			frm.clear_table("salary_details");
			frm.refresh_field("salary_details");
		}
	},
	get_salary_details(frm) {
        frappe.call({
            method: "gplast.gplast.doctype.revision_summary.revision_summary.get_salary_details",
            args: {
                employee: frm.doc.employee,
            },
            callback(r) {
                if (r.message && Array.isArray(r.message)) {
                    frm.clear_table("salary_details");

                    $.each(r.message, function (i, v) {
                        frm.add_child("salary_details", v);
                        // frm.add_child("salary_details", {
                        //     basic: v.basic,
                        //     cca: v.cca,
                        //     house_rent_allowance: v.house_rent_allowance,
                        //     special_allowance: v.special_allowance,
                        //     conveyance_allowance: v.conveyance_allowance,
                        //     medical_allowances: v.medical_allowances,
                        //     shift_allowance: v.shift_allowance,
                        //     other_allowance: v.other_allowance,
                        //     uniform_allowance: v.uniform_allowance,
                        //     magazine_allowances: v.magazine_allowances,

                        //     reference_document: v.reference_document,
                        //     gross_salary: v.gross_salary,
                        //     increment_amount: v.increment_amount,
                        //     salary_increment_date:v.salary_increment_date,
						// 	increment_type:v.increment_type,

                        //     revised_basic: v.revised_basic,
                        //     revised_cca: v.revised_cca,
                        //     revised_house_rent_allowance: v.revised_house_rent_allowance,
                        //     revised_special_allowance: v.revised_special_allowance,
                        //     revised_conveyance_allowance: v.revised_conveyance_allowance,
                        //     revised_medical_allowances: v.revised_medical_allowances,
                        //     revised_shift_allowance: v.revised_shift_allowance,
                        //     revised_other_allowance: v.revised_other_allowance,
                        //     revised_uniform_allowance: v.revised_uniform_allowance,
                        //     revised_magazine_allowances: v.revised_magazine_allowances,
                        //     revised_gross_salary: v.revised_gross_salary
                        // });
                    });

                    frm.refresh_field("salary_details");
                } else {
                    frappe.msgprint("Salary Increment not available for the Employee");
                }
            }
        });
    }


});
