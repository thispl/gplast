frappe.pages['privacy-policy'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Privacy Policy',
		single_column: true
	});
}