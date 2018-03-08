## Build Jenkins jobs by using Jenkins REST API

### Requirements

python-jenkins >= 0.4.12

### Build job from shell:

```bash
ansible localhost -m jenkins_build -a "name='test' user='admin' password='admin' url='http://localhost:32769'" -M ./library
```

### Build Jenkins job from task:

```yaml
- jenkins_job:
    params:
        'param1': 'test value 1'
        'param2': 'test value 2'
    name: test
    token: asdfasfasfasdfasdfadfasfasdfasdfc
    url: http://localhost:8080
    user: admin
```

###  Build a jenkins job anonymously with job remote build token

```yaml
- jenkins_job:
    name: test
    url: http://localhost:8080
    build_token: token_eDahX3ve
```

### Parameters

* params - Dictionary with job parameters

* name - Name of the Jenkins job

* password - Password to authenticate with the Jenkins server

* token - API token used to authenticate alternatively to password

* url - Url where the Jenkins server is accessible

* user - User to authenticate with the Jenkins server

* wait_build - Wait last build to complete

* wait_build_timeout - Wait last build timeout, sec

* build_token - Token for building job

## remote_jenkins_job

### Call remote Jenkins jobs from shell:

```bash
ansible localhost -m remote_jenkins_job -a "host=https://jenkins.example.com/jenkins \
job=/job/TEST/job/mytest2/ token=lalalala params='param1=lala' username=jenkins-username \
password=b0b522504bdf38ddae22169220dc08d0 validate_certs=False"
```

### Call remote Jenkins jobs from task:

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

### Parameters

* `host` - Jenkins server url in the form (http|https)://host.domain[:port]/site_root

* `job` - Jenkins job path /job/JobName

* `token` - Token for remote jenkins job call

* `params` - Job parameters in the url's parameters form param1=val1&param2=val2

* `span` -  Time in seconds for wait between job status checking, default 10 sec

* `retry` - Count of job status checking retries, default 30

* `validate_certs` - If *no*, SSL certificates will not be validated. This should only set to *no* used on personally controlled sites using self-signed certificates.

* `user` - User name.

* `password` - User's password or jenkins's password hash.
