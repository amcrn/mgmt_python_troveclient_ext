# Copyright 2011 OpenStack Foundation
# Copyright 2013 Rackspace Hosting
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from troveclient import base
from troveclient import utils
from troveclient.v1 import flavors


class MgmtFlavor(base.ManagerWithFind):
    """
    Manage :class:`Flavor` resources.
    """
    resource_class = flavors.Flavor

    def __repr__(self):
        return "<Flavors Manager at %s>" % id(self)

    # Appease the abc gods
    def list(self):
        pass

    def create(self, name, ram, disk, vcpus,
               flavorid="auto", ephemeral=None, swap=None, rxtx_factor=None,
               service_type=None):
        """
        Create a new flavor.
        """
        body = {"flavor": {
            "flavor_id": flavorid,
            "name": name,
            "ram": ram,
            "disk": disk,
            "vcpu": vcpus,
            "ephemeral": 0,
            "swap": 0,
            "rxtx_factor": "1.0",
            "is_public": "True"
        }}
        if ephemeral:
            body["flavor"]["ephemeral"] = ephemeral
        if swap:
            body["flavor"]["swap"] = swap
        if rxtx_factor:
            body["flavor"]["rxtx_factor"] = rxtx_factor
        if service_type:
            body["flavor"]["service_type"] = service_type

        return self._create("/mgmt/flavors", body, "flavor")


@utils.arg('name', metavar='<name>', help='Name of the new flavor')
@utils.arg('ram', metavar='<ram>', help='Memory size in MB')
@utils.arg('disk', metavar='<disk>', help='Disk size in GB')
@utils.arg('vcpus', metavar='<vcpus>', help='Number of vcpus')
@utils.arg('--flavorid', metavar='<flavorid>', default="auto",
           help='Unique ID (integer or UUID) for the new flavor.')
@utils.arg('--ephemeral', metavar='<ephemeral>', default=None,
           help='Ephemeral space size in GB (default 0)')
@utils.arg('--swap', metavar='<swap>', default=None,
           help='Swap space size in MB (default 0)')
@utils.arg('--rxtx_factor', metavar='<rxtx_factor>', default=None,
           help='RX/TX factor (default 1)')
@utils.arg('--service_type', metavar='<service_type>', default=None,
           help='The service type')
@utils.service_type('database')
def do_mgmt_flavor_create(cs, args):
    """Create a new flavor"""
    ext = cs.management_flavor_python_troveclient_ext
    flavor = ext.create(args.name, args.ram, args.disk, args.vcpus,
                        args.flavorid, args.ephemeral, args.swap,
                        args.rxtx_factor, args.service_type)
    utils.print_dict(flavor)
