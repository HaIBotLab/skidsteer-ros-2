#!/usr/bin/env bash
set -Ee -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROBOT_WS="$HOME/Desktop/skid_robot_v2"

if [[ ! -f /opt/ros/humble/setup.bash ]]; then
    echo "ERROR: Không tìm thấy ROS 2 Humble." >&2
    exit 1
fi

if [[ ! -f "$ROBOT_WS/install/setup.bash" ]]; then
    echo "ERROR: Workspace chưa được build: $ROBOT_WS" >&2
    exit 1
fi

source /opt/ros/humble/setup.bash
source "$ROBOT_WS/install/setup.bash"

cleanup() {
    for pid in "${MIRROR_PID:-}" "${PC_PID:-}" "${RELAY_PID:-}" "${CAM_PID:-}"; do
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            kill -TERM "$pid" 2>/dev/null || true
        fi
    done

    for pid in "${MIRROR_PID:-}" "${PC_PID:-}" "${RELAY_PID:-}" "${CAM_PID:-}"; do
        if [[ -n "$pid" ]]; then
            wait "$pid" 2>/dev/null || true
        fi
    done
}

trap cleanup EXIT INT TERM

# 1. Khoi dong driver Astra Pro
ros2 component standalone astra_camera astra_camera::OBCameraNodeFactory \
    -n camera \
    --node-namespace /camera \
    -p color_width:=640 \
    -p color_height:=480 \
    -p color_fps:=30 \
    -p enable_color:=true \
    -p ir_width:=640 \
    -p ir_height:=480 \
    -p ir_fps:=30 \
    -p enable_ir:=false \
    -p depth_width:=640 \
    -p depth_height:=480 \
    -p depth_fps:=30 \
    -p enable_depth:=true \
    -p depth_align:=true \
    -p serial_number:="" \
    -p number_of_devices:=1 \
    -p depth_scale:=1 \
    -p uvc_camera.enable:=true \
    -p uvc_camera.vid:=0x2bc5 \
    -p uvc_camera.pid:=0x0501 \
    -p uvc_camera.format:=mjpeg \
    -p publish_tf:=true \
    -p tf_publish_rate:=10.0 \
    -p reconnect_timeout:=6.0 &
CAM_PID=$!

# 2. Relay QoS: BEST_EFFORT -> RELIABLE
/usr/bin/python3 "$SCRIPT_DIR/depth_relay.py" &
RELAY_PID=$!

# 3. Tao point cloud tu depth image
sleep 2

ros2 run depth_image_proc point_cloud_xyz_node --ros-args \
    -r image_rect:=/camera/depth/image_raw_relay \
    -r camera_info:=/camera/depth/camera_info_relay \
    -r points:=/camera/depth/points &
PC_PID=$!

# 4. Anh mau lat ngang (topic phu)
if [[ -f "$SCRIPT_DIR/mirror_color_image.py" ]]; then
    /usr/bin/python3 "$SCRIPT_DIR/mirror_color_image.py" &
    MIRROR_PID=$!
fi

echo "Astra Pro dang chay tu workspace: $ROBOT_WS"
echo "RGB:         /camera/color/image_raw"
echo "RGB relay:   /camera/color/image_raw_relay"
echo "Depth:       /camera/depth/image_raw"
echo "Depth relay: /camera/depth/image_raw_relay"
echo "Point cloud: /camera/depth/points"
echo "RGB mirrored:/camera/color/image_mirrored"

wait "$CAM_PID"
