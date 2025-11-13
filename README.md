# Frozen Pipe Analyzer 🧊

A Python-based weather analysis tool to understand non-linear pipe freezing patterns. This tool collects local weather data based on GPS location and analyzes why pipes freeze at certain cold temperatures but not at much colder temperatures.

## Overview

Frozen pipes don't always follow simple temperature rules. This analyzer helps identify the complex factors that contribute to pipe freezing, including:

- **Wind chill effects** - How wind speed and direction affect heat loss
- **Wind direction** - Vulnerability to specific directional exposure
- **Humidity** - Impact on heat transfer and condensation
- **Solar radiation** - Day vs night freezing patterns
- **Duration** - Time-dependent thermal mass effects
- **Human behavior** - Extreme cold warnings trigger preventive measures

## Key Features

- 🌡️ **Real-time weather data collection** from OpenWeatherMap API
- 📊 **Multi-factor analysis** considering temperature, wind, humidity, and more
- 🔍 **Hypothesis generation** to explain non-linear freezing behavior
- 📈 **Historical data tracking** in CSV format
- ⚠️ **Freeze risk assessment** with confidence scores
- 📍 **GPS-based location** for accurate local weather

## Installation

1. Clone this repository:
```bash
git clone https://github.com/ahmetbombaci/frozen.git
cd frozen
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your location and API key:
```bash
cp config.yaml.example config.yaml
# Edit config.yaml with your GPS coordinates and API key
```

4. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)

## Configuration

Edit `config.yaml` to set:

- **GPS Location**: Your kitchen/pipe location coordinates
- **API Key**: Weather service API credentials
- **Pipe Parameters**: Observed freeze temperatures and pipe details
- **Analysis Settings**: Wind directions, thresholds, and factors

Example:
```yaml
location:
  latitude: 42.3601
  longitude: -71.0589
  name: "Kitchen Area"

weather_api:
  provider: "openweathermap"
  api_key: "YOUR_API_KEY_HERE"

pipe_parameters:
  observed_freeze_temp_f: 28
  observed_no_freeze_temps_f: [15, 10, 5]
  pipe_location: "North-facing exterior wall"
```

## Usage

### Quick Start

**Collect current weather data:**
```bash
python main.py collect
```

**Record a freeze event:**
```bash
python main.py collect --freeze --notes "Kitchen pipe frozen this morning"
```

**Analyze current conditions:**
```bash
python main.py analyze
```

**Generate hypothesis report:**
```bash
python main.py hypotheses --output report.txt
```

**View data summary:**
```bash
python main.py summary
```

**Continuous monitoring:**
```bash
python main.py monitor --interval 30
```

### Detailed Commands

#### 1. Data Collection

Regularly collect weather data to build historical patterns:

```bash
# Normal observation
python main.py collect

# Record freeze event
python main.py collect --freeze

# Add notes to observation
python main.py collect --notes "Noticed ice formation"
```

#### 2. Real-time Analysis

Get instant freeze risk assessment:

```bash
python main.py analyze
```

Output includes:
- Current temperature and wind chill
- Risk factors contributing to freeze potential
- Protective factors reducing risk
- Overall freeze risk score (0-100%)

#### 3. Hypothesis Generation

After collecting data over time, generate insights:

```bash
python main.py hypotheses
```

This analyzes patterns and proposes hypotheses such as:
- **Wind Direction Effect**: Pipes freeze with certain wind directions
- **Extreme Cold Preparedness**: Warnings prompt protective measures
- **Humidity Impact**: High humidity increases heat loss
- **Solar Radiation**: Day vs night freezing differences
- **Wind Speed Threshold**: Optimal wind speeds for freezing

#### 4. Continuous Monitoring

Set up automated data collection:

```bash
# Collect every 30 minutes (default from config)
python main.py monitor

