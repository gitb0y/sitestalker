#!/usr/bin/python

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from email.mime.multipart import MIMEMultipart
from selenium.webdriver.common.by import By
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from fake_useragent import UserAgent
from subprocess import Popen, PIPE
from defang import defang, refang
from selenium import webdriver
from urlparse import urlparse
from dominate.tags import *
from bsddb3 import db
from PIL import Image 
from lxml import html
import subprocess
import threading 
import ipaddress
import dominate
import datetime
import StringIO
import argparse
import requests
import httplib
import smtplib
import getpass
import socket
#import psutil
import uuid
import yaml
import json
import time
import sys
import ssl
import os
import re
import io

parser = argparse.ArgumentParser(description='A program that collects and stores statistics of one or more domains or websites (e.g., potentially brand-infringing parked domains) and monitors changes in these parameters. Screenshots are taken and email alerts are sent.',
        epilog='EXAMPLE: "python sitestalker.py -i stalker_input.txt -c stalker_config.yaml -g group1 -v" See https://github.com/gitb0y/sitestalker for the complete documentation.')
parser.add_argument('-i', '--infile', nargs='?', help='Input file containing a list of domains or URLs to monitor. ')
parser.add_argument('-c', '--configfile', nargs='?', const='stalker_config.yaml', default='stalker_config.yaml',
                    help='sitestalker.py configuration file in yaml format. Initial run will create stalker_config.yaml.')
parser.add_argument('-g', '--group-name', nargs='?', default='sitestalker', const='sitestalker', help='Group in --configfile where the input file belongs to. (i.e., which configuration to use for the --inputfile). Defaults to "sitestalker" group. ')
parser.add_argument('-v', '--verbose', help='Display verbose output in the screen.', action='store_true'),
parser.add_argument('-t', '--test-infile', help='Do nothing, just parse the input file.', action='store_true'),
args = parser.parse_args()

startTime = time.time()
update_html = False	
previous_data = {}



         
def get_screenshot(url, stalkerdb, change_status):

	db_hash = json.loads(stalkerdb[url])

	if 'screenshots' in json.loads(stalkerdb[url]):  #FOR EXISTING HOSTS THAT WE NEED TO UPDATE, OVERWRITE EXISTING SCREENSHOT FILE NAMES
	    if args.verbose: ">>> Retrieving old screenshot entries for " + url
	    screenshot_full_name = db_hash['screenshots']['full']
	    screenshot_name = db_hash['screenshots']['normal']
	    screenshot_crop_name = db_hash['screenshots']['crop']
	    screenshot_thumb_name = db_hash['screenshots']['thumb']
	else: #FOR NEW HOST ENTRIES OR UPDATED ENTRIES THAT DON'T HAVE SCREENSHOTS YET
		#if args.verbose: print ">>> CREATING SCREENSHOTS COLLECTIONS FOR " + url[0:40]
		db_hash['screenshots'] = {}
		if args.verbose: print ">>> Creating randomized screenshot filenames for " + url[0:40]
        	rand_str = str(uuid.uuid4().hex) 
		screenshot_full_name = rand_str + "_full.png"
		screenshot_crop_name = rand_str + "_crop.png"
		screenshot_thumb_name = rand_str + "_thumb.png"
		screenshot_name = rand_str + ".png"
	screenshot_full_path = os.path.join(config[group]['screenshot_dir'], screenshot_full_name)
	screenshot_crop_path = os.path.join(config[group]['screenshot_dir'], screenshot_crop_name)
	screenshot_thumb_path = os.path.join(config[group]['screenshot_dir'], screenshot_thumb_name)
	screenshot_path = os.path.join(config[group]['screenshot_dir'], screenshot_name)

# FOR BYTES TRANSFERRED VIA WEBDRIVER LOGS. EXTREMELY SLOW (NO LONGER IMPLEMENTED)
	#logging_prefs = {'performance' : 'INFO' }  #https://stackoverflow.com/questions/27490472/how-to-get-transferred-size-of-a-complete-page-load
	#caps = DesiredCapabilities.CHROME.copy()
	#caps['loggingPrefs'] = logging_prefs
	chromium_options = Options()
	chromium_options.add_argument('--headless')
	chromium_options.add_argument('--user-agent=' + ua.random)
	chromium_options.add_argument('--no-sandbox')
	chromium_options.add_argument("--disable-gpu") #https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc
	chromium_options.add_argument('--disable-dev-shm-usage')
	chromium_options.add_argument("--no-default-browser-check") #Overrides default choices
	chromium_options.add_argument("--no-first-run")
	chromium_options.add_argument("--disable-default-apps") 
        chromium_options.add_argument("--disable-infobars") #https://stackoverflow.com/a/43840128/1689770
        chromium_options.add_argument("--disable-browser-side-navigation") #https://stackoverflow.com/a/49123152/1689770
        chromium_options.add_argument("enable-automation") # https://stackoverflow.com/a/43840128/1689770


	chromium_options.binary_location = '/usr/bin/chromium-browser'
       	driver = webdriver.Remote(service.service_url, options=chromium_options)
       	#driver = webdriver.Remote('http://127.0.0.1:9515', options=chromium_options)
       	#driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=chromium_options)
        #driver.set_page_load_timeout(20)           
	driver.set_window_size(2048,2048)
	try:
	    driver.get(url)
	    time.sleep(5)
	#wait = WebDriverWait(driver, 4)
	#wait.until(ExpectedConditions.visibilityOfElementLocated(By.tagName("html")))
	#element = wait.until(EC.presence_of_element_located(By.tagName, 'html'))

	except Exception:
		print "SCREENSHOT GET FAILED FOR URL " + url[0:40]
   		#driver.navigate().refresh()
		db_hash['screenshots'] = {}
		db_hash['elements'] = []
		db_hash['host_status'] = 'unknown'
		db_hash['screenshots']['normal'] = 'unknown'
        	db_hash['screenshots']['crop'] = 'unknown'
        	db_hash['screenshots']['thumb'] = 'unknown'
        	db_hash['screenshots']['full'] = 'unknown'
		envlock = dbenv.lock_detect(db.DB_LOCK_DEFAULT)
		while envlock != 0:
			if args.verbose: print ">>> Lock detected when trying to update " + url[0:40] + ". retrying.."
			time.sleep(1)
			envlock = dbenv.lock_detect(db.DB_LOCK_DEFAULT)
		stalkerdb[url] = json.dumps(db_hash)
		driver.quit()
		return

