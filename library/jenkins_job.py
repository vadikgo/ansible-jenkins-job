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
    timeout:
        description:
            - Time in seconds for wait successfully job execution
        required: false
        default: 600
    force_basic_auth:
        description:
          - The library used by the uri module only sends authentication information when a webservice
            responds to an initial request with a 401 status. Since some basic auth services do not properly
            send a 401, logins will fail. This option forces the sending of the Basic authentication header
            upon initial request.
            required: false
        choices: [ "yes", "no" ]
        default: "no"
    user:
        description:
            - username for the module to use for Digest, Basic or WSSE authentication.
        required: false
        default: null
    password:
        description:
            - password for the module to use for Digest, Basic or WSSE authentication.
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
  jenkins_job:
    host: http://172.17.0.2:8080
    job: /job/test1
    token: token1
    username: admin
    password: 57033f8c2abc058d3b154cd79735f012
    force_basic_auth: yes
    params: URL=https://10.116.111.179&APP_PORT=9443&JSON_PORT=9080&TAGS=test*
'''

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host = dict(required=True),
            job = dict(required=True),
            token = dict(required=True),
            params = dict(required=False, default=None),
            timeout = dict(required=False, default=600),
            force_basic_auth = dict(required=False, default=False),
            username = dict(required=False, default=None),
            password = dict(required=False, default=None),
            validate_certs = dict(required=False, default=True)
        )
    )

    host = module.params["host"]
    job = module.params["job"]
    url = urlparse.urljoin(host, job)
    token = module.params["token"]
    params = module.params["params"]
    timeout = module.params["timeout"]
    validate_certs = module.params["validate_certs"]
    force_basic_auth = module.params["force_basic_auth"]
    username = module.params["username"]
    password = module.params["password"]

    nextBuildNumber = json.load(\
                open_url("{0}/api/json?token={1}&tree=nextBuildNumber".\
                format(url, token), validate_certs=validate_certs, url_username=username,\
                url_password=password, force_basic_auth=force_basic_auth))['nextBuildNumber']

    # Jenkins CSRF Protection
    crumb = json.load(open_url(urlparse.urljoin(host, "/crumbIssuer/api/json"),\
                    validate_certs=validate_certs, url_username=username,\
                    url_password=password, force_basic_auth=force_basic_auth))
    token = token + "&" + crumb['crumbRequestField'] + "=" + crumb['crumb']

    if params in ["", None]:
        jobUrl = "{0}/build?token={1}".format(url, token)
    else:
        jobUrl = "{0}/buildWithParameters?token={1}&{2}".format(url, token, params)

    code = open_url(jobUrl, method='POST', validate_certs=validate_certs, url_username=username,\
                    url_password=password, force_basic_auth=force_basic_auth).getcode()
    if code not in [200, 201]:
        module.fail_json(
            msg="Jenkins job url {0} execute failed with HTTP code {1}".format(jobUrl, code)
        )

    for i in range(int(timeout)/10):
        lastCompletedBuild = json.load(open_url("{0}/api/json?token={1}".format(url, token),\
            validate_certs=validate_certs, url_username=username, url_password=password,\
            force_basic_auth=force_basic_auth))
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
