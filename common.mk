SHELL=/bin/bash

ifeq ($(shell echo ${GOLLYX_MAPS_HOME}),)
$(error Environment variable GOLLYX_MAPS_HOME not defined. Please run "source environment" in the gollyx-maps repo root directory before running make commands)
endif

