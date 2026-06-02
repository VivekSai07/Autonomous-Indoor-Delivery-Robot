#!/usr/bin/env python3
"""
Waits for Gazebo's /spawn_entity service using rclpy (no ros2 CLI daemon),
then spawns the robot from the /robot_description topic.

Bypasses the ros2 CLI which hangs on WSL2 due to daemon socket issues.
"""
import sys
import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SpawnEntity
from std_msgs.msg import String


class RobotSpawner(Node):
    def __init__(self):
        super().__init__('robot_spawner')
        self._urdf = None
        self._spawned = False

        self._desc_sub = self.create_subscription(
            String,
            'robot_description',
            self._desc_cb,
            qos_profile=rclpy.qos.QoSProfile(
                depth=1,
                durability=rclpy.qos.DurabilityPolicy.TRANSIENT_LOCAL,
            ),
        )
        self._client = self.create_client(SpawnEntity, '/spawn_entity')
        self.get_logger().info('Waiting for /spawn_entity service...')

    def _desc_cb(self, msg):
        if self._urdf is None:
            self._urdf = msg.data
            self.get_logger().info('Got robot_description.')

    def ready(self):
        return self._urdf is not None and self._client.service_is_ready()

    def spawn(self, x=0.0, y=0.0, z=0.05, yaw=0.0):
        req = SpawnEntity.Request()
        req.name = 'amr_robot'
        req.xml = self._urdf
        req.initial_pose.position.x = x
        req.initial_pose.position.y = y
        req.initial_pose.position.z = z
        import math
        req.initial_pose.orientation.z = math.sin(yaw / 2.0)
        req.initial_pose.orientation.w = math.cos(yaw / 2.0)
        req.reference_frame = 'world'

        self.get_logger().info('Calling /spawn_entity...')
        future = self._client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=30.0)

        if future.result() is not None:
            self.get_logger().info(f'Spawn result: {future.result().status_message}')
            self._spawned = True
        else:
            self.get_logger().error('Spawn call timed out or failed.')

        return self._spawned


def main():
    rclpy.init()
    node = RobotSpawner()

    x   = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    y   = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    z   = float(sys.argv[3]) if len(sys.argv) > 3 else 0.05
    yaw = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0

    import time
    deadline = time.time() + 300.0   # give up after 5 minutes
    while not node.ready() and time.time() < deadline:
        rclpy.spin_once(node, timeout_sec=2.0)
        if not node._client.service_is_ready():
            node.get_logger().info('/spawn_entity not ready yet, retrying...')
        if node._urdf is None:
            node.get_logger().info('robot_description not received yet, retrying...')

    if not node.ready():
        node.get_logger().error('Timed out waiting for /spawn_entity or robot_description.')
        node.destroy_node()
        rclpy.shutdown()
        sys.exit(1)

    node.spawn(x, y, z, yaw)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
