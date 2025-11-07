"""
Data clients module for HAM backend.

This module contains clients for fetching data from external APIs.
"""

from .satellite_client import SatelliteClient

__all__ = ['SatelliteClient']