import os
import logging

SALESFORCE = {
    'username': os.getenv('SFDC_USERNAME', 'svc_account'),
    'password': os.getenv('SFDC_PASSWORD', 'password'),
    'domain': os.getenv('SFDC_DOMAIN', 'salesforce'),
    'version': os.getenv('SFDC_VERSION', '39.0')
}

FILE_INFO = {
    'source_directory': os.getenv('SOURCE_DIRECTORY', 'test_files'),
    'folder_to_search': os.getenv('FOLDER_TO_SEARCH', 'get_files'),
    'custom_file_parser': os.getenv('CUSTOM_FILE_PARSER', False)
}


def get_logger_config(log_file_name='ses_salesforce_upload', file_logger=None):
    """
    Logger config with optional file logger
    """

    logger = logging.getLogger(log_file_name)
    logger.setLevel(logging.DEBUG)

    # Formatter for log representation: Can be manipulated to desired state
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handlers
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    if file_logger:
        log_file = logging.FileHandler(filename="{}.log".format(log_file_name))
        log_file.setLevel(logging.DEBUG)
        log_file.setFormatter(formatter)
        logger.addHandler(log_file)

    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
