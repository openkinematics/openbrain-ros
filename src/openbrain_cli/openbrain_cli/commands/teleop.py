"""`openbrain teleop` — terminal WASD teleop.

Publishes ``/safety/cmd_vel/dashboard`` (the right input for `twist_mux`).
Press a key, get a single Twist; press space or release for a moment to
let the safety mux time out.

Implementation lives entirely in the terminal — uses ``select`` so we don't
need curses. ``q`` quits cleanly.
"""

from __future__ import annotations

import select
import sys
import termios
import tty

KEYBINDS = """
WASD-style teleop — press to move, space to stop, q to quit.

   w / s   — forward / back
   a / d   — turn left / right
   q / e   — strafe left / right (for holonomic bases)
   space   — emergency-stop pulse
   1/2/3   — set speed profile (beginner/normal/insane)
   x       — quit
"""


def run(*, linear: float, angular: float) -> int:
    try:
        import rclpy
        from geometry_msgs.msg import Twist
        from std_srvs.srv import Trigger as _  # noqa: F401  (verifies srvs present)
    except ImportError as exc:
        print(f"openbrain teleop needs rclpy: {exc}", file=sys.stderr)
        return 2

    rclpy.init()
    node = rclpy.create_node("openbrain_cli_teleop")
    pub = node.create_publisher(Twist, "/safety/cmd_vel/dashboard", 10)
    print(KEYBINDS)
    print(f"linear={linear:.2f} m/s  angular={angular:.2f} rad/s")

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    try:
        while rclpy.ok():
            twist = Twist()
            ch = _read_key(timeout=0.1)
            if ch is None:
                pub.publish(twist)  # zero — let mux timeout
                continue
            if ch == "x":
                break
            elif ch == "w":
                twist.linear.x = linear
            elif ch == "s":
                twist.linear.x = -linear
            elif ch == "a":
                twist.angular.z = angular
            elif ch == "d":
                twist.angular.z = -angular
            elif ch == "q":
                twist.linear.y = linear
            elif ch == "e":
                twist.linear.y = -linear
            elif ch == " ":
                pass  # publish zero
            elif ch in ("1", "2", "3"):
                _set_profile(node, {"1": "beginner", "2": "normal", "3": "insane"}[ch])
                continue
            else:
                continue
            pub.publish(twist)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        node.destroy_node()
        rclpy.shutdown()
    return 0


def _read_key(*, timeout: float) -> str | None:
    r, _, _ = select.select([sys.stdin], [], [], timeout)
    if not r:
        return None
    return sys.stdin.read(1)


def _set_profile(node, profile: str) -> None:
    from openbrain_msgs.srv import SetSpeedProfile

    cli = node.create_client(SetSpeedProfile, "/teleop/set_speed_profile")
    if not cli.wait_for_service(timeout_sec=0.5):
        node.get_logger().warn("set_speed_profile service not available")
        return
    req = SetSpeedProfile.Request(profile=profile)
    cli.call_async(req)
    node.get_logger().info(f"speed profile -> {profile}")
