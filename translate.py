#!/usr/bin/env python3

from datetime import datetime
from os import path, remove, system
from paths import Paths

import argparse, re, traceback

allowed_langs = ['de', 'en', 'fi', 'fr', 'nl', 'sv']

parser = argparse.ArgumentParser(description='Translate SRT-formatted subtitles between six MeMAD languages: de, en, fi, fr, nl, sv.')

required_arguments = parser.add_argument_group('required arguments')
required_arguments.add_argument('-i', '--input', type=str, required=True, help='path to the input subtitle file (required)')
required_arguments.add_argument('-o', '--output', type=str, required=True, help='name of the output subtitle file (required)')
required_arguments.add_argument('-s', '--src-lang', choices=allowed_langs, required=True, help='the language of the translation input (required)')
required_arguments.add_argument('-t', '--tgt-lang', choices=allowed_langs, required=True, help='the language of the translation output (required)')

parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose feedback messages (default: False)')
parser.add_argument('-l', '--log', type=str, default=None, help='path to the log file to use for progress logging (default: None)')
parser.add_argument('-p', '--strict-sentence-parsing', action='store_true', default=False, help='use a strict sentence parser alternative that relies on punctuation (default: False)')
parser.add_argument('-g', '--gpu-devices', type=int, default=0, help='use this many GPU devices for NMT decoding (default: 0, CPU-based computation)')
parser.add_argument('-c', '--cpu-threads', type=int, default=1, help='use this many CPU threads for NMT decoding (default: 1)')
parser.add_argument('--plain-text-mode', action='store_true', default=False, help='translate from plain text (one sentence per line) instead of SRT (default: False)')

args = parser.parse_args()

paths = Paths()

moses_dir = paths.get('MOSES-DIR')
marian_dir = paths.get('MARIAN-DIR')
opustoolsperl_dir = paths.get('OPUSTOOLSPERL-DIR')
subalign_dir = paths.get('SUBALIGN-DIR')
scripts_dir = paths.get('SCRIPTS-DIR')
models_dir = paths.get('MODELS-DIR')
temp_dir = paths.get('TEMP-DIR')

def append_to_file(path, line):
  with open(path, mode='a', encoding='utf-8') as out_file:
    out_file.write('%s\n' % line)

def log(source, message):
  line = '[%s] [%s] %s' % (datetime.now(), source.upper(), message)
  
  if args.verbose:
    print(line)
  if args.log:
    append_to_file(args.log, line)

if args.src_lang == args.tgt_lang:
  log('EXCEPTION', 'The translation direction %s->%s is not valid.' % (args.src_lang, args.tgt_lang))

