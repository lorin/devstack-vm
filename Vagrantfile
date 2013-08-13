Vagrant.configure("2") do |config|
  config.vm.box = "raring64"
    config.vm.network :private_network, ip: "192.168.27.100" # Local IP
    config.vm.network :private_network, ip: "192.168.50.100", :auto_config => false  # Subnet for floating IPs
    config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", 2048]
    vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
  end
 config.vm.provision :ansible do |ansible|
   ansible.playbook = "devstack.yaml"
   ansible.inventory_file = "ansible_hosts"
 end
end
