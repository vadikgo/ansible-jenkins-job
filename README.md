### remote_jenkins_job

Call remote Jenkins jobs from shell:

```bash
ansible localhost -m remote_jenkins_job -a "host=https://jenkins.example.com/jenkins \
job=/job/TEST/job/mytest2/ token=lalalala params='param1=lala' username=jenkins-username \
password=b0b522504bdf38ddae22169220dc08d0 validate_certs=False"
```

Call remote Jenkins jobs from task:

```yaml
- name: Call system test
  remote_jenkins_job:
    host: http://172.17.0.2:8080
    job: /job/test1
    token: token1
    username: admin
    password: 57033f8c2abc058d3b154cd79735f012
    params: URL=https://10.116.111.179&APP_PORT=9443&JSON_PORT=9080&TAGS=test*
```

#### options

* `host` - Jenkins server url in the form (http|https)://host.domain[:port]/site_root

* `job` - Jenkins job path /job/JobName

* `token` - Token for remote jenkins job call

* `params` - Job parameters in the url's parameters form param1=val1&param2=val2

* `span` -  Time in seconds for wait between job status checking, default 10 sec

* `retry` - Count of job status checking retries, default 30

* `validate_certs` - If *no*, SSL certificates will not be validated. This should only set to *no* used on personally controlled sites using self-signed certificates.

* `user` - User name.

* `password` - User's password or jenkins's password hash.
