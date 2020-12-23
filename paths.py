#!/usr/bin/env python3

import re

class Paths:
  def __init__(self):
    self.config = {}
    with open('paths.conf', mode='r', encoding='utf-8') as config_file:
      for line in config_file:
        line = line[:line.find('#')].strip()
        
        if ':' in line:
          var, value = line.split(':')
          self.config[var.strip()] = value.strip()
    
    resolved = False
    
    while not resolved:
      resolved = True
      
      for var, value in self.config.items():
        syms = re.findall('\$\{(.+)\}', value)
        
        for sym in syms:
          value = value.replace('${%s}' % sym, self.config[sym])
        
        self.config[var] = value
        
        if re.search('\$\{(.+)\}', value):
          resolved = False
  
  def get(self, var):
    return self.config[var]

