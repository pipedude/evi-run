#!/usr/bin/env bash
set -euo pipefail

# Check that the script is run as root or with sudo
if [[ "$EUID" -ne 0 ]]; then
  echo "This script must be run as root or with sudo."
  exit 1
fi

echo "Removing old Docker packages and related..."
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  apt-get remove -y "$pkg"
done

echo "Updating package list and installing dependencies..."
apt-get update
apt-get install -y ca-certificates curl

echo "Creating directory for GPG keys and downloading Docker key..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo "Adding Docker repository to apt sources..."
ARCH=$(dpkg --print-architecture)
CODENAME=$(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
cat <<EOF > /etc/apt/sources.list.d/docker.list
deb [arch=$ARCH signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $CODENAME stable
EOF

echo "Updating package list..."
apt-get update

echo "Installing latest versions of Docker Engine and plugins..."
apt-get install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

echo "Running hello-world test container..."
docker run --rm hello-world

echo "Done! Docker installed and verified."