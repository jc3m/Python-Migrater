#!/usr/bin/python3

import argparse
import os
import sys
import mysql.connector

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
    print('generating migration...')

def migrateHandler(args):
  cnx = getConnector(args)
  pass

def rollbackHandler(args):
  cnx = getConnector(args)
  pass

def resetHandler(args):
  cnx = getConnector(args)
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