# Custom interval (in minutes)
python main.py monitor --interval 15
```

## Understanding the Non-Linear Pattern

### The Paradox

Pipes may freeze at 28°F but not at 10°F. Why?

### Key Hypotheses

1. **Extreme Cold Preparedness**: Weather warnings at extreme temperatures prompt protective actions (dripping faucets, opening cabinets), while moderate cold doesn't trigger these measures.

2. **Wind Chill + Direction**: Specific combinations of temperature, wind speed, and wind direction create localized extreme conditions on the pipe.

3. **Duration Effect**: Moderate cold for extended periods allows gradual heat loss, while brief extreme cold doesn't provide enough time.

4. **Humidity Factor**: High humidity at moderate temperatures enhances heat loss through convection and condensation.

5. **Solar Radiation**: Daytime warming protects pipes even in extreme cold, while nighttime moderate cold has no solar protection.

## Data Structure

Collected data is stored in `data/observations.csv` with fields:

- Timestamp
- Temperature (°F)
- Feels like temperature
- Wind chill
- Humidity
- Wind speed and direction
- Weather conditions
- Sunrise/sunset times
- Pipe frozen status
- Notes

## Scientific Background

### Wind Chill Formula

The tool uses the National Weather Service wind chill formula:
```
WC = 35.74 + 0.6215T - 35.75(V^0.16) + 0.4275T(V^0.16)
```
Where:
- WC = Wind Chill (°F)
- T = Air Temperature (°F)
- V = Wind Speed (mph)

### Heat Transfer Factors

Pipe freezing depends on:
1. **Conductive heat loss** through pipe walls
2. **Convective heat loss** to moving air
3. **Radiative heat loss** to cold surfaces
4. **Thermal mass** of water in pipes
5. **Insulation** effectiveness

## Advanced Usage

### Interactive Mode

```bash
python frozen_pipe_analyzer.py
```

Commands:
- `collect` - Collect current data
- `freeze` - Record freeze event
- `analyze` - Analyze conditions
- `summary` - Show statistics
- `quit` - Exit

### Custom Configuration

Use different config files:
```bash
python main.py --config custom_config.yaml collect
```

### Scheduled Collection

Use cron (Linux/Mac) or Task Scheduler (Windows):

```bash
# Crontab example: collect every 30 minutes
*/30 * * * * cd /path/to/frozen && python main.py collect
```

## Example Output

### Current Analysis
```
==========================================
CURRENT WEATHER ANALYSIS
==========================================

Timestamp: 2025-11-13T08:30:00

Current Conditions:
  Temperature: 28°F
  Wind Chill: 20°F
  Wind: 12 mph from N
  Humidity: 75%
  Conditions: clear sky

🎯 FREEZE RISK SCORE: 72%

⚠️  Risk Factors:
  • Below Freezing Temperature: 28°F
    Risk contribution: 20%
  • Wind Chill Effect: 20°F (feels 8°F colder)
    Risk contribution: 35%
  • Vulnerable Wind Direction: N at 12 mph
    Risk contribution: 15%
  • High Humidity: 75%
    Risk contribution: 2%

✓ Protective Factors:
  (none)

Assessment: HIGH freeze risk - Consider protective measures!
```

### Hypothesis Report
```
======================================================================
FROZEN PIPE NON-LINEAR BEHAVIOR ANALYSIS
======================================================================

1. Wind Direction and Chill Combination
   Confidence: 85%

   Pipes are more likely to freeze when cold wind comes from specific
   vulnerable directions (e.g., north-facing exposure), creating
   localized wind chill effects on the pipe.

   Evidence:
     • 80% of freeze events occurred with vulnerable wind direction
     • Only 20% of cold no-freeze events had vulnerable wind direction

2. Extreme Cold Preparedness Paradox
   Confidence: 75%

   The non-linear pattern may be explained by human behavior: extreme
   cold weather triggers warnings and preventive measures...
```

## Troubleshooting

### API Connection Issues
- Verify your API key in `config.yaml`
- Check internet connection
- Ensure API quota hasn't been exceeded

### No Data Collected
- Check GPS coordinates are valid
- Verify API key permissions
- Review error messages in output

### Import Errors
- Install all requirements: `pip install -r requirements.txt`
- Check Python version (3.8+ recommended)

## Contributing

Contributions welcome! Areas of interest:
- Additional weather data sources
- Machine learning models for pattern recognition
- Visualization dashboard
- Mobile app integration
- Real-time pipe temperature sensors

## Future Enhancements

- [ ] Machine learning prediction model
- [ ] Real-time alerting system
- [ ] Web dashboard for visualization
- [ ] Integration with smart home sensors
- [ ] Multi-location monitoring
- [ ] Historical weather data import

## License

See LICENSE file for details.

## Acknowledgments

- Weather data from [OpenWeatherMap](https://openweathermap.org/)
- Wind chill formula from National Weather Service
- Inspired by real-world pipe freezing mysteries

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review existing hypotheses and data patterns
- Share your freeze event data to improve analysis

---

**Remember**: The goal is to understand WHY pipes behave non-linearly, not just WHEN they freeze. Keep collecting data across various conditions!
