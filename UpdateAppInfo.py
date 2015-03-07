#!/usr/bin/python2.7
import json
import sys
import urllib2
import xml.etree.ElementTree as etree

# Python script reads in an XML document containing payloads for App Store apps and
# performs an Apple Search API lookup, gets the version number, compares it to the
# version in the JSS and then updates the JSS record if needed
#
# Path to XML file is first parameter
#
# The following schema should be used for the XML:
# <apps>
#     <app>
#         <name>'Optional, not used by script'</name>
#         <appstore_id>123456789</appstore_id>
#         <jss_id>1</jss_id>
#     </app>
# </apps>

JSSUser = 'username'
JSSPass = 'password'
JSSURL = 'https://myjss.com'

def ParseXML(Path):
    Apps = etree.parse(Path)
    AppList = []
    for App in Apps.iter('app'):
        AppList.append([app.find('appstore_id').text, app.find('jss_id').text])
        
    return AppList
    

def ReturnCurrentVersion(ID):
    request = urllib2.Request('http://itunes.apple.com/lookup?id=%s' % ID)
    response = urllib2.urlopen(request)
    data = json.loads(response.read())
    return data['results'][0]['version']
    

def CheckJSSApp(ID, CurrentVersion):
    Auth = base64.b64encode(JSSUser + ':' + JSSPass)
    ResourceURL = '%s/JSSResource/mobiledeviceapplications/id/%s' % (JSSURL, ID)
    request = urllib2.Request(ResourceURL)
    request.add_header('Authorization', 'Basic %s' % Auth)
    response = urllib2.urlopen(request)
    JSSApp = etree.fromstring(response.read())
    if JSS.find('general/version').text != CurrentVersion:
        Update = '''<mobile_device_application><general><version>%s</version></general></mobile_device_application>''' % CurrentVersion
        request = urllib2.Request(ResourceURL)
        request.add_header('Authorization', 'Basic %s' % Auth)
        request.add_header('Content-Type', 'text/xml')
        request.get_method = lambda: 'PUT'
        response = urllib2.urlopen(request, Update)
    

def Main(Apps)
    for App in Apps:
        CurrentVersion = ReturnCurrentVersion(App[0])
        CheckJSSApp(App[1], CurrentVersion)
    

Main(ParseXML(sys.argv[1]))