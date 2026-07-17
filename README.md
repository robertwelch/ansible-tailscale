## Initialize
- Create Tailscale Telnet: [https://console.tailscale.com/](https://console.tailscale.com/)
- Click `Add device` > `Linux server`
    - Fill out `Tags`
    - Check `Ephemeral`
    - Check `Set up authentication key`
    - Update `Auth key expiration` if necessary
    - Click `Generate install script`
- Copy `secrets.rb` to `.vagrant/secrets.rb` and update `TAILSCALE_AUTHKEY`
- Create and provision VMs: `vagrant up`
