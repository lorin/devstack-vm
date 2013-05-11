# Run DevStack in a VM using Vagrant and Ansible


This project was inspired by Brian Waldon's [vagrant_devstack][1] repository.

It sets up a virtual machine suitable for running devstack. It's configured
for Ubuntu 12.04 (precise) to run the stable/grizzly branch.

## Prereqs

You need to have the following installed to use this:

 * [Vagrant][2]
 * [Ansible][3]
 * [vagrant-ansible][4]


[1]: https://github.com/bcwaldon/vagrant_devstack
[2]: http://vagrantup.com
[3]: http://ansible.cc
[4]: https://github.com/dsander/vagrant-ansible

You also need the Ubuntu precise 64 box installed. If you have vagrant
installed, just do:

    vagrant box add precise64 http://files.vagrantup.com/precise64.box

## Boot the instance

    git clone https://github.com/lorin/devstack-vm
    cd devstack-vm
    vagrant up


## ssh in and set up devstack

    vagrant ssh
    cd ~/devstack
    ./stack.sh

## nova credentials

When lgoged into the instance, to run as the demo user:

    cd ~/devstack
    source openrc

To run as the admin user:

    cd ~/devstack
    source openrc admin
