# sitestalker
[![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)](https://www.python.org/downloads/release/python-360/)


_**sitestalker**_ consumes a list of URLs or domains and constantly tracks changes in certain parameters. These parameters are any or combination of the following:

* Content Length - this is an optional [HTTP header](https://en.wikipedia.org/wiki/List_of_HTTP_header_fields).
* Response Length - the computed length of the response from a **GET** request.
* Status Code - refers to [HTTP Status Codes](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes) returned by the server.
* Reason - a short textual description of the status code.
* Headers - number of HTTP headers returned by a server.
* Elements - number of elements by ID found on the returned page through XPath notation.

Once changes are detected from the previous run, an alert is sent via email. An HTML page containing screenshots of all active hosts is also created. See sample from this [link](http://infosecscripts.org/sitestalker/test/index.html) (click on the images to view their full sizes.)

This tool was initially intended to be used for tracking domains that appear to be suspicious. Malicious authors often register domains that closely resembles that of their target organization's when launching a phishing campaign (i.e., [typo-squatting](https://en.wikipedia.org/wiki/Typosquatting)). 

Sometimes, these domains don't have any content yet or in a "parked" status. This tool enables you to monitor these sites and get alerted as soon as the contents have changed (e.g., no longer redirects to a domain registrar's default page). A screen capture of the infringing website is often enough to initiate a takedown process.

### Sample Console Output
**First Run:**
```bash
$ python sitestalker.py -i sample.txt

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
```
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
Stats changed for http://qq.com...
	content_length - Old: 46944	New: 46882
	response_length - Old: 241375	New: 241278
	elements - Old: 0	New: 158
Taking screenshots for http://qq.com
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
# Requirements
## BerkeleyDB
**sitestalker** uses an embedded/nosql database BerkeleyDB from Oracle to store monitored sites' statistics and compare the latest from the previous run.
The last version of BerkeleyDB that doesn't have a commercial license is 5.3.x. **sitestalker** makes use of BerkeleyDB 5.3.28 which can be downloaded from this [link](https://www.oracle.com/technetwork/database/database-technologies/berkeleydb/downloads/index-082944.html).

Instructions for building and installation of BerkeleyDB can be found on this [site](https://docs.oracle.com/cd/E17076_05/html/installation/build_unix.html). Typical steps are summarized below:
```
$ cd build_unix
$ ../dist/configure
$ make
$ sudo make install
...
...
Installing DB include files: /usr/local/BerkeleyDB.5.3/include ...
Installing DB library: /usr/local/BerkeleyDB.5.3/lib ...

```
## Python Bindings for BerkeleyDB (bsddb3)
The next step is to install the python library **bsddb3** which provides bindings for the BerkeleyDB database. The latest version comapatible with version 5.3.x can be downloaded from this [page](https://www.jcea.es/programacion/pybsddb.htm) which contains all necessary information: 

###### [bsddb3-5.3.0](https://pypi.org/project/bsddb3/5.3.0/): Testsuite verified with Unix 32 bit Python 2.4-2.7 and 3.1-3.2, and **Berkeley DB 4.3-5.3**. (20120116)

To build and install, use the following command below:

```
python setup.py --berkeley-db-incdir=/usr/local/BerkeleyDB.5.3/include --berkeley-db-libdir=/usr/local/BerkeleyDB.5.3/lib install
```
##  Webdriver and Headless Browser
To take website screenshots, **sitestalker** has to render the webpage on a "headless" browser (a real browser minus the GUI). These so-called "headless browsers" are in turn controlled by a "webdriver" application. Within a python script, webdrivers are controlled using Selenium library that exposes bindings for the webdriver protocol.

The following packages are used by **sitestalker** and were installed via "apt install" command on Ubuntu 16.04
```
$ apt-cache policy chromium-browser
chromium-browser:
  Installed: 71.0.3578.98-0ubuntu0.16.04.1

$ apt-cache polichy chromium-chromedriver:
chromium-chromedriver:
  Installed: 71.0.3578.98-0ubuntu0.16.04.1
 
 ```
Another headless browser, **phantomjs** is used to take full page screenshots. This headless browser although no longer being developed, supports taking full page screenshots that other browsers such as Chrome/Chromium don't. Installation was done using Node Package Manager (npm). **npm** was installed along with nodejs via "apt install".

```
$ apt-install nodejs
```
PhantomJS can then be installed using:
```
$ npm -g install phantomjs-prebuilt
```

## Python Libraries





# Configuration
# Help Menu
# Sample Output
