# -*- mode: ruby -*-
# vi: set ft=ruby :

require_relative '.vagrant/secrets.rb'
include Secrets

Vagrant.configure("2") do |config|
    config.trigger.before :destroy do |trigger|
        trigger.info = "Logout of Tailscale"
        trigger.run_remote = { inline: "sudo tailscale logout || true" }
        trigger.on_error = :continue
    end

    config.vm.provision :shell, :privileged => true, path: "Vagrantfile.Provisioner.sh"
    config.vm.provision :shell, :privileged => true, path: "Vagrantfile.Tailscale.sh", args: "#{TAILSCALE_AUTHKEY}"

    (1..VM_COUNT).each do |vmnum|
        ## https://portal.cloud.hashicorp.com/vagrant/discover/cloud-image/rocky-10
        config.vm.define "vagrantvm-#{vmnum}" do |vagrantvm|
            vagrantvm.vm.box = VM_BOX
            vagrantvm.vm.hostname = "vagrantvm-#{vmnum}"
            vagrantvm.vm.provider "virtualbox" do |vb|
                vb.default_nic_type = "virtio"
                vb.memory = VM_MEMORY_GB * 1024
                vb.cpus = VM_CPUS
                (1..VM_EXTRA_DISK_COUNT).each do |disknum|
                    disk_file = "./vagrantvm-#{vmnum}_disk#{disknum}.vdi"
                    unless File.exist?(disk_file)
                        vb.customize ['createhd', '--filename', disk_file, '--size', VM_EXTRA_DISK_GB * 1024]
                        vb.customize ['storageattach', :id, '--storagectl', 'VirtIO Controller', '--port', disknum, '--device', 0, '--type', 'hdd', '--medium', disk_file]
                    end
                end
            end
        end
    end
end
