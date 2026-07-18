#!/usr/bin/env bash
TAILSCALE_AUTHKEY="$1"
if [[ -n "${TAILSCALE_AUTHKEY}" ]]; then
    curl -fsSL https://tailscale.com/install.sh | sh 2>&1
    sudo tailscale up --reset --auth-key=${TAILSCALE_AUTHKEY} --ssh --force-reauth --advertise-tags vagrantvms
else
    echo "ERROR: Must provide TAILSCALE_AUTHKEY in ./vagrant/secrets.rb"
    echo "       View README.md for steps on how to acquire the TAILSCALE_AUTHKEY"
    exit 1
fi