# NORMAL SCREENSHOT (VIEWPORT)
	print "Taking screenshots for " + url[0:40]
	try:
	    driver.get_screenshot_as_file(screenshot_path)
	except UnexpectedAlertPresentException:
	    alert = driver.switch_to_alert()
	    alert.dismiss()
	    driver.get_screenshot_as_file(screenshot_path)
	    
	#if not os.path.exists(screenshot_path):
	#	print "HOLY COW NO SCREENSHOT", url
	#	print db_hash
	if args.verbose: print ">>> Cropping screenshot for " + url[0:40]
        crop_image(screenshot_name)	
	if args.verbose: print ">>> Creating thumbnail for " + url[0:40]
        thumb_image(screenshot_name)	
	try:
		db_hash['screenshots']['normal'] = screenshot_name
	except:
		print "EXCEPTION ON URL " + url[0:40] + " WHILE TAKING NORMAL SCREENSHOT."
		print db_hash
	db_hash['screenshots']['crop'] = screenshot_crop_name
	db_hash['screenshots']['thumb'] = screenshot_thumb_name
# ELEMENTS (OLD METHOD VIA HEADLESS BROWSER)
	#ids = driver.find_elements_by_xpath('//*[@id]')
	#for ii in ids: #https://stackoverflow.com/questions/20244691/python-selenium-how-do-i-find-all-element-ids-on-a-page
	#    try:
	#         db_hash['elements'].append(ii.get_attribute('id'))
	#    except:
	#	 continue

    	#db_hash['elements'] = len(ids)

# CLOSE CHROMIUM BROWSER
	driver.quit()


# FULL SCREENSHOT
    	dcap = dict(DesiredCapabilities.PHANTOMJS)
	dcap["phantomjs.page.settings.userAgent"] = ( ua.random
     )

       	driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--cookies-file=/tmp/cookies.txt'])
	driver.set_window_size(2048,1024)
        #driver.set_page_load_timeout(20)
	try:
        	driver.get(url)
	    	time.sleep(5)
	except Exception, e:
		print "FULL SCREENSHOT GET FAILED FOR URL " + url[0:40]
                db_hash['host_status'] = str(e)
                db_hash['screenshots']['normal'] = 'unknown'
                db_hash['screenshots']['crop'] = 'unknown'
                db_hash['screenshots']['thumb'] = 'unknown'
                db_hash['screenshots']['full'] = 'unknown'
		envlock = dbenv.lock_detect(db.DB_LOCK_DEFAULT)
		while envlock != 0:
			if args.verbose: print ">>> Lock detected when trying to update " + url[0:40] + ". retrying.."
			time.sleep(1)
			envlock = dbenv.lock_detect(db.DB_LOCK_DEFAULT)
                db[url] = json.dumps(db_hash)
                driver.quit()
                return
	try:
	        if args.verbose: print ">>> Taking full screenshots for " + url[0:40]
        	driver.get_screenshot_as_file(screenshot_full_path) #SOME SITES DENY QUICK SUCCEEDING CONNECTIONS USE VIEW PORT SCREENSHOT INSTEAD
        	db_hash['screenshots']['full'] = screenshot_full_name
	except Exception, e:
	        if args.verbose: print "FULL SCREENSHOT FAILED. USING VIEWPORT INSTEAD."
        	db_hash['screenshots']['full'] = screenshot_name
# CLOSE PHANTOMJS BROWSER
	driver.quit()
# SAVE EVERYTHING TO THE DATABASE
	envlock = dbenv.lock_detect(db.DB_LOCK_DEFAULT)
	while envlock != 0:
		if args.verbose: print ">>> Lock detected when trying to update " + url[0:40] + ". retrying.."
		time.sleep(1)
		envlock = dbenv.lock_detect(db.DB_LOCK_DEFAULT)
	stalkerdb[url] = json.dumps(db_hash)



# UPDATE HTML GALLERY
def create_html(stalkerdb): #https://stackoverflow.com/questions/2301163/creating-html-in-python

	   
        if not os.path.exists(os.path.join(config[group]['html_dir'], 'style.css')):

