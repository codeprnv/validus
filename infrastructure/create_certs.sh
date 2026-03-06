#!/bin/bash

# Configuration
# Path relates to the directory this script is executed from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
CERT_FILE="${SCRIPT_DIR}/cert.pem"
KEY_FILE="${SCRIPT_DIR}/key.pem"

echo "Checking for existing SSL certificates in the infrastructure folder..."

# If certificates already exist and are regular files (not empty directories Docker might have made), skip generation
if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "✅ Certificates already exist. Skipping generation."
    exit 0
fi

# Clean up empty directories that Docker might have incorrectly created during bind-mounting
if [ -d "$CERT_FILE" ]; then
    echo "⚠️ Removing incorrect directory: $CERT_FILE"
    rm -rf "$CERT_FILE"
fi

if [ -d "$KEY_FILE" ]; then
    echo "⚠️ Removing incorrect directory: $KEY_FILE"
    rm -rf "$KEY_FILE"
fi

echo "Generating dummy self-signed certificates..."

# Generate a silent self-signed cert valid for 365 days
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "$KEY_FILE" \
  -out "$CERT_FILE" \
  -subj "/C=US/ST=State/L=City/O=Validus/CN=localhost" \
  > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Successfully generated dummy certificates."
    echo "You can now safely run 'docker-compose up -d' with both HTTP and HTTPS."
else
    echo "❌ Failed to generate certificates. Please ensure openssl is installed."
    exit 1
fi
