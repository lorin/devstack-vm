# Neutron-enabled DevStack in a Vagrant VM with Ansible

This repository contains a Vagrantfile and an accompanying Ansible playbook
that sets up a VirtualBox VM that installs [DevStack][4].

The accompanying `localrc` file configures OpenStack to use Neutron (OpenStack
Networking). It also disables security groups.

This project was inspired by Brian Waldon's [vagrant_devstack][1] repository.


## Prereqs

Install the following applications on your local machine first:

 * [VirtualBox][5]
 * [Vagrant][2]
 * [Ansible][3]

If you want to try out the OpenStack command-line tools once DevStack is running, install the following Python packages:

  * python-novaclient
  * python-neutronclient

The easiest way to install the Python packages is with pip:

    sudo pip install python-novaclient python-neutronclient


[1]: https://github.com/bcwaldon/vagrant_devstack
[2]: http://vagrantup.com
[3]: http://ansibleworks.com
[4]: http://devstack.org
[5]: http://virtualbox.org


## Boot the virtual machine and install DevStack

Grab this repo and do a `vagrant up`, lke so:

    git clone https://github.com/lorin/devstack-vm
    cd devstack-vm
    vagrant up

The `vagrant up` command will:

 1. Download an Ubuntu 13.04 (raring) vagrant box if it hasn't previously been downloaded to your machine.
 2. Boot the virtual machine (VM).
 3. Clone the DevStack git repository inside of the VM.
 4. Run DevStack inside of the VM.
 5. Add eth2 to the br-ex bridge inside of the VM to enable floating IP access from the host machine.

It will take at least ten minutes for this to run, and possibly much longer depending on your internet connection and whether it needs to download the Ubuntu vagrant box.


You may ocassionally see the following error message:

```
[default] Waiting for VM to boot. This can take a few minutes.
[default] Failed to connect to VM!
Failed to connect to VM via SSH. Please verify the VM successfully booted
by looking at the VirtualBox GUI.
```

If you see this, retry by doing:

    vagrant destroy --force && vagrant up


## Logging in the virtual machine

The VM is accessible at 192.168.27.100

You can use ssh to access it using `vagrant` as username and password, or use the
provided `id_vagrant` private key to avoid typing a password.

You can also type `vagrant ssh` to start an ssh session.

Note that you do not need to be logged in to the VM to run commands against the OpenStack endpoint.






## Loading OpenStack credentials

From your local machine, to run as the demo user:

    source demo.openrc

To run as the admin user:

    source admin.openrc

## Horizon

* URL: http://192.168.27.100
* Username: admin or demo
* Password: password


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


Next, switch back to the "demo" user and boot an instance.

    source demo.openrc
    nova keypair-add --pub-key ~/.ssh/id_rsa.pub mykey
    nova boot --flavor m1.nano --image cirros-0.3.1-x86_64-uec --key-name mykey cirros

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

