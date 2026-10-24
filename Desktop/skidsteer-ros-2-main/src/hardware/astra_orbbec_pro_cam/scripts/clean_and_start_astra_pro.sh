#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Dang dung cac tien trinh Astra/point cloud cu..."

# Chi ket thuc cac tien trinh lien quan den driver Astra va point cloud.
pkill -TERM -f '[a]stra_camera::OBCameraNodeFactory' 2>/dev/null || true
pkill -TERM -f '[p]oint_cloud_xyz_node' 2>/dev/null || true

sleep 2

echo "Khoi dong lai Astra Pro..."
exec bash "$SCRIPT_DIR/start_astra_pro_all.sh"