# HTML STYLING C/O https://www.quackit.com/css/grid/examples/css_grid_photo_gallery_examples.cfm
	    stylesheet = '''
.grid { 
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
	grid-gap: 10px;
	align-items: stretch;
}
.grid img {
	border: 1px solid #ccc;
	box-shadow: 2px 2px 6px 0px  rgba(0,0,0,0.3);
	max-width: 100%;
}
'''
	    with open(os.path.join(config[group]['html_dir'], 'style.css'), "w") as cssfile:
	        cssfile.write(stylesheet)


	doc = dominate.document(title='Sitestalker')
 
	with doc.head:
	     link(rel='stylesheet', href='style.css')
	with doc:
	    with div(_class='grid'):
	        for url in stalkerdb.keys():
		    if args.verbose: print ">>> CREATING HTML ENTRY FOR " + url[0:40]
		    #print "TESTING URL " + url + " IF ACTIVE"
		    if json.loads(stalkerdb[url])['host_status'] != 'ACTIVE': continue
		    #	print "URL " + url + " NOT ACTIVE, SKIPPING"
		    #	continue
		    #else:
		    #	print "URL " + url + " ACTIVE, MAKING HTML"
    		    try:
		        path = os.path.basename(config[group]['screenshot_dir']) + "/" + json.loads(stalkerdb[url])['screenshots']['crop']
		        full_path = os.path.basename(config[group]['screenshot_dir']) + "/" + json.loads(stalkerdb[url])['screenshots']['full']
		    except Exception, e:
			print "WE GOT AN EXCEPTION ON " + url[0:40] + " IN CREATE_HTML"
			print path, full_path
			print e
		    d = div(style="width:image width px; font-size:80%; text-align:center;")
		    with d:
            	        a(img(src=path, width="width", height="height", style="padding-bottom:0.5em; max-width:95%;border:6px double #545565"), href=full_path)
            	        a(url[0:40], style="font-size:1vw", href=url)
                        db_hash = json.loads(stalkerdb[url])
			with td():
			     with table(border="1", style="border-collapse:collapse; font-size:.8vw", align="center", ):
			       for stat in db_hash:
				 with tr():
				   if stat == 'redirects':
					td("redirect_history:", align="right")
				   else:
					td(stat + ":", align="right") 
			           if (isinstance(db_hash[stat], dict)) or (isinstance(db_hash[stat], list)):
			               td(str(len(db_hash[stat])).strip(), align="center")
			           else:
				       if stat=="effective_url":
				           td(a(str(db_hash[stat])[0:30].strip(), href=db_hash[stat]), align="center")
				       else:
				           td(str(db_hash[stat])[0:30].strip(), align="center")
				 if stat == 'redirects':
				      count = 0
				      with tr():
					for url in db_hash[stat]:
					    count+=1
				            with tr():
					        td(a( "   " + str(count) + ". "  + url[0:30], href=url), align="left", colspan="2")
			              with tr():
					count+=1
					td(a("   " + str(count) + ". " + db_hash['effective_url'][0:30], href=db_hash['effective_url']), align="left", colspan="2")
	with open(os.path.join(config[group]['html_dir'], 'index.html'), 'w') as f:
	    if args.verbose: print ">>> WRITING HTML GALLERY"
    	    f.write(doc.render())

def crop_image(screenshot_name): #https://stackoverflow.com/questions/1197172/how-can-i-take-a-screenshot-image-of-a-website-using-python
    
    crop_name = screenshot_name[:-4] 
    screenshot_path = os.path.join(config[group]['screenshot_dir'], screenshot_name)
    crop_path = os.path.join(config[group]['screenshot_dir'], crop_name + "_crop.png")

    result = Popen(' '.join(['convert',  screenshot_path, '-gravity', 'North', '-crop', '%sx%s+0+0' % (800,800), '+repage', crop_path]), shell=True, stdout=PIPE).stdout.read()
    if len(result) > 0 and not result.isspace():
        raise Exception(result)
    #if args.verbose: print ">>> Crop image written to " + crop_path

def thumb_image(screenshot_name): #https://stackoverflow.com/questions/1197172/how-can-i-take-a-screenshot-image-of-a-website-using-python
    thumb_name = screenshot_name[:-4] 
    screenshot_path = os.path.join(config[group]['screenshot_dir'], screenshot_name)
    thumb_path = os.path.join(config[group]['screenshot_dir'], thumb_name + "_thumb.png")

    result = Popen(' '.join(['convert',  screenshot_path, '-filter', 'Lanczos', '-thumbnail', '%sx%s' % (500,500), thumb_path]), shell=True, stdout=PIPE).stdout.read()
    if len(result) > 0 and not result.isspace():
        raise Exception(result)

