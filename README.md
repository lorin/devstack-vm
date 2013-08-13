# Neutron-enabled DevStack in a Vagrant VM with Ansible

This project was inspired by Brian Waldon's [vagrant_devstack][1] repository.

It sets up a virtual machine suitable for running devstack. It's configured
for Ubuntu 13.04 (raring) to run the master branch.

It configures OpenStack with Neutron (OpenStack Networking) with support
for floating IPs, which can be reached from the host operating system.

## Prereqs

You need to have the following installed to use this:

 * [Vagrant][2]
 * [Ansible][3]


[1]: https://github.com/bcwaldon/vagrant_devstack
[2]: http://vagrantup.com
[3]: http://ansibleworks.com

You also need the Ubuntu raring 64 box installed. If you have vagrant
installed, just do:

    vagrant box add raring64 http://cloud-images.ubuntu.com/raring/current/raring-server-cloudimg-vagrant-amd64-disk1.box

## Getting DevStack up and running

### Boot the instance

    git clone https://github.com/lorin/devstack-vm
    cd devstack-vm
    vagrant up

### ssh in and install devstack

    vagrant ssh
    cd ~/devstack
    ./stack.sh

### configure the external bridge

    sudo ip link set dev eth2 up
    sudo ip link set dev eth2 promisc on
    sudo ovs-vsctl add-port br-ex eth2

## Accessing credentials

You can make calls against the OpenStack endpoint from either inside of the
instance or from the host.


### Loading credentials on your local machine

    source openrc

These are configured for the admin tenant.

### Inside the instance

When logged into the instance, to run as the demo user:

    cd ~/devstack
    source openrc

To run as the admin user:

    cd ~/devstack
    source openrc admin


## Networking configuration

DevStack configures an internal network ("private") and an external network ("public"):


    quantum net-list

    +--------------------------------------+---------+------------------------------------------------------+
    | id                                   | name    | subnets                                              |
    +--------------------------------------+---------+------------------------------------------------------+
    | 07048c67-a7fe-40cb-a059-dcc554a6212f | private | b7733765-e316-4173-9060-e3d16897ec53 10.0.0.0/24     |
    | 5770a693-cfc7-431d-ae29-76f36a2e63c0 | public  | fcc4c031-27a2-46f5-a238-38ddb7160c7e 192.168.50.0/24 |
    +--------------------------------------+---------+------------------------------------------------------+


## Launch a cirros instance and attach a floating IP.

First, configure the local router so it is connected to the public network.

    neutron router-gateway-set router1 public


Next, boot an instance

    nova boot --flavor m1.nano --image cirros-0.3.1-x86_64-uec cirros

Once the instance has booted, get its ID.

    nova list

    +--------------------------------------+--------+--------+---------------------------------+
    | ID                                   | Name   | Status | Networks                        |
    +--------------------------------------+--------+--------+---------------------------------+
    | b24fc4ad-2d66-4f28-928b-f1cf78075d33 | cirros | ACTIVE | private=10.0.0.3                |
    +--------------------------------------+--------+--------+---------------------------------+

Use the instance ID to get its neutron port :

    neutron port-list -c id -- --device_id b24fc4ad-2d66-4f28-928b-f1cf78075d33

    +--------------------------------------+
    | id                                   |
    +--------------------------------------+
    | 02491b08-919e-4582-9eb7-f8119c03b8f9 |
    +--------------------------------------+


Use the neutron port ID to create an attach a floating IP to the public network:

    neutron floatingip-create --port-id 02491b08-919e-4582-9eb7-f8119c03b8f9 public

    Created a new floatingip:
    +---------------------+--------------------------------------+
    | Field               | Value                                |
    +---------------------+--------------------------------------+
    | fixed_ip_address    | 10.0.0.3                             |
    | floating_ip_address | 192.168.50.11                        |
    | floating_network_id | 5770a693-cfc7-431d-ae29-76f36a2e63c0 |
    | id                  | 480524e1-a5b3-491f-a6ee-9356fc52f81d |
    | port_id             | 02491b08-919e-4582-9eb7-f8119c03b8f9 |
    | router_id           | 0deb0811-78b0-415c-9464-f05d278e9e3d |
    | tenant_id           | 512e45b937a149d283718ffcfc36b8c7     |
    +---------------------+--------------------------------------+

Finally, access your instance:

    ssh cirros@192.168.50.11

