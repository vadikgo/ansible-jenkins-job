### jenkins_job

Call remote Jenkins jobs

```
- name: Call system test
  jenkins_job:
    host: http://172.17.0.2:8080
    job: /job/test1
    token: token1
    username: admin
    password: 57033f8c2abc058d3b154cd79735f012
    force_basic_auth: yes
    params: URL=https://10.116.111.179&APP_PORT=9443&JSON_PORT=9080&TAGS=test*
```

#### options

* `host` - Jenkins server url in the form (http|https)://host.domain[:port]

* `job` - Jenkins job path /job/JobName

* `token` - Token for remote jenkins job call

* `params` - Job parameters in the url's parameters form param1=val1&param2=val2

* `timeout` - Time in seconds for wait successfully job execution

* `validate_certs` - If *no*, SSL certificates will not be validated. This should only set to *no* used on personally controlled sites using self-signed certificates.

* `force_basic_auth` - The library used by the uri module only sends authentication information when a webservice responds to an initial request with a 401 status. Since some basic auth services do not properly send a 401, logins will fail. This option forces the sending of the Basic authentication header upon initial request.

* `user` - username for the module to use for Digest, Basic or WSSE authentication.

* `password` - password for the module to use for Digest, Basic or WSSE authentication.
