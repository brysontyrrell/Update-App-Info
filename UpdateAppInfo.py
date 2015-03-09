#!/usr/bin/env python
import argparse
import base64
import getpass
import json
import os
import sys
import urllib2
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree


class ArgParser(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            prog="Update App Info",
            description="Read App Store apps in the JSS and update their information with the latest data from iTunes.",
            formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""Example usage:
$ ./UpdateAppInfo.py https://jss.myorg.com
$ ./UpdateAppInfo.py https://jss.myorg.com --skip-descriptions
$ ./UpdateAppInfo.py https://jss.myorg.com -u username -p pass
            """)

        parser.add_argument('jssurl', type=str, default=None, help="JSS URL")
        parser.add_argument('-d', '--skip-descriptions', action='store_true', help="do not update descriptions")
        parser.add_argument('-u', '--username', dest='username', type=str, default=None, help="API username")
        parser.add_argument('-p', '--password', dest='password', type=str, default=None, help="API user password")

        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)

        args = parser.parse_args()

        self.jssurl = self.clean_url(args.jssurl)
        self.skip_descriptions = args.skip_descriptions if args.skip_descriptions else False
        self.username = args.username if args.username else str(raw_input("API Username: "))
        self.password = args.password if args.password else getpass.getpass("API Password: ")

    @staticmethod
    def clean_url(url):
        cleaned_url = url.rstrip('/')
        if not (cleaned_url.startswith('http://') or cleaned_url.startswith('https://')) :
            print("valid prefix for server url not found: prefixing with https://")
            cleaned_url = 'https://' + cleaned_url

        return cleaned_url


class JSS(object):
    def __init__(self, url, username, password, skip_description=False):
        self.server = url
        self.auth = base64.b64encode(username + ':' + password)
        self.skip_description = skip_description

    def get_mobile_device_apps(self):
        """Returns a list of dictionaries containing mobile device app data"""
        endpoint = '/JSSResource/mobiledeviceapps'
        #print("retrieving resource: ..{0}".format(endpoint))
        request = urllib2.Request(self.server + endpoint)
        root = etree.fromstring(self.request(request))
        size = int(root.find('size').text)
        if size < 1:
            print("no mobile device apps were found on the JSS")
            sys.exit(0)
        else:
            print("there are {0} app(s) listed in the JSS: retrieving their data".format(size))

        app_list = []
        for app in root.findall('mobile_device_application'):
            app_id = int(app.find('id').text)
            app_name = app.find('name').text
            app_version = app.find('version').text
            response = self.get_mobile_device_app(app_id)
            if not response:
                print('the app "{0}" will be skipped'.format(app_name))
                continue
            else:
                app_data = etree.fromstring(response)

            itunes_url = app_data.find('general/itunes_store_url').text
            if not itunes_url:
                itunes_url = app_data.find('general/url').text
                if not itunes_url:
                    print('the app "{0}" will be skipped because no iTunes URL could be found'.format(app_name))
                    continue

            app_itunes_id = self.parse_itunes_id(itunes_url)
            app_description = app_data.find('general/description').text
            app_list.append(
                {
                    app_id: {
                        'itunes_id': app_itunes_id,
                        'name': app_name,
                        'version': app_version,
                        'description': app_description,
                        'icon': ''
                    }
                }
            )

        return app_list

    def get_mobile_device_app(self, app_id):
        """Returns XML for a mobile device app or None"""
        endpoint = '/JSSResource/mobiledeviceapps/id/{0}/subset/general'.format(app_id)
        #print("retrieving resource: ..{0}".format(endpoint))
        request = urllib2.Request(self.server + endpoint)
        return self.request(request)

    def update_mobile_device_app(self, app_id, app_dict):
        """Takes a JSS ID and dictionary representing a mobile device app, builds an XML object and updates the JSS"""
        endpoint = '/JSSResource/mobiledeviceapps/id/{0}'.format(app_id)

        data = etree.Element('mobile_device_application')
        data_general = etree.SubElement(data, 'general')
        data_general_name = etree.SubElement(data_general, 'name')
        data_general_name.text = app_dict['name']
        data_general_version = etree.SubElement(data_general, 'version')
        data_general_version.text = app_dict['version']
        if not self.skip_description:
            data_general_description = etree.SubElement(data_general, 'description')
            data_general_description.text = app_dict['description']
            data_self_service = etree.SubElement(data, 'self_service')
            data_self_service_description = etree.SubElement(data_self_service, 'self_service_description')
            data_self_service_description.text = app_dict['description']

        xml = etree.tostring(data, 'utf-8')

        #print("updating resource: ..{0}".format(endpoint))
        request = urllib2.Request(self.server + endpoint, xml)
        request.get_method = lambda: 'PUT'
        self.request(request)

    def request(self, request):
        request.add_header('Authorization', 'Basic ' + self.auth)
        request.add_header('Content-Type', 'text/xml')
        try:
            response = urllib2.urlopen(request)
        except ValueError as e:
            print("an error occurred during the request: {0}".format(e.message))
            print("check the URL used and try again\n")
            sys.exit(1)
        except urllib2.HTTPError as e:
            print("an error occurred during the request: {0} {1}: {2}".format(type(e).__name__, e.code, e.reason))
            if e.code != 200:
                return None

        except urllib2.URLError as e:
            print("an error occurred during the request: {0}: {1}".format(type(e).__name__, e.reason))
            print("check the server URL used and try again\n")
            sys.exit(1)
        except Exception as e:
            print("an unknown error has occurred: {0}: {1}\n".format(type(e).__name__, e.message))
            sys.exit(1)

        return response.read()

    def get_itunes_data(self, app_id):
        """Returns a dictionary containing data matching mobile device app fields"""
        request = urllib2.Request('http://itunes.apple.com/lookup?id={0}'.format(app_id))
        data = json.loads(self.request(request))
        if data['resultCount'] < 1:
            print('the search for the iTunes ID yielded no results')
            return None
        elif data['resultCount'] > 1:
            print('the search for the iTunes ID yielded multiple results: the app will be skipped')
            return None

        app_data = data['results'][0]
        try:
            icon_url = app_data['artworkUrl512']
        except KeyError:
            icon_url = app_data['artworkUrl100']

        return {
            'name': app_data['trackName'],
            'description': app_data['description'],
            'version': app_data['version'],
            'icon_url': icon_url
        }

    @staticmethod
    def parse_itunes_id(resource=''):
        """Returns the 'id' from an iTunes URL string"""
        itunes_id = os.path.split(resource)[-1].split('?')[0][2:]
        return itunes_id


def compare_version(app_name, jss_version, itunes_version):
    """Compares two dictionaries for values, returns True if matched or False if not"""
    if jss_version != itunes_version:
        print('"{0}" needs update: version in JSS: "{1}", version in iTunes: "{2}"'.format(app_name, jss_version, itunes_version))
        return False
    else:
        print('"{0}" does not need to be updated'.format(app_name))
        return True


def encodingcheck():
    """This is a hack method of avoiding encoding issues"""
    current = sys.getdefaultencoding()
    if current != 'utf-8':
        reload(sys)
        sys.setdefaultencoding('utf-8')


def main():
    encodingcheck()
    args = ArgParser()
    jss = JSS(args.jssurl, args.username, args.password, args.skip_descriptions)
    applist = jss.get_mobile_device_apps()
    print("{0} apps will be checked for updates".format(len(applist)))
    for app in applist:
        for key in app.keys():
            key = key
            appdata = app[key]

        app_itunes = jss.get_itunes_data(appdata['itunes_id'])
        if app_itunes:
            if not compare_version(app[key]['name'], app[key]['version'], app_itunes['version']):
                print('updating info for mobile device app "{0}" at JSS ID: {1}'.format(app_itunes['name'], key))
                jss.update_mobile_device_app(key, app_itunes)

    print("updates complete\n")
    sys.exit(0)

if __name__ == '__main__':
    main()