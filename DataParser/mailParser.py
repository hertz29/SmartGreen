from __future__ import print_function
import sys
sys.path.insert(0, '/home/ubuntu/idan/smart_green_vir_env/smart_green')
import os
import django 
import logging
from oauth2client import tools
from GmailHandler import GmailHandler
from McdonaldsReader import McdonaldsReader

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smart_green.settings")
django.setup()




logger = logging.getLogger('mailParser')
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler('daily_report.log')
fh.setLevel(logging.INFO)
# create console handler with a higher log level
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)


def main():
    """
        The program flow:
         - create a GmailHandler, the Class locate at GmailHandler.py
         - The GmailHandler instance performing parse_messages method which iterate the Gmail Account Inbox
         - Each Client will be represented by instance of Reader Class witch implements 'parse_files' method.
         - Therefore, we will create instace for every client.

         GmailHandler:
         - Instance of GmailHandler will holds the following fields:
            * self.service - the service that provided by Google.
            * self.attached - a dictionary, which holds Clients names as 'Key' and list of files as 'Value'
    """
    logger.info("Application Start")
    gmail_handler = GmailHandler()
    gmail_handler.parse_messages()
    mcdonalds_reader = McdonaldsReader(gmail_handler.attached['Mcdonalds'])
    mcdonalds_reader.parse_files()
    logger.info("Application End")


if __name__ == '__main__':
    main()
