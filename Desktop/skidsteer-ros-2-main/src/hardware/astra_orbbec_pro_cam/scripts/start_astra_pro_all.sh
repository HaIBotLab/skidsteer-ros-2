#!/usr/bin/env bash
set -Ee -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CAM_PID=""
RVIZ_PID=""

cleanup() {
    trap - EXIT INT TERM

    for pid in "$RVIZ_PID" "$CAM_PID"; do
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            kill -TERM "$pid" 2>/dev/null || true
        fi
    done

    for pid in "$RVIZ_PID" "$CAM_PID"; do
        if [[ -n "$pid" ]]; then
            wait "$pid" 2>/dev/null || true
        fi
    done
}

trap cleanup EXIT INT TERM

# Khoi dong camera va cac node xu ly
bash "$SCRIPT_DIR/start_astra_pro_camera.sh" &
CAM_PID=$!

# Cho driver khoi dong
sleep 8

if ! kill -0 "$CAM_PID" 2>/dev/null; then
    echo "ERROR: Tien trinh camera da dung. Kiem tra log phia tren." >&2
    wait "$CAM_PID"
    exit 1
fi

# Khoi dong RViz
bash "$SCRIPT_DIR/start_astra_pro_rviz.sh" &
RVIZ_PID=$!

echo "Astra Pro va RViz da duoc yeu cau khoi dong."
echo "Nhan Ctrl+C de dung cac tien trinh do script nay quan ly."

wait "$CAM_PID"
