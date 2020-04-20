#!/usr/bin/env python

# Central file to manage all constants used in the project
CONNECTION_STRING = "localhost"
EXCHANGE = "main"

# data_processing constants
DATA_PROCESSING_QUEUE_NAME = "data_processing"
DATA_PROCESSING_BINDING_KEY = "#.data_processing.#"

# log constants
LOG_QUEUE_NAME = "log"
LOG_BINDING_KEY = "#.log.#"

# logic constants
LOGIC_QUEUE_NAME = "logic"
LOGIC_BINDING_KEY = "#.logic.#"

# status constants
STATUS_QUEUE_NAME = "status"
STATUS_BINDING_KEY = "#.status.#"

STATUS_DATA_PROC_PX4_FLAG_TRUE  = "data_processing: __px4_running True"
STATUS_DATA_PROC_PX4_FLAG_FALSE = "data_processing: __px4_running False"

# init constants

