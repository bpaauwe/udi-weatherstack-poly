
# WeatherStack.com node server

This is the weatherstack.com node server for the [Universal Devices ISY994i](https://www.universal-devices.com/residential/ISY) [Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/) with  [Polyglot V2](https://github.com/Einstein42/udi-polyglotv2)
(c) 2019 Robert Paauwe
MIT license.

This node server is intended to pull weather related data from [WeatherStack](http://www.weatherstack.com/) and make it available via ISY nodes. To access this data you must register with weatherstack.com and obtain an API key. Note that currently the first 10000 requests per month are free so set your polling intervals appropriately.

## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please
2. Go to the Polyglot Store in the UI and install.
3. Add NodeServer in Polyglot Web
   * After the install completes, Polyglot will reboot your ISY, you can watch the status in the main polyglot log.
4. Once your ISY is back up open the Admin Console.
5. Configure the node server with your access key, location, etc.

### Node Settings
The settings for this node are:

#### Short Poll
   * Query weatherstack.com server for current conditions data
#### Long Poll
   * Query weatherstack.com server for forecast data


## Requirements

1. Polyglot V2 itself should be run on Raspian Stretch.
  To check your version, ```cat /etc/os-release``` and the first line should look like
  ```PRETTY_NAME="Raspbian GNU/Linux 9 (stretch)"```. It is possible to upgrade from Jessie to
  Stretch, but I would recommend just re-imaging the SD card.  Some helpful links:
   * https://www.raspberrypi.org/blog/raspbian-stretch/
   * https://linuxconfig.org/raspbian-gnu-linux-upgrade-from-jessie-to-raspbian-stretch-9
2. This has only been tested with ISY 5.0.15 so it is not guaranteed to work with any other version.

# Upgrading

Open the Polyglot web page, go to nodeserver store and click "Update" for "APIXU".

For Polyglot 2.0.35, hit "Cancel" in the update window so the profile will not be updated and ISY rebooted.  The install procedure will properly handle this for you.  This will change with 2.0.36, for that version you will always say "No" and let the install procedure handle it for you as well.

Then restart the weatherstack.com nodeserver by selecting it in the Polyglot dashboard and select Control -> Restart, then watch the log to make sure everything goes well.

The weatherstack.com nodeserver keeps track of the version number and when a profile rebuild is necessary.  The profile/version.txt will contain the Apixu.com profile_version which is updated in server.json when the profile should be rebuilt.

# Release Notes

- 1.0.0 08/10/2019
   - Started development of node server
