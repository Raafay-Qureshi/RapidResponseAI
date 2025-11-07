import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

from data.weather_client import WeatherClient


async def test_weather_client():
    """Test the WeatherClient with multiple sample locations"""
    
    # Initialize the client
    client = WeatherClient()
    
    # Check if API key is loaded
    if not client.api_key:
        print("ERROR: OPENWEATHER_API_KEY not found in environment variables!")
        print("Please add it to your .env file")
        return
    
    print(f"✓ API Key loaded: {client.api_key[:10]}...")
    
    # Test multiple locations
    test_locations = [
        {'name': 'Toronto, Canada', 'lat': 43.6532, 'lon': -79.3832},
        {'name': 'New York, USA', 'lat': 40.7128, 'lon': -74.0060},
        {'name': 'London, UK', 'lat': 51.5074, 'lon': -0.1278},
        {'name': 'Tokyo, Japan', 'lat': 35.6762, 'lon': 139.6503},
    ]
    
    for test_location in test_locations:
        print(f"\n{'='*60}")
        print(f"🌤️  Testing location: {test_location['name']}")
        print(f"   Coordinates: {test_location['lat']}, {test_location['lon']}")
        print('='*60)
        
        try:
            # Fetch current weather
            print("\n📡 Fetching current weather data from OpenWeather API...")
            current_weather = await client.fetch_current(test_location)
            
            # Display current weather results
            print("\n✅ Current Weather Results:")
            print(f"Temperature: {current_weather['main']['temp']}°C")
            print(f"Feels like: {current_weather['main']['feels_like']}°C")
            print(f"Description: {current_weather['weather'][0]['description']}")
            print(f"Humidity: {current_weather['main']['humidity']}%")
            print(f"Wind speed: {current_weather['wind']['speed']} m/s")
            print(f"Pressure: {current_weather['main']['pressure']} hPa")
            
            # Save current weather to JSON file
            output_file = f"backend/tests/sample_data/sample_weather_current_{test_location['name'].lower().replace(' ', '_').replace(',', '')}.json"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(current_weather, f, indent=2)
            print(f"\n💾 Current weather data saved to {output_file}")
            
            # Fetch forecast
            print("\n📡 Fetching weather forecast (next 6 hours)...")
            forecast = await client.fetch_forecast(test_location)
            
            if forecast and 'list' in forecast:
                print("\n✅ Forecast Results:")
                print(f"Forecast periods: {len(forecast['list'])}")
                
                for i, period in enumerate(forecast['list'], 1):
                    print(f"\n  Period {i} ({period['dt_txt']}):")
                    print(f"    Temperature: {period['main']['temp']}°C")
                    print(f"    Description: {period['weather'][0]['description']}")
                    print(f"    Humidity: {period['main']['humidity']}%")
                
                # Save forecast to JSON file
                output_file = f"backend/tests/sample_data/sample_weather_forecast_{test_location['name'].lower().replace(' ', '_').replace(',', '')}.json"
                with open(output_file, 'w') as f:
                    json.dump(forecast, f, indent=2)
                print(f"\n💾 Forecast data saved to {output_file}")
            
            # Successfully tested one location, stop testing others
            print("\n" + "="*60)
            print("✅ SUCCESS: Weather data retrieved successfully!")
            print("="*60)
            return
                
        except Exception as e:
            print(f"\n❌ Error with {test_location['name']}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("❌ Failed to retrieve weather data from all test locations")
    print("="*60)


if __name__ == "__main__":
    print("=" * 60)
    print("🌤️  Testing WeatherClient")
    print("=" * 60)
    
    asyncio.run(test_weather_client())