#!/bin/bash

MARIAN_DIR=$1
MODEL_PATH=$2
VOCAB_PATH=$3
INPUT_PATH=$4
OUTPUT_PATH=$5
MAX_LENGTH=$6
NORM_EXPONENT=$7
COMP_NODE=$8

${MARIAN_DIR}/marian-decoder \
    --models ${MODEL_PATH} \
    --vocabs ${VOCAB_PATH} ${VOCAB_PATH} \
    --input ${INPUT_PATH} \
    --output ${OUTPUT_PATH} \
    --max-length ${MAX_LENGTH} \
    --max-length-crop \
    --normalize ${NORM_EXPONENT} \
    ${COMP_NODE}

chmod 640 ${OUTPUT_PATH}

