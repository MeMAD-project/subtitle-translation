#!/usr/bin/env python3

import argparse, regex

parser = argparse.ArgumentParser(description='Convert SRT-formatted subtitles to a one-sentence-per-line plain text format.')
parser.add_argument('-i', '--input', type=str, required=True, help='path to the input SRT file')
parser.add_argument('-o', '--output', type=str, required=True, help='name of the output file')
parser.add_argument('-p', '--output-parse', type=str, default=None, help='filename for the parsed SRT output (disabled if unspecified)')

args = parser.parse_args()

id_line_format = regex.compile('^[\t ]*[0-9]+[\t ]*$')
timestamp_line_format = regex.compile('^[0-9\:\,\t ]+-->[0-9\:\,\t ]+$')

non_abbr_terminal_punc = regex.compile('(?<!(' + '(^| )[Nn]'
                                         + '|' + '(^| )[MmCcKk]m'
                                         + '|' + '(^| )[Kk]pl'
                                         + '|' + '(^| )[Ee]sim'
                                         + '|' + '(^| )[MmDd]r'
                                         + '|' + '(^| )[Mm]r?s'
                                         + '|' + '(^| )[Ee]tc'
                                         + '|' + '(^| )i\.?e'
                                         + '|' + '(^| )[Mm]in'
                                         + '|' + '(^| )[Ss]ec'
                                         + '|' + '(^| )[Hh]r?)'
                                         + ')' + '[\?\!\.…]')

def is_id(line):
  return regex.search(id_line_format, line)

def is_timestamp(line):
  return regex.search(timestamp_line_format, line)

def is_empty(line):
  return line.strip() == ''

with open(args.input, mode='r', encoding='utf-8') as in_file:
  with open(args.output, mode='w', encoding='utf-8') as out_file:
    prev_is_text = False
    curr_is_text = False
    
    parse = []
    
    for line in in_file:
      prev_is_text = curr_is_text
      curr_is_text = not is_id(line) and not is_timestamp(line) and not is_empty(line)
      
      if curr_is_text:
        if parse:
          if prev_is_text:
            parse.append('<LINE_BREAK>')
          else:
            parse.append('<SEGMENT_BREAK>')
        
        parse.append(line.strip())
    
    if (args.output_parse):
      with open(args.output_parse, mode='w', encoding='utf-8') as parsed_out_file:
        parsed_out_file.write('\n'.join(parse))
    
    sent_parts = []
    
    def add_sent_part(part):
      part = part.strip()
      
      if part.endswith(' -'):
        part = part[:-2].strip()
      
      sent_parts.append(part)
    
    for i in range(len(parse)):
      curr_line = parse[i]
      next_line = "" if i == len(parse) - 1 else parse[i + 1]
      
      if curr_line == '<LINE_BREAK>' or curr_line == '<SEGMENT_BREAK>':
        continue
      
      match = regex.search(non_abbr_terminal_punc, curr_line)
      
      while match:
        add_sent_part(curr_line[:match.end()])
        
        out_file.write(' '.join(sent_parts) + '\n')
        
        sent_parts = []
        
        curr_line = curr_line[match.end():].strip()
        
        match = regex.search(non_abbr_terminal_punc, curr_line)
      
      if curr_line:
        add_sent_part(curr_line)
    
    if sent_parts:
      out_file.write(' '.join(sent_parts) + '\n')
