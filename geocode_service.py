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
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from google_geocode_provider import GoogleGeocodeProvider, GeocodeException
from heremaps_geocode_provider import HeremapsGeocodeProvider


class GeocodeHTTPRequestHandler(BaseHTTPRequestHandler):
    """Provides REST Api service to geocode addresses"""

    endpoint = '/geocode'
    primary_provider = None
    secondary_provider = None

    def do_GET(self):
        """Get geocode api eg. access via GET /geocode?address=<address>"""
        pathinfo = urlparse(self.path)
        logging.debug('route:' + str(pathinfo))

        # validate route
        if pathinfo.path != self.endpoint:
            self.output_json(404, json.dumps({"status": "NOT_FOUND", "message": "Endpoint not found."}))
            return

        # validate input
        geo_address = parse_qs(pathinfo.query).get('address', None)
        if not geo_address:
            logging.warning('Address not provided')
            self.output_json(400, json.dumps({"status": "INVALID", "message": "Address is missing"}))
            return

        # try preferred geocode service, if it fails due to empty result or network or other error, try the secondary if provided
        try:
            self.try_provider(self.primary_provider, geo_address)
        except GeocodeException as e:
            logging.error('Primary provider failed: ' + e.message)
            if self.secondary_provider:
                try:
                    self.try_provider(self.secondary_provider, geo_address)
                except GeocodeException as e:
                    if e.type == GeocodeException.type_geocode_not_found:
                        self.output_geocode_not_found()
                    else:
                        logging.error('Secondary provider failed; ' + e.message)
                        self.output_server_error()
            else:
                logging.warning('Secondary not available')
                if e.type == GeocodeException.type_geocode_not_found:
                    self.output_geocode_not_found()
                else:
                    self.output_server_error()
        return

    def try_provider(self, provider, address):
        """Try geocoding using given provider for given address"""
        logging.debug("fetching geocode using " + provider.get_name())
        lat_lng = provider.get_geocode(address)
        if lat_lng:
            logging.info('Geocode found for address: %s : %s', address, str(lat_lng))
            self.output_json(200, json.dumps({"status": "OK", "lat": lat_lng.lat, "lng": lat_lng.lng}))
        else:
            logging.debug('Geocode not found for address')
            e = GeocodeException("Geocode not found for address")
            e.set_type(GeocodeException.type_geocode_not_found)
            raise e

    def output_geocode_not_found(self):
        self.output_json(200, json.dumps({"status": "GEOCODE_NOT_FOUND", "message": "Geocode not found for given address"}))

    def output_server_error(self):
        self.output_json(500, json.dumps({"status": "ERROR", "message": "Server error occurred. Please try again later."}))

    def output_json(self, http_code, str_data):
        """Write given json string to the http response"""
        self.send_response(http_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(str_data.encode('utf8'))


class GeocoderApp:
    """Wrapper class that configures and starts the Geocoder HTTP service"""

    def make_provider(self, geocoder_type, timeout):
        """Builds a geocode provider of given type with given timeout"""
        if geocoder_type == "google":
            google_provider = GoogleGeocodeProvider(self.config['provider.google']['ApiKey'])
            google_provider.timeout = timeout
            return google_provider
        elif geocoder_type == "here":
            heremaps_provider = HeremapsGeocodeProvider(self.config['provider.here']['AppId'], self.config['provider.here']['AppCode'])
            heremaps_provider.timeout = timeout
            return heremaps_provider

    def setup_config(self, args):
        """Reads config file and sets up service"""
        configfile = args.config or 'config.ini'
        if not Path(configfile).is_file():
            raise GeocodeException("Config file doesn't exist: " + configfile)

        self.config = configparser.ConfigParser()
        self.config.read(configfile)  # use given arg first
        self.server_port = int(args.port or self.config.get('DEFAULT', 'ServerPort'))  # use given port first
        timeout = int(self.config.get('DEFAULT', 'RemoteTimeout'))

        logging.info('Using config file: ' + configfile)
        logging.info('Using server port: ' + str(self.server_port))
        logging.info('Using timeout: ' + str(timeout))

        if not self.server_port:
            raise GeocodeException("Server port not provided.")
        if self.config.get('DEFAULT', 'PrimaryProvider', fallback=0):
            GeocodeHTTPRequestHandler.primary_provider = self.make_provider(self.config.get('DEFAULT', 'PrimaryProvider'), timeout)
        else:
            raise GeocodeException("Primary provider not provided.")
        if self.config.get('DEFAULT', 'SecondaryProvider', fallback=0):
            GeocodeHTTPRequestHandler.secondary_provider = self.make_provider(self.config.get('DEFAULT', 'SecondaryProvider'), timeout)
        else:
            logging.warning('Secondary provider not provided. Fallback will not be used.')

    def run(self):
        """Run gecoding service"""

        # parse command line arguments
        argparser = argparse.ArgumentParser()
        argparser.add_argument("--config", help="config file to use; if omitted, defaults to config.ini. See included sample for an example.")
        argparser.add_argument("--port", help="server port to run service on; if omitted, defaults to value in config file")
        args = argparser.parse_args()
        logging.debug('Command args: '  + str(args))

        try:
            self.setup_config(args)
            server_address = ('127.0.0.1', int(self.server_port))
            httpd = HTTPServer(server_address, GeocodeHTTPRequestHandler)
            logging.info('starting server on port: ' + str(self.server_port) + '...')
            httpd.serve_forever()
        except (GeocodeException) as e:
            logging.error('Config issue: ' + str(e))
        except (configparser.Error) as e:
            logging.error('Could not read config file. Please check for proper format: ' + str(e))


# create logger
logging.config.fileConfig('logging.conf')

# start app
logging.info('starting Geocoding app')
geocoder = GeocoderApp()
geocoder.run()
