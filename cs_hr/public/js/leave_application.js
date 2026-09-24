frappe.ui.form.on("Leave Application", {

    refresh: function(frm) {
        set_balance_deducted_from(frm);
    },

    leave_type: function(frm) {
        set_balance_deducted_from(frm);
    }

});


function set_balance_deducted_from(frm) {

    if (!frm.doc.leave_type) {

        frm.set_value(
            "custom_balance_deducted_from",
            null
        );

        return;
    }

    frappe.db.get_value(
        "Leave Type",
        frm.doc.leave_type,
        "custom_deduct_from_leave_type",
        function(r) {

            if (!r) {
                return;
            }

            let balance_leave_type =
                r.custom_deduct_from_leave_type ||
                frm.doc.leave_type;

            frm.set_value(
                "custom_balance_deducted_from",
                balance_leave_type
            );

        }
    );
}