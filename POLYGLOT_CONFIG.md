## Configuration

The APIXU node server has the following user configuration parameters:

- APIkey   : Your API ID, needed to authorize connection to the APIXU API.

- Location : Specify location using one of the following
	- latitude and longitude in decimal degrees.  I.E. 48.85,2.35
	- city name
	- US zip code
	- UK postcode
	- Canada postal code
	- meta:<meta code> I.E. metar:EGLL
	- 3 digit airport code  I.E. iata:DXB

- Units    : 'metric' or 'imperial' request data in this units format.

- Elevation : The elevation, in meters, of the location.

- Plant Type: Used as part of the ETo calculation to compensate or different types of ground cover.  Default is 0.23

To get an API key, register at www.apixu.com

