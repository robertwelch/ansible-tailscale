# ansible-tailscale

An automation template and framework to model, provision, and securely orchestrate a fleet of Linux devices using **Ansible** and **Tailscale** within a **Vagrant**-managed virtual environment.

This project demonstrates how to build a zero-config, secure administrative network (Tailnet) to run Ansible playbooks against remote hosts dynamically, using Tailscale's MagicDNS and tags instead of maintaining static SSH configurations or IP addresses.

### Key Capabilities

- **Automated Virtual Environment**: Quickly spins up a multi-node Rocky Linux environment on VirtualBox using [Vagrant](file:///home/rlw0289/Documents/git/ansible-tailscale/Vagrantfile).
- **Dynamic Tailscale Registration**: Automatically joins newly provisioned nodes to your Tailscale network (Tailnet) during bootstrapping.
- **Dynamic Ansible Inventory**: Uses a custom Python script ([ansible_tailscale_inventory.py](file:///home/rlw0289/Documents/git/ansible-tailscale/ansible_tailscale_inventory.py)) that queries the local Tailscale client status to automatically discover and group active nodes by OS, tags, and online state.
- **Secure Provisioning**: Runs Ansible playbooks directly over encrypted Tailscale tunnels using Tailscale SSH, avoiding the need for manual SSH key management.
- **Pre-configured Ansible Roles**:
  - `linux_ping`: For connectivity checks.
  - `linux_init`: Installs base utilities (Podman, Firewalld) and configures security rules.
  - `linux_storage`: Configures LVM (Logical Volume Management) dynamically.
  - `linux_homeassistant`: Installs and exposes Home Assistant inside a Podman container, securely reachable via Tailnet MagicDNS.

## Tailscale
[Tailscale Documentation](https://tailscale.com/docs)

### Create Tailscale Telnet
[https://console.tailscale.com/](https://console.tailscale.com/)

### Modify Access controls
- Click `Access controls` > `JSON editor` (feel free to use `Visual editor`, but using the `JSON editor` makes it easier to copy/paste)
- Update `tagOwners`
```
	"tagOwners": {
		"tag:admins":        ["autogroup:admin"],
		"tag:homeassistant": ["autogroup:member"],
		"tag:vagrantvms":       ["autogroup:member"],
		"tag:home":          ["autogroup:member"],
	},
```
- Update `ssh`
```
	"ssh": [
		{
			"src":    ["tag:home"],
			"dst":    ["tag:vagrantvms"],
			"users":  ["autogroup:nonroot", "root"],
			"action": "accept",
		},
		{
			"src":    ["tag:home"],
			"dst":    ["tag:home"],
			"users":  ["autogroup:nonroot", "root"],
			"action": "accept",
		},
	],
```
- Update `nodeAttrs`
```
	"nodeAttrs": [
		{
			"target": ["*"],
			"app":    {"tailscale.com/app-connectors": []},
		},
		{
			"target": ["*"],
			"attr":   ["drive:share", "drive:access"],
		},
	],
```

### Create ephemeral auth key
- Click `Settings` > `Keys` > `Generate auth key...`
    - Description: `vagrant`
    - Reusable: `Yes`
    - Expiration: `90 days`
    - Ephemeral: `Yes`
    - Tags: `N/A`

### Add auth key to secrets file
- Copy `./secrets.rb` to `./.vagrant/secrets.rb` (you may have to create the `./.vagrant` directory) and update `TAILSCALE_AUTHKEY`
    - NOTE: Anything you put in `./.vagrant/secrets.rb` will NOT be checked into git because `.vagrant` is in `.gitignore`.
    - NOTE: Anything you put in `./secrets.rb` WILL be checked into git, so be careful to place your key in the right place.

### Join this computer to your tailnet
- For Linux:
    ``` shell
    curl -fsSL https://tailscale.com/install.sh | sh
    sudo tailscale up \
        --reset \
        --force-reauth \
        --advertise-exit-node \
        --ssh \
        --advertise-tags home
    ```
- For other clients, click `Machines` > `Add device` > `Client device` and make sure to tag the device with `home`

## Vagrant
[Vagrant Documentation](https://developer.hashicorp.com/vagrant/docs)

### Installing VirtualBox & Vagrant

Before starting, you must install VirtualBox and Vagrant on your machine.

#### Install VirtualBox
The `Vagrantfile` is set up to use `VirtualBox`.

- **Ubuntu/Debian**:
  ```shell
  sudo apt update
  sudo apt install -y virtualbox virtualbox-ext-pack
  ```
- **Fedora**:
  ```shell
  sudo dnf install -y VirtualBox akmods
  sudo akmods
  sudo systemctl restart vboxdrv
  ```
- **macOS**:
  - Intel Macs:
    ```shell
    brew install --cask virtualbox
    ```
  - Apple Silicon (M1/M2/M3): VirtualBox support is in Developer Preview and may not be stable. You may need to adapt the `Vagrantfile` for alternative providers.
- **Windows**:
  ```powershell
  winget install Oracle.VirtualBox
  ```
  Or download from the [VirtualBox Downloads Page](https://www.virtualbox.org/wiki/Downloads).

#### Install Vagrant
Vagrant orchestrates the creation and provisioning of the VMs.

- **Ubuntu/Debian**:
  ```shell
  sudo apt update && sudo apt install -y wget gpg
  wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
  sudo apt update && sudo apt install -y vagrant
  ```
- **Fedora**:
  ```shell
  wget -O- https://rpm.releases.hashicorp.com/fedora/hashicorp.repo | sudo tee /etc/yum.repos.d/hashicorp.repo
  sudo dnf -y install vagrant
  ```
- **RHEL/CentOS/Rocky Linux**:
  ```shell
  sudo yum install -y yum-utils
  sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
  sudo yum -y install vagrant
  ```
- **macOS**:
  ```shell
  brew tap hashicorp/tap
  brew install hashicorp/tap/hashicorp-vagrant
  ```
- **Windows**:
  ```powershell
  winget install HashiCorp.Vagrant
  ```
  Or download from the [Vagrant Downloads Page](https://developer.hashicorp.com/vagrant/install).

Verify the installation by running:
```shell
vagrant --version
```

### Vagrantfile
- Read `Vagrantfile` and update if necessary
- By default, Vagrant will spin up 2 Rocky10 VMs with 2 GB memory and 2 CPUs. Be sure your computer can handle this before trying to spin them up.
- Modify `./.vagrant/secrets.rb` to change the number of VMs, memory or CPUs.

### Create and provision VMs
- Create
``` shell
vagrant up
```
- When you're finished, make sure to destroy the VMs:
``` shell
vagrant destroy -f # -f allows for no-prompt destruction
```

## Ansible
[Ansible Documentation](https://docs.ansible.com/)

### Use `ansible.sh`
- Use `ansible.sh` to create and activate a python3 venv, install requirements.txt, install requirements.yml, run linter, then run main.yml
``` shell
## 1. create and activate a python3 venv, install requirements.txt, install requirements.yml, run linter
/bin/bash ansible.sh

## 2. do everything in example 1 plus run ansible-playbook using the `ansible_tailscale_inventory.py` inventory
/bin/bash ansible.sh main.yml

## 3. do everything in step 2 except only for tasks tagged with `ping`... View `main.yml` for more tag options.
/bin/bash ansible.sh main.yml --tags ping
```

### Test with molecule
``` shell
molecule reset
molecule test
```

## Home Assistant
[Home Assistant Documentation](https://www.home-assistant.io/docs/)
- In your Tailscale console, pick a VM to be your home assistant and add the `homeassistant` tag.
- Use `ansible.sh` with the `homeassistant` tag to configure home assistant on your chosen VM:
``` shell
/bin/bash ansible.sh --tags homeassistant
```
- When the role finishes, it will show a debug message with the full URL to open `Home Assistant`. This URL utilizes your Tailnet magic DNS and because we opened firewall in the role, you should be able to access it from any device in your Tailnet.
