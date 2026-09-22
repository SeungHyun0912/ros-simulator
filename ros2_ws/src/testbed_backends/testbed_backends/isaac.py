class IsaacMotion:
    """Extension point only. Never silently fall back to mock."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            'Isaac backend is not implemented. Pin Isaac/ROS versions, '
            'implement cmd_vel/odom or your controller contract, and run '
            'end-to-end tests before enabling it.'
        )
