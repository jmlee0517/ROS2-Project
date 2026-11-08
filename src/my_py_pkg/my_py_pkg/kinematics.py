import math


# Robot dimensions in metres
SHOULDER_HEIGHT = 0.110
L1 = 0.1375
L2 = 0.120
L3 = 0.075


def forward_kinematics(joint_angles):
    """
    Calculate the end-effector position of the 4-DOF robot.

    Args:
        joint_angles: [base, shoulder, elbow, wrist] in radians

    Returns:
        (x, y, z): End-effector position in metres,
                   relative to base_link.
    """

    if len(joint_angles) != 4:
        raise ValueError(
            "Expected four joint angles: base, shoulder, elbow, wrist"
        )

    theta0, theta1, theta2, theta3 = joint_angles

    # Cumulative angles
    phi1 = theta1
    phi2 = theta1 + theta2
    phi3 = theta1 + theta2 + theta3

    # Radial distance from the base rotation axis
    r = (
        L1 * math.sin(phi1)
        + L2 * math.sin(phi2)
        + L3 * math.sin(phi3)
    )

    # Vertical position
    z = (
        SHOULDER_HEIGHT
        + L1 * math.cos(phi1)
        + L2 * math.cos(phi2)
        + L3 * math.cos(phi3)
    )

    # Apply base rotation
    x = r * math.cos(theta0)
    y = r * math.sin(theta0)

    return x, y, z
