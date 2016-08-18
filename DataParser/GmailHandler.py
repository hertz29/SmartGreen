from __future__ import print_function
import sys
sys.path.insert(0, '/home/ubuntu/idan/smart_green_vir_env/smart_green')
import os
#import django 
import httplib2
import logging
import base64
import oauth2client
from datetime import datetime, timedelta
from oauth2client import tools, client, file
from googleapiclient import discovery
try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
	
	
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smart_green.settings")
#django.setup()
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

module_logger = logging.getLogger("mail_parser_daily_report.GmailHandler")


class GmailHandler(object):
    """
        GmailHandler Class represent the connection with Gmail API.
        The __init__ open a service, a connection to Gmail, and initialize a dictionary that will holds the data files
    """
    def __init__(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=http)
        self.logger = logging.getLogger('mail_parser_daily_report.gmail_handler.Gmail_Handler')
        self.attached = {
            'Mcdonalds': [],
            'Shufersal': []
        }

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'gmail-python-quickstart.json')

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def get_message(self, user_id, msg_id):
        """
        The method takes the params, and return a single mail in a spacial format (for more details, goto Gmail Python API)
        :param user_id: user_id: User's email address. The special value "me"
        :param msg_id: every mail message have id. with the
                       msg_id we get the all mail
        :return:  the full message
        """
        try:
            message = self.service.users().messages().get(userId=user_id, id=msg_id).execute()
            return message
        except:
            print('An error occurred')

    def list_messages_matching_query(self, user_id, query=''):
        """List all Messages of the user's mailbox matching the query.

      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        query: String used to filter messages returned.
        Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

      Returns:
        List of Messages that match the criteria of the query. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate ID to get the details of a Message.
      """
        try:
            response = self.service.users().messages().list(userId=user_id,
                                                            q=query).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(userId=user_id, q=query,pageToken=page_token).execute()
                messages.extend(response['messages'])
            return messages
        #except errors.HttpError, error:
         #   print('An error occurred: %s' % error)
        except:
            print('An error occurred')

    def list_messages_with_labels(self, user_id, label_ids=[]):
        """List all Messages of the user's mailbox with label_ids applied.

      Args:
        self.service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        label_ids: Only return Messages with these labelIds applied.

      Returns:
        List of Messages that have all required Labels applied. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate id to get the details of a Message.
      """
        from email import errors
        try:
            response = self.service.users().messages().list(userId=user_id,
                                                            labelIds=label_ids).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(userId=user_id,
                                                                labelIds=label_ids,
                                                                pageToken=page_token).execute()
                messages.extend(response['messages'])

            return messages
        except:
            print('An error occurred')

    def get_attachments(self, message, msg_id, user_id, prefix=""):
        """Get and store attachment from Message with given id.
        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: ID of Message containing attachment.
        prefix: prefix which is added to the attachment filename on saving
        """
        attached_file = []
        from email import errors
        try:
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['filename']:
                        if '.csv' in part['filename']:
                            if 'data' in part['body']:
                                data = part['body']['data']
                            else:
                                find_sender = message['payload']['headers']
                                for mail in find_sender:
                                    if mail['name'] == 'From':
                                        sender = mail['value']
                                        self.logger.info('       Open Mail From: ' + sender)
                                att_id = part['body']['attachmentId']
                                att = self.service.users().messages().attachments().get(userId='me', messageId=msg_id,
                                                                                   id=att_id).execute()
                                data = att['data']
                            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                            path = prefix + part['filename']
                            with open(path, 'w+') as f:
                                f.write(file_data)
                                attached_file.append(part['filename'])

                                self.logger.info('Extract : ' + part['filename'])
                                self.logger.info('---------------------')
            return attached_file
        except:
            print('An error occurred')

    def parse_messages(self):
        """
        The method gets list of mails from the label 'INBOX'.
        For each mail, the method call to 'insert' method.
        'insert' method purpose is to get the attatched files to the message,
        and insert them to the correct place in the data structure
        """
        messages = self.list_messages_with_labels('me', ['INBOX'])
        self.logger.info('Get All Mails')
        self.logger.info('Start to look over attachments into mails')
        for msg_id in messages:
            message = self.get_message(user_id='me', msg_id=msg_id["id"])
            if self.date_validation(message):
                self.insert(message, msg_id, 'me')
            else:
                break
        self.logger.info('Finished to look over attachments into mails')

    def insert(self, msg, msg_id, user_id):
        """
        insert(id) takes a message id, open the attached file in the mail
        and add the file to a specific place in the data structure
        :param id: message id
        """
        attached_file = self.get_attachments(msg,msg_id ,user_id)

        if 'V_OpsStoreAndMail.csv' in attached_file:
            if not 'V_OpsStoreAndMail.csv' in self.attached['Mcdonalds']:
                self.attached['Mcdonalds'].extend(attached_file)
        else:
            if 'StoreOpenHour.csv' in attached_file:
                if not 'StoreOpenHour.csv' in self.attached['Mcdonalds']:
                    self.attached['Mcdonalds'].extend(attached_file)
            else:
                self.attached['Shufersal'].extend(attached_file)

    def date_validation(self, message):
        for header in message['payload']['headers']:
            if header['name'] == 'Date':
                mail_date = str(header['value'])
                splited_mail_date = mail_date.split(' ')
                (mail_day,mail_month,mail_year) = splited_mail_date[1], self.month_convetor(splited_mail_date[2]), splited_mail_date[3]
                try:
                    mail_date = datetime.strptime(mail_year+'-'+mail_month+'-'+mail_day, "%Y-%m-%d")
                    curr_date = datetime.now()
                    return curr_date-mail_date < timedelta(1)
                except:
                    return False

    def month_convetor(self,mail_month):
        try:
            month_dict = {'Jan': '1','Feb': '2','Mar': '3','Apr': '4',
                          'May': '5','Jun': '6','Jul': '7','Aug': '8',
                          'Sep': '9','Oct': '10','Nov': '11','Dec': '12'
                          }
            return month_dict[mail_month]
        except:
            return mail_month

    def print_date(self, message):
        for header in message['payload']['headers']:
            if header['name'] == 'Date':
                mail_date = str(header['value'])
                splited_mail_date = mail_date.split(' ')
                (mail_day, mail_month, mail_year) = splited_mail_date[1], self.month_convetor(splited_mail_date[2]), splited_mail_date[3]
                print(mail_year, mail_month, mail_day)
            if header['name'] == 'From':
                sender = header['value']
                print(sender)



