# Database

The central database tracks the identification and patching of vulnerabilities as well as track the success of exploit scripts. Three tables are created: Service, Vuln, and Exploit. Each service has potentially many vulnerabilities, and each vulnerability and service have potentially many exploits, in many-to-one relationships.

## Entity Relationship Diagram for CLAMP DB

```mermaid
erDiagram
  SERVICE ||--o{ EXPLOIT : attacked_by
  SERVICE ||--o{ VULNERABILITY : has
  SERVICE {
    int id
    string name
    int port
  }
  VULNERABILITY {
    int id
    bool benign
    bool patched
    string sequence
    int service
  }
  EXPLOIT ||--o{ VULNERABILITY: exploits
  EXPLOIT {
    int id
    string path
    int flagCountRound
    int flagCountCumulative
    int vuln
    int service
  }
``` 

## Files

- The inital schema design was created using the standard SQL Data Definition Language. See [db_schema.ddl](db_schema.ddl).
- The [models.py](../models.py) file (in the root dir) defines and initializes a `sqlite3` database using the `sqlalchemy` ORM.
- The actual SQLite3 database is in the [pctf.db](pctf.db) file.
- Unit tests for the models can be found in the [tests.py](../tests.py) file (in the root dir).

### Usage

Using the methods provided by the ORM, we could add to the database and query it without writing SQL code. To query the database, for example,

```python
engine = models.get_db_engine()
Session = models.get_db_session(engine)
Exploit = models.Exploit
with Session() as session:
  with session.begin():
    query = session.query(Exploit.query.filter(
      Exploit.path == exploit_path)
```

And to add to the database, for example,

```python
engine = models.get_db_engine()
Session = models.get_db_session(engine)
Exploit = models.Exploit
with Session() as session:
  with session.begin():
    if not session.query(Exploit.query.filter(
      Exploit.path == exploit_path).exists()
      ).scalar():

      new_exploit = Exploit(
        path = exploit_path,
        service_id = exploit_obj.service.id)
      session.add(new_exploit)
``` 