#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import socket
import sys
import urllib.error
import urllib.request
from typing import Any, TypedDict


managed_host_properties = ("OS", "Relay", "PeerRelay", "Tags")
managed_host_booleans = ("Online", "Active", "ExitNode", "ExitNodeOption", "InNetworkMap", "InMagicSock", "InEngine")


ansible_inventory_type = dict[str, dict[str, list[str] | dict[str, Any]]]


class InventoryType(TypedDict):
    """
    Type annotation for internal representation of the inventory
    """

    metadata: dict[str, dict[str, Any]]  # Maps hostnames to mappings of their hostvars
    groups: dict[str, list[str]]  # Maps group names to their list of group members


class TailscaleHostType(TypedDict, total=False):
    """
    Type annotation for Tailscale hosts mapped from the API
    """

    Active: bool
    Addrs: list[str] | None
    Capabilities: list[str]
    CapMap: dict[str, Any]
    Created: str
    CurAddr: str | None
    DNSName: str
    ExitNode: bool
    ExitNodeOption: bool
    HostName: str
    ID: str
    InEngine: bool
    InMagicSock: bool
    InNetworkMap: bool
    KeyExpiry: str
    LastHandshake: str
    LastSeen: str
    LastWrite: str
    Online: bool
    OS: str
    PeerAPIURL: list[str]
    PublicKey: str
    Relay: str
    RxBytes: int
    Tags: list[str]
    TailscaleIPs: list[str]
    TxBytes: int
    UserID: int


def parse_iso_timestamp(ts_str: str) -> datetime:
    """
    Parses an ISO 8601 UTC timestamp string into a timezone-aware datetime object.
    Supports older Python versions (like Python 3.6) without fromisoformat.
    """
    if ts_str.endswith("Z"):
        ts_str = ts_str[:-1]

    if "." in ts_str:
        date_part, ms_part = ts_str.split(".", 1)
        ms_part = ms_part[:6]
        ts_str = f"{date_part}.{ms_part}"
        fmt = "%Y-%m-%dT%H:%M:%S.%f"
    else:
        fmt = "%Y-%m-%dT%H:%M:%S"

    dt = datetime.strptime(ts_str, fmt)
    return dt.replace(tzinfo=timezone.utc)


def is_online(device: dict[str, Any]) -> bool:
    """
    Determines if a device is online.
    Checks clientConnectivity online status if present, otherwise falls back
    to comparing lastSeen with current UTC time.
    """
    conn = device.get("clientConnectivity", {})
    if conn and isinstance(conn, dict):
        if "online" in conn:
            return bool(conn["online"])

    last_seen_str = device.get("lastSeen")
    if last_seen_str:
        try:
            last_seen_dt = parse_iso_timestamp(last_seen_str)
            now = datetime.now(timezone.utc)
            # Consider online if last seen in the last 10 minutes (600 seconds)
            return (now - last_seen_dt).total_seconds() < 600
        except Exception:
            pass

    return False


def get_tailscale_devices(tailnet_id: str, tailnet_apikey: str) -> list[dict[str, Any]]:
    """
    Fetches the list of devices in the tailnet using the Tailscale API
    """
    url = f"https://api.tailscale.com/api/v2/tailnet/{tailnet_id}/devices"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {tailnet_apikey}")

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            return res_data.get("devices", [])
    except urllib.error.HTTPError as e:
        print(f"Tailscale API request failed (HTTP {e.code}): {e.reason}", file=sys.stderr)
        try:
            err_body = e.read().decode()
            print(f"Response: {err_body}", file=sys.stderr)
        except Exception:
            pass
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Failed to connect to Tailscale API: {e.reason}", file=sys.stderr)
        sys.exit(1)


def map_api_device_to_host_type(device: dict[str, Any]) -> TailscaleHostType:
    """
    Maps a device object from the Tailscale API to the TailscaleHostType structure.
    """
    hostname = device.get("hostname")
    if not hostname:
        hostname = device.get("name", "").split(".")[0]

    os_name = device.get("os", "")
    dns_name = device.get("name", "")
    tailscale_ips = device.get("addresses", [])
    tags = device.get("tags", [])
    online = is_online(device)

    mapped: TailscaleHostType = {
        "Active": online,
        "Created": device.get("created", ""),
        "DNSName": dns_name,
        "ExitNode": False,
        "ExitNodeOption": False,
        "HostName": hostname,
        "ID": device.get("id", ""),
        "InEngine": online,
        "InMagicSock": online,
        "InNetworkMap": True,
        "KeyExpiry": device.get("expires", ""),
        "LastSeen": device.get("lastSeen", ""),
        "Online": online,
        "OS": os_name,
        "Tags": tags,
        "TailscaleIPs": tailscale_ips,
    }
    return mapped


