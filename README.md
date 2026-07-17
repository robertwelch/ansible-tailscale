## Tailscale
[Tailscale Documentation](https://tailscale.com/docs)
- Create Tailscale Telnet: [https://console.tailscale.com/](https://console.tailscale.com/)
- Join this computer to your tailnet (i.e. `Add device` > `Client device`), it will act as the ansible controller.
- Tag this device:
    - Click `Access controls` > `Tags` > `Create tag` and name it `home`
    - Now go to `Machines`, click the 3 dots at the end of your client machine and click `Edit ACL tags...` then add the tag you just created
- Get auth key to join the VirtualBox VMs:
    - Click `Add device` > `Linux server`
    - Fill out `Tags`
        - Use `tag:workstations` so we can filter for these VMs later when modifying the access controls
    - Check `Ephemeral`
    - Check `Set up authentication key`
    - Update `Auth key expiration` if desired
    - Click `Generate install script`
- Add auth key to secrets file:
    - Copy `./secrets.rb` to `./.vagrant/secrets.rb` (you may have to create the `./.vagrant` directory) and update `TAILSCALE_AUTHKEY`
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
- Run the `main.yml` playbook:
``` shell
ansible-playbook -i ansible_tailscale_inventory.py main.yml
```
