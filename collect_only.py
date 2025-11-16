#!/usr/bin/env python3
"""
Lightweight collection script for low-memory devices
Collects data without loading full analyzer into memory
"""

import sys
import yaml
from weather_data_collector import WeatherDataCollector
from pathlib import Path
import csv
from datetime import datetime


def collect_lightweight(config_path='config.yaml'):
    """Collect data with minimal memory footprint"""

    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Collect weather
    collector = WeatherDataCollector(config_path)
    weather = collector.collect_current_weather()

    if not weather:
        print("Failed to collect weather data", file=sys.stderr)
        return 1

    # Add extra fields
    weather['wind_direction_name'] = collector.get_wind_direction_name(
        weather['wind_direction_deg']
    )
    weather['is_daytime'] = collector.is_daytime(
        weather['timestamp'],
        weather['sunrise'],
        weather['sunset']
    )
    weather['pipe_frozen'] = False
    weather['notes'] = ""

    # Ensure data directory exists
    data_path = Path(config['data_collection']['storage_path'])
    data_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to CSV (append mode)
    file_exists = data_path.exists()

    with open(data_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=weather.keys())

        # Write header if new file
        if not file_exists:
            writer.writeheader()

        writer.writerow(weather)

    print(f"✓ Data collected: {weather['temperature_f']}°F, "
          f"Wind chill: {weather['wind_chill_f']}°F, "
          f"Wind: {weather['wind_speed_mph']} mph {weather['wind_direction_name']}")

    return 0


if __name__ == "__main__":
    sys.exit(collect_lightweight())
