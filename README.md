# ansible-tailscale
Create and use a Tailscale Tailnet to manage a fleet of devices using ansible.

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

### VirtualBox
The `Vagrantfile` is setup to use `VirtualBox`, so make sure [Virtualbox is installed first](https://www.virtualbox.org/wiki/Downloads).

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
- Use `run.sh` to create and activate a python3 venv, install requirements.txt, install requirements.yml, run linter, then run main.yml
``` shell
/bin/bash run.sh
/bin/bash run.sh --tags ping
/bin/bash run.sh --tags init
/bin/bash run.sh --tags storage
/bin/bash run.sh --tags homeassistant
```

## Home Assistant
[Home Assistant Documentation](https://www.home-assistant.io/docs/)
- Run ansible to configure homeassistant:
``` shell
ansible-playbook -i ansible_tailscale_inventory.py main.yml --tags homeassistant
```
- When the role finishes, it will show a debug message with the full URL to open `Home Assistant`. This URL utilizes your Tailnet magic DNS and because we opened firewall in the role, you should be able to access it from any device in your Tailnet.
