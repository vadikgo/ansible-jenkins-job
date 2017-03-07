#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

DOCUMENTATION = '''
---
module: remote_jenkins_job
short_description: Call remote Jenkins job
description:
    - Call remote jenkins job
options:
    host:
        description:
            - Jenkins server url in the form (http|https)://host.domain[:port]
        required: true
        default: null
    job:
        description:
            - Jenkins job path /job/JobName
        required: true
        default: null
    token:
        description:
            - Token for remote jenkins job call
        required: true
        default: null
    params:
        description:
            - Job parameters in the url's parameters form param1=val1&param2=val2
            - May be "" or null
        required: false
        default: null
    span:
        description:
            - Time in seconds for wait between job status checking
        required: false
        default: 10
    retry:
        description:
            - Count of job status checking retries
        required: false
        default: 30
    user:
        description:
            - User name
        required: false
        default: null
    password:
        description:
            - User password.
        required: false
        default: null
    validate_certs:
        description:
          - If C(no), SSL certificates will not be validated.  This should only
            set to C(no) used on personally controlled sites using self-signed
            certificates.
        required: false
        default: 'yes'
        choices: ['yes', 'no']
'''
EXAMPLES = '''
- name: Call system test
  remote_jenkins_job:
    host: http://172.17.0.2:8080
    job: /job/test1
    token: token1
    username: admin
    password: 57033f8c2abc058d3b154cd79735f012
    params: URL=https://10.116.111.179&APP_PORT=9443&JSON_PORT=9080&TAGS=test*
'''

urljoin = lambda urls: '/'.join([p.strip('/') for p in urls])

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host = dict(required=True),
            job = dict(required=True),
            token = dict(required=True),
            params = dict(required=False, default=None),
            span = dict(required=False, default=10, type='int'),
            retry = dict(required=False, default=30, type='int'),
            username = dict(required=False, default=None),
            password = dict(required=False, default=None),
            validate_certs = dict(required=False, default=True, type='bool')
        ),
        supports_check_mode=True
    )

    host = module.params["host"]
    job = module.params["job"]
    url = urljoin([host, job])
    token = module.params["token"]
    params = module.params["params"]
    span = module.params["span"]
    retry = module.params["retry"]
    validate_certs = module.params["validate_certs"]
    username = module.params["username"]
    password = module.params["password"]

    # Jenkins CSRF Protection
    r = requests.get(urljoin([host, "/crumbIssuer/api/json"]), auth=(username, password), verify=validate_certs)

    if r.status_code in [401, 403]:
        module.fail_json(changed=True, msg="Access denied with http status code %i" % r.status_code)

    if r.status_code != 404:
        crumb = r.json()
        token = token + "&" + crumb['crumbRequestField'] + "=" + crumb['crumb']

    r = requests.get("{0}?token={1}&tree=nextBuildNumber".format(urljoin([url, '/api/json']), token),
                            auth=(username, password), verify=validate_certs)

    if r.status_code != 200:
        module.fail_json(changed=True, msg="Job status failed with http status code %i" % r.status_code)

    nextBuildNumber = r.json()['nextBuildNumber']

    if params in ["", None]:
        jobUrl = "{0}?token={1}".format(urljoin([url, '/build']), token)
    else:
        jobUrl = "{0}?token={1}&{2}".format(urljoin([url, '/buildWithParameters']), token, params)

    if module.check_mode:
        module.exit_json(changed=True, msg="open url: {0}".format(jobUrl))

    code = requests.post(jobUrl, auth=(username, password), verify=validate_certs).status_code
    if code not in [200, 201]:
        module.fail_json(
            msg="Jenkins job url {0} execute failed with HTTP code {1}".format(jobUrl, code)
        )

    for i in range(retry):
        lastCompletedBuild = requests.get("{0}?token={1}".format(urljoin([url, '/api/json']), token),
            auth=(username, password), verify=validate_certs).json()
        if lastCompletedBuild['lastCompletedBuild']['number'] == nextBuildNumber:
            if lastCompletedBuild['lastSuccessfulBuild']['number'] == nextBuildNumber:
                module.exit_json(
                    changed=True,
                    msg="Jenkins job executed successfully: {0}".format(lastCompletedBuild['lastCompletedBuild']['url'])
                )
            else:
                module.fail_json(
                    msg="Jenkins job execute failed: {0}".format(lastCompletedBuild['lastCompletedBuild']['url'])
                )
        time.sleep(span)

    module.fail_json(
        msg="Jenkins job wait timeout: {0}".format(url)
    )

from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
if __name__ == "__main__":
    main()
