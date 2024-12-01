## Execution

### Basic functional tests
```bash
pytest --cov-report term-missing --cov=src tests --log-cli-level=INFO -x
```

### Tests for integration
```bash
pytest tests/test_integration --log-cli-level=INFO -x
```

```bash
uvicorn main:app --env-file environment.txt --port 8001 --reload
```

```bash
docker build --no-cache -t hrbolek/gql_ug:latest .
```

```gql
query {
	userPage(where: {fullname: {_ilike: "%newbie%"}}, orderby: "email", desc: true) {
    id
    name
    email
    surname
  }
}
```

```gql
{
  userPage {
    id
    email
    lastchange
    created
    createdby {
      id
    }
    name
    createdbyId
    firstname
    fullname
    givenname
    isThisMe
    middlename
    surname
    valid
    changedby {
      id
    }
    rbacobjectId
    rbacobject {
      id
    }
  }
}
```

## Environment variables

### DB related variables
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=example
- POSTGRES_HOST=postgres:5432
- POSTGRES_DB=data

### Authorization related variables
- JWTPUBLICKEYURL=http://localhost:8000/oauth/publickey
- JWTRESOLVEUSERPATHURL=http://localhost:8000/oauth/userinfo
- ROLELISTURL=http://localhost:8088/gql/
- RBACURL=http://localhost:8088/gql

## Syslog related variables
- SYSLOGHOST=host.docker.internal:514

### 
- DEMO=true
