#!/usr/bin/env python3
"""
Polyglot v2 node server weatherstack.com weather data
Copyright (C) 2019 Robert Paauwe
"""

CLOUD = False
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
    CLOUD = True
import sys
import requests
import json
import weatherstack_daily
import write_profile

LOGGER = polyinterface.LOGGER

class Controller(polyinterface.Controller):
    id = 'weatherstack'
    hint = [0,0,0,0]
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'weatherstack'
        self.address = 'weatherstack'
        self.primary = self.address
        self.location = ''
        self.apikey = ''
        self.units = 'imperial'
        self.configured = False
        self.myConfig = {}
        self.plant_type = 0.23
        self.elevation = 0

        self.poly.onConfig(self.process_config)

    # Process changes to customParameters
    def process_config(self, config):
        if 'customParams' in config:
            # Check if anything we care about was changed...
            if config['customParams'] != self.myConfig:
                changed = False
                if 'Location' in config['customParams']:
                    if self.location != config['customParams']['Location']:
                        self.location = config['customParams']['Location']
                        changed = True
                if 'Elevation' in config['customParams']:
                    if self.elevation != config['customParams']['Elevation']:
                        self.elevation = config['customParams']['Elevation']
                        changed = True
                if 'Plant Type' in config['customParams']:
                    if self.plant_type != config['customParams']['Plant Type']:
                        self.plant_type = config['customParams']['Plant Type']
                        changed = True
                if 'APIkey' in config['customParams']:
                    if self.apikey != config['customParams']['APIkey']:
                        self.apikey = config['customParams']['APIkey']
                        changed = True
                if 'Units' in config['customParams']:
                    if self.units != config['customParams']['Units']:
                        self.units = config['customParams']['Units']
                        changed = True
                        try:
                            if CLOUD:
                                self.set_cloud_driver_units()
                            else:
                                self.set_driver_units()
                        except:
                            LOGGER.debug('set driver units failed')

                self.myConfig = config['customParams']
                if changed:
                    self.removeNoticesAll()
                    self.configured = True

                    if self.location == '':
                        self.addNotice("Location parameter must be set");
                        self.configured = False
                    if self.apikey == '':
                        self.addNotice("APIXU API ID must be set");
                        self.configured = False

    def start(self):
        LOGGER.info('Starting node server')
        LOGGER.info('Add node for forecast')
        for day in range(1,7):
            address = 'forecast_' + str(day)
            title = 'Forecast ' + str(day)

            try:
                node = weatherstack.DailyNode(self, self.address, address, title)
                self.addNode(node);
            except:
                LOGGER.error('Failed to create forecast node ' + title)
                LOGGER.debug('%s, %s, %s' % (self.address, address, title))


        self.check_params()
        LOGGER.info('Node server started')

        # Do an initial query to get the data filled in as soon as possible
        self.query_conditions(True)
        self.query_forecast(True)

    def shortPoll(self):
        self.query_conditions(False)

    def longPoll(self):
        self.query_forecast(False)

    def icon_2_int(self, icn):
        return {
                'clear-day': 0,
                'clear-night': 1,
                'rain': 2,
                'snow': 3,
                'sleet': 4,
                'wind': 5,
                'fog': 6,
                'cloudy': 7,
                'partly-cloudy-day': 8,
                'partly-cloudy-night': 9,
                }.get(icn, 0)

    def query_conditions(self, force):
        # Query for the current conditions. We can do this fairly
        # frequently, probably as often as once every 2 minutes.
        #
        # By default JSON is returned

        request = 'http://api.weatherstack.com/current?'
        # TODO: handle other methods of setting location
        request += 'access_key=' + self.apikey
        request += '&query=' + self.location
        request += '&unit=' + self.units  # m= metric, f = imperial

        # request += '&lang=' + self.language

        LOGGER.debug('request = %s' % request)

        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return

        c = requests.get(request)
        jdata = c.json()
        LOGGER.debug(jdata)

        # All data is available in both metric and imperial so the self.units
        # setting will determine which bit of data to use.
        self.setDriver('CLITEMP', float(jdata['current']['temperature']), True, force)
        self.setDriver('BARPRES', float(jdata['current']['pressure']), True, force)
        self.setDriver('CLIHUM', float(jdata['current']['humidity']), True, force)
        self.setDriver('GV4', float(jdata['current']['wind_speed']), True, force)
        #self.setDriver('GV5', float(jdata['current']['gust_kph']), True, force)
        self.setDriver('WINDDIR', float(jdata['current']['wind_degree']), True, force)
        self.setDriver('GV14', float(jdata['current']['cloudcover']), True, force)
        self.setDriver('GV2', float(jdata['current']['feelslike_c']), True, force)
        self.setDriver('GV16', float(jdata['current']['uv_index']), True, True)
        self.setDriver('GV6', float(jdata['current']['precip']), True, force)
        self.setDriver('GV15', float(jdata['current']['visibility']), True, force)
        self.setDriver('GV13', float(jdata['current']['weather_code']), True, force)

        # last update time:  jdata['last_updated_epoch']
        # condition code: jdata['condition']['code'] ??
        #  condition URL http://www.weatherstack.com/doc/Apixu_weather_conditions.json

        # is there a location object with lat and lon we can use?

    def query_forecast(self, force):
        # Not available with free plan!
        request = 'http://api.weatherstack.com/forecast?'
        request += 'access_key=' + self.apikey
        request += '&query=' + self.location
        request += '&forecast_days=8'

        # request += '&lang=' + self.language

        LOGGER.debug('request = %s' % request)

        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return

        c = requests.get(request)
        jdata = c.json()
        #LOGGER.debug(jdata)
        # Daily data is 7 day forecast, index 0 is today
        for day in range(1,7):
            address = 'forecast_' + str(day)
            forecast = jdata['forecast']['forecastday'][day]
            fcast = {}

            LOGGER.debug(forecast)

            fcast['time'] = forecast['date_epoch']
            fcast['code'] = forecast['day']['condition']['code']
            fcast['avghumidity'] = forecast['day']['avghumidity']
            fcast['uv'] = forecast['day']['uv']
            LOGGER.info('** Found forecast for %s %d' % (forecast['date'], fcast['code']))
            if self.units == 'metric':
                fcast['mintemp'] = forecast['day']['mintemp_c']
                fcast['maxtemp'] = forecast['day']['maxtemp_c']
                fcast['totalprecip'] = forecast['day']['totalprecip_mm']
                fcast['avgvis'] = forecast['day']['avgvis_km']
                fcast['maxwind'] = forecast['day']['maxwind_kph']
            else:
                fcast['mintemp'] = forecast['day']['mintemp_f']
                fcast['maxtemp'] = forecast['day']['maxtemp_f']
                fcast['totalprecip'] = forecast['day']['totalprecip_in']
                fcast['avgvis'] = forecast['day']['avgvis_miles']
                fcast['maxwind'] = forecast['day']['maxwind_mph']

            self.nodes[address].update_forecast(fcast, jdata['location']['lat'], self.elevation, self.plant_type, self.units)
        
    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        # Create any additional nodes here
        LOGGER.info("In Discovery...")

    # Delete the node server from Polyglot
    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        LOGGER.info('Stopping node server')

    def update_profile(self, command):
        st = self.poly.installprofile()
        return st

    def check_params(self):

        if 'Location' in self.polyConfig['customParams']:
            self.location = self.polyConfig['customParams']['Location']
        if 'APIkey' in self.polyConfig['customParams']:
            self.apikey = self.polyConfig['customParams']['APIkey']
        if 'Elevation' in self.polyConfig['customParams']:
            self.elevation = self.polyConfig['customParams']['Elevation']
        if 'Plant Type' in self.polyConfig['customParams']:
            self.plant_type = self.polyConfig['customParams']['Plant Type']
        if 'Units' in self.polyConfig['customParams']:
            self.units = self.polyConfig['customParams']['Units']
        else:
            self.units = 'imperial';

        self.configured = True

        self.addCustomParam( {
            'Location': self.location,
            'APIkey': self.apikey,
            'Units': self.units,
            'Elevation': self.elevation,
            'Plant Type': self.plant_type} )

        LOGGER.info('api id = %s' % self.apikey)

        self.removeNoticesAll()
        if self.location == '':
            self.addNotice("Location parameter must be set");
            self.configured = False
        if self.apikey == '':
            self.addNotice("Apixu API ID must be set");
            self.configured = False

        if CLOUD:
            self.set_cloud_driver_units()
        else:
            self.set_driver_units()

    def set_cloud_driver_units(self):
        LOGGER.info('Configure driver units to ' + self.units)
        if self.units == 'metric':
            for drv in self.drivers:
                if drv == 'CLITEMP': self.drivers[drv]['uom'] = 4
                if drv == 'DEWPT': self.drivers[drv]['uom'] = 4
                if drv == 'GV0': self.drivers[drv]['uom'] = 4
                if drv == 'GV1': self.drivers[drv]['uom'] = 4
                if drv == 'GV2': self.drivers[drv]['uom'] = 4
                if drv == 'GV3': self.drivers[drv]['uom'] = 4
                if drv == 'BARPRES': self.drivers[drv]['uom'] = 117
                if drv == 'GV4': self.drivers[drv]['uom'] = 49
                if drv == 'GV5': self.drivers[drv]['uom'] = 49
                if drv == 'GV6': self.drivers[drv]['uom'] = 82
                if drv == 'GV15': self.drivers[drv]['uom'] = 38
            for day in range(1,7):
                address = 'forecast_' + str(day)
                self.nodes[address].set_units('metric')
        else:
            for drv in self.drivers:
                if drv == 'CLITEMP': self.drivers[drv]['uom'] = 17
                if drv == 'DEWPT': self.drivers[drv]['uom'] = 17
                if drv == 'GV0': self.drivers[drv]['uom'] = 17
                if drv == 'GV1': self.drivers[drv]['uom'] = 17
                if drv == 'GV2': self.drivers[drv]['uom'] = 17
                if drv == 'GV3': self.drivers[drv]['uom'] = 17
                if drv == 'BARPRES': self.drivers[drv]['uom'] = 23
                if drv == 'GV4': self.drivers[drv]['uom'] = 48
                if drv == 'GV5': self.drivers[drv]['uom'] = 48
                if drv == 'GV6': self.drivers[drv]['uom'] = 105
                if drv == 'GV15': self.drivers[drv]['uom'] = 116
            for day in range(1,7):
                address = 'forecast_' + str(day)
                self.nodes[address].set_units('imperial')

    def set_driver_units(self):
        LOGGER.info('Configure drivers ---')
        if self.units == 'metric':
            for driver in self.drivers:
                if driver['driver'] == 'CLITEMP': driver['uom'] = 4
                if driver['driver'] == 'DEWPT': driver['uom'] = 4
                if driver['driver'] == 'BARPRES': driver['uom'] = 117
                if driver['driver'] == 'GV0': driver['uom'] = 4
                if driver['driver'] == 'GV1': driver['uom'] = 4
                if driver['driver'] == 'GV2': driver['uom'] = 4
                if driver['driver'] == 'GV3': driver['uom'] = 4
                if driver['driver'] == 'GV4': driver['uom'] = 49
                if driver['driver'] == 'GV5': driver['uom'] = 49
                if driver['driver'] == 'GV6': driver['uom'] = 82
                if driver['driver'] == 'GV15': driver['uom'] = 38
            for day in range(1,7):
                address = 'forecast_' + str(day)
                self.nodes[address].set_units('metric')

        # Write out a new node definition file here.
        else:  # imperial
            for driver in self.drivers:
                if driver['driver'] == 'CLITEMP': driver['uom'] = 17
                if driver['driver'] == 'DEWPT': driver['uom'] = 17
                if driver['driver'] == 'BARPRES': driver['uom'] = 23
                if driver['driver'] == 'GV0': driver['uom'] = 17
                if driver['driver'] == 'GV1': driver['uom'] = 17
                if driver['driver'] == 'GV2': driver['uom'] = 17
                if driver['driver'] == 'GV3': driver['uom'] = 17
                if driver['driver'] == 'GV4': driver['uom'] = 48
                if driver['driver'] == 'GV5': driver['uom'] = 48
                if driver['driver'] == 'GV6': driver['uom'] = 105
                if driver['driver'] == 'GV15': driver['uom'] = 116
            for day in range(1,7):
                address = 'forecast_' + str(day)
                self.nodes[address].set_units('imperial')

        # Write out a new node definition file here.
        LOGGER.info('Write new node definitions and publish to ISY')
        write_profile.write_profile(LOGGER, self.drivers, self.nodes['forecast_1'].drivers)
        self.poly.installprofile()

    def remove_notices_all(self, command):
        self.removeNoticesAll()


    commands = {
            'DISCOVER': discover,
            'UPDATE_PROFILE': update_profile,
            'REMOVE_NOTICES_ALL': remove_notices_all
            }

    # For this node server, all of the info is available in the single
    # controller node.
    #
    # TODO: Do we want to try and do evapotranspiration calculations? 
    #       maybe later as an enhancement.
    # TODO: Add forecast data
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},   # node server status
            {'driver': 'CLITEMP', 'value': 0, 'uom': 4},   # temperature
            {'driver': 'GV2', 'value': 0, 'uom': 4},       # feelslike temp
            {'driver': 'CLIHUM', 'value': 0, 'uom': 22},   # humidity
            {'driver': 'BARPRES', 'value': 0, 'uom': 117}, # pressure
            {'driver': 'GV4', 'value': 0, 'uom': 49},      # wind speed
            {'driver': 'WINDDIR', 'value': 0, 'uom': 76},  # direction
            {'driver': 'GV13', 'value': 0, 'uom': 25},     # climate conditions
            {'driver': 'GV14', 'value': 0, 'uom': 22},     # cloud conditions
            {'driver': 'GV15', 'value': 0, 'uom': 83},     # visability
            {'driver': 'GV6', 'value': 0, 'uom': 24},      # rain
            {'driver': 'GV16', 'value': 0, 'uom': 71},     # UV index
            ]

    
if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('WeatherStack')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

