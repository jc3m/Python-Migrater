#!/usr/bin/python3

import argparse
import os
import sys

def checkMigrationsFolder():
  if not os.path.isdir('migrations'):
    os.makedirs('migrations')

def handleArgs(args):
  command = args.command[0]
  if command == 'generate':
    genHandler(args)
  elif command == 'migrate':
    migrateHandler(args)
  elif command == 'rollback':
    rollbackHandler(args)
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

def rollbackhandler(args):
  pass

def main():
  parser = argparse.ArgumentParser(description='Manage MySQL migrations')
  parser.add_argument('command', nargs='+')
  parser.add_argument('--version', type=int)
  checkMigrationsFolder()
  handleArgs(parser.parse_args())
  print(parser.parse_args())

if __name__ == '__main__':
  main()
