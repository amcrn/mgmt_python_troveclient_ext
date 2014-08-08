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
from troveclient import common
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

    def index(self, deleted=None, limit=None, marker=None):
        """Show an overview of all local clusters.

        Optionally, filter by deleted status.

        :rtype: list of :class:`Cluster`.
        """
        form = ''
        if deleted is not None:
            if deleted:
                form = "?deleted=true"
            else:
                form = "?deleted=false"

        url = "/mgmt/clusters%s" % form
        return self._paginated(url, "clusters", limit, marker)

    def _action(self, cluster_id, body):
        """Perform a cluster action, e.g. reset-task."""
        url = "/mgmt/clusters/%s/action" % cluster_id
        resp, body = self.api.client.post(url, body=body)
        common.check_for_exceptions(resp, body, url)

    def reset_task(self, cluster_id):
        """Reset the current cluster task to NONE."""
        body = {'reset-task': {}}
        self._action(cluster_id, body)


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
    cluster._info['task_name'] = cluster.task['name']
    cluster._info['task_description'] = cluster.task['description']
    del cluster._info['task']
    if hasattr(cluster, 'ip'):
        cluster._info['ip'] = ', '.join(cluster.ip)
    del cluster._info['instances']
    _print_cluster(cluster)


@utils.arg('--deleted', metavar='<deleted>', default=None,
           help='Optional. Filter clusters on deleted.')
@utils.service_type('database')
def do_mgmt_cluster_list(cs, args):
    """List all clusters"""
    clusters = cs.management_cluster_python_troveclient_ext.index(
        deleted=args.deleted)
    for cluster in clusters:
        if hasattr(cluster, 'datastore'):
            setattr(cluster, 'datastore_version',
                    cluster.datastore['version'])
            setattr(cluster, 'datastore', cluster.datastore['type'])
        setattr(cluster, 'task_name', cluster.task['name'])
    utils.print_list(clusters,
                     ['id', 'name', 'tenant_id',
                      'datastore', 'datastore_version', 'task_name', 'created',
                      'deleted_at'])


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
        instances, ['id', 'name', 'type', 'flavor_id', 'size'],
        obj_is_dict=True)


@utils.arg('cluster', metavar='<cluster>', help='ID of the cluster.')
@utils.service_type('database')
def do_mgmt_cluster_reset_task(cs, args):
    """Reset the current cluster task to NONE."""
    cs.management_cluster_python_troveclient_ext.reset_task(args.cluster)
