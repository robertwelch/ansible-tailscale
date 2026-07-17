# -*- mode: ruby -*-
# vi: set ft=ruby :

require_relative '.vagrant/secrets.rb'
include Secrets

VM_COUNT = 4
VM_MEMORY_GB = 2
VM_CPUS = 2

Vagrant.configure("2") do |config|
    (1..VM_COUNT).each do |i|
        ## https://portal.cloud.hashicorp.com/vagrant/discover/cloud-image/rocky-10
        config.vm.define "rocky10-#{i}" do |rocky10|
            rocky10.vm.box = "cloud-image/rocky-10"
            rocky10.vm.hostname = "rocky10-#{i}"
            rocky10.vm.provider "virtualbox" do |vb|
                vb.default_nic_type = "virtio"
                vb.memory = VM_MEMORY_GB * 1024
                vb.cpus = VM_CPUS
            end
            rocky10.vm.provision :shell, :privileged => true, path: "Vagrantfile.Provisioner.sh"
            rocky10.vm.provision :shell, :privileged => true, inline: <<-SHELL
            sudo tailscale up --auth-key=#{TAILSCALE_AUTHKEY} --ssh --force-reauth
            SHELL
        end
    end
end
