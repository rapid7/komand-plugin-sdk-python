import logging
import json
import re
import os

def extract_value(begin, key, end, s):
  '''Returns a string from a given key/pattern using provided regexes
  It takes 4 arguments:
  * begin: a regex/pattern to match left side
  * key: a regex/pattern that should be the key
  * end: a regex/pattern to match the right side
  * s: the string to extract values from

  Example: The following will use pull out the /bin/bash from the string s
  s = '\nShell: /bin/bash\n'
  shell = get_value(r'\s', 'Shell', r':\s(.*)\s', s)   

  This function works well when you have a list of keys to iterate through where the pattern is the same.
  '''
  regex = begin + key + end
  r = re.search(regex, s)
  if hasattr(r, 'group'):
    if r.lastindex == 1:
      return r.group(1)
  return None

def clean_dict(dictionary):
  '''Returns a new but cleaned dictionary:

  * Keys with None type values are removed
  * Keys with empty string values are removed

  This function is designed so we only return useful data
  '''
  newdict = dict(dictionary)
  for key in dictionary.keys():
    if dictionary.get(key) == None:
      del newdict[key]
    if dictionary[key] == '':
      del newdict[key]
  return newdict

def check_cachefile(cache_file):
  '''Return boolean on whether cachefile exists'''
  cache_dir  = '/var/cache'
  if cache_dir not in cache_file:
    cache_file = cache_dir + '/' + cache_file
  if os.path.isdir(cache_dir):
    if os.path.isfile(cache_file):
      logging.info('Cache file exists', cache_file)
      return True
    logging.info('Cache file %s did not exist, skipping', cache_file)
  return False

def open_cachefile(cache_file):
  '''Return file object if cachefile exists, create and return new cachefile if it doesn't exist'''
  cache_dir  = '/var/cache'
  if cache_dir not in cache_file:
    cache_file = cache_dir + '/' + cache_file
  if os.path.isdir(cache_dir):
    if os.path.isfile(cache_file):
      f = open(cache_file, 'r+')
      logging.info('Cache file %s exists, returning it', cache_file)
    else:
      if not os.path.isdir(os.path.dirname(cache_file)):
        os.makedirs(os.path.dirname(cache_file))
      f = open(cache_file, 'w')
      logging.info('Cache file %s created', cache_file)
    return f
  logging.error('%s is not a directory or does not exist', cache_dir)

def remove_cachefile(cache_file):
  '''Returns boolean on whether cachefile was removed'''
  cache_dir  = '/var/cache'
  if cache_dir not in cache_file:
    cache_file = cache_dir + '/' + cache_file
  if os.path.isdir(cache_dir):
    if os.path.isfile(cache_file):
      os.remove(cache_file)
      return True
    logging.info('Cache file %s did not exist, not removing it', cache_file)
  return False
