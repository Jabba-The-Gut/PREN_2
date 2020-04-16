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

# init constants

# module name to put in header
LOGIC_HEADER_NAME = "logic"
LOG_HEADER_NAME = "log"
STATUS_HEADER_NAME = "status"
INIT_HEADER_NAME = "init"
DATA_PROCESSING_HEADER_NAME = "data_processing"