class get_url(threading.Thread):
    def __init__(self, url, stalkerdb):
        threading.Thread.__init__(self)
        self.url = url
	self.stalkerdb = stalkerdb

    def run(self):

	current_data = {}
	global previous_data
    	global update_html
	methodrex = re.search(r'(^https?)', self.url, re.IGNORECASE)
	hostname = urlparse(self.url).hostname
        try:
	    method = methodrex.group(0)
	except:
	    self.url = 'http://' + self.url

	current_data['content_length'] = 'unknown'
	current_data['status_code'] = 'unknown'
	current_data['reason'] = 'unknown'
	current_data['response_length'] = 'unknown'
	current_data['change_status'] = 'unknown'
	current_data['effective_url'] = 'unknown'
	current_data['headers'] = {}
	current_data['elements'] = []
	current_data['redirects'] = []


	try:	
	   if ipaddress.ip_address(unicode(socket.gethostbyname(hostname))).is_private == True:
		if args.verbose: print ">>> Hostname maps to loopback address. Skipping..."
		current_data['host_status'] = 'PRIVATE IP ASSIGNED'
	   else:
	       print "Browsing " + self.url[0:40] + "..."
	       res = requests.get(self.url, timeout=10)
	       current_data['host_status'] = 'ACTIVE'
	except requests.exceptions.Timeout:
        	current_data['host_status'] = 'CONNECTION TIMED OUT'
	except requests.exceptions.ConnectionError:
        	current_data['host_status'] = 'CONNECTION ERROR'
	except requests.exceptions.HTTPError:
        	current_data['host_status'] = 'HTTP ERROR'
	except requests.exceptions.TooManyRedirects:
        	current_data['host_status'] = 'TOO MANY REDIRECTS'
	except :
        	current_data['host_status'] = 'UNKNOWN ERROR'

	if current_data['host_status'] == 'ACTIVE':
		try:
		    current_data['content_length'] = res.headers['content-length'] 
		except:
		    current_data['content_length'] = 'unknown'
		current_data['status_code'] = res.status_code 
       		current_data['reason'] = res.reason 
		current_data['response_length'] = len(res.content)
		current_data['effective_url'] = res.url
		#if args.verbose: print ">>> Extracting HTTP headers for " + self.url[0:40]
        # SAVE HEADERS
		for k,v in res.headers.iteritems():
	     	    current_data['headers'][k] = [v]
	# SAVE ELEMENTS 
		#if args.verbose: print ">>> Extracting XPATH elements for " + self.url[0:40]
		try:
	            tree = html.fromstring(res.content)
	            trs = tree.xpath('//*')
	            elements_with_id = [tr for tr in trs if tr.attrib.get('id') != None]
		    for element in elements_with_id:
		        try:
	                    elementid = str(element.attrib.get('id'))
		        except:
			    continue
		        #current_data['elements'].append(str(element.attrib.get('id')))
		        current_data['elements'].append(elementid)
		except:
			if args.verbose: print ">>> No XPATH elements found for " + self.url[0:40]
        # SAVE REDIRECT URLS
		for redirect in res.history:
		    current_data['redirects'].append(redirect.url)
	else:
		if args.verbose: print current_data['host_status'] + " FOR " + self.url[0:40] + " skipping.."
		current_data['change_status'] = 'error'
		envlock = dbenv.lock_detect(db.DB_LOCK_DEFAULT)
		while envlock != 0:
			if args.verbose: print ">>> Lock detected when trying to update " + url[0:40] + ". retrying.."
			time.sleep(1)
			envlock = dbenv.lock_detect(db.DB_LOCK_DEFAULT)
	        self.stalkerdb[self.url] = json.dumps(current_data)
		return


	# COMPARE NEW AND PREVIOUS STATS
	if self.url in self.stalkerdb: 
            stalkerdb_hash = json.loads(stalkerdb[self.url])
	    changed_stats = compare_stats(self.url, stalkerdb, current_data, previous_data)
	    if len(changed_stats) >= config[group]['min_stats'] : 
		update_html = True
		stalkerdb_hash['change_status'] = 'updated'
		print "Stats changed for " + self.url[0:40] + "..."
		## SAVE THE CHANGED STATS TO THE EXISTING DB ENTRY
	        for stat in changed_stats:
		    if isinstance(stalkerdb_hash[stat], dict) :
		        print "\t" + stat + " - Old: " + str(len(stalkerdb_hash[stat])) + "\tNew: " + str(len(current_data[stat]))
			stalkerdb_hash[stat] = {} # EMPTY  EXISTING DICT BEFORE PUTTING NEW ITEMS
			for k,v in current_data[stat].iteritems():
				stalkerdb_hash[stat][k] = [v]

		    elif isinstance(stalkerdb_hash[stat], list):
		        print "\t" + stat + " - Old: " + str(len(stalkerdb_hash[stat])) + "\tNew: " + str(len(current_data[stat]))
		    	stalkerdb_hash[stat] = [] # EMPTY EXISTING LIST BEFORE PUTTING NEW ITEMS
			for i in current_data[stat]:
			    stalkerdb_hash[stat].append(i)
		    else: 
			print "\t" + stat + " - Old: " + str(stalkerdb_hash[stat]) + "\tNew: " + str(current_data[stat])
			stalkerdb_hash[stat] = current_data[stat] # JUST REPLACE THE OLD ITEM WITH THE NEW ONE

		## SAVE THE HOST STATUS SO WE DON'T SKIP INACTIVE HOSTS THAT BECAME ACTIVE WHEN SENDING NOTIFICATION OR CREATING GALLERY
		stalkerdb_hash['host_status'] = current_data['host_status']
		envlock = dbenv.lock_detect(db.DB_LOCK_DEFAULT)
		while envlock != 0:
			if args.verbose: print ">>> Lock detected when trying to update " + url[0:40] + ". retrying.." 
			time.sleep(1)
			envlock = dbenv.lock_detect(db.DB_LOCK_DEFAULT)
	        self.stalkerdb[self.url] = json.dumps(stalkerdb_hash)
            else:		
		## IF NOTHING HAS CHANGED, SET change_status TO unmodified
		if args.verbose: print ">>> No change seen on " + self.url[0:40] + "..."
		stalkerdb_hash['change_status'] = 'unmodified'
		envlock = dbenv.lock_detect(db.DB_LOCK_DEFAULT)
		while envlock != 0:
			if args.verbose: print ">>> Lock detected when trying to update " + url[0:40] + ". retrying.." 
			time.sleep(1)
			envlock = dbenv.lock_detect(db.DB_LOCK_DEFAULT)
	        self.stalkerdb[self.url] = json.dumps(stalkerdb_hash)
	else:
	      ## IF IT IS A COMPLETELY NEW ENTRY, SAVE THE current_data, SET change_status TO new
	      update_html = True
	      current_data['change_status'] = 'new'
	      envlock = dbenv.lock_detect(db.DB_LOCK_DEFAULT)
	      while envlock != 0:
		if args.verbose: print ">>> Lock detected when trying to update " + url[0:40] + ". retrying.." 
		time.sleep(1)
		envlock = dbenv.lock_detect(db.DB_LOCK_DEFAULT)
	      self.stalkerdb[self.url] = json.dumps(current_data)

def compare_stats(url, stalkerdb, current_data, previous_data):
    changed_stats = []
    previous_data[url] = {}
    db_hash = json.loads(stalkerdb[url])
    for stat in config[group]['monitored_stats']:
        if isinstance(json.loads(stalkerdb[url])[stat], dict) or isinstance(json.loads(stalkerdb[url])[stat], list):
            if len(json.loads(stalkerdb[url])[stat]) != len(current_data[stat]):
                changed_stats.append(stat)
                if isinstance(json.loads(stalkerdb[url])[stat], dict):
	    	    previous_data[url][stat] = {}
	            for i in db_hash[stat]:
			 previous_data[url][stat][i] = db_hash[stat][i]
 	        else:
		    previous_data[url][stat] = []
		    for i in db_hash[stat]:
			previous_data[url][stat].append(i)	
        else:
            if json.loads(stalkerdb[url])[stat] != current_data[stat]:
                 changed_stats.append(stat)
	         previous_data[url][stat] = db_hash[stat]
    return changed_stats
	    
            



