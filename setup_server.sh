#!/usr/bin/env bash
# setup_server.sh — Raspberry Pi setup for the Hexapod robot server
# Run from the repository root: sudo bash setup_server.sh

set -euo pipefail

# ── Colours ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
info() { echo -e "${CYAN}[--]${NC} $*"; }
warn() { echo -e "${YELLOW}[!!]${NC} $*"; }
die()  { echo -e "${RED}[FAIL]${NC} $*" >&2; exit 1; }

# ── Root check ─────────────────────────────────────────────────────────────────
[[ $EUID -eq 0 ]] || die "Please run with sudo: sudo bash setup_server.sh"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}  Freenove Hexapod — Server Setup (Raspberry Pi)${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""

# ── 1. python3 symlink ─────────────────────────────────────────────────────────
info "Ensuring 'python' points to python3..."
if ! command -v python &>/dev/null || [[ "$(python --version 2>&1)" != *"Python 3"* ]]; then
    ln -sf "$(command -v python3)" /usr/bin/python
    ok "Created python → python3 symlink"
else
    ok "python already points to python3"
fi

# ── 2. apt update ──────────────────────────────────────────────────────────────
info "Running apt-get update..."
apt-get update -y || die "apt-get update failed"
ok "apt-get update done"

# ── 3. System packages ─────────────────────────────────────────────────────────
info "Installing system packages..."
apt-get install -y \
    python3-dev \
    python3-pip \
    python3-smbus \
    python3-numpy \
    python3-pyqt5 \
    i2c-tools \
    libqt5gui5 \
    libopenblas-dev \
    || die "apt-get install failed"
ok "System packages installed"

# ── 4. Enable I2C ──────────────────────────────────────────────────────────────
info "Enabling I2C interface..."
BOOT_CONFIG="/boot/config.txt"
# Raspberry Pi 5 / Bookworm uses /boot/firmware/config.txt
[[ -f /boot/firmware/config.txt ]] && BOOT_CONFIG="/boot/firmware/config.txt"

if grep -q "^dtparam=i2c_arm=on" "$BOOT_CONFIG"; then
    ok "I2C already enabled in $BOOT_CONFIG"
else
    echo "dtparam=i2c_arm=on" >> "$BOOT_CONFIG"
    ok "I2C enabled in $BOOT_CONFIG"
fi

if ! grep -q "^i2c-dev" /etc/modules 2>/dev/null; then
    echo "i2c-dev" >> /etc/modules
fi

# Load i2c-dev now (without requiring reboot for this session)
modprobe i2c-dev 2>/dev/null && ok "i2c-dev module loaded" || warn "Could not load i2c-dev — will be active after reboot"

# ── 5. pip packages ────────────────────────────────────────────────────────────
info "Upgrading pip..."
python3 -m pip install --upgrade pip

info "Installing pip packages..."
pip3 install \
    mpu6050-raspberrypi \
    picamera2 \
    smbus2 \
    || die "pip3 install failed"
ok "pip packages installed"

# ── 6. rpi-ws281x (NeoPixel LED library) ──────────────────────────────────────
WS281X_DIR="$SCRIPT_DIR/Code/Libs/rpi-ws281x-python/library"
if [[ -d "$WS281X_DIR" ]]; then
    info "Installing rpi-ws281x from bundled source..."
    pushd "$WS281X_DIR" > /dev/null
    python3 setup.py install || die "rpi-ws281x install failed"
    popd > /dev/null
    ok "rpi-ws281x installed"
else
    warn "Bundled rpi-ws281x library not found at $WS281X_DIR"
    info "Attempting pip install of rpi-ws281x fallback..."
    pip3 install rpi-ws281x || warn "rpi-ws281x pip install also failed — LEDs may not work"
fi

# ── 7. Verify I2C devices (informational) ─────────────────────────────────────
echo ""
info "Scanning I2C bus 1 for connected devices..."
if command -v i2cdetect &>/dev/null; then
    i2cdetect -y 1 2>/dev/null || warn "i2cdetect failed — I2C may not be active until reboot"
else
    warn "i2cdetect not found — install i2c-tools manually if needed"
fi

# ── 8. Quick import check ──────────────────────────────────────────────────────
echo ""
info "Verifying Python imports..."
IMPORT_ERRORS=0

check_import() {
    local mod="$1"
    if python3 -c "import $mod" 2>/dev/null; then
        ok "  import $mod"
    else
        warn "  import $mod — NOT FOUND"
        IMPORT_ERRORS=$((IMPORT_ERRORS + 1))
    fi
}

check_import smbus
check_import RPi.GPIO
check_import PyQt5
check_import numpy
check_import mpu6050
check_import rpi_ws281x

# picamera2 is optional depending on OS version
if python3 -c "import picamera2" 2>/dev/null; then
    ok "  import picamera2"
else
    warn "  import picamera2 — may need manual install (see: sudo apt install python3-picamera2)"
fi

# ── Done ───────────────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}================================================${NC}"
if [[ $IMPORT_ERRORS -eq 0 ]]; then
    echo -e "${GREEN}  Setup complete! Please reboot the Raspberry Pi.${NC}"
    echo -e "${GREEN}  Then start the server:${NC}"
    echo -e "${GREEN}    cd Code/Server && sudo python3 main.py${NC}"
    echo -e "${GREEN}  Or headless (no GUI):${NC}"
    echo -e "${GREEN}    cd Code/Server && sudo python3 main.py -n -t${NC}"
else
    echo -e "${YELLOW}  Setup finished with $IMPORT_ERRORS missing import(s).${NC}"
    echo -e "${YELLOW}  Check warnings above, then reboot and re-run if needed.${NC}"
fi
echo -e "${CYAN}================================================${NC}"
echo ""
