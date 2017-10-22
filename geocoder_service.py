# Copyright Adarsh Uppula, 2017
#
# This program provides a REST-based Geocoding service to resolve addresses to latitude, longitude coordinates
#
#
import argparse
import configparser
import json
import logging
import logging.config
from http.server import BaseHTTPRequestHandler, HTTPServer
from google_geocoder_provider import GoogleGeocoderProvider, MyException
from urllib.parse import urlparse, parse_qs

from heremaps_geocoder_provider import HeremapsGeocoderProvider


class GeocoderHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    """Provides REST Api service to geocode addresses"""
    primary = None
    secondary = None

    def do_GET(self):
        """Get geocode api eg. access via GET /geocode?address=<address>"""
        # input validation
        geo_address = parse_qs(urlparse(self.path).query).get('address', None)
        if not geo_address:
            logging.warning('Address not provided')
            self.output_json(400, json.dumps({"status": "INVALID", "message": "Address is missing"}))
            return

        # first try preferred service
        try:
            geo_address = parse_qs(urlparse(self.path).query).get('address', None)
            self.try_provider(self.primary, geo_address)
        except (MyException) as e:
            logging.error('Primary failed: ' + e.message)
            # try second
            if self.secondary:
                try:
                    self.try_provider(self.secondary, geo_address)
                except (MyException) as e:
                    logging.error('Secondary failed; ' + e.message)
                    self.output_json(500, json.dumps({"status": "ERROR", "message": "Server error occurred. Please try again later."}))
            else:
                logging.warning('Secondary not available')
                self.output_json(500, json.dumps({"status": "ERROR", "message": "Server error occurred. Please try again later."}))
        return

    def try_provider(self, provider, address):
        logging.info("fetching geocode using " + provider.get_name())
        lat_lng = provider.geocode_address(address)
        logging.info("fetched latlng: " + str(lat_lng))
        if lat_lng:
            logging.info('Geocode found for address: %s', address)
            self.output_json(200, json.dumps({"status": "OK", "lat": lat_lng.lat, "lng": lat_lng.lng}))
        else:
            logging.warning('Geocode not found for address')
            self.output_json(200, json.dumps({"status": "GEOCODE_NOT_FOUND", "message": "Geocode not found for given address"}))

    def output_json(self, http_code, str_data):
        """write given json string to the http response"""
        self.send_response(http_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(str_data.encode('utf8'))


class GeocoderApp:
    def get_geocoder(self, geocoder_type, timeout):
        if geocoder_type == "google":
            google_provider = GoogleGeocoderProvider(self.config['provider.google']['ApiKey'])
            google_provider.set_timeoout(timeout)
            return google_provider
        elif geocoder_type == "here":
            heremaps_provider = HeremapsGeocoderProvider(self.config['provider.here']['AppId'], self.config['provider.here']['AppCode'])
            heremaps_provider.set_timeoout(timeout)
            return heremaps_provider

    def setup_config(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.server_port = self.config.get('DEFAULT', 'ServerPort')
        timeout = int(self.config['DEFAULT']['RemoteTimeout'])

        if not self.server_port:
            raise MyException("Server port not provided.")

        if self.config.get('DEFAULT', 'PrimaryProvider', fallback=0):
            GeocoderHTTPServer_RequestHandler.primary = self.get_geocoder(self.config.get('DEFAULT', 'PrimaryProvider'), timeout)
        else:
            raise MyException("Primary provider not provided.")

        if self.config.get('DEFAULT', 'SecondaryProvider', fallback=0):
            GeocoderHTTPServer_RequestHandler.secondary = self.get_geocoder(self.config.get('DEFAULT', 'SecondaryProvider'), timeout)

        else:
            logging.warning('Secondary provider not provided. Fallback will not be used.')

    def run(self):
        # handle command line arguments
        argparser = argparse.ArgumentParser()
        argparser.add_argument("--port", help="server port to run service on; if omitted, defaults to 8801")
        argparser.add_argument("--provider", help="primary geocoding provider to use; if omitted, defaults to Google Maps")
        argparser.add_argument("--logging", help="log level to use to output to console; if omitted, defaults to WARNING")
        argparser.parse_args()

        try:
            # setup server config
            self.setup_config()
            # start http server
            server_address = ('127.0.0.1', int(self.server_port))
            httpd = HTTPServer(server_address, GeocoderHTTPServer_RequestHandler)
            logging.info('starting server on port: ' + self.server_port + '...')
            httpd.serve_forever()
        except (MyException) as e:
            logging.error('Config issue: ' + e.message)
        except (configparser.Error) as e:
            logging.error('Could not read config file. Please check for proper format: ' + str(e))


# create logger
logging.config.fileConfig('logging.conf')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# start app
logging.info('starting Geocoding app...')
geocoder = GeocoderApp()
geocoder.run()
