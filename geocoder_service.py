# Copyright Adarsh Uppula, 2017
#
# This program provides a REST-based Geocoding service to resolve addresses to latitude, longitude coordinates
#
#
import argparse
import configparser
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from postmates.google_geocoder import GoogleGeocoderProvider, MyException


class GeocoderHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    def set_primary_provider(self, primary_provider):
        self.primary_provider = primary_provider

    def set_secondary_provider(self, secondary_provider):
        self.secondary_provider = secondary_provider

    # GET
    def do_GET(self):
        # input validation
        geo_address = parse_qs(urlparse(self.path).query).get('address', None)
        if (geo_address is None):
            logging.warning('Address not provided')
            self.output_json(400, json.dumps({"status": "INVALID", "message": "Address is missing"}))
            return

        google_api_key = "AIzaSyB705HK0ZIq9OXlNGY-U4mqNCbnPc2qy8c"

        try:
            geo_address = parse_qs(urlparse(self.path).query).get('address', None)
            # first try preferred service
            google_geocoder = GoogleGeocoderProvider(google_api_key)
            lat_lng = google_geocoder.geocode_address(geo_address)
            logging.info("fetched latlng: " + str(lat_lng))
            if lat_lng is not None:
                logging.info('Geocode found for address: %s', geo_address)
                self.output_json(200, json.dumps({"status": "OK", "lat": lat_lng.lat, "lng": lat_lng.lng}))
            else:
                logging.warning('Geocode not found for address')
                self.output_json(200, json.dumps({"status": "GEOCODE_NOT_FOUND", "message": "Geocode not found for given address"}))
        except (MyException) as e:
            logging.error('Error: %s', e.message)
            self.output_json(500, json.dumps({"status": "ERROR", "message": "Server error occurred. Please try again later."}))
        return

    def output_json(self, http_code, str_data):
        """write given json string to the http response"""
        self.send_response(http_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(str_data)


def run():

    #handle command line arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--port", help="server port to run service on; if omitted, defaults to 8801")
    argparser.add_argument("--provider", help="primary geocoding provider to use; if omitted, defaults to Google Maps")
    argparser.add_argument("--logging", help="log level to use to output to console; if omitted, defaults to WARNING")
    argparser.parse_args()

    # TODO: use logging library to track log messages
    print('starting Geocoding server...')

    #get config info
    parser = configparser.ConfigParser()
    parser.read('config.ini')

    primary = parser.get('DEFAULT', 'PrimaryProvider')
    secondary = parser.get('DEFAULT', 'SecondaryProvider')
    primary_api_key = parser.get('provider.' + primary, 'ApiKey')
    secondary_api_key = parser.get('provider.' + secondary, 'ApiKey')


    # start http server
    # TODO: get the config from config file
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, GeocoderHTTPServer_RequestHandler)

    print('running server...')
    httpd.serve_forever()


run()
