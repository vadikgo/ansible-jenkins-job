#!/usr/bin/python
#
# Copyright: (c) Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
author: Vladislav Gorbunov
module: jenkins_run_script
short_description: Executes a groovy script in the jenkins instance
version_added: '2.5'
description:
    - The C(jenkins_run_script) module takes a script plus a dict of values
      to use within the script and returns the result of the script being run.
requirements:
  - "python-jenkins >= 0.4.12"
options:
  script:
    description:
      - The groovy script to be executed.
        This gets passed as a string Template if args is defined.
    required: true
    default: null
  url:
    description:
      - The jenkins server to execute the script against. The default is a local
        jenkins instance that is not being proxied through a webserver.
    required: false
    default: http://localhost:8080
  validate_certs:
    description:
      - If set to C(no), the SSL certificates will not be validated.
        This should only set to C(no) used on personally controlled sites
        using self-signed certificates as it avoids verifying the source site.
    required: false
    default: True
  user:
    description:
      - The username to connect to the jenkins server with.
    required: false
    default: null
  password:
    description:
      - The password to connect to the jenkins server with.
    required: false
    default: null
  timeout:
    description:
      - The request timeout in seconds
    required: false
    default: 10
  args:
    description:
      - A dict of key-value pairs used in formatting the script using string. Template (see https://docs.python.org/2/library/string.html#template-strings). It's better to use ansible 'template' lookup for script parameter.
    required: false
    default: null
notes:
    - Since the script can do anything this does not report on changes.
      Knowing the script is being run it's important to set changed_when
      for the ansible output to be clear on any alterations made.
'''

EXAMPLES = '''
- name: Obtaining a list of plugins
  jenkins_run_script:
    script: 'println(Jenkins.instance.pluginManager.plugins)'
    user: admin
    password: admin
- name: Setting master using a variable to hold a more complicate script
  vars:
    setmaster_mode: |
        import jenkins.model.*
        instance = Jenkins.getInstance()
        instance.setMode(${jenkins_mode})
        instance.save()
- name: use the variable as the script
  jenkins_run_script:
    script: "{{ setmaster_mode }}"
    args:
      jenkins_mode: Node.Mode.EXCLUSIVE
- name: interacting with an untrusted HTTPS connection
  jenkins_run_script:
    script: "println(Jenkins.instance.pluginManager.plugins)"
    user: admin
    password: admin
    url: https://localhost
    validate_certs: no
'''

RETURN = '''
output:
    description: Result of script
    returned: success
    type: string
    sample: 'Result: true'
'''


import traceback
import time
import uuid

try:
    import jenkins
    python_jenkins_installed = True
except ImportError:
    python_jenkins_installed = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native


class JenkinsScript:

    def __init__(self, module):
        self.module = module

        self.script = module.params.get('script')
        self.url = module.params.get('url')
        self.validate_certs = module.params.get('validate_certs')
        self.user = module.params.get('user')
        self.password = module.params.get('password')
        self.token = module.params.get('token')
        self.timeout = module.params.get('timeout')
        self.args = module.params.get('args')

        self.server = self.get_jenkins_connection()

        self.result = {
            'output': {}
        }

    def get_jenkins_connection(self):
        try:
            if (self.user and self.password):
                return jenkins.Jenkins(self.url, self.user, self.password, self.timeout)
            elif (self.user and self.token):
                return jenkins.Jenkins(self.url, self.user, self.token, self.timeout)
            elif (self.user and not (self.password or self.token)):
                return jenkins.Jenkins(self.url, self.user, timeout=self.timeout)
            else:
                return jenkins.Jenkins(self.url, timeout=self.timeout)
        except Exception as e:
            self.module.fail_json(msg='Unable to connect to Jenkins server, %s' % to_native(e), exception=traceback.format_exc())

    def run_script(self):
        result = self.result
        if self.args is not None:
            from string import Template
            script_contents = Template(self.script).substitute(self.args)
        else:
            script_contents = self.script
        if not self.module.check_mode:
            try:
                result['output'] = self.server.run_script(script_contents)
                if 'Exception:' in result['output'] and 'at java.lang.Thread' in result['output']:
                    self.module.fail_json(msg="script failed with stacktrace:\n " + result['output'])
            except Exception as e:
                self.module.fail_json(msg='Fail to run script, %s'% to_native(e), exception=traceback.format_exc())
        return result

def test_dependencies(module):
    if not python_jenkins_installed:
        module.fail_json(msg="python-jenkins required for this module. "
                         "see http://python-jenkins.readthedocs.io/en/latest/install.html")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            script=dict(required=True, type="str"),
            url=dict(required=False, type="str", default="http://localhost:8080"),
            validate_certs=dict(required=False, type="bool", default=True),
            user=dict(required=False, type="str", default=None),
            password=dict(required=False, no_log=True, type="str", default=None),
            token=dict(required=False, no_log=True),
            timeout=dict(required=False, type="int", default=10),
            args=dict(required=False, type="dict", default=None)
        ),
        mutually_exclusive=[
            ['password', 'token'],
        ],
        supports_check_mode=True,
    )

    test_dependencies(module)
    jenkins_script = JenkinsScript(module)

    result = jenkins_script.run_script()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
