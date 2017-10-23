# GeocodeService
Geocoding REST service using GMaps and Here maps. Fetches the latitude/longitude given a street address.

Google Maps api is used as the primary geocoding provider by default. On failure or unavailability, Here maps is used. See below for details and configuration.

Requirements: Python 3 runtime. Tested against Python 3.6

## Using the REST API
GET /geocode?address=xxx

Query parameter:
- address - the geographic address eg. 1600 Amphitheatre Parkway, Mountain View, CA

Response:
- response will be Content-type: application/json
- 400 HTTP code for invalid input
- 500 HTTP code for server error
- `status` is a code that indicates success or type of failure
    - OK - geocode found
    - INVALID - indicates invalid input
    - GEOCODE_NOT_FOUND - if no geocode was found
    - ERROR - server error occurred

Sample response:
<pre>
{
    "status": "OK",
    "lat": 37.4216548,
    "lng": -122.0856374
}
</pre>

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

## Extending the code
- 2 geocoding providers are provided: Google Maps, and Here maps
- new Geocoding providers may be created via simply extending `GeocodeProvider` and using them as the primary or secondary provider

## TODOs/Future enhancements
- make the code follow the "Pythonic" way
- (future) use popular 3rd party libraries to handle a lot of the logic and simplify the code
- allow user to specify which geocode service to use in the API itself
- cache repeat, frequent queries
- secure storage of api keys
- allow list of fallback providers
- use enums to enumerate providers and validate
- return metadata in response (such as Geocode provider used)
- more thorough input validation (server port range check, config file, etc)
- more unit tests