def get_stats(url, stalkerdb, threads):
    get_url_thread = get_url(url, stalkerdb)
    threads.append(get_url_thread)
    get_url_thread.start()

def purge_url(purged_url, stalkerdb):

    url = purged_url
    global update_html

    if url in stalkerdb.keys() and 'screenshots' in json.loads(stalkerdb[url]):
        if 'screenshots' in json.loads(stalkerdb[url]): 
            print "Purging " + url[0:40]
            db_hash = json.loads(stalkerdb[url])
            try:
	        del stalkerdb[url]
		update_html = True
            except Exception, e:
	        if args.verbose: print ">>> " +  url[0:40] + str(e) + " . Skipping.."
	        return 
# DELETE SCREENSHOTS
            for img_size in db_hash['screenshots']:
	        img_path = os.path.join(config[group]['screenshot_dir'], db_hash['screenshots'][img_size])
	        if args.verbose: print ">>> Deleting " + img_path + "..." 
                try:
	           os.remove(img_path)
	        except:
	           if args.verbose: print ">>> Unable to delete " + img_path + "..."
	           continue
        else:
	    if args.verbose: print ">>> Purging " + url[0:40] + " skipped. Duplicate infile entry for " + url[0:40] 
	    return
    else:
	if args.verbose: print ">>> Purging " + url[0:40] + " skipped. No longer exists."
	return 
    return 0

def send_notification(stalkerdb):

    TO_div = ', '
    msg = MIMEMultipart()
    msg['Subject'] = config[group]['email_alerts']['subject'] + " (" + group + ")"
    msg['From'] = config[group]['email_alerts']['sender']
    msg['To'] = TO_div.join(config[group]['email_alerts']['recipients'])
    msg.preamble = config[group]['email_alerts']['subject']


    doc = dominate.document(title='Sitestalker Notification')
    with doc:
	d_msg = div()
	with d_msg:
		p("Sitestalker has detected changes to the following url(s) under group " + "\"" + group + "\"" + ". Click ", a("here ", href=config[group]['sitestalker_baseurl']), "to view all monitored sites.")
		
	    
        for url in stalkerdb.keys():
            if json.loads(stalkerdb[url])['host_status'] != 'ACTIVE': 
		if args.verbose: print url[0:40] + " is not active. Skipping.."
		continue
            if json.loads(stalkerdb[url])['change_status'] == 'unmodified': 
		if args.verbose: print url[0:40] + " is not modified. Skipping.."
		continue
            try:
		
	        screenshot_thumb_name = json.loads(stalkerdb[url])['screenshots']['thumb']
                screenshot_thumb_path = os.path.join(config[group]['screenshot_dir'], screenshot_thumb_name)

   	    except:
	            print "SEND NOTIFICATION EXCEPTION ON " + url[0:40] 
		    print json.loads(stalkerdb[url])
	    d = div(style="width:image width px; font-size:80%; text-align:left;")
	    img_url = config[group]['sitestalker_baseurl'] + "/" + os.path.basename(config[group]['screenshot_dir']) + "/" + json.loads(stalkerdb[url])['screenshots']['full']
	    with d:
	        br()
		with table(border="1"):
                 with tbody():
		    with tr():
		         th(h3(defang(url)[0:30] + "... (" + json.loads(stalkerdb[url])['change_status'] + ")"), colspan="2", align="left")
		    with tr():
			 th('Stats',  align="center")
			 th('Screenshot (click to enlarge)', align="center")
		    with tr():
			if url in previous_data:
			   with td():
				with table(border="1", style="border-collapse:collapse"):
				       th('')
				       th('Old', align="center")
				       th('New', align="center")
		                       for stat in previous_data[url]:
				     	  with tr():
			                          if (isinstance(previous_data[url][stat], dict)) or (isinstance(previous_data[url][stat], list)):
				                    td(stat + ":") 
						    td(str(len(previous_data[url][stat])).strip(), align="center")
						    td(str(len(json.loads(stalkerdb[url])[stat])).strip(), align="center")
			                          else:
				                     td(stat + ":")
						     td(str(previous_data[url][stat]).strip(), align="center")
						     td(str(json.loads(stalkerdb[url])[stat]).strip(), align="center")
                        else:
                           db_hash = json.loads(stalkerdb[url])
			   with td():
			     with table(border="1", style="border-collapse:collapse"):
			       for stat in db_hash:
				 with tr():
				   if stat == 'redirects':
					td("redirects:")
				   else:
					td(stat + ":") 
			           if (isinstance(db_hash[stat], dict)) or (isinstance(db_hash[stat], list)):
			               td(str(len(db_hash[stat])).strip(), align="center")
			           else:
				       td(defang(str(db_hash[stat])[0:30].strip()), align="center")
				 if stat == 'redirects':
				      count = 0
				      with tr():
					for url in db_hash[stat]:
					    count+=1
				            with tr():
					        td( "   " + str(count) + ". "  + defang(url)[0:30], colspan="2")
			              with tr():
					count+=1
					td("   " + str(count) + ". " + defang(db_hash['effective_url'])[0:30], colspan="2")
		        with td(align="center"):
				a(img(src="cid:" + screenshot_thumb_name), href=img_url)
	    #if args.verbose: print ">>> Attaching thumbnail " + screenshot_thumb_path + " for " + url[0:40]
 	    fp = open(screenshot_thumb_path, 'rb')	
	    msgImage = MIMEImage(fp.read())
	    fp.close()
	    msgImage.add_header('Content-ID', '<' + screenshot_thumb_name + '>')
	    msg.attach(msgImage)
	
    #print doc.render()
    #msg.attach(MIMEText(config[group]['email_alerts']['message'], "plain"))
    if args.verbose: print ">>> Attaching html to email notification.."
    try:
	msg.attach(MIMEText(doc.render(), "html"))
    except:
	if args.verbose: print ">>> Exception while attaching html to notification.."
	print doc.render()
    context = ssl.create_default_context()
    print "Sending email notification to " + TO_div.join(config[group]['email_alerts']['recipients'])
    server = smtplib.SMTP_SSL(config[group]['email_alerts']['smtp_server'], config[group]['email_alerts']['smtp_port']) 
    #server.set_debuglevel(1)
    if config[group]['email_alerts']['password'] == "sender_email_password" or config[group]['email_alerts']['password'] == "":
	email_password = getpass.getpass(prompt='Email Password for "' + group + '" group:')
    else:
	email_password = config[group]['email_alerts']['password']
    server.login(config[group]['email_alerts']['sender'], email_password)
    try:
        server.sendmail(config[group]['email_alerts']['sender'], config[group]['email_alerts']['recipients'], msg.as_string())
    except Exception, e:
	print "Sending notification failed: " + str(e)
	pass
    server.quit()
    	
	
