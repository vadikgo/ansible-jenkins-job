### jenkins_job

Call remote Jenkins jobs

```
- name: Call system test
  jenkins_job:
    url: http://10.116.96.95:8080/job/Test_Smoke
    token: c6ccd3fa2b06cd667b74c06aa299aa54
    params: URL=https://10.116.111.179&APP_PORT=9443&JSON_PORT=9080&TAGS=test*
```

#### options

* `url` HTTP or HTTPS in the form (http|https)://host.domain[:port]/job/JobName

* `token` Token for remote jenkins job call

* `params` Job parameters in the url's parameters form param1=val1&param2=val2

* `timeout` Time in seconds for wait successfully job execution

* `validate_certs` If *no*, SSL certificates will not be validated. This should only set to *no* used on personally controlled sites using self-signed certificates.
