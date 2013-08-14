# Neutron-enabled DevStack in a Vagrant VM with Ansible

This project was inspired by Brian Waldon's [vagrant_devstack][1] repository.

This repository contains a Vagrantfile and an accompanying Ansible playbook
that sets up a VirtualBox VM that installs [DevStack][4].

The accompanying `localrc` file configures OpenStack with Neutron (OpenStack
Networking) with support for floating IPs, which can be reached from the host
operating system. It also has security groups disabled.

## Prereqs

Install the following packages first:

 * [VirtualBox][5]
 * [Vagrant][2]
 * [Ansible][3]


[1]: https://github.com/bcwaldon/vagrant_devstack
[2]: http://vagrantup.com
[3]: http://ansibleworks.com
[4]: http://devstack.org
[5]: http://virtualbox.org

You also need the Ubuntu 13.04 (raring) 64-bit vagrant box installed. Once you
have vagrant installed, download a raring box:

    vagrant box add raring64 http://cloud-images.ubuntu.com/raring/current/raring-server-cloudimg-vagrant-amd64-disk1.box

## Boot the virtual machine and install DevStack

    git clone https://github.com/lorin/devstack-vm
    cd devstack-vm
    vagrant up


## Accessing credentials

You can make calls against the OpenStack endpoint from either inside of the
instance or from the host.


### Loading credentials

From your local machine, to run as the demo user:

    source demo.openrc

To run as the admin user:

    source admin.openrc


## Networking configuration

DevStack configures an internal network ("private") and an external network ("public"):


    neutron net-list

    +--------------------------------------+---------+------------------------------------------------------+
    | id                                   | name    | subnets                                              |
    +--------------------------------------+---------+------------------------------------------------------+
    | 07048c67-a7fe-40cb-a059-dcc554a6212f | private | b7733765-e316-4173-9060-e3d16897ec53 10.0.0.0/24     |
    | 5770a693-cfc7-431d-ae29-76f36a2e63c0 | public  | fcc4c031-27a2-46f5-a238-38ddb7160c7e 192.168.50.0/24 |
    +--------------------------------------+---------+------------------------------------------------------+


## Launch a cirros instance and attach a floating IP.

First, configure the local router so it is connected to the public network.
Only the admin account has permissions to set the gateway on the router to the public network:

    source admin.openrc
    neutron router-gateway-set router1 public


Next, switch back to the "demo" user and boot an instance

	source demo.openrc
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


Use the neutron port ID to create an attach a floating IP to the "public"" network:

    neutron floatingip-create public --port-id 02491b08-919e-4582-9eb7-f8119c03b8f9

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

