# Copyright Adarsh Uppula, 2017
#
import abc


class GeocodeProvider(metaclass=abc.ABCMeta):
    """An abstract Geocode provider that may use a third party service to fetch the lat/lng for a given geo address."""

    def __init__(self):
        self._timeout = 10

    @property
    def timeout(self):
        """Get the timeout (in seconds) of this provider. Default is 10 seconds."""
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        """Set the timeout (in seconds) of this provider."""
        self._timeout = value

    @abc.abstractmethod
    def get_name(self):
        """"Get the name of this provider.
        """

    @abc.abstractmethod
    def get_geocode(self, address):
        """Fetch the latitude and longitude for the given address.

         Args:
             address: The geographical address.
         Returns:
             A LatLng object containing the geocoded latitude and longitude
         """
