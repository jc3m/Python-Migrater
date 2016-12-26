#!/usr/bin/python3

import argparse
import os
import sys
import mysql.connector

MIGRATION_TABLE_NAME = 'pythonMigrationTracker'

def checkMigrationsFolder():
  if not os.path.isdir('migrations'):
    os.makedirs('migrations')

def getDbConfig(args):
  if (args.host is not None and args.user is not None and
    args.password is not None and args.database is not None):
    return {
      "host": args.host,
      "user": args.user,
      "password": args.password,
      "database": args.database
    }
  elif os.path.exists('config.py'):
    import config
    return config.mysql
  else:
    print("error: database connection information not specified")
    sys.exit()

def getConnector(args):
  db = getDbConfig(args)
  cnx = mysql.connector.connect(host=db["host"], user=db["user"],
    password=db["password"], database=db["database"])
  return cnx

def hasMigrationTable(cursor):
  cursor.execute("SHOW tables;")
  for t in cursor:
    if MIGRATION_TABLE_NAME in t:
      return True
  return False

def createMigrationTable(cursor, cnx):
  cursor.execute("CREATE TABLE {0} (version INT NOT NULL);".format(MIGRATION_TABLE_NAME))
  cursor.execute("INSERT INTO {0} (version) VALUES (0);".format(MIGRATION_TABLE_NAME))
  cnx.commit()

def setTableVersion(args, version):
  cnx = getConnector(args)
  cursor = cnx.cursor()
  cursor.execute("UPDATE {0} SET version = {1};".format(MIGRATION_TABLE_NAME, version))
  cnx.commit()
  cursor.close()
  cnx.close()

def handleArgs(args):
  command = args.command[0]
  if command == 'generate':
    genHandler(args)
  elif command == 'migrate':
    migrateHandler(args)
  elif command == 'rollback':
    rollbackHandler(args)
  elif command == 'reset':
    resetHandler(args)
  else:
    print('error: unrecognized command ' + command)

def genHandler(args):
  if len(args.command) < 2:
    print('error: must provide type of generation')
    return
  genType = args.command[1]
  if genType == 'migration':
    version = 0
    for f in os.listdir('migrations'):
      if os.path.isfile(os.path.join('migrations', f)) and f[:4].isnumeric():
        version = max(version, int(f[:4]))
    version += 1
    name = 'migration'
    if len(args.command) >= 3:
      name = args.command[2]
    outFileName = os.path.join('migrations', '%04d-%s-%s.sql')
    open(outFileName % (version, 'up', name), 'w')
    open(outFileName % (version, 'down', name), 'w')

def migrateHandler(args):
  cnx = getConnector(args)
  cursor = cnx.cursor()
  if not hasMigrationTable(cursor):
    createMigrationTable(cursor, cnx)
  upfiles = [f for f in os.listdir('migrations') if f[5:7] == 'up' and f[:4].isnumeric()]
  upfiles.sort(key=lambda k: int(k[:4]))
  cursor.execute("SELECT version FROM {0} LIMIT 1".format(MIGRATION_TABLE_NAME))
  version = None
  for t in cursor:
    version = t[0]
  reached = version
  for q in upfiles:
    if int(q[:4]) > version:
      query = open(os.path.join('migrations', q)).read()
      try:
        cursor.execute(query)
        reached = int(q[:4])
      except mysql.connector.Error as err:
        setTableVersion(args, reached)
        print("Failed query in: {}".format(q))
        print("{}".format(err))
        exit(1)
  setTableVersion(args, reached)
  cnx.commit()
  cursor.close()
  cnx.close()

def rollbackHandler(args):
  cnx = getConnector(args)
  cnx.close()
  pass

def resetHandler(args):
  cnx = getConnector(args)
  cnx.close()
  pass

def main():
  parser = argparse.ArgumentParser(description='Manage MySQL migrations')
  parser.add_argument('command', nargs='+')
  parser.add_argument('--host', '-host')
  parser.add_argument('--user', '-u')
  parser.add_argument('--password', '-p')
  parser.add_argument('--database', '-db')
  parser.add_argument('--version', type=int)

  checkMigrationsFolder()
  args = parser.parse_args()
  handleArgs(args)

  # Debugging output
  print(args)

if __name__ == '__main__':
  main()