def extract_urls(line):	

# MISC CLEANUP
    line = line.replace('[:]', ':')
    line = line.replace('[.]', '.')
    line = line.replace('[://]', '://')
    line = line.replace('"', '')
    line = refang(line)
    line = line.strip()
    line = line.decode("utf-8", "ignore").encode("utf-8", "ignore").lower()

    domains = line.split()
    newurls = []
    purgeurls = []
    skipurls = []

    for domain in domains:
       domain = domain.strip()
       if len(domain) > 2000: 
	  if args.verbose: print ">>> DOMAIN " + domain + " TOO LONG. Skipping.."
	  continue 

## CONVERT INPUT DOMAINS INTO PROPER URLs
       if (domain[0:4] != 'http' and domain[0] != '-' and domain[0] != '#'): 
	     newurl = 'http://' + domain
	     newurl = urlparse(newurl)
	     newurls.append(newurl.geturl())
       elif domain[0] == '-': # 
	     if domain[1:5] != 'http':
	         purgeurl = 'http://' + domain
	         purgeurl = purgeurl.replace('http://-','-http://')
		 purgeurl = urlparse(purgeurl)
		 purgeurls.append(purgeurl.geturl())
	     else:	
		purgeurl = urlparse(domain)
	        purgeurls.append(purgeurl.geturl())
       elif domain[0] == '#':
	     if domain[1:5] != 'http':
	        skipurl = 'http://' + domain
	        skipurl = skipurl.replace('http://#','#http://')
		skipurl = urlparse(skipurl)
		skipurls.append(skipurl.geturl())
	     else:
		skipurl = urlparse(domain)
	        skipurls.append(skipurl.geturl())
       else:
	   newurl = urlparse(domain)
	   newurls.append(newurl.geturl())
	      

## EXTRACT ALL URLs ON EACH LINE OF INPUT
    ## https://mail.python.org/pipermail/tutor/2002-February/012481.html
    urls = '(%s)' % '|'.join("""http https""".split())
    ltrs = r'\w'
    gunk = r'/#~:.?+=&%@!\-'
    punc = r'.:?\-'
    any = "%(ltrs)s%(gunk)s%(punc)s" % { 'ltrs' : ltrs,
                                         'gunk' : gunk,
                                         'punc' : punc }
    url = r"""
        \b                            # start at word boundary
        (                             # begin \1 {
            %(urls)s    :             # need resource and a colon
            [%(any)s] +?              # followed by one or more
                                      #  of any valid character, but
                                      #  be conservative and take only
                                      #  what you need to....
        )                             # end   \1 }
        (?=                           # look-ahead non-consumptive assertion
                [%(punc)s]*           # either 0 or more punctuation
                [^%(any)s]            #  followed by a non-url char
            |                         # or else
                $                     #  then end of the string
        )
        """ % {'urls' : urls,
               'any' : any,
               'punc' : punc }
    url_re = re.compile(url, re.VERBOSE)
    newmatch = url_re.findall(" ".join(newurls))
    skipmatch = url_re.findall(" ".join(skipurls))
    purgematch = url_re.findall(" ".join(purgeurls))

    extractedurls = {}
    for item in newmatch:
	url = urlparse(item[0])
	hostname = url.netloc
	hostname = hostname.strip()
	if not re.search(r'[a-zA-Z]+\.', hostname):
	    continue 
	url = url.geturl()
        extractedurls[url] = 0

    for item in skipmatch:
	url = urlparse(item[0])
	hostname = url.netloc
	hostname = hostname.strip()
	if not re.search(r'[a-zA-Z]+\.', hostname):
	   continue
	url = url.geturl()
        extractedurls[url] = -1

    for item in purgematch:
	url = urlparse(item[0])
	hostname = url.netloc
	hostname = hostname.strip()
	if not re.search(r'[a-zA-Z]+\.', hostname):
	   continue
	url = url.geturl()
        extractedurls[url] = 1
    return extractedurls

def cleanup(stalkerdb, lock_file, service):
	if args.verbose: print ">>> Syncing database..."
	stalkerdb.sync()
	if args.verbose: print ">>> Closing database..."
	stalkerdb.close()
	if args.verbose: print ">>> Stopping webdriver service..."
	service.stop()	
	if args.verbose: print ">>> Removing sitestalker lock file..."
	os.remove(lock_file)
	
if __name__ == '__main__':
    
    if not args.test_infile:
        lock_file = os.path.join(os.getcwd(), ".stalker.lock") # CHECK ANY RUNNING INSTANCE
        if os.path.exists(lock_file):
           for start_time in open(lock_file, "r"):
              if args.verbose: print " >>> Another instance of sitestalker is running since " + start_time + ". Try removing \".stalker.lock\" file."
           exit()
        else:
           if args.verbose: print ">>> Creating lockfile"
           with open(lock_file, "w") as l:
	       l.write(datetime.datetime.now().strftime("%H:%M %Y-%m-%d"))
	   
           if args.verbose: print ">>> Lock file created..."
