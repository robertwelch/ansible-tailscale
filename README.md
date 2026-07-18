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
		"tag:workstations":  ["autogroup:member"],
		"tag:home":          ["autogroup:member"],
	},
```
- Update `ssh`
```
	"ssh": [
		{
			"src":    ["tag:home"],
			"dst":    ["tag:workstations"],
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

    - NOTE: Anything you put in `./.vagrant/secrets.rb` will NOT be checked into git because `.vagrant` is in `.gitignore`.
    - NOTE: Anything you put in `./secrets.rb` WILL be checked into git, so be careful to place your key in the right place.
- Update access controls to allow SSH:
    - Click `Access controls` > `Tailscale SSH` > `Add rule`
    - Source: `tag:home`
    - Destination: `tag:workstations`
    - As destination user: `autogroup:nonroot` and `root`
    - Check mode: `Off`

## Vagrant
[Vagrant Documentation](https://developer.hashicorp.com/vagrant/docs)
- The `Vagrantfile` is setup to use `VirtualBox`, so make sure [Virtualbox is installed first](https://www.virtualbox.org/wiki/Downloads).
- Read `Vagrantfile` and update if necessary
    - By default, Vagrant will spin up 2 Rocky10 VMs with 2 GB memory and 2 CPUs. Be sure your computer can handle this before trying to spin them up.
    - Modify `./.vagrant/secrets.rb` to change the number of VMs, memory or CPUs.
- Create and provision VMs:
``` shell
vagrant up
```
- When you're finished, make sure to destroy the VMs:
``` shell
vagrant destroy -f # -f allows for no-prompt destruction
```

## Ansible
[Ansible Documentation](https://docs.ansible.com/)
- Install requirements:
``` shell
ansible-galaxy install -r requirements.yml
```
- Ping hosts using the `main.yml` playbook:
``` shell
ansible-playbook -i ansible_tailscale_inventory.py main.yml --tags ping
```
- Configure hosts using the `main.yml` playbook:
``` shell
ansible-playbook -i ansible_tailscale_inventory.py main.yml
```

## Home Assistant
[Home Assistant Documentation](https://www.home-assistant.io/docs/)
- In order to install home assistant, you have to choose a VM and tag it in Tailscale, then run ansible to configure it.
- Open Tailscale and create the tag:
    - Click `Access controls` > `Tags` > `Create tag` and name it `homeassistant`
- Pick a VM and tag it
    - Go to `Machines`, click the 3 dots at the end of your client machine and click `Edit ACL tags...` then add the tag you just created
- Run ansible to configure homeassistant:
``` shell
ansible-playbook -i ansible_tailscale_inventory.py main.yml --tags homeassistant
```
- When the role finishes, it will show a debug message with the full URL to open `Home Assistant`. This URL utilizes your Tailnet magic DNS and because we opened firewall in the role, you should be able to access it from any device in your Tailnet.
