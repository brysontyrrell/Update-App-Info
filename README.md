# Update-App-Info #

A script that will read all published App Store iOS apps in the JSS and update their information according to the latest data available in the App Store.

## What does it do? ##

After entering an iOS app into the JSS for deployment (either pushed or via Self Service) the information pulled from the original search is never updated by the server.  As app developers can frequently upload new versions that contain new titles, descriptions and icons it can be a chore to some admins to ensure these entries are updated.

The 'UpdateAppInfo' script compares the information for these iOS apps in the JSS against the latest information available via the iTunes API.  If the version number in iTunes does not match the version in the JSS then the app will have its data refreshed with the correct version number, name and (optional) description.

In-house apps are skipped over in this process and not touched by the script (the in-house app will lack an 'itunes_store_url').

### What about icons? ###

At this time there appears to be an issue with updating a mobile device app's icon via the '/uploads' API endpoint. Once that has been resolved this script will be updated to handle icons as well.

## Usage ##

The script contains built-in help text that can be called by passing the '-h/--help' argument, or no arguments.

```
$ ./UpdateAppInfo.py https://jss.myorg.com
usage: Update App Info [-h] [-d] [-u USERNAME] [-p PASSWORD] jssurl

Read App Store apps in the JSS and update their information with the latest data from iTunes.

positional arguments:
  jssurl                JSS URL

optional arguments:
  -h, --help            show this help message and exit
  -d, --skip-descriptions
                        do not update descriptions
  -u USERNAME, --username USERNAME
                        API username
  -p PASSWORD, --password PASSWORD
                        API user password

Example usage:
$ ./UpdateAppInfo.py https://jss.myorg.com
$ ./UpdateAppInfo.py https://jss.myorg.com --skip-descriptions
$ ./UpdateAppInfo.py https://jss.myorg.com -u username -p pass
```

The username and password are optional parameters.  The script will prompt for these values if you do not pass them (a sort of interactive mode).  When run you will see an output of what actions are being performed:

```
$ ./UpdateAppInfo.py https://jss.myorg.com
API Username: bryson
API Password: 
there are 9 app(s) listed in the JSS: retrieving their data
the app "My App" will be skipped because no iTunes URL could be found
8 apps will be checked for updates
"Box for iPhone and iPad" needs update: version in JSS: "3.2.2", version in iTunes: "3.6.2"
updating info for mobile device app "Box for iPhone and iPad" at JSS ID: 4
"Casper Focus" needs update: version in JSS: "9.30", version in iTunes: "9.64"
updating info for mobile device app "Casper Focus" at JSS ID: 3
"Cisco WebEx Meetings" needs update: version in JSS: "6.5", version in iTunes: "7.0"
updating info for mobile device app "Cisco WebEx Meetings" at JSS ID: 29
"CrashPlan PROe" needs update: version in JSS: "3.5.4", version in iTunes: "3.5.5"
updating info for mobile device app "CrashPlan PROe" at JSS ID: 19
"HipChat" needs update: version in JSS: "2.3.3", version in iTunes: "3.1.0"
updating info for mobile device app "HipChat - Group & Video Chat for Teams" at JSS ID: 6
"iBooks" does not need to be updated
"Microsoft Word for iPad" needs update: version in JSS: "1.1", version in iTunes: "1.6.1"
updating info for mobile device app "Microsoft Word" at JSS ID: 8
"OneDrive for Business" needs update: version in JSS: "1.2.2", version in iTunes: "1.2.5"
updating info for mobile device app "OneDrive for Business (formerly SkyDrive Pro)" at JSS ID: 15
updates complete
```

## About the initial commit ##

My original script was a proof-of-concept for automating the updating of listed iOS app versions in the JSS. If an admin had been displaying app updates in the Self Service Web Clip they had to ensure that the listing in the JSS was up-to-date with the listing in the App Store or else false positives may appear for end users under their available updates.

The first attempt at this script was based on an 'inclusive' model where the admin would define which apps in the JSS were required to have their versions updated and then run it.  It was posted before the version described above for my own reference.