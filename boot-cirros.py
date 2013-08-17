#!/usr/bin/env python -u
'''

This script does the following

1. Connect the router to the public network
2. Add a public key
3. Boot a cirros instance
4. Attach a floating IP


'''
import os.path
import time

from novaclient.v1_1 import client as novaclient
from neutronclient.v2_0 import client as neutronclient

auth_url = "http://192.168.27.100:35357/v2.0"
password = "password"
tenant_name = "demo"

neutron_admin = neutronclient.Client(auth_url=auth_url,
                                     username="admin",
                                     password=password,
                                     tenant_name=tenant_name)
neutron_demo = neutronclient.Client(auth_url=auth_url,
                                    username="demo",
                                    password=password,
                                    tenant_name=tenant_name)

nova = novaclient.Client(auth_url=auth_url,
                         username="demo",
                         api_key=password,
                         project_id=tenant_name)



print "Adding public gateway to router...",
# There should only be one router, named 'router1'
router, = [x for x in neutron_admin.list_routers()['routers']
                   if x['name'] == 'router1']

# Similiarly, there should be one external network
ext_net, = [x for x in neutron_admin.list_networks()['networks']
                    if x['router:external']]

neutron_admin.add_gateway_router(router['id'], {'network_id': ext_net['id'],
                                                'enable_snat': True})
print "done"

print "Creating keypair: mykey...",
if not nova.keypairs.findall(name="mykey"):
    with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as fpubkey:
        nova.keypairs.create(name="mykey", public_key=fpubkey.read())
print "done"

print "Booting cirros instance...",
image = nova.images.find(name="cirros-0.3.1-x86_64-uec")
flavor = nova.flavors.find(name="m1.nano")
instance = nova.servers.create(name="cirros", image=image, flavor=flavor,
                              key_name="mykey")

# Poll at 5 second intervals, until the status is no longer 'BUILD'
status = instance.status
while status == 'BUILD':
    time.sleep(5)
    # Retrieve the instance again so the status field updates
    instance = nova.servers.get(instance.id)
    status = instance.status
print "done"


print "Creating floating ip...",
# Get the port corresponding to the instance
port, = [x for x in neutron_demo.list_ports()['ports']
                 if x['device_id'] == instance.id]

# Create the floating ip
args = dict(floating_network_id=ext_net['id'],
            port_id=port['id'])
ip = neutron_demo.create_floatingip(body={'floatingip': args})
print "done"

print "IP:", ip['floatingip']['floating_ip_address']
