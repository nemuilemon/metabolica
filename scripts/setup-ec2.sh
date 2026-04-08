#!/bin/bash
# EC2 setup script for Metabolica Daemon
# Run as ec2-user: bash scripts/setup-ec2.sh

set -euo pipefail

REPO_URL="https://github.com/nemuilemon/metabolica.git"
INSTALL_DIR="/opt/metabolica"

echo "=== Metabolica EC2 Setup ==="

# Install system dependencies
echo "[1/5] Installing system packages..."
sudo dnf update -y
sudo dnf install -y python3.12 python3.12-pip git

# Clone repository
echo "[2/5] Cloning repository..."
sudo mkdir -p "$INSTALL_DIR"
sudo chown ec2-user:ec2-user "$INSTALL_DIR"
git clone "$REPO_URL" "$INSTALL_DIR"

# Setup Python venv
echo "[3/5] Setting up Python virtual environment..."
cd "$INSTALL_DIR"
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install schedule boto3 requests

# Create .env template
echo "[4/5] Creating .env file..."
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cp .env.example .env
    echo ">>> Edit /opt/metabolica/.env and add your API keys <<<"
fi

# Install systemd service
echo "[5/5] Installing systemd service..."
sudo cp daemon/metabolica.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable metabolica
sudo systemctl start metabolica

echo ""
echo "=== Setup Complete ==="
echo "Check status: sudo systemctl status metabolica"
echo "View logs:    sudo journalctl -u metabolica -f"
echo "IMPORTANT:    Edit /opt/metabolica/.env with your API keys"
