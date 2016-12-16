#!/usr/bin/python

import getopt
import random
import re
import sys
import time

from bs4 import BeautifulSoup as bs
from selenium import webdriver

out_delimiter = ';'
mindelay = 10
maxdelay = 12
ackdelay = 2
random.seed()
whitespace = re.compile(r'\s+')

field_index = {i: n for i, n in
               enumerate([
                   "name", "neighborhood", "cuisine", "rating", "noratings", "pricerange", "date", "time"])
               }


def delay():
    currentdelay = random.randint(mindelay, maxdelay)
    print "sleeping for {0} seconds...".format(currentdelay)
    time.sleep(currentdelay)


def parser1(date, time, soup, outfile):
    rows = soup.find("table", {'id': "AlRestList_ResultsGrid"}).findAll("tr", {'class', "a"})
    restaurants = {}
    j = 0
    for element in rows:
        j = j + 1
        restaurants['date'] = date
        restaurants['time'] = time
        restaurants['name'] = element.a.get_text()
        restaurants['neighborhood'] = element.find("div", {"class", "nn"}).get_text(strip=True)
        restaurants['cuisine'] = element.find("div", {"class", "nf"}).get_text(strip=True)
        restaurants['pricerange'] = element.find("td", {"class", "p"}).get_text(strip=True)
        restaurants['rating'] = None
        restaurants['noratings'] = 0
        outfile.write(out_delimiter.join(
            [re.sub(whitespace, ' ', unicode(restaurants[field_index[i]]).encode('utf-8', 'ignore')) for i in
             range(len(field_index))]
        ))
        outfile.write('\n')
    rows = soup.find("table", {'id': "AlRestList_ResultsGrid"}).findAll("tr", {'class', "r"})
    for element in rows:
        j = j + 1
        restaurants['date'] = date
        restaurants['time'] = time
        restaurants['name'] = element.a.get_text()
        restaurants['neighborhood'] = element.find("div", {"class", "nn"}).get_text(strip=True)
        restaurants['cuisine'] = element.find("div", {"class", "nf"}).get_text(strip=True)
        restaurants['pricerange'] = element.find("td", {"class", "p"}).get_text(strip=True)
        restaurants['rating'] = None
        restaurants['noratings'] = 0
        outfile.write(out_delimiter.join(
            [re.sub(whitespace, ' ', unicode(restaurants[field_index[i]]).encode('utf-8', 'ignore')) for i in
             range(len(field_index))]
        ))
        outfile.write('\n')
    print("Done processing {0} records".format(j))


def parser2(date, time, soup, outfile):
    rows = soup.find("table", {'id': "AlRestList_ResultsGrid"}).findAll("tr", {"class": "ResultRow"})
    restaurants = {}
    j = 0
    for element in rows:
        j = j + 1
        restaurants['date'] = date
        restaurants['time'] = time
        restaurants['name'] = element.a.get_text()
        neightype = element.find("div", {"class", "d"}).get_text()
        matchObj = re.match('(.*) \| (.*)', neightype, re.I)
        restaurants['neighborhood'] = matchObj.group(1)
        restaurants['cuisine'] = matchObj.group(2)
        restaurants['pricerange'] = element.find("td", {"class", "PrCol"}).get_text()
        restaurants['rating'] = None
        restaurants['noratings'] = 0
        outfile.write(out_delimiter.join(
            [re.sub(whitespace, ' ', unicode(restaurants[field_index[i]]).encode('utf-8', 'ignore')) for i in
             range(len(field_index))]
        ))
        outfile.write('\n')
    print("Done processing {0} records".format(j))


def parser3(date, time, soup, outfile):
    rows = soup.find("table", {'id': "AlRestList_ResultsGrid"}).findAll("tr", {"class": "ResultRow"})
    restaurants = {}
    j = 0
    for element in rows:
        j = j + 1
        restaurants['date'] = date
        restaurants['time'] = time
        restaurants['name'] = element.a.get_text()
        neightype = element.find("div", {"class", "d"}).get_text()
        matchObj = re.match('(.*) \| (.*)', neightype, re.I)
        restaurants['neighborhood'] = matchObj.group(1)
        restaurants['cuisine'] = matchObj.group(2)
        temp = element.find("td", {"class", "RaCol"}).findAll("div")
        if len(temp) > 0:
            restaurants['rating'] = temp[0].div['title']
            restaurants['noratings'] = temp[0].get_text()
        else:
            restaurants['rating'] = "NA"
            restaurants['noratings'] = "0 Reviews"
        restaurants['pricerange'] = element.find("td", {"class", "PrCol"}).get_text()
        outfile.write(out_delimiter.join(
            [re.sub(whitespace, ' ', unicode(restaurants[field_index[i]]).encode('utf-8', 'ignore')) for i in
             range(len(field_index))]
        ))
        outfile.write('\n')
    print("Done processing {0} records".format(j))


def process(outputfilename):
    with open(outputfilename, 'a', 1) as outfile:
        url = raw_input("URL to start (if nothing entered, will default to 20090905)? ")
        if (url == ""):
            url = "http://web.archive.org/web/20090905072738/http://www.opentable.com/new-york-restaurant-listings"
        cont = "y"
        k = 0
        browser = webdriver.Chrome()
        browser.get(url)
        while (cont == 'y'):
            if k == 0:
                k = 1
            else:
                browser.find_element_by_xpath(
                    '/html/body/div[1]/div/div/table/tbody/tr/td[2]/table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[3]/a/img').click()
            matchObj = re.match(r'(.*\/(\d{8})(\d{6}).*)', browser.current_url, re.I)
            date = matchObj.group(2)
            time = matchObj.group(3)
            print("Processing capture on {0} at {1} hours".format(date, time))
            soup = bs(browser.page_source, "html.parser")
            if (soup.find("table", {'class': "AlRestList_ResultsGrid"}) != None):
                parser1(date, time, soup, outfile)
            elif (soup.find("table", {'class': "ResultsGrid SortingEnabled"}) != None):
                if (soup.find("table", {'id': "AlRestList_ResultsGrid"}).find("tr", {"class": "ResultRow"}).find("td", {
                "class", "RaCol"}) != None):
                    parser3(date, time, soup, outfile)
                else:
                    parser2(date, time, soup, outfile)
            else:
                print "Don't know how to parse this page"
                # cont = raw_input("Continue with next page (y/n)?")
            delay()
            cont = "y"
        browser.quit()


usage = "OTParser_webdriver.py -o <outfile>"


def main(argv):
    inputfilename = None
    outputfilename = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho", ["help", "ofile="])
        for opt, arg in opts:
            if opt == '-h':
                print usage
                sys.exit()
            elif opt in ("-o", "--ofile"):
                outputfilename = arg
    except getopt.GetoptError:
        print usage
        sys.exit(2)
    except:
        print usage
        sys.exit(3)
    if outputfilename == None:
        print "ERROR: no input file provided, use OTparser.py -h for help"
        sys.exit(4)
    if outputfilename[-4:] != '.csv':
        print outputfilename
        print "ERROR: expect output file to be of type csv"
        sys.exit(5)
    try:
        with open(outputfilename):
            print "output file '{0}' already exists, appending new results".format(outputfilename)
    except IOError:
        with open(outputfilename, 'w') as outfile:
            outfile.write(out_delimiter.join([field_index[i] for i in range(len(field_index))]))
            outfile.write("\n")
    process(outputfilename)


if __name__ == "__main__":
    main(sys.argv[1:])
