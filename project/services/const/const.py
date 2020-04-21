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
HEIGHT_TO_FLIGHT_MIN = 90
HEIGHT_TO_FLIGHT_MAX = 110
MAX_RIGHT_DISTANCE = 30
MIN_RIGHT_DISTANCE = 10
MIN_FRONT_DISTANCE = 40

# status constants
STATUS_QUEUE_NAME = "status"
STATUS_BINDING_KEY = "#.status.#"

# init constants
INIT_QUEUE_NAME = "init"
INIT_BINDING_KEY = "#.init.#"

# module name to put in header
LOGIC_HEADER_NAME = "logic"
LOG_HEADER_NAME = "log"
STATUS_HEADER_NAME = "status"
INIT_HEADER_NAME = "init"
DATA_PROCESSING_HEADER_NAME = "data_processing"

