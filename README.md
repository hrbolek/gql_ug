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


### graphQL description rules

Výstup přepisu je vždy v jedné sekci, kód se nedělí

Níže je souhrn pravidel, pro generování description u GraphQL modelů:

#### Dvojjazyčné popisy:

Každý description musí obsahovat anglickou a českou verzi.
Tyto verze by měly být uvedeny na samostatných řádcích (např. první řádek anglicky, druhý řádek česky).
Neuvádět prefixy pro tyto popisy.

#### Strukturované dokumentace pomocí Markdown:

U typů, dotazů i mutací použij strukturovaný popis s oddělenými sekcemi, například:
Description: Stručný popis účelu daného typu nebo operace.
Details: Podrobnější informace o fungování, významu či specifikách.
Permissions: Informace o tom, kdo a za jakých podmínek má oprávnění operaci provádět.

Doplň detaily kde můžeš

#### Konzistence a šablonovitost:

Veškeré popisy by měly být konzistentní napříč celým API. To znamená použití jednotné šablony (např. vždy se sekcemi Description, Details a Permissions tam, kde je to relevantní).

příklad
```md
## Description
Group is an entity with members.  
Skupina je entita se členy.

## Details
- It can have a master group; only one master group is allowed.  
  Může mít nadřazenou skupinu; je povolena pouze jedna nadřazená skupina.
- Groups are organized in a hierarchical tree structure.  
  Skupiny jsou organizovány ve stromové hierarchii.
- Roles can be defined on the group to control permissions and access.  
  Na skupině lze definovat role, které ovlivňují oprávnění a přístup.

## Business Rules
- A group may have only one master group.  
  Skupina může mít pouze jednu nadřazenou skupinu.
- The hierarchy must be consistent.  
  Hierarchie musí být udržována konzistentně.
```

U jednotlivých polí je vhodné uvádět stručný popis s oddělením anglické a české verze (na samostatných řádcích).

U volitelných polí pro třídy popisující vstupní graphql typy zabezpeč tvar 

```python
parameter: Optional[] = strawberry.field(description, default=None) 
```

s parametrem default=None (případně default="" u textových polí) a popis je uveden.

U povinných polí pro třídy popisující vstupní graphql typy zabezpeč tvar 

```python
parameter: Optional[] = strawberry.field(description) 
```

U polí označených jako strawberry.Private se do SDL neintegruje description ani volání strawberry.field – jsou definována pouze jako anotovaná pole s výchozí hodnotou.
Specifické požadavky pro dotazy a mutace:

U dotazů (queries) a mutací se do popisu přidává také sekce Permissions, která uvádí, kdo má oprávnění danou operaci vykonat.
Například u mutací se doplňuje informace o tom, že pouze autentizovaní uživatelé s příslušnými RBAC oprávněními mohou operaci provést.
Tato pravidla slouží k tomu, aby výsledná dokumentace (například v GraphiQL) byla bohatá, přehledná a konzistentní, což usnadňuje porozumění API jak vývojářům, tak i business analytikům.