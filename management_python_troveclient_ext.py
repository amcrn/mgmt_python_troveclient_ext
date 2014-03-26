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
from troveclient import common
from troveclient import utils
from troveclient.v1 import instances


class RootHistory(base.Resource):
    def __repr__(self):
        return ("<Root History: Instance %s enabled at %s by %s>"
                % (self.id, self.created, self.user))


class Management(base.ManagerWithFind):
    """
    Manage :class:`Instances` resources.
    """
    resource_class = instances.Instance

    # Appease the abc gods
    def list(self):
        pass

    def show(self, instance):
        """
        Get details of one instance.

        :rtype: :class:`Instance`.
        """

        return self._get("/mgmt/instances/%s" % base.getid(instance),
                         'instance')

    def index(self, deleted=None, limit=None, marker=None):
        """
        Show an overview of all local instances.
        Optionally, filter by deleted status.

        :rtype: list of :class:`Instance`.
        """
        form = ''
        if deleted is not None:
            if deleted in ('true', 'True', '1'):
                form = "?deleted=true"
            else:
                form = "?deleted=false"

        url = "/mgmt/instances%s" % form
        return self._paginated(url, "instances", limit, marker)

    def root_enabled_history(self, instance):
        """
        Get root access history of one instance.

        """
        url = "/mgmt/instances/%s/root" % base.getid(instance)
        resp, body = self.api.client.get(url)
        if not body:
            raise Exception("Call to " + url + " did not return a body.")
        return body['root_history']

    def _action(self, instance_id, body):
        """
        Perform a server "action" -- reboot/rebuild/resize/etc.
        """
        url = "/mgmt/instances/%s/action" % instance_id
        resp, body = self.api.client.post(url, body=body)
        common.check_for_exceptions(resp, body, url)
        if body:
            return self.resource_class(self, body, loaded=True)
        return body

    def stop(self, instance_id):
        """
        Stop the database on an instance
        """
        body = {'stop': {}}
        self._action(instance_id, body)

    def reboot(self, instance_id):
        """
        Reboot the underlying OS.

        :param instance_id: The :class:`Instance` (or its ID) to share onto.
        """
        body = {'reboot': {}}
        self._action(instance_id, body)

    def migrate(self, instance_id, host=None):
        """
        Migrate the instance.

        :param instance_id: The :class:`Instance` (or its ID) to share onto.
        """
        if host:
            body = {'migrate': {'host': host}}
        else:
            body = {'migrate': {}}
        self._action(instance_id, body)

    def update(self, instance_id):
        """
        Update the guest agent via apt-get.
        """
        body = {'update': {}}
        self._action(instance_id, body)

    def reset_task_status(self, instance_id):
        """
        Set the task status to NONE.
        """
        body = {'reset-task-status': {}}
        self._action(instance_id, body)


def _print_instance(instance):
    if instance._info.get('links'):
        del(instance._info['links'])
    utils.print_dict(instance._info)


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.service_type('database')
def do_mgmt_show(cs, args):
    """Show details of an instance"""
    instance = cs.management_python_troveclient_ext.show(args.instance)
    instance._info['flavor'] = instance.flavor['id']
    if hasattr(instance, 'volume'):
        instance._info['volume'] = instance.volume['size']
        if 'id' in instance.volume:
            instance._info['volume_id'] = instance.volume['id']
        if 'used' in instance.volume:
            instance._info['volume_used'] = instance.volume['used']
        if 'status' in instance.volume:
            instance._info['volume_status'] = instance.volume['status']

    if hasattr(instance, 'ip'):
        instance._info['ip'] = ', '.join(instance.ip)
    if hasattr(instance, 'datastore'):
        instance._info['datastore'] = instance.datastore['type']
        instance._info['datastore_version'] = instance.datastore['version']
    if hasattr(instance, 'guest_status'):
        description = instance.guest_status['state_description']
        instance._info['guest_status'] = description
    _print_instance(instance)


@utils.arg('--deleted', metavar='<deleted>', default=None,
           help='Optional. Filter instances on deleted.')
@utils.service_type('database')
def do_mgmt_list(cs, args):
    """List all instances"""
    instances = cs.management_python_troveclient_ext.index(deleted=args.deleted)
    for instance in instances:
        setattr(instance, 'flavor_id', instance.flavor['id'])
        if hasattr(instance, 'volume'):
            setattr(instance, 'size', instance.volume['size'])
        if hasattr(instance, 'datastore'):
            setattr(instance, 'datastore_version',
                    instance.datastore['version'])
            setattr(instance, 'datastore', instance.datastore['type'])
    utils.print_list(instances,
                     ['id', 'name', 'tenant_id', 'flavor_id', 'size',
                      'datastore', 'datastore_version', 'status', 'created',
                      'deleted_at'])


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.service_type('database')
def do_mgmt_root_history(cs, args):
    """Get the root enabled history of an instance"""
    ext = cs.management_python_troveclient_ext
    history = ext.root_enabled_history(args.instance)
    utils.print_dict(history)


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
def do_mgmt_stop(cs, args):
    """Stop the database on an instance"""
    cs.management_python_troveclient_ext.stop(args.instance)


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
def do_mgmt_reboot(cs, args):
    """Soft reboot an instance"""
    cs.management_python_troveclient_ext.reboot(args.instance)


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.arg('--host', metavar='<host>', default=None,
           help='Optional. Name of the host.')
def do_mgmt_migrate(cs, args):
    """Migrate an instance"""
    ext = cs.management_python_troveclient_ext
    ext.migrate(args.instance, host=args.host)


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
def do_mgmt_update(cs, args):
    """Update an instance"""
    cs.management_python_troveclient_ext.update(args.instance)


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
def do_mgmt_reset_task_status(cs, args):
    """Update the task status to None for an instance"""
    cs.management_python_troveclient_ext.reset_task_status(args.instance)
