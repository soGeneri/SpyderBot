#!/usr/bin/env bash
# setup_client.sh — PC/Mac setup for the Hexapod robot client
# Run from the repository root: bash setup_client.sh
#
# Supported platforms: Linux, macOS, Windows (Git Bash / WSL)

set -euo pipefail

# ── Colours ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
info() { echo -e "${CYAN}[--]${NC} $*"; }
warn() { echo -e "${YELLOW}[!!]${NC} $*"; }
die()  { echo -e "${RED}[FAIL]${NC} $*" >&2; exit 1; }

echo ""
echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}  Freenove Hexapod — Client Setup (PC / Mac)   ${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""

# ── Detect OS ──────────────────────────────────────────────────────────────────
OS="$(uname -s)"
case "$OS" in
    Linux*)   PLATFORM="linux"  ;;
    Darwin*)  PLATFORM="macos"  ;;
    MINGW*|MSYS*|CYGWIN*) PLATFORM="windows" ;;
    *)        PLATFORM="unknown" ;;
esac
info "Detected platform: $PLATFORM ($OS)"

# ── Detect Python ──────────────────────────────────────────────────────────────
if command -v python3 &>/dev/null; then
    PYTHON=python3
    PIP=pip3
elif command -v python &>/dev/null && python --version 2>&1 | grep -q "Python 3"; then
    PYTHON=python
    PIP=pip
else
    die "Python 3 not found. Install it from https://www.python.org/downloads/ then re-run."
fi

PYVER=$($PYTHON --version 2>&1)
info "Using: $PYTHON ($PYVER)"

# ── Upgrade pip ────────────────────────────────────────────────────────────────
info "Upgrading pip..."
$PYTHON -m pip install --upgrade pip --quiet
ok "pip upgraded"

# ── Core pip packages ──────────────────────────────────────────────────────────
info "Installing PyQt5..."
$PIP install PyQt5 --quiet || die "PyQt5 install failed"
ok "PyQt5 installed"

info "Installing Pillow..."
$PIP install Pillow --quiet || die "Pillow install failed"
ok "Pillow installed"

info "Installing numpy..."
$PIP install numpy --quiet || die "numpy install failed"
ok "numpy installed"

# ── OpenCV ─────────────────────────────────────────────────────────────────────
info "Installing OpenCV..."
if [[ "$PLATFORM" == "macos" ]]; then
    # headless avoids macOS GUI framework conflicts
    $PIP install opencv-python-headless opencv-contrib-python-headless --quiet \
        || die "OpenCV install failed"
else
    $PIP install opencv-python opencv-contrib-python --quiet \
        || die "OpenCV install failed"
fi
ok "OpenCV installed"

# ── Platform-specific extras ───────────────────────────────────────────────────
if [[ "$PLATFORM" == "linux" ]]; then
    info "Linux detected — checking for Qt system libs..."
    if command -v apt-get &>/dev/null; then
        # Best-effort; don't fail the whole script if this needs sudo
        sudo apt-get install -y python3-pyqt5 libqt5gui5 2>/dev/null \
            && ok "Qt system packages installed via apt" \
            || warn "Could not install Qt system packages via apt (try manually if UI fails)"
    fi
elif [[ "$PLATFORM" == "macos" ]]; then
    info "macOS detected — no extra system packages required"
elif [[ "$PLATFORM" == "windows" ]]; then
    info "Windows detected — no extra system packages required"
fi

# ── Set default IP if IP.txt is empty or missing ───────────────────────────────
IP_FILE="$(dirname "${BASH_SOURCE[0]}")/Code/Client/IP.txt"
if [[ ! -s "$IP_FILE" ]]; then
    warn "Code/Client/IP.txt is empty or missing."
    echo ""
    read -rp "  Enter your Raspberry Pi's IP address (or press Enter to skip): " ROBOT_IP
    if [[ -n "$ROBOT_IP" ]]; then
        echo "$ROBOT_IP" > "$IP_FILE"
        ok "Saved $ROBOT_IP to Code/Client/IP.txt"
    else
        echo "192.168.1.100" > "$IP_FILE"
        warn "Used placeholder 192.168.1.100 — edit Code/Client/IP.txt before connecting"
    fi
else
    ok "Code/Client/IP.txt already set to: $(cat "$IP_FILE")"
fi

# ── Verify imports ─────────────────────────────────────────────────────────────
echo ""
info "Verifying Python imports..."
IMPORT_ERRORS=0

check_import() {
    local mod="$1"
    if $PYTHON -c "import $mod" 2>/dev/null; then
        ok "  import $mod"
    else
        warn "  import $mod — NOT FOUND"
        IMPORT_ERRORS=$((IMPORT_ERRORS + 1))
    fi
}

check_import PyQt5
check_import PIL
check_import cv2
check_import numpy

# ── Done ───────────────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}================================================${NC}"
if [[ $IMPORT_ERRORS -eq 0 ]]; then
    echo -e "${GREEN}  All dependencies installed successfully!${NC}"
    echo ""
    echo -e "${GREEN}  To launch the client:${NC}"
    echo -e "${GREEN}    cd Code/Client && $PYTHON Main.py${NC}"
else
    echo -e "${YELLOW}  Setup finished with $IMPORT_ERRORS missing import(s).${NC}"
    echo -e "${YELLOW}  Check warnings above and re-run if needed.${NC}"
fi
echo -e "${CYAN}================================================${NC}"
echo ""
