#!/usr/bin/env python3

import argparse
import sentencepiece as spm

parser = argparse.ArgumentParser(description='Segment corpora using a SentencePiece model.')
parser.add_argument('-i', '--input', type=str, required=True, help='path to the input corpus file')
parser.add_argument('-o', '--output', type=str, required=True, help='name of the output corpus file')
parser.add_argument('-c', '--model', type=str, required=True, help='path to the SentencePiece model file')

args = parser.parse_args()

sp = spm.SentencePieceProcessor()
sp.Load(args.model)

with open(args.input, mode='r', encoding='utf-8') as input_file:
  with open(args.output, mode='w', encoding='utf-8') as output_file:
    for sentence in input_file:
      output_file.write('%s\n' % ' '.join(sp.EncodeAsPieces(sentence)))
