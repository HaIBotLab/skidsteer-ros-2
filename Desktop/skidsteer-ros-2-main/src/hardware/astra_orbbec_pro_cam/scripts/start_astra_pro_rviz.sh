#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROBOT_WS="$HOME/Desktop/skid_robot_v2"
RVIZ_CONFIG="$SCRIPT_DIR/astrapro_pointcloud.rviz"

source /opt/ros/humble/setup.bash
source "$ROBOT_WS/install/setup.bash"

if [[ ! -f "$RVIZ_CONFIG" ]]; then
    echo "ERROR: Không tìm thấy cấu hình RViz: $RVIZ_CONFIG" >&2
    exit 1
fi

exec rviz2 -d "$RVIZ_CONFIG"
