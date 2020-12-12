SHELL=/bin/bash

ifeq ($(shell echo ${GOLLY_MAPS_HOME}),)
$(error Environment variable GOLLY_MAPS_HOME not defined. Please run "source environment" in the golly-maps repo root directory before running make commands)
endif

