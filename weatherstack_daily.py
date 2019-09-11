# Node definition for a daily forecast node

CLOUD = False
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
    CLOUD = True

import json
import time
import datetime
import et3

LOGGER = polyinterface.LOGGER

class DailyNode(polyinterface.Node):
    id = 'daily'
    drivers = [
            {'driver': 'GV19', 'value': 0, 'uom': 25},     # day of week
            {'driver': 'GV0', 'value': 0, 'uom': 4},       # high temp
            {'driver': 'GV1', 'value': 0, 'uom': 4},       # low temp
            {'driver': 'GV6', 'value': 0, 'uom': 24},      # rain
            {'driver': 'CLIHUM', 'value': 0, 'uom': 22},   # humidity
            {'driver': 'GV13', 'value': 0, 'uom': 25},     # conditions
            {'driver': 'GV4', 'value': 0, 'uom': 49},      # wind speed
            {'driver': 'GV15', 'value': 0, 'uom': 71},     # visability
            {'driver': 'GV16', 'value': 0, 'uom': 71},     # UV index
            {'driver': 'GV20', 'value': 0, 'uom': 106},    # mm/day
            ]

    def set_units(self, units):
        try:
            for driver in self.drivers:
                if units == 'imperial':
                    if driver['driver'] == 'BARPRES': driver['uom'] = 117
                    if driver['driver'] == 'GV0': driver['uom'] = 17
                    if driver['driver'] == 'GV1': driver['uom'] = 17
                    if driver['driver'] == 'GV4': driver['uom'] = 48
                    if driver['driver'] == 'GV6': driver['uom'] = 105
                    if driver['driver'] == 'GV19': driver['uom'] = 25
                    if driver['driver'] == 'GV15': driver['uom'] = 116
                elif units == 'metric':
                    if driver['driver'] == 'BARPRES': driver['uom'] = 118
                    if driver['driver'] == 'GV0': driver['uom'] = 4
                    if driver['driver'] == 'GV1': driver['uom'] = 4
                    if driver['driver'] == 'GV4': driver['uom'] = 49
                    if driver['driver'] == 'GV6': driver['uom'] = 82
                    if driver['driver'] == 'GV19': driver['uom'] = 25
                    if driver['driver'] == 'GV15': driver['uom'] = 38
        except:
            for drv in self.drivers:
                if units == 'imperial':
                    if drv == 'BARPRES': self.drivers[drv]['uom'] = 117
                    if drv == 'GV0': self.drivers[drv]['uom'] = 17
                    if drv == 'GV1': self.drivers[drv]['uom'] = 17
                    if drv == 'GV4': self.drivers[drv]['uom'] = 48
                    if drv == 'GV6': self.drivers[drv]['uom'] = 105
                    if drv == 'GV19': self.drivers[drv]['uom'] = 25
                    if drv == 'GV15': self.drivers[drv]['uom'] = 116
                elif units == 'metric':
                    if drv == 'BARPRES': self.drivers[drv]['uom'] = 118
                    if drv == 'GV0': self.drivers[drv]['uom'] = 4
                    if drv == 'GV1': self.drivers[drv]['uom'] = 4
                    if drv == 'GV4': self.drivers[drv]['uom'] = 49
                    if drv == 'GV6': self.drivers[drv]['uom'] = 82
                    if drv == 'GV19': self.drivers[drv]['uom'] = 25
                    if drv == 'GV15': self.drivers[drv]['uom'] = 38

    def mm2inch(self, mm):
        return mm/25.4

    def update_forecast(self, jdata, latitude, elevation, plant_type, units):
        epoch = int(jdata['time'])
        dow = time.strftime("%w", time.gmtime(epoch))
        LOGGER.info('Day of week = ' + dow)
        self.setDriver('CLIHUM', round(float(jdata['avghumidity']), 0), True, False)
        self.setDriver('GV0', float(jdata['maxtemp']), True, False)
        self.setDriver('GV1', float(jdata['mintemp']), True, False)
        self.setDriver('GV13', jdata['code'], True, False)
        self.setDriver('GV16', float(jdata['uv']), True, False)
        self.setDriver('GV6', float(jdata['totalprecip']), True, False)
        self.setDriver('GV4', float(jdata['maxwind']), True, False)
        self.setDriver('GV15', float(jdata['avgvis']), True, False)
        self.setDriver('GV19', int(dow), True, False)

        # Calculate ETo
        #  Temp is in degree C and windspeed is in m/s, we may need to
        #  convert these.
        Tmin = float(jdata['mintemp'])
        Tmax = float(jdata['maxtemp'])
        Hmin = Hmax = float(jdata['avghumidity'])
        Ws = float(jdata['maxwind'])
        J = datetime.datetime.fromtimestamp(jdata['time']).timetuple().tm_yday

        if units != 'metric':
            LOGGER.info('Conversion of temperature/wind speed required')
            Tmin = et3.FtoC(Tmin)
            Tmax = et3.FtoC(Tmax)
            Ws = et3.mph2ms(Ws)
        else:
            Ws = et3.kph2ms(Ws)

        et0 = et3.evapotranspriation(Tmax, Tmin, None, Ws, float(elevation), Hmax, Hmin, latitude, float(plant_type), J)
        self.setDriver('GV20', round(et0, 2), True, False)
        LOGGER.info("ETo = %f %f" % (et0, self.mm2inch(et0)))