def get_self_hostname(devices: list[dict[str, Any]]) -> str:
    """
    Determines the self hostname.
    Checks TAILSCALE_SELF_HOSTNAME env var first, then falls back to local hostname
    and checks if it matches any device in the tailnet.
    """
    env_self = os.environ.get("TAILSCALE_SELF_HOSTNAME")
    if env_self:
        return env_self

    local_hostname = socket.gethostname().split(".")[0].lower()

    for dev in devices:
        hostname = dev.get("hostname", "").lower()
        if hostname == local_hostname:
            return dev.get("hostname", "")

        name = dev.get("name", "").split(".")[0].lower()
        if name == local_hostname:
            return dev.get("hostname") or name

    return socket.gethostname().split(".")[0]


def assemble_inventory(
    tailscale_hosts: list[TailscaleHostType],
    tailscale_self_hostname: str,
) -> InventoryType:
    """
    Given a list of tailscale hosts with their metadata return an inventory object. This
    is where we select set the metadata ansible will be aware of for each host as
    hostvars, and defines group memberships. The "self" hostname needs to be identified
    explicitly so it can be put into its own group
    """

    # Create the base inventory data structure
    inventory: InventoryType = {
        "metadata": {},
        "groups": {
            "all": [],
            "self": [tailscale_self_hostname],
        },
    }

    for host_data in tailscale_hosts:
        # We intentionally avoid adding any the funnel-ingress-node to the inventory
        # because we can't manage it
        if host_data["HostName"] == "funnel-ingress-node":
            continue

        # We ignore endpoints that have no OS, like Mullvad exit nodes
        if not host_data["OS"]:
            continue

        # We add each host to the list of all hosts
        inventory["groups"]["all"].append(host_data["HostName"])

        # Set host's inventory metadata
        inventory["metadata"][host_data["HostName"]] = {
            "ansible_host": host_data["DNSName"],
            "tailscale_ips": host_data["TailscaleIPs"],
            **({"ansible_connection": "local"} if host_data["HostName"] == tailscale_self_hostname else {})
        }

        # Loop through managed host properties, create group if necessary and append host to group
        for host_property in managed_host_properties:
            if host_data.get(host_property):
                if isinstance(host_data[host_property], str):
                    loop_value = [host_data[host_property]]
                elif isinstance(host_data[host_property], list):
                    loop_value = host_data[host_property]
                else:
                    loop_value = []
                for value in loop_value:
                    safe_value = value.replace(":", "_").replace("-", "_").lower()
                    if safe_value in inventory["groups"]:
                        inventory["groups"][safe_value].append(host_data["HostName"])
                    else:
                        inventory["groups"][safe_value] = [host_data["HostName"]]

        # Loop through managed host booleans and append to group if boolean is truthy
        for host_boolean in managed_host_booleans:
            if host_data.get(host_boolean):
                group_name = host_boolean.lower()
                if group_name in inventory["groups"]:
                    inventory["groups"][group_name].append(host_data["HostName"])
                else:
                    inventory["groups"][group_name] = [host_data["HostName"]]

    return inventory


def format_ansible_inventory(inventory: InventoryType) -> ansible_inventory_type:
    """
    Given an inventory object, returns the inventory formatted to be read by ansible
    """

    # Create the base ansible inventory object
    ansible_inventory: ansible_inventory_type = {
        "_meta": {"hostvars": inventory["metadata"]},
    }

    # Create groups
    for key, value in inventory["groups"].items():
        ansible_inventory[key] = {"hosts": value}

    return ansible_inventory


def main() -> None:
    """
    This is the main function run when the script is executed
    """
    tailnet_id = os.environ.get("TAILNET_ID")
    tailnet_apikey = os.environ.get("TAILNET_APIKEY")

    if not tailnet_apikey:
        print("Error: TAILNET_APIKEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    if not tailnet_id:
        print("Error: TAILNET_ID environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    devices = get_tailscale_devices(tailnet_id, tailnet_apikey)
    self_hostname = get_self_hostname(devices)

    ts_hosts = [map_api_device_to_host_type(dev) for dev in devices]
    inventory = assemble_inventory(ts_hosts, self_hostname)
    ansible_inventory = format_ansible_inventory(inventory)

    print(json.dumps(ansible_inventory, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
