import sys
sys.path.insert(0, '/home/ubuntu/idan/smart_green_vir_env/smart_green/smart_green_interface')
sys.path.insert(0, '/home/ubuntu/idan/smart_green_vir_env/smart_green')
import os
#import django 
import logging
import csv
from datetime import datetime
module_logger = logging.getLogger("mail_parser_daily_report.csv_reader")
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smart_green.settings")
#django.setup()


class McdonaldsReader(object):
    def __init__(self, attached_files):
        self.logger = logging.getLogger('mail_parser_daily_report.gmail_handler.McdonaldsReader')
        self.files = attached_files

    def check_files(self):
        """
        :return: True if all files exist, False otherwise
        """
        if 'V_OpsStoreAndMail.csv' in self.files:
            is_store_and_mail = True
        else:
            self.logger.critical('Missing File!! V_OpsStoreAndMail is missing')
            is_store_and_mail = False
        if 'StoreOpenHour.csv' in self.files:
            is_store_open_hour = True
        else:
            self.logger.critical('Missing File!! StoreOpenHour is missing')
            is_store_open_hour = False
        return is_store_and_mail and is_store_open_hour

    def parse_files(self):
        """
        the method parse the files
        call to method according to the file name
        :return:
        """
        if self.check_files():
            for data_file in self.files:
                with open(data_file) as csvfile:
                    reader = csv.DictReader(csvfile)
                    if data_file == 'StoreOpenHour.csv':
                        self.parse_store_open_hours(reader)
                    if data_file == 'V_OpsStoreAndMail.csv':
                        self.init_site_contant(reader)

	from models import Site, SgClientLinkage, SiteContact, SiteWorkingHoursDetail
    def parse_store_open_hours(self, reader):
        """
        for each row in the file reader, first, the function check if the site
        in our site_list (sit in SgClientLinkage) otherwise the missing site writen to the logger.
        secondly, the function checks if the data exists, in not, the data is written to the database
        write the missing data to the database.
        :param reader:
        :return:
        """
        self.logger.info('Start handle sites open hours')
        unbounded_sites = []
        for row in reader:
            site_id = row['StoreIndex'].decode('UTF-8')
            if SgClientLinkage.objects.filter(client_linkage=site_id).exists():
                sg_site = SgClientLinkage.objects.get(client_linkage=site_id)
                current_site = Site.objects.get(site_number=sg_site.sg_index)
                date = self.convert_date_format(row['Date']).decode('UTF-8')
                if SiteWorkingHoursDetail.objects.filter(date=date, site_id=current_site).exists():
                    continue
                else:
                    open_time = row['OpenHour'].decode('UTF-8')
                    close_time = row['CloseHour'].decode('UTF-8')
                    data = SiteWorkingHoursDetail(date=date, time_from=open_time, time_to=close_time,
                                                  site_id=current_site)
                    data.save()
                    self.logger.info('Add New Site Working Hours, Site ID: %s , Date: %s' % (site_id, date))
            else:
                if not site_id in unbounded_sites:
                    unbounded_sites.append(site_id)
                continue
        self.logger.info('Finished handle sites open hours ')
        for site_id in unbounded_sites:
            self.logger.info('NOTICE!!!! Site ID %s do not exist in our system' % site_id)

    def convert_date_format(self, date):
        """
         convet the date format, otherwise it will not enter to the database and will crush the program
        :return: date in correct format
        """
        date2 = date.split()
        date3 = date2[0].split('/')
        date4 = date3[2] + '-' + date3[1] + '-' + date3[0]
        return date4

    def init_site_contant(self, reader):
        """
        the function extarct the data from the file, row by row
        init_site_contant enter data if needs
        :return:
        """
        self.logger.info('Start Init Site Contant')
        for row in reader:
            site_id = row['StoreIndex'].decode('UTF-8')
            # check if site_id exists in our sites list. else, continue
            if SgClientLinkage.objects.filter(client_linkage=site_id).exists():
                #sg_site = (client_linkage, sg_index = smart_green index)
                sg_site = SgClientLinkage.objects.get(client_linkage=site_id)
                #get the current site number, due to insert the data
                current_site = Site.objects.get(site_number=sg_site.sg_index)
                area_manager = row['AreaMail'].decode('UTF-8')
                area_Phone = row['AreaPhone'].decode('UTF-8')
                region_manager = row['RegionMail'].decode('UTF-8')
                region_Phone = row['RegionPhone'].decode('UTF-8')
                self.site_contant_insertion(area_manager, area_Phone, region_manager, region_Phone, current_site)
                self.init_daily_managers(row, current_site)
        self.logger.info('Finished Init Site Contant')

    def init_daily_managers(self, row, current_site):
        self.logger.info('Start Init Daily Manager')
        date = datetime.year+'-'+datetime.month+'-'+datetime.day
        temp_site = SiteWorkingHoursDetail.objects.get(date=date, site_id=current_site)
        daily_manager = row['SuperMail'].decode('UTF-8')
        if temp_site.daily_manager == 'aaa@aaa.com' or daily_manager != temp_site.daily_manager:
            daily_manager_phone = row['Telpone'].decode('UTF-8')
            temp_site.daily_manager = daily_manager
            temp_site.daily_manager_phone = daily_manager_phone
            temp_site.save()
            self.logger.info('Insert Daily Manager %s To Site Id %s at %s'
                             % (daily_manager, temp_site.site_id, date))
        self.logger.info('Finished Init Daily Manager')

    def site_contant_insertion(self, area_manager, area_Phone, region_manager, region_Phone, current_site):
        """
        site_contant_insertion insert data to SiteContant model.
            first, the function check if the contant exists in the model.
            if the data is not exist, then the function insert to the model
        """
        self.site_contant_insertion_helper(area_manager, area_Phone, current_site, 'Area')
        self.site_contant_insertion_helper(region_manager, region_Phone, current_site, 'Reqion')

    def site_contant_insertion_helper(self, manager, phone, current_site, type):
        if not SiteContact.objects.filter(email=manager, phone=phone, site_id=current_site, type=type).exists():
            contant = SiteContact(email=manager, phone=phone, site_id=current_site, type=type)
            contant.save()
            self.logger.info('Insert %s as %s Manager To Site: %s' % (manager, type, current_site))
        else:
            current_manager = SiteContact.objects.get(email=manager, phone=phone, site_id=current_site,type=type)
            if not current_manager.email == manager:
                current_manager.email = manager
                current_manager.phone = phone
                current_manager.save()