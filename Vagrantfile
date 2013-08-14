Vagrant.configure("2") do |config|
    config.vm.box = "raring64"
    config.vm.box_url = "http://cloud-images.ubuntu.com/raring/current/raring-server-cloudimg-vagrant-amd64-disk1.box"
    # eth1, this will be the endpoint
    config.vm.network :private_network, ip: "192.168.27.100"
    # eth2, this will be the OpenStack "public" network, use DevStack default
    config.vm.network :private_network, ip: "172.24.4.225", :netmask => "255.255.255.224", :auto_config => false
    config.vm.provider :virtualbox do |vb|
        vb.customize ["modifyvm", :id, "--memory", 2048]
       	# eth2 must be in promiscuous mode for floating IPs to be accessible
       	vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
    end
    config.vm.provision :ansible do |ansible|
        ansible.playbook = "devstack.yaml"
        ansible.inventory_file = "ansible_hosts"
    end
    config.vm.provision :shell, :inline => "cd devstack; sudo -u vagrant env HOME=/home/vagrant ./stack.sh"
    config.vm.provision :shell, :inline => "ovs-vsctl add-port br-ex eth2"
end
