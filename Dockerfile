# syntax=docker/dockerfile:1

FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

ENV ROS_DISTRO=jazzy
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    curl \
    gnupg2 \
    lsb-release \
    ca-certificates \
    software-properties-common \
    build-essential \
    git \
    wget \
    python3-pip \
    python3-opencv \
    && locale-gen en_US en_US.UTF-8 \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*


RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu noble main" \
    > /etc/apt/sources.list.d/ros2.list

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-ros-base \
    ros-jazzy-librealsense2 \
    ros-jazzy-launch-pytest \
    ros-jazzy-xacro \
    ros-jazzy-diagnostic-updater \
    ros-jazzy-rmw-cyclonedds-cpp \
    ros-jazzy-rmw-fastrtps-cpp \
    python3-tqdm \
    python3-requests \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-image-transport \
    ros-jazzy-camera-info-manager \
    ros-jazzy-cv-bridge \
    ros-jazzy-image-proc \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*

RUN rosdep init 2>/dev/null || true
RUN rosdep update

WORKDIR /ros2_ws

COPY src ./src

# Install dependencies declared by packages in src/
RUN . /opt/ros/${ROS_DISTRO}/setup.sh && \
    rosdep install \
        --from-paths src \
        --ignore-src \
        --rosdistro ${ROS_DISTRO} \
        -y

RUN . /opt/ros/${ROS_DISTRO}/setup.sh && \
    colcon build --symlink-install

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["bash"]