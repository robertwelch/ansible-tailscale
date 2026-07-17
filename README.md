## Initialize Tailscale
- Create Tailscale Telnet: [https://console.tailscale.com/](https://console.tailscale.com/)
- Click `Add device` > `Linux server`
    - Fill out `Tags`
    - Check `Ephemeral`
    - Check `Set up authentication key`
    - Update `Auth key expiration` if necessary
    - Click `Generate install script`
- Copy `secrets.rb` to `.vagrant/secrets.rb` and update `TAILSCALE_AUTHKEY`
    - Anything you put in `./.vagrant/` will NOT be checked into git because `.vagrant` is in `.gitignore`.
    - Anything you put in `./secrets.rb` WILL be checked into git, so be careful to place your key in the right place.
- Also be sure to join this computer, which will act as your ansible controller. to your Tailnet.

## Vagrant
- The `Vagrantfile` is setup to use `VirtualBox`, so make sure that is installed first.
- Read `Vagrantfile` and update if necessary
    - By default, Vagrant will spin up 2 Rocky10 VMs with 2 GB memory and 2 CPUs. Be sure your computer can handle this before trying to spin them up.
- Create and provision VMs:
``` shell
vagrant up
```
- When you're finished, make sure to destroy the VMs:
``` shell
vagrant destroy -f # -f allows for no-prompt destruction
```

## Ansible
- Install requirements:
``` shell
ansible-galaxy install -r requirements.yml
```
- Run the `main.yml` playbook:
``` shell
ansible-playbook -i ansible_tailscale_inventory.py main.yml
```
