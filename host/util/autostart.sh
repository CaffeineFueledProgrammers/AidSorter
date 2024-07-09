#!/usr/bin/env bash

AIDSORTER_PATH="${HOME}/AidSorter/host"
AIDSORTER_MODNAME="aidsorter"
AIDSORTER_ARGS="--model 'lite-model_efficientdet_lite0_detection_metadata_1.tflite'"

tmux -c "cd '${AIDSORTER_PATH}' && python3 -m ${AIDSORTER_MODNAME} ${AIDSORTER_ARGS}"
