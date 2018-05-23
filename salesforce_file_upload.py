import logging
import time
import base64
import requests
import os
import json
from simple_salesforce import Salesforce, SalesforceLogin
import config

logger = config.get_logger_config()


class ResponseException(Exception):
    pass


class SFDCFileUpload(object):
    """
	This class has funcitonality to write files and any associated metadata to Salesforce
	The file is written to the standard object ContentVersion
	"""

    def __init__(self):
        # self.postgres_client = self._get_psycopg_conn()
        self.session_id, self.instance = SalesforceLogin(username=config.SALESFORCE['username'],
                                                         password=config.SALESFORCE['password'],
                                                         domain=config.SALESFORCE['domain'])

        logger.debug('session_id={}, instance={}'.format(self.session_id, self.instance))

    def sf_upload_driver(self, file_path, file_name):

        start = time.time()

        self.upload_file_request(file_path, file_name)

        end = time.time()
        duration = end - start

        logger.info("Successfully uploaded file '{}' to SalesForce - upload duration {} "
                    "seconds".format(file_name, duration))

        self.delete_file_from_disk(file_path)

    def delete_file_from_disk(self, file_path):
        try:
            os.remove(file_path)
            logger.info("Successfully deleted file at path '{}' from disk!".format(file_path))
        except Exception as e:
            logger.error("Error when deleting file from disk. Message: {}".format(e))
            raise e

    def metadata_request(self, file_name):
        # Use this function if you need to upload file metadata to another Salesforce object, add it to the driver

        pass

    def upload_file_request(self, file_path, file_name):
        # This function uploads the file itself to the ContentVersion object in Salesforce
        try:
            with open(file_path, "rb") as f:
                file_body = base64.b64encode(f.read())

            url = 'https://{}/services/data/v{}/sobjects/ContentVersion/'.format(self.instance,
                                                                                 config.SALESFORCE['version'])
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(self.session_id)}

            data = json.dumps({
                'Title': file_name,
                'PathOnClient': file_name,
                'VersionData': file_body.decode('ascii')
            })

            response = requests.post(url, headers=headers, data=data)

            if int(response.status_code) >= 400:
                logger.error(
                    "Salesforce failed to upload file '{}' with response status code '{}' with message:\n{}".format(
                        file_name, response.status_code, response.text))
                raise ResponseException('Response returned error status code')
            else:
                logger.info("SalesForce response object from uploading file: {}".format(response.text))
                logger.info("SalesForce response status_code: {}".format(response.status_code))

        except requests.exceptions.RequestException as e:
            logger.error("Error when uploading file to Salesforce. Message: {}".format(e))
            logger.exception(e)
            raise e


def main():
    sf_driver = SFDCFileUpload()

    path_to_files = config.FILE_INFO['source_directory']
    logger.info('Directory to find files for Salesforce upload: {}'.format(path_to_files))

    for upload in os.listdir(path_to_files):
        logger.info('================================')
        sf_driver.sf_upload_driver(os.path.join(path_to_files, upload), upload)
        logger.info('================================')


if __name__ == "__main__":
    main()