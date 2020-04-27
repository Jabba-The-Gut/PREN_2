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
LOGIC_STATUS_QUEUE_NAME = "logic_status"
LOGIC_STATUS_BINDING_KEY = "#.logic_status.#"
LOGIC_PX4_FLAG_FALSE = "logic: __px4_running: False"
HEIGHT_TO_FLIGHT_MIN = 90
HEIGHT_TO_FLIGHT_MAX = 110
MAX_RIGHT_DISTANCE = 30
MIN_RIGHT_DISTANCE = 10
MIN_FRONT_DISTANCE = 40

# status constants
STATUS_QUEUE_NAME = "status"
STATUS_BINDING_KEY = "#.status.#"
STATUS_PX4_FLAG_FALSE = "status: __px4_running: False"
STATUS_PX4_FLAG_TRUE = "status: __px4_running: True"

STATUS_COMMANDS_UNSUCCESSFUL = "logic: __px4_running: False"
# This is temporary string need to change it
STATUS_DATAPROC_MODULE_FLAG_TRUE  = "data_processing: MODULE_FLAG: True"
STATUS_DATAPROC_MODULE_FLAG_FALSE  = "data_processing: MODULE_FLAG: False"
LOGIC_MODULE_FLAG_TRUE = "logic: MODULE_FLAG: True"
LOGIC_MODULE_FLAG_FALSE = "logic: MODULE_FLAG: False"
LOG_MODULE_FLAG_TRUE = "log: MODULE_FLAG: True"
LOG_MODULE_FLAG_FALSE = "log: MODULE_FLAG: False"
INIT_MODULE_FLAG_TRUE = "INIT: MODULE_FLAG: True"
INIT_MODULE_FLAG_FALSE = "INIT: MODULE_FLAG: False"

# init constants
INIT_QUEUE_NAME = "init"
INIT_BINDING_KEY = "#.init.#"
INIT_PX4_FLAG_TRUE = "init: __px4_running: True"
INIT_PX4_FLAG_FALSE = "init: __px4_running: False"


