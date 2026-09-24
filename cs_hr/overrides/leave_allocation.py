import frappe

from hrms.hr.doctype.leave_allocation.leave_allocation import (
    LeaveAllocation,
)


class CustomLeaveAllocation(LeaveAllocation):

    def is_dependent_leave(self):
        """
        A dependent Leave Type has another Leave Type configured
        in custom_deduct_from_leave_type.

        Example:

            Ex-Pakistan Leave
                ->
            Leave on Full Pay(LFP) Faculty
        """

        return bool(
            frappe.db.get_value(
                "Leave Type",
                self.leave_type,
                "custom_deduct_from_leave_type",
            )
        )


    def set_total_leaves_allocated(self):
        """
        Dependent Leave Types always have zero allocation.

        Their balance comes from the parent Leave Type.

        Example:

            Ex-Pakistan Leave allocation = 0
            LFP Faculty allocation       = 8
        """

        if self.is_dependent_leave():

            # Dependent leaves must never carry their own balance.
            self.unused_leaves = 0
            self.total_leaves_allocated = 0

            # Do not carry dependent leave balances forward.
            self.carry_forward = 0

            return

        # Normal Leave Types use standard HRMS behavior.
        return super().set_total_leaves_allocated()


    def validate_against_leave_applications(self):
        """
        Dependent Leave Types have zero allocation by design.

        Therefore HRMS must not reject the allocation because
        approved dependent applications are greater than zero.

        The actual balance validation happens against the parent
        Leave Type in CustomLeaveApplication.
        """

        if self.is_dependent_leave():
            return

        return super().validate_against_leave_applications()