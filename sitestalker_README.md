# sitestalker
[![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)](https://www.python.org/downloads/release/python-360/)


_**sitestalker**_ consumes a list of URLs or domains and constantly tracks changes in certain parameters. These parameters are any or combination of the following:

* Content Length - this is an optional [HTTP header](https://en.wikipedia.org/wiki/List_of_HTTP_header_fields).
* Response Length - the computed length of the response from a **GET** request.
* Status Code - refers to [HTTP Status Codes](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes) returned by the server.
* Reason - a short textual description of the status code.
* Headers - number of HTTP headers returned by a server.
* Elements - number of elements by ID found on the returned page through XPath notation.

Once changes are detected from the previous run, an alert is sent via email. An HTML page containing screenshots of all active hosts is also created. See sample from this [link](http://infosecscripts.org/sitestalker/test/index.html) (click on the images to view their full size.)

This tool was initially intended to be used for tracking domains that appear to be suspicious. Malicious authors often register domains that closely resembles that of their target organization's when launching a phishing campaign (i.e., [typo-squatting](https://en.wikipedia.org/wiki/Typosquatting)). 

Sometimes, these domains don't have any content yet or in a "parked" status. This tool enables you to monitor these sites and get alerted as soon as the contents have changed (e.g., no longer redirects to a domain registrar's default page). A screen capture of the infringing website is often enough to initiate a takedown process.

### Sample Console Output
**First Run:**
```bash
$ python -W ignore sitestalker.py -i alexa_10.txt -c alexa10_config.yaml

Browsing http://youtube.com...
Browsing http://facebook.com...
Browsing http://baidu.com...
Browsing http://wikipedia.org...
Browsing http://qq.com...
Browsing http://taobao.com...
Browsing http://tmall.com...
Browsing http://yahoo.com...
Browsing http://amazon.com...
Browsing http://sohu.com...
Taking screenshots for http://baidu.com
Taking screenshots for http://sohu.com
Taking screenshots for http://youtube.com
Taking screenshots for http://amazon.com
Taking screenshots for http://facebook.com
Taking screenshots for http://qq.com
Taking screenshots for http://taobao.com
Taking screenshots for http://tmall.com
Taking screenshots for http://wikipedia.org
Taking screenshots for http://yahoo.com
Updating HTML gallery..
	http://baidu.com (ACTIVE)
	http://sohu.com (ACTIVE)
	http://youtube.com (ACTIVE)
	http://amazon.com (ACTIVE)
	http://facebook.com (ACTIVE)
	http://qq.com (ACTIVE)
	http://taobao.com (ACTIVE)
	http://tmall.com (ACTIVE)
	http://wikipedia.org (ACTIVE)
	http://yahoo.com (ACTIVE)
```
**Second Run:**

# Requirements
### Python Libraries
### BerkeleyDB
### Selenium Webdriver


# Configuration
# Help Menu
# Sample Output
