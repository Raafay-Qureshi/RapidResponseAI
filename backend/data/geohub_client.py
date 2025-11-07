import geopandas as gpd
from typing import Dict, Any, Optional
import os
import json


class GeoHubClient:
    """
    Client for loading static Brampton infrastructure and population data
    from GeoHub-sourced files.
    """
    
    def __init__(self):
        # Define paths to static data
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        
        self.infra_path = os.path.join(
            static_dir,
            'brampton_infrastructure.geojson'
        )
        self.pop_path = os.path.join(
            static_dir,
            'brampton_population.geojson'
        )
        self.roads_path = os.path.join(
            static_dir,
            'brampton_roads.geojson'
        )
        
        # Cache for loaded data
        self._infra_cache: Optional[gpd.GeoDataFrame] = None
        self._pop_cache: Optional[gpd.GeoDataFrame] = None
        self._roads_cache: Optional[gpd.GeoDataFrame] = None
    
    async def fetch_infrastructure(self, location: Dict) -> Optional[gpd.GeoDataFrame]:
        """
        Load static Brampton infrastructure data.
        
        Args:
            location: Dictionary with 'lat' and 'lon' keys for filtering
        
        Returns:
            GeoDataFrame containing infrastructure data, or None if loading fails
        """
        try:
            # Load from cache or file
            if self._infra_cache is None:
                if not os.path.exists(self.infra_path):
                    print(f"Warning: Infrastructure data not found at {self.infra_path}")
                    return self._create_sample_infrastructure()
                
                self._infra_cache = gpd.read_file(self.infra_path)
            
            # Filter by location if needed (within a radius)
            if location:
                filtered_data = self._filter_by_location(
                    self._infra_cache, 
                    location, 
                    radius_km=10
                )
                return filtered_data
            
            return self._infra_cache
            
        except Exception as e:
            print(f"Error loading infrastructure data: {e}")
            return self._create_sample_infrastructure()
    
    async def fetch_population(self, location: Dict) -> Optional[gpd.GeoDataFrame]:
        """
        Load static Brampton population/census data.
        
        Args:
            location: Dictionary with 'lat' and 'lon' keys for filtering
        
        Returns:
            GeoDataFrame containing population data, or None if loading fails
        """
        try:
            # Load from cache or file
            if self._pop_cache is None:
                if not os.path.exists(self.pop_path):
                    print(f"Warning: Population data not found at {self.pop_path}")
                    return self._create_sample_population()
                
                self._pop_cache = gpd.read_file(self.pop_path)
            
            # Filter by location if needed
            if location:
                filtered_data = self._filter_by_location(
                    self._pop_cache,
                    location,
                    radius_km=15
                )
                return filtered_data
            
            return self._pop_cache
            
        except Exception as e:
            print(f"Error loading population data: {e}")
            return self._create_sample_population()
    
    async def fetch_roads(self, location: Dict) -> Optional[gpd.GeoDataFrame]:
        """
        Load static Brampton roads data.
        
        Args:
            location: Dictionary with 'lat' and 'lon' keys for filtering
        
        Returns:
            GeoDataFrame containing roads data, or None if loading fails
        """
        try:
            # Load from cache or file
            if self._roads_cache is None:
                if not os.path.exists(self.roads_path):
                    print(f"Warning: Roads data not found at {self.roads_path}")
                    return self._create_sample_roads()
                
                self._roads_cache = gpd.read_file(self.roads_path)
            
            # Filter by location if needed
            if location:
                filtered_data = self._filter_by_location(
                    self._roads_cache,
                    location,
                    radius_km=10
                )
                return filtered_data
            
            return self._roads_cache
            
        except Exception as e:
            print(f"Error loading roads data: {e}")
            return self._create_sample_roads()
    
    def _filter_by_location(
        self, 
        gdf: gpd.GeoDataFrame, 
        location: Dict, 
        radius_km: float
    ) -> gpd.GeoDataFrame:
        """
        Filter GeoDataFrame to features within radius of location.
        
        Args:
            gdf: GeoDataFrame to filter
            location: Dictionary with 'lat' and 'lon' keys
            radius_km: Radius in kilometers
        
        Returns:
            Filtered GeoDataFrame
        """
        from shapely.geometry import Point
        
        # Create point from location
        point = Point(location['lon'], location['lat'])
        
        # Calculate distance in degrees (rough approximation)
        # 1 degree ≈ 111 km
        radius_deg = radius_km / 111.0
        
        # Create buffer around point
        buffer = point.buffer(radius_deg)
        
        # Filter features that intersect with buffer
        filtered = gdf[gdf.geometry.intersects(buffer)]
        
        return filtered
    
    def _create_sample_infrastructure(self) -> gpd.GeoDataFrame:
        """
        Create sample infrastructure data for Brampton.
        This is used as fallback when static files are not available.
        """
        from shapely.geometry import Point
        
        # Sample infrastructure locations in Brampton
        data = {
            'name': [
                'Brampton City Hall',
                'Peel Memorial Hospital',
                'Fire Station 201',
                'Fire Station 202',
                'Water Treatment Plant',
                'Emergency Operations Centre'
            ],
            'type': [
                'government',
                'hospital',
                'fire_station',
                'fire_station',
                'water',
                'emergency'
            ],
            'capacity': [500, 1200, 50, 50, 100000, 200],
            'lat': [43.7315, 43.6832, 43.7412, 43.6892, 43.7156, 43.7285],
            'lon': [-79.7624, -79.7645, -79.7892, -79.7234, -79.7845, -79.7534]
        }
        
        # Create Point geometries
        geometry = [Point(lon, lat) for lat, lon in zip(data['lat'], data['lon'])]
        
        # Remove lat/lon from data dict (they're now in geometry)
        data.pop('lat')
        data.pop('lon')
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(data, geometry=geometry, crs='EPSG:4326')
        
        return gdf
    
    def _create_sample_population(self) -> gpd.GeoDataFrame:
        """
        Create sample population data for Brampton.
        This is used as fallback when static files are not available.
        """
        from shapely.geometry import Polygon
        
        # Sample census tracts in Brampton with population data
        data = {
            'tract_id': ['BT001', 'BT002', 'BT003', 'BT004', 'BT005'],
            'population': [8500, 12000, 9800, 11500, 7200],
            'density': [3200, 4500, 3800, 4200, 2900],  # per sq km
            'vulnerable_pop': [850, 1440, 980, 1380, 720],  # elderly/children
            'area_km2': [2.66, 2.67, 2.58, 2.74, 2.48]
        }
        
        # Create sample polygon geometries (small rectangles)
        geometries = [
            # Downtown Brampton
            Polygon([
                (-79.7700, 43.7250),
                (-79.7550, 43.7250),
                (-79.7550, 43.7350),
                (-79.7700, 43.7350),
                (-79.7700, 43.7250)
            ]),
            # North Brampton
            Polygon([
                (-79.7700, 43.7350),
                (-79.7550, 43.7350),
                (-79.7550, 43.7450),
                (-79.7700, 43.7450),
                (-79.7700, 43.7350)
            ]),
            # East Brampton
            Polygon([
                (-79.7550, 43.7250),
                (-79.7400, 43.7250),
                (-79.7400, 43.7350),
                (-79.7550, 43.7350),
                (-79.7550, 43.7250)
            ]),
            # West Brampton
            Polygon([
                (-79.7850, 43.7250),
                (-79.7700, 43.7250),
                (-79.7700, 43.7350),
                (-79.7850, 43.7350),
                (-79.7850, 43.7250)
            ]),
            # South Brampton
            Polygon([
                (-79.7700, 43.7150),
                (-79.7550, 43.7150),
                (-79.7550, 43.7250),
                (-79.7700, 43.7250),
                (-79.7700, 43.7150)
            ])
        ]
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(data, geometry=geometries, crs='EPSG:4326')
        
        return gdf
    
    def _create_sample_roads(self) -> gpd.GeoDataFrame:
        """
        Create sample roads data for Brampton.
        This is used as fallback when static files are not available.
        """
        from shapely.geometry import LineString
        
        # Sample major roads in Brampton
        data = {
            'name': [
                'Queen Street',
                'Main Street North',
                'Bovaird Drive',
                'Steeles Avenue',
                'Highway 410'
            ],
            'road_class': [
                'arterial',
                'arterial',
                'arterial',
                'arterial',
                'highway'
            ],
            'lanes': [4, 4, 4, 6, 8],
            'capacity_vph': [2000, 2000, 2000, 3000, 6000]  # vehicles per hour
        }
        
        # Create sample LineString geometries
        geometries = [
            # Queen Street (east-west)
            LineString([
                (-79.7850, 43.7300),
                (-79.7400, 43.7300)
            ]),
            # Main Street (north-south)
            LineString([
                (-79.7625, 43.7150),
                (-79.7625, 43.7450)
            ]),
            # Bovaird Drive (east-west)
            LineString([
                (-79.7850, 43.7400),
                (-79.7400, 43.7400)
            ]),
            # Steeles Avenue (east-west)
            LineString([
                (-79.7850, 43.7150),
                (-79.7400, 43.7150)
            ]),
            # Highway 410 (north-south)
            LineString([
                (-79.7500, 43.7100),
                (-79.7500, 43.7500)
            ])
        ]
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(data, geometry=geometries, crs='EPSG:4326')
        
        return gdf
    
    def clear_cache(self):
        """Clear cached data to force reload from files."""
        self._infra_cache = None
        self._pop_cache = None
        self._roads_cache = None