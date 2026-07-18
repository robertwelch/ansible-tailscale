# -*- mode: ruby -*-
# vi: set ft=ruby :

require_relative '.vagrant/secrets.rb'
include Secrets

Vagrant.configure("2") do |config|
    ## https://portal.cloud.hashicorp.com/vagrant/discover/cloud-image/rocky-10
    config.vm.define "homeassistant" do |homeassistant|
        homeassistant.vm.box = "cloud-image/rocky-10"
        homeassistant.vm.hostname = "homeassistant"
        homeassistant.vm.provider "virtualbox" do |vb|
            vb.default_nic_type = "virtio"
            vb.memory = VM_MEMORY_GB * 1024
            vb.cpus = VM_CPUS
        end
        homeassistant.vm.provision :shell, :privileged => true, path: "Vagrantfile.Provisioner.sh"
        homeassistant.vm.provision :shell, :privileged => true, inline: <<-SHELL
        if [[ -n "#{TAILSCALE_AUTHKEY}" ]]; then
            curl -fsSL https://tailscale.com/install.sh | sh 2>&1
            sudo tailscale up --reset --auth-key=#{TAILSCALE_AUTHKEY} --ssh --force-reauth --advertise-tags workstations,homeassistant
        else
            echo "ERROR: Must provide TAILSCALE_AUTHKEY in ./vagrant/secrets.rb"
            echo "       View README.md for steps on how to acquire the TAILSCALE_AUTHKEY"
            exit 1
        fi
        SHELL
    end
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
            if [[ -n "#{TAILSCALE_AUTHKEY}" ]]; then
                curl -fsSL https://tailscale.com/install.sh | sh 2>&1
                sudo tailscale up --reset --auth-key=#{TAILSCALE_AUTHKEY} --ssh --force-reauth --advertise-tags workstations
            else
                echo "ERROR: Must provide TAILSCALE_AUTHKEY in ./vagrant/secrets.rb"
                echo "       View README.md for steps on how to acquire the TAILSCALE_AUTHKEY"
                exit 1
            fi
            SHELL
        end
    end
end
