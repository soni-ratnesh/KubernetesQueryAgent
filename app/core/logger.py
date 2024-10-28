# app logger

import logging

def setup_logging():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s - %(message)s',
                    filename='agent.log', filemode='a')

def shutdown_logging():
    logging.shutdown()
