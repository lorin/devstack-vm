require 'vagrant-ansible'


Vagrant::Config.run do |config|
  config.vm.box = "precise64"
  config.vm.customize ["modifyvm", :id, "--memory", 2048]
  config.vm.network(:hostonly, "192.168.27.100", :mac => '080027027100')
  config.vm.provision :ansible do |ansible|
    ansible.playbook = "devstack.yaml"
    ansible.hosts = "devstack"
  end
end
