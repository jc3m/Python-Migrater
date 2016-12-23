#!/usr/bin/python3

import argparse
import os
import sys

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
  pass

def rollbackHandler(args):
  pass

def resetHandler(args):
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
  db = getDbConfig(args)
  handleArgs(args)
  print(args)
  print(db)

if __name__ == '__main__':
  main()
