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
module: jenkins_build
short_description: Build jenkins jobs
description:
    - Build Jenkins jobs by using Jenkins REST API.
requirements:
  - "python-jenkins >= 0.4.12"
version_added: "2.2"
author: "Vladislav Gorbunov (@vadikso), Sergio Millan Rodriguez (@sermilrod)"
options:
  params:
    description:
      - Dictionary with job parameters.
    required: false
  name:
    description:
      - Name of the Jenkins job.
    required: true
  password:
    description:
      - Password to authenticate with the Jenkins server.
    required: false
  token:
    description:
      - API token used to authenticate alternatively to password.
    required: false
  url:
    description:
      - Url where the Jenkins server is accessible.
    required: false
    default: http://localhost:8080
  user:
    description:
       - User to authenticate with the Jenkins server.
    required: false
  wait_build:
    descripton:
      - Wait last build to complete
    required: false
    default: true
  wait_build_timeout:
    descripton:
      - Wait last build timeout, sec
    required: false
    default: 600
'''

EXAMPLES = '''
# Build a parameterized job using basic authentication
- jenkins_job:
    params:
        'param1': 'test value 1'
        'param2': 'test value 2'
    name: test
    password: admin
    url: http://localhost:8080
    user: admin

# Build a parameterized job using the token
- jenkins_job:
    params:
        'param1': 'test value 1'
        'param2': 'test value 2'
    name: test
    token: asdfasfasfasdfasdfadfasfasdfasdfc
    url: http://localhost:8080
    user: admin

# Build a jenkins job using basic authentication
- jenkins_job:
    name: test
    password: admin
    url: http://localhost:8080
    user: admin

# Build a jenkins job using basic authentication, don't wait job end
- jenkins_job:
    name: test
    password: admin
    url: http://localhost:8080
    user: admin
    wait_build: false
'''

RETURN = '''
---
build_info:
  description: Jenkins job build info.
  returned: success
  type: dict
  sample: {u'building': False, u'queueId': 3, u'displayName': u'#2', u'description': None, u'changeSets': [], u'artifacts': [], u'timestamp': 1520431274718, u'previousBuild': {u'url': u'http://localhost:32769/job/test/1/', u'number': 1}, u'number': 2, u'id': u'2', u'keepLog': False, u'url': u'http://localhost:32769/job/test/2/', u'result': u'SUCCESS', u'executor': None, u'duration': 172, u'_class': u'org.jenkinsci.plugins.workflow.job.WorkflowRun', u'nextBuild': None, u'fullDisplayName': u'test #2', u'estimatedDuration': 905}
'''

import traceback
import time

try:
    import jenkins
    python_jenkins_installed = True
except ImportError:
    python_jenkins_installed = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native


class JenkinsJob:

    def __init__(self, module):
        self.module = module

        self.params = module.params.get('params')
        self.name = module.params.get('name')
        self.password = module.params.get('password')
        self.token = module.params.get('token')
        self.user = module.params.get('user')
        self.jenkins_url = module.params.get('url')
        self.server = self.get_jenkins_connection()
        self.wait_build = module.params.get('wait_build')
        self.wait_build_timeout = module.params.get('wait_build_timeout')

        self.result = {
            'build_info': {}
        }

    def get_jenkins_connection(self):
        try:
            if (self.user and self.password):
                return jenkins.Jenkins(self.jenkins_url, self.user, self.password)
            elif (self.user and self.token):
                return jenkins.Jenkins(self.jenkins_url, self.user, self.token)
            elif (self.user and not (self.password or self.token)):
                return jenkins.Jenkins(self.jenkins_url, self.user)
            else:
                return jenkins.Jenkins(self.jenkins_url)
        except Exception as e:
            self.module.fail_json(msg='Unable to connect to Jenkins server, %s' % to_native(e), exception=traceback.format_exc())

    def job_exists(self):
        try:
            return bool(self.server.job_exists(self.name))
        except Exception as e:
            self.module.fail_json(msg='Unable to validate if job exists, %s for %s' % (to_native(e), self.jenkins_url),
                                  exception=traceback.format_exc())

    def wait_job_build(self):
        for _ in range(1, self.wait_build_timeout):
            if self.server.get_job_info(self.name)['lastBuild']['number'] == \
                self.server.get_job_info(self.name)['lastCompletedBuild']['number']:
                return self.server.get_job_info(self.name)['lastBuild']['number']
            else:
                time.sleep(1)
        self.module.fail_json(msg='Job build complete timeout exceed, %s for %s' % (self.name,
                              self.jenkins_url),
                              exception=traceback.format_exc())       

    def build_job(self):
        result = self.result
        if self.job_exists():
            self.server.build_job(self.name, self.params)
            if self.wait_build:
                last_build_number = self.wait_job_build()
            else:
                last_build_number = self.server.get_job_info(self.name)['lastBuild']['number']
            result['build_info'] = self.server.get_build_info(self.name, last_build_number)
            del result['build_info']['actions']
        return result

def test_dependencies(module):
    if not python_jenkins_installed:
        module.fail_json(msg="python-jenkins required for this module. "
                         "see http://python-jenkins.readthedocs.io/en/latest/install.html")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            params=dict(required=False, default=None, type='dict'),
            name=dict(required=True),
            password=dict(required=False, no_log=True),
            token=dict(required=False, no_log=True),
            url=dict(required=False, default="http://localhost:8080"),
            user=dict(required=False),
            wait_build=dict(required=False, default=True, type='bool'),
            wait_build_timeout=dict(required=False, default=600, type='int')
        ),
        mutually_exclusive=[
            ['password', 'token'],
        ],
        supports_check_mode=True,
    )

    test_dependencies(module)
    jenkins_job = JenkinsJob(module)

    result = jenkins_job.build_job()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
