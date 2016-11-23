#!/usr/bin/python

import os, sys, getopt, fileinput
import random, time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC

in_delimiter = '|'
out_delimiter = '|'
mindelay = 1
maxdelay = 3
ackdelay = 2
random.seed()
whitespace = re.compile(r'\s+')

field_index = {i: n for i, n in
               enumerate([
                   "camis", "name_recode", "name_google", "status", "SW_lat", "SW_long", "NE_lat",
                   "NE_long", "LOC_lat", "LOC_long", "neighborhood"])
               }


def delay():
    currentdelay = random.randint(mindelay, maxdelay)
    print "sleeping for {0} seconds...".format(currentdelay)
    time.sleep(currentdelay)


def set_context_details(context, camis, name_recode, name_google, status, SW_lat,
                        SW_long, NE_lat, NE_long, LOC_lat, LOC_long, NEIGH):
    context['camis'] = camis
    context['name_recode'] = name_recode
    context['name_google'] = name_google
    context['status'] = status
    context['SW_lat'] = SW_lat
    context['SW_long'] = SW_long
    context['NE_lat'] = NE_lat
    context['NE_long'] = NE_long
    context['LOC_lat'] = LOC_lat
    context['LOC_long'] = LOC_long
    context['neighborhood'] = NEIGH


def geolocate(browser, context, processed_entities):
    #	url = "https://maps.googleapis.com/maps/api/geocode/xml?address={}".format(context['name_recode'])
    url = "https://maps.googleapis.com/maps/api/geocode/xml?address={}&key=AIzaSyBgm8yoDjo-7wiGAnau9we_vCcCt60hLN0".format(
        context['name_recode'])
    print url
    browser.get(url)
    soup = bs(browser.page_source, "xml")
    if soup.GeocodeResponse.status.string == "OK":
        NEIGH = "ERROR"
        try:
            address_string = soup.GeocodeResponse.result.formatted_address.string
        except:
            address_string = "ERROR"
        try:
            b_SW_LT = soup.GeocodeResponse.result.geometry.viewport.southwest.lat.string
        except:
            b_SW_LT = "ERROR"
        try:
            b_SW_LN = soup.GeocodeResponse.result.geometry.viewport.southwest.lng.string
        except:
            b_SW_LN = "ERROR"
        try:
            b_NE_LT = soup.GeocodeResponse.result.geometry.viewport.northeast.lat.string
        except:
            b_NE_LT = "ERROR"
        try:
            b_NE_LN = soup.GeocodeResponse.result.geometry.viewport.northeast.lng.string
        except:
            b_NE_LN = "ERROR"
        try:
            LC_LT = soup.GeocodeResponse.result.geometry.location.lat.string
        except:
            LC_LT = "ERROR"
        try:
            LC_LN = soup.GeocodeResponse.result.geometry.location.lng.string
        except:
            LC_LN = "ERROR"
        try:
            NEIG = soup.findAll('address_component')
            for n in NEIG:
                if n.findAll('type')[0].get_text() == "neighborhood":
                    NEIGH = n.find('long_name').get_text()
        except:
            NEIGH = "ERROR"

        set_context_details(context, context['camis'], context['name_recode'], address_string, "OK",
                            b_SW_LT,
                            b_SW_LN,
                            b_NE_LT,
                            b_NE_LN,
                            LC_LT,
                            LC_LN,
                            NEIGH)
    else:
        set_context_details(context, context['camis'], context['name_recode'], "ERROR",
                            "ERROR",
                            "ERROR",
                            "ERROR",
                            "ERROR",
                            "ERROR",
                            "ERROR",
                            "ERROR",
                            "ERROR")
        browser.quit()
        sys.exit()


def process(outputfilename, inputfilename):
    processed_entities = {}
    completed = {}
    processed_data = []
    try:
        with open(outputfilename) as outfile:
            data = outfile.read().splitlines()
            for line in data[1:]:
                fields = line.split(out_delimiter)
                context = {name: fields[i] for (i, name) in field_index.iteritems()}
                if context['status'] == "OK":
                    processed_data.append(line)
                    completed[context['camis']] = True
    except IOError:
        pass
    tmpoutputfilename = "{}.tmp".format(outputfilename)

    with open(tmpoutputfilename, 'w') as outfile:
        outfile.write(out_delimiter.join([field_index[i] for i in range(len(field_index))]))
        outfile.write("\n")
        for line in processed_data:
            outfile.write(line)
            outfile.write('\n')
        outfile.close()
        os.remove(outputfilename)
        os.rename(tmpoutputfilename, outputfilename)
    del processed_data

    with open(inputfilename) as infile:
        data = [s.strip() for s in infile.read().splitlines()]
    browser = webdriver.Chrome()
    last_state = None

    try:
        with open(outputfilename, 'a', 1) as outfile:
            for line in data[1:]:
                fields = line.split(in_delimiter)
                context = {name: '' for name in field_index.values()}
                context['camis'] = fields[0].strip()
                context['name_recode'] = fields[1].strip()
                if context['camis'] in completed:
                    print "skipping {}, already processed".format(context['camis'])
                    continue
                geolocate(browser, context, processed_entities)
                outfile.write(out_delimiter.join(
                    [re.sub(whitespace, ' ', unicode(context[field_index[i]]).encode('utf-8', 'ignore')) for i in
                     range(len(field_index))]
                ))
                outfile.write('\n')
            #				delay()
    finally:
        browser.quit()


usage = "geolocator_address.py -i <inputfile> -o <outfile>"


def main(argv):
    inputfilename = None
    outputfilename = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o", ["help", "ifile=", "ofile="])
        for opt, arg in opts:
            if opt == '-h':
                print usage
                sys.exit()
            elif opt in ("-i", "--ifile"):
                inputfilename = arg
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
    if inputfilename[-4:] != '.csv':
        print inputfilename
        print "ERROR: expect input file to be of type csv"
        sys.exit(5)
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
    process(outputfilename, inputfilename)


if __name__ == "__main__":
    main(sys.argv[1:])
