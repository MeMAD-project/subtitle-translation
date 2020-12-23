#!/bin/bash

MARIAN_DIR=$1
MODEL_PATH=$2
VOCAB_PATH=$3
INPUT_PATH=$4
OUTPUT_PATH=$5
NORM_EXPONENT=$6
COMP_NODE=$7

${MARIAN_DIR}/marian-decoder \
    --models ${MODEL_PATH} \
    --vocabs ${VOCAB_PATH} ${VOCAB_PATH} \
    --input ${INPUT_PATH} \
    --output ${OUTPUT_PATH} \
    --normalize ${NORM_EXPONENT} \
    ${COMP_NODE}

chmod 640 ${OUTPUT_PATH}

