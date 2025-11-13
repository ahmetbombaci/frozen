"""
Frozen Pipe Analyzer
Main module for analyzing weather conditions and pipe freezing patterns
"""

import pandas as pd
import yaml
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Optional
from weather_data_collector import WeatherDataCollector


class FrozenPipeAnalyzer:
    """Analyzes weather patterns to understand pipe freezing behavior"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize analyzer with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.collector = WeatherDataCollector(config_path)
        self.data_path = Path(self.config['data_collection']['storage_path'])
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize or load historical data
        self.df = self._load_or_create_dataframe()

    def _load_or_create_dataframe(self) -> pd.DataFrame:
        """Load existing data or create new dataframe"""
        if self.data_path.exists():
            return pd.read_csv(self.data_path)
        else:
            return pd.DataFrame(columns=[
                'timestamp', 'temperature_f', 'feels_like_f', 'wind_chill_f',
                'humidity', 'pressure', 'wind_speed_mph', 'wind_direction_deg',
                'wind_direction_name', 'wind_gust_mph', 'weather_condition',
                'weather_description', 'clouds_percent', 'visibility_meters',
                'rain_1h_mm', 'snow_1h_mm', 'is_daytime', 'sunrise', 'sunset',
                'pipe_frozen', 'notes'
            ])

    def collect_and_store(self, pipe_frozen: bool = False, notes: str = "") -> bool:
        """Collect current weather data and store it"""
        weather = self.collector.collect_current_weather()

        if not weather:
            print("Failed to collect weather data")
            return False

        # Enhance data
        weather['wind_direction_name'] = self.collector.get_wind_direction_name(
            weather['wind_direction_deg']
        )
        weather['is_daytime'] = self.collector.is_daytime(
            weather['timestamp'],
            weather['sunrise'],
            weather['sunset']
        )
        weather['pipe_frozen'] = pipe_frozen
        weather['notes'] = notes

        # Append to dataframe
        self.df = pd.concat([self.df, pd.DataFrame([weather])], ignore_index=True)

        # Save to CSV
        self.df.to_csv(self.data_path, index=False)

        print(f"✓ Data collected at {weather['timestamp']}")
        print(f"  Temperature: {weather['temperature_f']}°F")
        print(f"  Wind Chill: {weather['wind_chill_f']}°F")
        print(f"  Wind: {weather['wind_speed_mph']} mph from {weather['wind_direction_name']}")
        print(f"  Pipe Status: {'FROZEN' if pipe_frozen else 'OK'}")

        return True

    def analyze_conditions(self, weather: Dict) -> Dict:
        """Analyze current weather conditions for freeze risk"""
        analysis = {
            'timestamp': weather['timestamp'],
            'risk_factors': [],
            'protective_factors': [],
            'freeze_risk_score': 0.0
        }

        temp_f = weather['temperature_f']
        wind_chill_f = weather['wind_chill_f']
        wind_dir = weather['wind_direction_deg']
        wind_speed = weather['wind_speed_mph']
        humidity = weather['humidity']

        # Factor 1: Temperature
        if temp_f < 32:
            risk = min((32 - temp_f) / 20, 1.0)  # Scale 0-1
            analysis['risk_factors'].append({
                'factor': 'Below Freezing Temperature',
                'value': f"{temp_f}°F",
                'risk_contribution': risk
            })
            analysis['freeze_risk_score'] += risk * 0.3

        # Factor 2: Wind Chill (critical factor)
        if wind_chill_f < temp_f:
            chill_diff = temp_f - wind_chill_f
            risk = min(chill_diff / 15, 1.0)
            analysis['risk_factors'].append({
                'factor': 'Wind Chill Effect',
                'value': f"{wind_chill_f}°F (feels {chill_diff}°F colder)",
                'risk_contribution': risk
            })
            analysis['freeze_risk_score'] += risk * 0.4

        # Factor 3: Wind Direction (vulnerable directions)
        vulnerable_dirs = self.config['analysis']['vulnerable_wind_directions']
        tolerance = self.config['analysis']['vulnerable_direction_tolerance']

        is_vulnerable_direction = any(
            abs(wind_dir - vdir) <= tolerance or abs(wind_dir - vdir) >= (360 - tolerance)
            for vdir in vulnerable_dirs
        )

        if is_vulnerable_direction and wind_speed > 5:
            risk = min(wind_speed / 25, 1.0)
            analysis['risk_factors'].append({
                'factor': 'Vulnerable Wind Direction',
                'value': f"{self.collector.get_wind_direction_name(wind_dir)} at {wind_speed} mph",
                'risk_contribution': risk
            })
            analysis['freeze_risk_score'] += risk * 0.2

        # Factor 4: High Humidity (increases heat loss)
        if humidity > 70 and temp_f < 35:
            risk = min((humidity - 70) / 30, 1.0)
            analysis['risk_factors'].append({
                'factor': 'High Humidity',
                'value': f"{humidity}%",
                'risk_contribution': risk
            })
            analysis['freeze_risk_score'] += risk * 0.1

        # Protective Factor 1: Extreme Cold (pipes may have been protected/drained)
        if temp_f < 10:
            analysis['protective_factors'].append({
                'factor': 'Extreme Cold - Likely Prepared',
                'value': f"{temp_f}°F",
                'note': "In extreme cold, occupants likely took preventive measures"
            })
            analysis['freeze_risk_score'] *= 0.3  # Reduce risk significantly

        # Protective Factor 2: Low Wind (less heat loss)
        if wind_speed < 5:
            analysis['protective_factors'].append({
                'factor': 'Low Wind Speed',
                'value': f"{wind_speed} mph",
                'note': "Minimal convective heat loss"
            })
            analysis['freeze_risk_score'] *= 0.9

        # Protective Factor 3: Daytime with sun
        if weather.get('is_daytime') and weather['clouds_percent'] < 50:
            analysis['protective_factors'].append({
                'factor': 'Daytime Solar Warming',
                'value': f"{100 - weather['clouds_percent']}% clear",
                'note': "Solar radiation provides warming"
            })
            analysis['freeze_risk_score'] *= 0.8

        # Cap risk score at 1.0
        analysis['freeze_risk_score'] = min(analysis['freeze_risk_score'], 1.0)

        return analysis

    def get_freeze_events(self) -> pd.DataFrame:
        """Get all recorded freeze events"""
        if self.df.empty:
            return pd.DataFrame()

        freeze_df = self.df[self.df['pipe_frozen'] == True].copy()
        freeze_df['timestamp'] = pd.to_datetime(freeze_df['timestamp'])
        return freeze_df

    def get_no_freeze_cold_events(self, temp_threshold: float = 32) -> pd.DataFrame:
        """Get events where it was cold but pipe didn't freeze"""
        if self.df.empty:
            return pd.DataFrame()

        no_freeze_df = self.df[
            (self.df['pipe_frozen'] == False) &
            (self.df['temperature_f'] < temp_threshold)
        ].copy()
        no_freeze_df['timestamp'] = pd.to_datetime(no_freeze_df['timestamp'])
        return no_freeze_df

    def print_summary(self):
        """Print summary of collected data"""
        if self.df.empty:
            print("No data collected yet.")
            return

        print("\n" + "="*60)
        print("FROZEN PIPE ANALYSIS SUMMARY")
        print("="*60)

        print(f"\nTotal Observations: {len(self.df)}")

        freeze_events = self.get_freeze_events()
        print(f"Freeze Events Recorded: {len(freeze_events)}")

        if not freeze_events.empty:
            print("\nFreeze Event Details:")
            for _, event in freeze_events.iterrows():
                print(f"  • {event['timestamp']}")
                print(f"    Temp: {event['temperature_f']}°F, Wind Chill: {event['wind_chill_f']}°F")
                print(f"    Wind: {event['wind_speed_mph']} mph from {event['wind_direction_name']}")
                print(f"    Notes: {event['notes']}")

        # Temperature statistics
        if not self.df.empty:
            print(f"\nTemperature Statistics:")
            print(f"  Min: {self.df['temperature_f'].min()}°F")
            print(f"  Max: {self.df['temperature_f'].max()}°F")
            print(f"  Mean: {self.df['temperature_f'].mean():.1f}°F")

            print(f"\nWind Chill Statistics:")
            print(f"  Min: {self.df['wind_chill_f'].min()}°F")
            print(f"  Max: {self.df['wind_chill_f'].max()}°F")
            print(f"  Mean: {self.df['wind_chill_f'].mean():.1f}°F")

        print("="*60 + "\n")


if __name__ == "__main__":
    analyzer = FrozenPipeAnalyzer()

    print("Frozen Pipe Analyzer")
    print("=" * 50)
    print("\nCommands:")
    print("  collect - Collect current weather data")
    print("  freeze - Record current conditions with pipe frozen")
    print("  summary - Show data summary")
    print("  analyze - Analyze current conditions")
    print("  quit - Exit")

    while True:
        cmd = input("\n> ").strip().lower()

        if cmd == "quit":
            break
        elif cmd == "collect":
            analyzer.collect_and_store()
        elif cmd == "freeze":
            notes = input("Notes about freeze event: ")
            analyzer.collect_and_store(pipe_frozen=True, notes=notes)
        elif cmd == "summary":
            analyzer.print_summary()
        elif cmd == "analyze":
            weather = analyzer.collector.collect_current_weather()
            if weather:
                analysis = analyzer.analyze_conditions(weather)
                print(json.dumps(analysis, indent=2))
        else:
            print("Unknown command")
