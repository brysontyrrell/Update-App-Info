# Update-App-Info #
---

A script that will read all published App Store iOS apps in the JSS and update their information according to the lastest data available in the App Store.

## About the initial commit ##
===

My original script was a proof-of-concept for automating the updating of listed iOS app versions in the JSS - something that is not handled by the server. If an admin displays app updates in Self Service they must actively ensure that the listing in the JSS is up-to-date with the listing in the App Store, or else false positives may appear for end users under their available updates.

The first attempt at this script was based on an 'inclusive' model where the admin would define which apps in the JSS were required to have their versions updated and then run it.

## Coming in the next update ##
===

The next version that will be committed will be a dramatic re-write that will read all of the apps in the JSS and update each one with the most recent name, version and icon as these three values can be changed frequently by the developer (my two best examples of this are Cisco WebEx Meetings and Microsoft Word).