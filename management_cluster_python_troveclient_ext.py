# Copyright 2014 eBay Software Foundation
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
from troveclient.v1 import clusters


class MgmtClusters(base.ManagerWithFind):
    """Manage :class:`Cluster` resources."""
    resource_class = clusters.Cluster

    # Appease the abc gods
    def list(self):
        pass

    def show(self, cluster):
        """Get details of one cluster."""
        return self._get("/mgmt/clusters/%s" % base.getid(cluster), 'cluster')


def _print_cluster(cluster):
    if cluster._info.get('links'):
        del(cluster._info['links'])
    utils.print_dict(cluster._info)


@utils.arg('cluster', metavar='<cluster>', help='ID of the cluster.')
@utils.service_type('database')
def do_mgmt_cluster_show(cs, args):
    """Show details of a cluster."""
    cluster = cs.management_cluster_python_troveclient_ext.show(args.cluster)
    cluster._info['datastore'] = cluster.datastore['type']
    cluster._info['datastore_version'] = cluster.datastore['version']
    if hasattr(cluster, 'ip'):
        cluster._info['ip'] = ', '.join(cluster.ip)
    del cluster._info['instances']
    _print_cluster(cluster)


@utils.arg('cluster', metavar='<cluster>', help='ID of the cluster.')
@utils.service_type('database')
def do_mgmt_cluster_instances(cs, args):
    """Lists all instances of a cluster."""
    cluster = cs.management_cluster_python_troveclient_ext.show(args.cluster)
    instances = cluster._info['instances']
    for instance in instances:
        instance['flavor_id'] = instance['flavor']['id']
        if instance.get('volume'):
            instance['size'] = instance['volume']['size']
    utils.print_list(
        instances, ['id', 'name', 'flavor_id', 'size'],
        obj_is_dict=True)
