# Python-Migrater - a MySQL migration tool

This script is a basic migration tool written in Python3 that allows standard migrations on a MySQL server.

## Configuration

This script requires the MySQL Connector/Python to be installed which can be found [here](https://dev.mysql.com/doc/connector-python/en/).

## Download source from Github

```sh
## clone the repository
mkdir -p /path/to/project
cd /path/to/project
git clone https://github.com/jc3m/Python-Migrater.git
```

## Usage

```sh
./migrate.py [command] [options]
```

Supported commands:
- `generate migration [migrationName]` &mdash; Create up and down migration files, provide an optional name
- `migrate` &mdash; Run migration on given server
  - You must provide server connection details specified below
- `rollback` &mdash; Rollback the server to the previous migration
  - `-v` or `--version` &mdash; If this is specified, rollback the server up to and including the specified version
  - You must provide server connection details specified below
- `version` &mdash; Get the current version your server has migrated to

### Server connection details

To run migrations or rollbacks on the server, you must provide credentials for accessing your database. There are two ways to do this, the first being adding command line arguments.

```sh
./migrate.py migrate -host 127.0.0.1 -u username -p password -db test
```

Alternatively, you can create a config.py file that has a dictionary named mysql

```python
mysql = {
  "host": "localhost",
  "user": "username",
  "password": "password",
  "database": "test"
}
```
