#!/usr/bin/python
# -*- coding: utf-8 -*-
import time

try:
    import json
except ImportError:
    import simplejson as json

DOCUMENTATION = '''
---
module: jenkins_job
short_description: Call remote Jenkins job
description:
    - Call remote jenkins job
options:
    url:
        description:
            - HTTP or HTTPS in the form (http|https)://host.domain[:port]/job/JobName
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
        required: false
        default: ""
    timeout:
        description:
            - Time in seconds for wait successfully job execution
        required: false
        default: 600
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
  jenkins_job:
    url: http://10.116.96.95:8080/job/EFS_VRVR_Smoke
    token: c6ccd3fa2b06cd667b74c06aa299aa54
    params: URL=https://10.116.111.179&APP_PORT=9443&JSON_PORT=9080&TAGS=test*
'''

def main():
    module = AnsibleModule(
        argument_spec=dict(
            url=dict(required=True),
            token=dict(required=True),
            params=dict(required=False, default=""),
            timeout=dict(required=False, default=600),
            validate_certs=dict(required=False, default=True)
        )
    )

    params = module.params["params"]
    url = module.params["url"]
    token = module.params["token"]
    timeout = module.params["timeout"]
    validate_certs = module.params["validate_certs"]

    nextBuildNumber = json.load(\
                open_url("{0}/api/json?token={1}/&tree=nextBuildNumber".\
                format(url, token), validate_certs=validate_certs))['nextBuildNumber']

    if params == "":
        jobUrl = "{0}/build?token={1}".format(url, token)
    else:
        jobUrl = "{0}/buildWithParameters?token={1}&{2}".format(url, token, params)

    code = open_url(jobUrl, method='POST', validate_certs=validate_certs).getcode()
    if code not in [200, 201]:
        module.fail_json(
            msg="Jenkins job url {0} execute failed with HTTP code {1}".format(jobUrl, code)
        )

    for i in range(int(timeout)/10):
        lastCompletedBuild = json.load(open_url("{0}/api/json?token={1}".format(url, token), validate_certs=validate_certs))
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
        time.sleep(10)

    module.fail_json(
        msg="Jenkins job wait timeout: {0}".format(url)
    )

from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
if __name__ == "__main__":
    main()
