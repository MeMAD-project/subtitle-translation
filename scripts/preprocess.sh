#!/bin/bash

MOSES_DIR=$1
LANG=$2
INPUT=$3
OUTPUT=$4

cat ${INPUT} |\
${MOSES_DIR}/tokenizer/detokenizer.perl -l $LANG |\
${MOSES_DIR}/tokenizer/replace-unicode-punctuation.perl |\
${MOSES_DIR}/tokenizer/remove-non-printing-char.perl |\
${MOSES_DIR}/tokenizer/normalize-punctuation.perl -l $LANG |\
${MOSES_DIR}/tokenizer/tokenizer.perl -a -l $LANG |\
sed -r "s/\([^„“\"\'\)]+\)//g" |\
sed 's/  */ /g;s/^ *//g;s/ *$//g' |\
sed -r -e 's/&[^ ]+;//g' -e 's/@[^ ]+@//g' |\
perl -pe 's/(?<=[0-9])\.(?=[0-9])/DecimalSeparatorPoint/g; s/(?<=[0-9])\,(?=[0-9])/DecimalSeparatorComma/g' |\
sed 's/[[:punct:]]//g' |\
sed 's/DecimalSeparatorPoint/\./g; s/DecimalSeparatorComma/\,/g' |\
sed -r -e 's/ +/ /g' -e 's/^ +//g' -e 's/ +$//g' |\
${MOSES_DIR}/tokenizer/lowercase.perl > ${OUTPUT} 2>/dev/null

chmod 640 ${OUTPUT}

