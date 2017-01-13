#!/usr/bin/python3

import argparse
import os
import sys
import mysql.connector

MIGRATION_TABLE_NAME = 'pmt'

def checkMigrationsFolder():
  """Create a migration folder if it does not exist"""
  if not os.path.isdir('migrations'):
    os.makedirs('migrations')

def passError(err):
  print('error: {0}'.format(err))
  sys.exit(1)

def getDbConfig(args):
  """Get database configurations either from command line arguments or config.py"""
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
    if (args.production):
      try:
        return config.production
      except:
        passError('Production information not specified')
    return config.mysql
  else:
    passError('Database connection information not specified')

def getConnector(args):
  """Get the MySQL database connector using db configs"""
  db = getDbConfig(args)
  cnx = mysql.connector.connect(host=db["host"], user=db["user"],
    password=db["password"], database=db["database"])
  return cnx

def hasMigrationTable(cursor):
  """Check if the migration table already exists in the database"""
  cursor.execute("SHOW tables;")
  res = False
  for t in cursor:
    if MIGRATION_TABLE_NAME in t:
      res = True
  return res

def createMigrationTable(cursor, cnx):
  """Create the migration table and set version to 0"""
  cursor.execute("CREATE TABLE {0} (version INT NOT NULL);".format(MIGRATION_TABLE_NAME))
  cursor.execute("INSERT INTO {0} (version) VALUES (0);".format(MIGRATION_TABLE_NAME))
  cnx.commit()

def setTableVersion(args, version):
  """Set the current version in the database table"""
  cnx = getConnector(args)
  cursor = cnx.cursor()
  cursor.execute("UPDATE {0} SET version = {1};".format(MIGRATION_TABLE_NAME, version))
  cnx.commit()
  cursor.close()
  cnx.close()

def getTableVersion(cursor):
  """Get the current version from the migration table"""
  version = None
  cursor.execute("SELECT version FROM {0} LIMIT 1".format(MIGRATION_TABLE_NAME))
  for t in cursor:
    version = t[0]
  return version

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
  elif command == 'version':
    versionHandler(args)
  else:
    passError('unrecognized command ' + command)

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
  version = getTableVersion(cursor)
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
        sys.exit(1)
  setTableVersion(args, reached)
  versionHandler(args)
  cnx.commit()
  cursor.close()
  cnx.close()

def rollbackHandler(args):
  cnx = getConnector(args)
  cursor = cnx.cursor()
  serverVersion = getTableVersion(cursor)
  if serverVersion <= 0:
    passError('Nothing to rollback')
  downfiles = [f for f in os.listdir('migrations') if f[5:9] == 'down' and f[:4].isnumeric()]
  downfiles.sort(key=lambda k: int(k[:4]), reverse=True)
  rollbackVersion = serverVersion
  if args.version is not None:
    rollbackVersion = args.version
  curVersion = serverVersion
  for i in range(len(downfiles)):
    fileVer = int(downfiles[i][:4])
    if fileVer <= serverVersion and fileVer >= rollbackVersion:
      query = open(os.path.join('migrations', downfiles[i])).read()
      try:
        cursor.execute(query)
        if i == len(downfiles) - 1:
          curVersion = 0
        else:
          curVersion = int(downfiles[i+1][:4])
      except mysql.connector.Error as err:
        setTableVersion(args, curVersion)
        print("Failed query in: {}".format(downfiles[i]))
        print("{}".format(err))
        sys.exit(1)
  setTableVersion(args, curVersion)
  versionHandler(args)
  cnx.commit()
  cursor.close()
  cnx.close()

def resetHandler(args):
  cnx = getConnector(args)
  cnx.close()
  pass

def versionHandler(args):
  cnx = getConnector(args)
  cursor = cnx.cursor()
  v = getTableVersion(cursor)
  print("Server migration version: {0}".format(v))
  cursor.close()
  cnx.close()

def main():
  parser = argparse.ArgumentParser(description='Manage MySQL migrations')
  parser.add_argument('command', nargs='+')
  parser.add_argument('--host', '-host')
  parser.add_argument('--user', '-u')
  parser.add_argument('--password', '-p')
  parser.add_argument('--database', '-db')
  parser.add_argument('--version', '-v', type=int)
  parser.add_argument('--production', action='store_true')

  checkMigrationsFolder()
  args = parser.parse_args()
  handleArgs(args)

if __name__ == '__main__':
  main()
