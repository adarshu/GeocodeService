# GeocodeService
Geocoding REST service using GMaps and Here maps.

Google Maps api is used as the primary geocoding provider by default. On failure or unavailability, Here maps is used. See below for details.

Requirements: Python 3 runtime. Tested against Python 3.6

## Using the service
GET /geocode?address=<address>

Sample HTTP Get call: GET server:port/geocode?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA

## Run the service
Sample:
python geocode_service.py --config config.ini --port 8081

Commandline usage:
<pre>
usage: geocode_service.py [-h] [--config CONFIG] [--port PORT]

optional arguments:
  -h, --help       show this help message and exit
  --config CONFIG  config file to use; if omitted, defaults to config.ini. See
                   included sample for an example.
  --port PORT      server port to run service on; if omitted, defaults to
                   value in config file
</pre>

Logging control:
- included `logging.conf` controls the logging configuration
- set the `level` property to set the logging level

Config file:  
Note: xxx values should be set to the appropriate value  
The Api keys below are required for the Google and Here services below  

Sample config file:  
<pre>
[DEFAULT]
ServerPort = 8081
RemoteTimeout = 3
PrimaryProvider = google
SecondaryProvider = here

[provider.google]
ApiKey = xxx

[provider.here]
AppId = xxx
AppCode = xxx
</pre>