# START CRHOMEDRIVER SERVICE ONCE TO SAVE MEMORY RESOURCES
        service = Service('/usr/lib/chromium-browser/chromedriver')
        service.start()
# PROCESS CONFIG FILE
    if not os.path.exists(args.configfile):
		configdata = { 'sitestalker':{
					'db_dir': 'stalker_db',
					'db_file': 'stalker.db',
					'screenshot_dir': '/var/www/html/sitestalker/images', 
					'sitestalker_baseurl': 'http://www.infosecscripts.org/sitestalker', 
					'polling_threads' : 20, 
					'monitored_stats': [
							#'content_length', 
							'response_length', 
							'status_code', 
							#'reason', 
							'headers',
							'redirects',
							'elements'
							], 
					'min_stats': 3,
					'poll_history': 5,
					'html_dir': '/var/www/html/sitestalker',
					'email_alerts': {
						'subject' : '[sitestalker] Updates Seen on Monitored Sites',
						'sender'  : 'sender_email@gmail.com',
						'password'  : 'sender_email_password',
						'recipients' : ['soc@yourcompany.com', 'soc2@yourcompany.com'],
						'smtp_server' : 'smtp.gmail.com',
						'smtp_port' : 465
						}
					
				  }, 
				    'group1':{
					'db_dir': 'stalker_db',
					'db_file': 'group1.db',
					'screenshot_dir': '/var/www/html/sitestalker/group1/images', 
					'sitestalker_baseurl': 'http://www.infosecscripts.org/sitestalker/group1', 
					'polling_threads' : 20, 
					'monitored_stats': [
							'content_length', 
							'response_length', 
							'status_code', 'reason', 
							'headers',
							'redirects',
							'elements'
							], 
					'min_stats': 4,
					'poll_history': 5,
					'html_dir': '/var/www/html/sitestalker/group1',
					'email_alerts': {
						'subject' : '[sitestalker] Updates Seen on Monitored Sites',
						'sender'  : 'sender_email@gmail.com',
						'password'  : 'sender_email_password',
						'recipients' : ['soc@yourcompany.com', 'soc2@yourcompany.com'],
						'smtp_server' : 'smtp.gmail.com',
						'smtp_port' : 465
						}
					
				  } 
                               }

		if args.verbose: print ">>> Writing default config file into " + args.configfile
		with io.open(args.configfile, 'w', encoding='utf8') as outfile:
    			yaml.dump(configdata, outfile, default_flow_style=False, allow_unicode=True)
		print "Configuration file written to " + args.configfile + ". Edit this file before running the script.\nSee https://github.com/gitb0y/sitestalker" 
	        if args.verbose: print ">>> Removing sitestalker lock file..."
	        try:
	           os.remove(lock_file)
	        except:
		   pass
		exit()

    print "Reading config file: " + args.configfile
    config = yaml.load(open(args.configfile))

    for group in config:
	print "Processing group \"" + group + "\" in " + args.configfile + "..."
	threads = []
	ua = UserAgent()

# CREATE NECESSARY FOLDERS
	if not args.test_infile:
            if not os.path.exists(config[group]['screenshot_dir']) or not os.path.isdir(config[group]['screenshot_dir']):
	        if args.verbose: print ">>> Creating screenshots directory " + config[group]['screenshot_dir']
	        try:
		    os.makedirs(config[group]['screenshot_dir'])
	        except:
		    print "Unable to create a screenshot folder at " + config[group]['screenshot_dir'] + ". Check permissions or create it first."
        	    sys.exit(0)

            if not os.path.exists(config[group]['html_dir']) or not os.path.isdir(config[group]['html_dir']):
	        if args.verbose: print ">>> Creating html output directory " + config[group]['html_dir']
	        try:
		    os.makedirs(config[group]['html_dir'])
	        except:
		    print "Unable to create a html output folder at " + config[group]['html_dir'] + ". Check permissions or create it first.."
        	    sys.exit(0)

            if not os.path.exists(config[group]['db_dir']) or not os.path.isdir(config[group]['db_dir']):
	        if args.verbose: print ">>> Creating database file directory " + config[group]['db_dir']
	        try:
		    os.makedirs(config[group]['db_dir'])
	        except:
		    print "Unable to create a database folder at " + config[group]['db_dir'] + ". Check permissions or create it first.."
        	    exit(0)

# SETUP THE DATABASE ENVIRONMENT, OPEN THREADED DATABASE FOR ASYNCHRONOUS READ/WRITES
	    db_path = os.path.join(os.getcwd(),config[group]['db_dir'],config[group]['db_file'])
	    html_path = os.path.join(config[group]['html_dir'],'index.html')
	    dbenv = db.DBEnv()
	    dbenv.open(config[group]['db_dir'], db.DB_INIT_LOCK | db.DB_INIT_MPOOL | db.DB_CREATE | db.DB_THREAD , 0)
	    stalkerdb = db.DB(dbenv)
	    if args.verbose: print ">>> Opening database file " + db_path
	    db_handle = stalkerdb.open(db_path, None, db.DB_HASH, db.DB_CREATE | db.DB_THREAD  )
	    if db_handle == None:
	        if args.verbose: print ">>> Database open successful..."
	    else:
	        print "Database open failed. (" + str(db_handle) + ") Exiting.."
	        exit()
	


        thread_count = 0	
	processed_urls = []
