#!/bin/bash

MOSES_DIR=$1
SCRIPT_DIR=$2
LANG=$3
INPUT=$4
OUTPUT=$5

if [[ ${LANG} == "fi" ]]; then
  cat ${INPUT} |
  sed 's/  */ /g;s/^ *//g;s/ *$//g' |
  ${SCRIPT_DIR}/sentencepiece-deseg.sh |
  ${MOSES_DIR}/recaser/detruecase.perl |
  ${MOSES_DIR}/tokenizer/detokenizer.perl -l $LANG |
  perl -pe 's/(?:(?<=^)|(?<= ))(([Hh]err|[Rr]ouv|[Nn]ei[dt])[^ [[:punct:]]]*)[[:punct:]]+/\1/g' > ${OUTPUT}
else
  cat ${INPUT} |
  sed 's/  */ /g;s/^ *//g;s/ *$//g' |
  ${SCRIPT_DIR}/sentencepiece-deseg.sh |
  ${MOSES_DIR}/recaser/detruecase.perl |
  ${MOSES_DIR}/tokenizer/detokenizer.perl -l $LANG > ${OUTPUT}
fi