try:
  inp_path = args.input.strip()
  out_path = args.output.strip()
  
  inp_name = path.basename(inp_path)
  out_name = path.basename(out_path)
  tmp_name = '%s.%s' % (inp_name, out_name)
  
  src_lang = args.src_lang.strip()
  tgt_lang = args.tgt_lang.strip()
  
  tmp_paths = []
  
  log('PREPROCESSING', 'Preprocessing input subtitles...')
  
  if not args.plain_text_mode:
    log('PREPROCESSING', '...parsing sentences...')
    
    if args.strict_sentence_parsing:
      exe_path = path.join(scripts_dir, 'srt2sent.py')
      snt_path = path.join(temp_dir, tmp_name + '.sentences')
      tmp_paths.append(snt_path)
      
      system('%s -i %s -o %s' % (exe_path, inp_path, snt_path))
      assert path.isfile(snt_path)
    
    else:
      exe_path = path.join(subalign_dir, 'srt2xml')
      xml_path = path.join(temp_dir, tmp_name + '.xml')
      
      system('%s -e utf8 -r %s < %s' % (exe_path, xml_path, inp_path))
      assert path.isfile(xml_path)
      tmp_paths.append(xml_path)
      
      exe_path = path.join(opustoolsperl_dir, 'opus2text')
      snt_path = path.join(temp_dir, tmp_name + '.sentences')
      
      system('%s < %s > %s' % (exe_path, xml_path, snt_path))
      assert path.isfile(snt_path)
      tmp_paths.append(snt_path)
  
  else:
    snt_path = inp_path
 
  log('PREPROCESSING', '...preprocessing sentences...')
  
  exe_path = path.join(scripts_dir, 'preprocess.sh')
  str_path = path.join(temp_dir, tmp_name + '.strip')
  
  system('%s %s %s %s %s' % (exe_path, moses_dir, src_lang, snt_path, str_path))
  assert path.isfile(str_path)
  tmp_paths.append(str_path)
  
  log('PREPROCESSING', '...applying subword segmentation for restoration...')

  exe_path = path.join(scripts_dir, 'sentencepiece-apply.py')
  uni_path = path.join(temp_dir, tmp_name + '.strip.uni24k')
  mdl_path = path.join(models_dir, 'sentencepiece.%s.uni24k.model' % src_lang)

  system('%s --input %s --output %s --model %s' % (exe_path, str_path, uni_path, mdl_path))
  assert path.isfile(uni_path)
  tmp_paths.append(uni_path)

  log('PREPROCESSING', '...done!')

  if args.gpu_devices > 0:
    comp_node = '"--devices %s"' % (' '.join([str(gpuid) for gpuid in range(args.gpu_devices)]))
  else:
    comp_node = '"--cpu-threads %d"' % args.cpu_threads
  
  log('RESTORATION', 'Applying punctuation and letter case restoration...')
  
  exe_path = path.join(scripts_dir, 'marian-decode.sh')
  reu_path = path.join(temp_dir, tmp_name + '.restored.uni24k')
  mdl_path = '"%s"' % ' '.join([path.join(models_dir, 'restore-%s.s%d.npz' % (src_lang, i)) for i in range(5)])
  voc_path = path.join(models_dir, 'restore-%s.vocab.yml' % src_lang)
  
  system('%s %s %s %s %s %s 500 0.0 %s' % (exe_path, marian_dir, mdl_path, voc_path, uni_path, reu_path, comp_node))
  assert path.isfile(reu_path)
  tmp_paths.append(reu_path)
  
  log('RESTORATION', '...done!')
  
  log('PREPROCESSING', 'Resegmenting output for translation...')
  
  log('PREPROCESING', '...desegmenting output...')
  
  exe_path = path.join(scripts_dir, 'sentencepiece-deseg.sh')
  res_path = path.join(temp_dir, tmp_name + '.restored')
  
  system('%s < %s > %s' % (exe_path, reu_path, res_path))
  assert path.isfile(res_path)
  tmp_paths.append(res_path)
  
  log('PREPROCESSING', '...applying subword segmentation for translation...')
  
  exe_path = path.join(scripts_dir, 'sentencepiece-apply.py')
  reb_path = path.join(temp_dir, tmp_name + '.restored.bpe32k')
  mdl_path = path.join(models_dir, 'sentencepiece.%s+%s.bpe32k.model' % tuple(sorted([src_lang, tgt_lang])))

  system('%s --input %s --output %s --model %s' % (exe_path, res_path, reb_path, mdl_path))
  assert path.isfile(reb_path)
  tmp_paths.append(reb_path)
  
  log('PREPROCESSING', '...done!')
  
  log('TRANSLATION', 'Translating the processed sentences...')
  
  exe_path = path.join(scripts_dir, 'marian-decode.sh')
  trb_path = path.join(temp_dir, tmp_name + '.translated.bpe32k')
  mdl_path = '"%s"' % ' '.join([path.join(models_dir, '%s-%s.s%d.npz' % (src_lang, tgt_lang, i)) for i in range(5)])
  voc_path = path.join(models_dir, '%s-%s.vocab.yml' % (src_lang, tgt_lang))
  
  system('%s %s %s %s %s %s 500 1.0 %s' % (exe_path, marian_dir, mdl_path, voc_path, reb_path, trb_path, comp_node))
  assert path.isfile(trb_path)
  tmp_paths.append(trb_path)
  
  log('TRANSLATION', '...done!')
  
  log('POSTPROCESSING', 'Generating translated subtitles...')
  
  log('POSTPROCESSING', '...postprocessing translations...')
  
  exe_path = path.join(scripts_dir, 'postprocess.sh')
  
  if args.plain_text_mode:
    tra_path = out_path
  
  else:
    tra_path = path.join(temp_dir, tmp_name + '.translated')
  
  system('%s %s %s %s %s %s' % (exe_path, moses_dir, scripts_dir, tgt_lang, trb_path, tra_path))
  assert path.isfile(tra_path)
  
  if not args.plain_text_mode:
    tmp_paths.append(tra_path)
    
    log('POSTPROCESSING', '...fitting translations into subtitle segments...')
    
    exe_path = path.join(subalign_dir, 'mt2srt')
    
    system('%s -n %s < %s > %s' % (exe_path, inp_path, tra_path, out_path))
    assert path.isfile(out_path)
  
  log('POSTPROCESSING', '...done!')

except:
  log('EXCEPTION', 'Procedure aborted due to an exception --')
  log('EXCEPTION', traceback.format_exc())

finally:
  for tmp_path in tmp_paths:
    if path.isfile(tmp_path):
      remove(tmp_path)
