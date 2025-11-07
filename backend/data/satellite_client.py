import requests
from typing import Dict, List
import os


class SatelliteClient:
    def __init__(self):
        self.firms_api_key = os.getenv('NASA_FIRMS_API_KEY')
        self.firms_url = "https://firms.modaps.eosdis.nasa.gov/api/area"
    
    async def fetch_imagery(self, location: Dict, days: int = 7) -> Dict:
        """
        Fetch satellite imagery and fire detection data
        """
        # For fires: Use NASA FIRMS active fire data
        fires = await self._fetch_active_fires(location, days)
        
        # For satellite imagery: Use NOAA GOES or similar
        # For demo: Can use pre-downloaded images
        
        return {
            'fire_detections': fires,
            'fire_perimeter': self._calculate_fire_perimeter(fires),
            'thermal_intensity': fires[0]['bright_ti4'] if fires else 300,
            'satellite': 'VIIRS',
            'timestamp': fires[0]['acq_date'] if fires else None
        }
    
    async def _fetch_active_fires(self, location: Dict, days: int = 7) -> List[Dict]:
        """Query NASA FIRMS for active fires"""
        # FIRMS API format: /area/csv/{api_key}/VIIRS_SNPP_NRT/{bbox}/{days}
        bbox = self._create_bbox(location, radius_km=50)
        url = f"{self.firms_url}/csv/{self.firms_api_key}/VIIRS_SNPP_NRT/{bbox}/{days}"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            # Parse CSV
            fires = self._parse_firms_csv(response.text)
            return fires
        else:
            return []
    
    def _create_bbox(self, location: Dict, radius_km: float) -> str:
        """Create bounding box around location"""
        lat = location['lat']
        lon = location['lon']
        # Rough conversion: 1 degree ≈ 111 km
        delta = radius_km / 111
        
        west = lon - delta
        south = lat - delta
        east = lon + delta
        north = lat + delta
        
        return f"{west},{south},{east},{north}"

    def _parse_firms_csv(self, csv_text: str) -> List[Dict]:
        """Simplified CSV parser for FIRMS data"""
        fires = []
        lines = csv_text.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = lines[0].split(',')
        for row in lines[1:]:
            values = row.split(',')
            try:
                fire_data = dict(zip(headers, values))
                # Convert key fields
                fire_data['latitude'] = float(fire_data['latitude'])
                fire_data['longitude'] = float(fire_data['longitude'])
                fire_data['bright_ti4'] = float(fire_data['bright_ti4'])  # Kelvin
                fires.append(fire_data)
            except (ValueError, IndexError):
                continue  # Skip bad rows
        return fires

    def _calculate_fire_perimeter(self, fires: List[Dict]) -> Dict:
        """
        Calculate a simple bounding box polygon from fire points.
        In a real system, this would be a concave hull or alpha shape.
        """
        if not fires:
            return None
        
        lats = [f['latitude'] for f in fires]
        lons = [f['longitude'] for f in fires]
        
        min_lon, max_lon = min(lons), max(lons)
        min_lat, max_lat = min(lats), max(lats)
        
        # Create GeoJSON Polygon coordinates
        coordinates = [[
            [min_lon, min_lat],
            [max_lon, min_lat],
            [max_lon, max_lat],
            [min_lon, max_lat],
            [min_lon, min_lat]  # Close the loop
        ]]
        
        return {
            "type": "Polygon",
            "coordinates": coordinates
        }