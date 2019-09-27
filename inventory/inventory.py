#!/usr/bin/env python
from __future__ import print_function

"""
#!/usr/bin/env python3
#!/usr/bin/env python2
#!/usr/bin/env python
"""

'''
Ansible dynamic inventory script

see: http://allandenot.com/devops/2015/01/16/ansible-with-multiple-inventory-files.html
see: https://www.jeffgeerling.com/blog/creating-custom-dynamic-inventories-ansible
see: https://docs.ansible.com/ansible/2.5/dev_guide/developing_inventory.html

ansible-playbook -i inventory docker_login.yml
ansible-playbook -i inventory --limit "infra-bj-dev" docker_login.yml
ansible all -i inventory -m ping
ansible all -i inventory/inventory.py -m ping
'''

import os
import re
import sys
import argparse

try:
    import json
except ImportError:
    import simplejson as json


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


def properties(properties_file):
    pattern_comment = re.compile("^[ ]*#.+$")
    # In python2 `line.strip().split('=', maxsplit=1)` got TypeError: split() takes no keyword arguments
    properties_list = [line.strip().split('=', 1) for line in open(properties_file)
                                   if line.strip() and not pattern_comment.match(line)]
    #eprint("properties_list:", properties_list)
    return {key: value for key, value in properties_list}


class DynamicInventory(object):

    def __init__(self):
        self.inventory = {}
        self.read_cli_args()

        # Called with `--list`.
        if self.args.list:
            self.inventory = self.dynamic_inventory()
        # Called with `--host [hostname]`.
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            self.inventory = self.empty_inventory()
        # If no groups or vars are present, return an empty inventory.
        else:
            self.inventory = self.empty_inventory()

        print(json.dumps(self.inventory));

    def environment_dict(self, environment_dir):
        # eprint("environment_dir:", environment_dir)

        environment_dir_parts = environment_dir.split(os.path.sep)
        # eprint("parts:", environment_dir_parts)

        environment_name = environment_dir_parts[len(environment_dir_parts) - 1]
        # eprint("environment:", environment_name)

        environment_properties_file = os.path.join(environment_dir, "environment.properties")
        # eprint("environment_properties_file:", environment_properties_file)
        environment_properties = properties(environment_properties_file)
        # eprint("environment_properties:", environment_properties)

        # see: https://stackoverflow.com/questions/3964681/find-all-files-in-a-directory-with-extension-txt-in-python
        hosts = []
        for root, dirs, files in os.walk(environment_dir):
            for file in files:
                if os.path.basename(file) == "host.properties":
                    # eprint(os.path.join(root, file))
                    host_dir = os.path.dirname(os.path.join(root, file))
                    host = remove_prefix(host_dir, environment_dir + "/")
                    host_properties_file = os.path.join(host_dir, "host.properties")
                    host_properties = properties(host_properties_file)
                    host_properties['ansible_ssh_host'] = host
                    hosts.append({'host': host, 'vars': host_properties})
                    # eprint("host:", host, ", host_dir:", host_dir, ", host_properties:", host_properties)

        return {'environment': environment_name, 'vars': environment_properties, 'hosts': hosts}

    # Dynamic inventory.
    def dynamic_inventory(self):
        # eprint("args.list:", self.args.list, "args.host:", self.args.host)

        # see: https://stackoverflow.com/questions/3220755/how-to-find-the-target-files-fullabsolute-path-of-the-symbolic-link-or-soft-l
        # see: https://stackoverflow.com/questions/7116889/python-file-attribute-absolute-or-relative
        inventory_py = os.path.splitdrive(os.path.realpath(__file__))[1]
        # eprint("inventory_py:", inventory_py)
        inventory_dir = os.path.dirname(inventory_py)
        # eprint("inventory_dir:", inventory_dir)

        # inventory_parent_dir = os.path.dirname(inventory_dir)
        inventory_parent_dir = os.path.abspath(os.path.join(inventory_dir, os.pardir))
        # eprint("inventory_parent_dir:", inventory_parent_dir)

        environments = []
        for root, dirs, files in os.walk(inventory_parent_dir):
            for file in files:
                if os.path.basename(file) == "environment.properties":
                    environment_dir = os.path.dirname(os.path.join(root, file))
                    # eprint("environment_dir:", environment_dir)
                    environment = self.environment_dict(environment_dir)
                    environments.append(environment)

        inventory = {'_meta': {'hostvars': {}, 'all': {'children': []}}}
        for environment in environments:
            environment_hosts = environment['hosts']
            if self.args.host:
                environment_hosts = [host for host in environment_hosts if host['host'] == self.args.host]

            # group
            group = environment['environment']
            group_hosts = [host['host'] for host in environment_hosts]
            group_vars = environment['vars']

            if environment_hosts:
                inventory[group] = {'hosts': group_hosts, 'vars': group_vars}
                # all children
                inventory['_meta']['all']['children'].append(group)

            # meta hostvars
            for host in environment_hosts:
                inventory['_meta']['hostvars'][host['host']] = host['vars']

        # ungrouped
        inventory['_meta']['all']['children'].append('ungrouped')
        inventory['_meta']['ungrouped'] = {}

        return inventory

    # Empty inventory.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}, 'all': {'children': []}}}

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action='store_true')
        parser.add_argument('--host', action='store')
        self.args = parser.parse_args()

# Get the inventory.
DynamicInventory()
