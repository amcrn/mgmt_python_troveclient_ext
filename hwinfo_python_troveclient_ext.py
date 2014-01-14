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


class HwInfo(base.Resource):

    def __repr__(self):
        return "<HwInfo: %s>" % self.version


class HwInfoInterrogator(base.ManagerWithFind):
    """
    Manager class for HwInfo
    """
    resource_class = HwInfo

    def get(self, instance):
        """
        Get the hardware information of an instance.
        """
        return self._get("/mgmt/instances/%s/hwinfo" % base.getid(instance))

    # Appease the abc gods
    def list(self):
        pass


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.service_type('database')
def do_mgmt_hwinfo_show(cs, args):
    """Get the hardware information of an instance"""
    hosts = cs.hwinfo_python_troveclient_ext.get(args.instance)
    utils.print_dict(hosts)