# PROCESS INPUT FILE
        if args.infile:
          if group == args.group_name:
	      if args.test_infile:  print "Testing input file " + args.infile + " for group \"" + args.group_name + "\"..."
	      if not args.test_infile: print "Processing input file " + args.infile + " for group \"" + group + "\"..."
	      if args.verbose: print ">>> Processing input file " + args.infile + " for group " + "\"" + group + "\""

	      line_count = 0 
	      input_file = open(args.infile, "r")
	      input_lines = len(open(args.infile).readlines())
              url_count = 0
              purge_count = 0
              skip_count = 0
	      process_count = 0

	      unique_urls = {}

              for line in input_file:
	          line_count += 1
		  urls = extract_urls(line) # EXTRACT ALL VALID URLs ON EACH LINE OF INPUT
		  for url in urls:
		      if url in unique_urls:
			    if args.verbose: print "  >>> " + url[0:40] + " Already seen. Duplicate entries?"
			    continue
		      else:
			    unique_urls[url] = None
		      url_count += 1
		      if urls[url] == -1: 
			if args.test_infile: 
		           if args.verbose: print ">>> Will skip " + url[0:40]
			   skip_count += 1
			   continue
			if args.verbose: print ">>> Skipping " + url[0:40]
			continue
		      if urls[url] == 1:
			  if args.test_infile: 
				if args.verbose: print ">>> Will purge " + url[0:40]
			        purge_count += 1
				continue
		          if not args.test_infile:
                              purge_url(url, stalkerdb) 
		     	      continue

		      if args.test_infile:
			   if args.verbose: print ">>> Will process " + url[0:40]
			   process_count += 1
			   continue
	              get_stats (url, stalkerdb, threads)      
	              processed_urls.append(url)
	              thread_count += 1
	              if thread_count == config[group]['polling_threads'] or (line_count == input_lines  and url_count == len(urls)):
	                 if args.verbose: print ">>> Thread count (new): " + str(thread_count) + " .Joining threads..\n"
                         for thread in threads:
                              thread.join()
                              sys.stdout.flush()
         	              threads = []
		              thread_count = 0
			 url_count = 0

              if args.test_infile:
	           print "\nInput Count: " + str(url_count)
	           print "To Purge: " + str(purge_count)
	           print "To Skip: " + str(skip_count)
	           print "To Process: " + str(process_count) 
		   print "=====================\n"
	           exit() 
	  else:
		if args.verbose: print ">>> --group-name \"" + args.group_name + "\" doesn\'t match \"" + group + "\" group in \"" + args.configfile + "\" Skipping.."
        if not args.test_infile:
            for thread in threads:
                  thread.join()
                  sys.stdout.flush()
                  threads = []

#	free_mem =  dict(psutil.virtual_memory()._asdict())['free'] - FOR FUTURE IMPLEMENTATION THREADED INSTANCE OF WEBDRIVER FOR FASTER SCREENSHOT CAPTURES
	#print "FREE MEM AFTER REQUESTS IS " + str(free_mem)
	    if not os.path.exists(db_path):
	         print "No existing database, no input file, nothing to do. Exiting..."
	         if args.verbose: print ">>> Removing sitestalker lock file..."
	         try:
	            os.remove(lock_file)
	         except:
		    pass
	         exit()
	    else:
	        if len(stalkerdb.keys()) == 0:
		    print "Database " + config[group]['db_file'] + " empty. Nothing else to do. Moving on..." 
		    if args.verbose: print ">>> Purging empty database and html gallery..."
		    try:
		        stalkerdb.close()
		        os.remove(db_path)
		        os.remove(html_path)
		    except:
		        pass
	            if args.verbose: print ">>> Removing sitestalker lock file..."
	            try:
	                os.remove(lock_file)
	            except:
		        pass
		    continue
	        url_count = len(stalkerdb.keys()) - len(processed_urls) 
	        url_db_count  = 0
	
                for url in stalkerdb.keys():
		    if url in processed_urls: 
			    continue
		    print "Gettign stats for " + url
	            get_stats (url, stalkerdb, threads)      
	            thread_count += 1
		    url_db_count += 1
	            if thread_count == config[group]['polling_threads'] or url_db_count == len(stalkerdb.keys()):
	               if args.verbose: print "\n>>> Thread count (old): " + str(thread_count) + " .Joining threads..\n"
                       for thread in threads:
                          thread.join()
                          sys.stdout.flush()
         	          threads = []
		          thread_count = 0
                for thread in threads:
                    thread.join()
                    sys.stdout.flush()
         	    threads = []
	    if update_html:
		    time.sleep(10)
		    for url in stalkerdb.keys():
		         if (json.loads(stalkerdb[url])['change_status'] == 'updated' or json.loads(stalkerdb[url])['change_status'] == 'new') and json.loads(stalkerdb[url])['host_status'] == 'ACTIVE': 
		              get_screenshot(url, stalkerdb, json.loads(stalkerdb[url])['change_status'])
		    print "Updating HTML gallery in " + os.path.join(config[group]['html_dir'], "index.html...")
		    create_html(stalkerdb)
		    send_notification(stalkerdb)


	    active_count = 0
	    inactive_count = 0
	    print "\nActive Hosts:"
	    for url in stalkerdb.keys():
		host_status = str(json.loads(stalkerdb[url])['host_status'])
		change_status = str(json.loads(stalkerdb[url])['change_status'])
		
		if host_status == 'ACTIVE':
		    active_count += 1
	            print "\t" + url[0:40] 
   		    #print str(json.loads(stalkerdb[url]))
	    if args.verbose: print "\nInactive Hosts:"
	    for url in stalkerdb.keys():
		host_status = str(json.loads(stalkerdb[url])['host_status'])
		change_status = str(json.loads(stalkerdb[url])['change_status'])
		if host_status != 'ACTIVE':
		    inactive_count += 1
	            print "\t" + url[0:40]  + " (" + host_status + ")"

	    cleanup(stalkerdb, lock_file, service)

	    print "\nActive Hosts : " + str(active_count)
	    print "Inactive Hosts: " + str(inactive_count)
	    print "=====================\n"
	    print "\nDone. " + datetime.datetime.now().strftime("%H:%M %Y-%m-%d") 
	    elapsed_time =  time.time() - startTime
            print "Elapsed time: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
