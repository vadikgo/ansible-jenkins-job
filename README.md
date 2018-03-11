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
    token: LS30jWmkmPYF
    url: http://localhost:8080
    user: admin
```

### Build Jenkins job in folder:

```yaml
- jenkins_job:
    name: folder1/test2
    token: 1r06bg8XdSFD
    url: http://localhost:8080
    user: admin
```