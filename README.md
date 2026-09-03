# multi_realsense

A Dockerized ROS 2 tool for configuring and launching multiple Intel RealSense cameras from a single YAML configuration file.

The number of cameras, camera names, and USB ports are defined entirely in YAML. No camera-specific configuration is hard-coded into the launch file or Docker Compose configuration.

## Features

- ROS 2 Jazzy
- Supports multiple Intel RealSense cameras
- Camera count is determined by the YAML configuration
- Camera names are defined in YAML
- Cameras can be identified by USB port
- Optional camera serial number identification
- JPEG image compression
- Docker and Docker Compose support
- Designed for `x86_64` and `ARM64`
- External camera configuration
- No need to modify the launch file when cameras are added or removed

---

## How to use

1. Identify the camera and assosiated serial number/port, I recommend plugging in the camera's one at a time and running the following command to note down the port they are attached to:

        lsusb -t

2. clone repository

        git clone https://github.com/ds2000hehe/multi_realsense.git
        cd multi_realsense

3. change the config to add camera's and their usb ports

        nano camera_conf/camera_setup.yaml

4. build the docker container

        docker compose build

5. run container

        docker compose up


## Frame Assignment

Each RealSense camera has its own set of coordinate frames. The camera name defined in `cameras.yaml` is used to identify the camera and its associated frames.

The typical frame hierarchy is:

<camera_name>_link
├── <camera_name>_depth_frame
│   └── <camera_name>_depth_optical_frame
└── <camera_name>_color_frame
    └── <camera_name>_color_optical_frame

For example, a camera named `front` will use the following color optical frame:

front_color_optical_frame

The camera namespace is determined by the global namespace and camera name:

/robot/front

Therefore, the raw color image topic is:

/robot/front/color/image_raw

and the corresponding compressed image topic is:

/robot/front/color/image_compressed

The `frame_id` of the compressed image is preserved from the original image message. The image compressor does not create a new frame or change the coordinate frame.

The same rule applies to every configured camera:

| Camera | Compressed Topic | `frame_id` |
|---|---|---|
| `front` | `/robot/front/color/image_compressed` | `front_color_optical_frame` |
| `left` | `/robot/left/color/image_compressed` | `left_color_optical_frame` |
| `right` | `/robot/right/color/image_compressed` | `right_color_optical_frame` |

The `frame_id` identifies the physical camera coordinate frame associated with the image. It is not affected by JPEG compression.