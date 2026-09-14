import yaml

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import GroupAction
from launch.actions import IncludeLaunchDescription
from launch.actions import OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_cameras(context):

    config_file = LaunchConfiguration('config_file').perform(context)
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    robot_namespace = config.get('namespace', 'robot')
    cameras = config.get('cameras', {})
    jpeg_quality = config.get('compression', {}).get('jpeg_quality', 80)
    realsense_launch = PythonLaunchDescriptionSource(
        [
            FindPackageShare('realsense2_camera'),
            '/launch/rs_launch.py'
        ]
    )
    actions = []

    for camera_name, camera_config in cameras.items():
        serial = camera_config.get('serial')
        port = camera_config.get('port')
        if not serial and not port:
            print(
                f'WARNING: Camera "{camera_name}" has no '
                'serial or port configured. Skipping.'
            )
            continue
        input_topic = (
            f'{camera_name}/color/image_raw'
        )
        output_topic = (
            f'{camera_name}/color/image_compressed'
        )

        realsense_arguments = {
            'camera_namespace': robot_namespace,
            'camera_name': camera_name,
            'enable_color': 'true',
            'enable_depth': 'true',
            'rgb_camera.color_profile': '1280x720x30',
            'depth_module.depth_profile': '1280x720x30',
            'pointcloud.enable': 'true',
        }

        # Prefer serial number if available
        if serial:
            realsense_arguments['serial_no'] = f'_{serial}'

        # Otherwise use USB port
        elif port:
            realsense_arguments['usb_port_id'] = port

        realsense = IncludeLaunchDescription(
            realsense_launch,
            launch_arguments=realsense_arguments.items()
        )

        compressor = Node(
            package='image_compressor',
            executable='compressor_node',
            name='compressor',
            namespace=f'{robot_namespace}/{camera_name}',
            output='screen',

            parameters=[
                {
                    'input_topic': input_topic,
                    'output_topic': output_topic,
                    'jpeg_quality': jpeg_quality,
                }
            ],
        )

        actions.append(
            GroupAction([
                realsense,
                compressor,
            ])
        )

    print(
        f'Launching {len(actions)} camera(s)'
    )

    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'config_file',
            description='Path to camera configuration YAML'
        ),
        OpaqueFunction(
            function=launch_cameras
        ),
    ])