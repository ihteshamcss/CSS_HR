
frappe.ui.form.on('Meetings', {
	committee: function (frm) {

		if (!frm.doc.committee) {
			frm.clear_table('members');
			frm.refresh_field('members');
			return;
		}

		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Committee WUAJK",
				name: frm.doc.committee
			},
			callback: function (r) {

				if (!r.message) return;

				let source_rows = r.message.combined_committee_members || [];

				frm.clear_table('members');

				source_rows.forEach(row => {

					let child = frm.add_child('members');

					child.member_name = row.member_name;
					child.department = row.department;
					child.designation = row.designation;
					child.email = row.email;
					child.organization = row.organization;
					child.committee_designation = row.committee_designation;
					child.phone = row.phone;
				});

				frm.refresh_field('members');
			}
		});
	}
});