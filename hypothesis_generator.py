"""
Hypothesis Generator for Non-Linear Pipe Freezing Patterns

This module analyzes collected data to understand why pipes freeze at certain
temperatures but not at much colder temperatures (non-linear behavior).
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path
import yaml
from frozen_pipe_analyzer import FrozenPipeAnalyzer
from datetime import datetime


class HypothesisGenerator:
    """Generates hypotheses about non-linear pipe freezing patterns"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize hypothesis generator"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.analyzer = FrozenPipeAnalyzer(config_path)

    def analyze_non_linear_pattern(self) -> Dict:
        """
        Analyze why pipes freeze at moderate cold but not extreme cold.
        Returns comprehensive hypothesis analysis.
        """
        df = self.analyzer.df

        if df.empty:
            return {"error": "No data available for analysis"}

        # Separate freeze and no-freeze events
        freeze_events = df[df['pipe_frozen'] == True].copy()
        no_freeze_events = df[df['pipe_frozen'] == False].copy()
        cold_no_freeze = no_freeze_events[no_freeze_events['temperature_f'] < 32].copy()

        hypotheses = {
            'timestamp': datetime.now().isoformat(),
            'data_summary': {
                'total_observations': len(df),
                'freeze_events': len(freeze_events),
                'cold_no_freeze_events': len(cold_no_freeze)
            },
            'hypotheses': []
        }

        # Hypothesis 1: Wind Chill + Direction Combination
        h1 = self._hypothesis_wind_chill_direction(freeze_events, cold_no_freeze)
        if h1:
            hypotheses['hypotheses'].append(h1)

        # Hypothesis 2: Moderate Cold + Prolonged Exposure
        h2 = self._hypothesis_duration_exposure(freeze_events, cold_no_freeze)
        if h2:
            hypotheses['hypotheses'].append(h2)

        # Hypothesis 3: Extreme Cold Preparedness
        h3 = self._hypothesis_extreme_cold_preparation(freeze_events, cold_no_freeze)
        if h3:
            hypotheses['hypotheses'].append(h3)

        # Hypothesis 4: Humidity and Condensation
        h4 = self._hypothesis_humidity_effect(freeze_events, cold_no_freeze)
        if h4:
            hypotheses['hypotheses'].append(h4)

        # Hypothesis 5: Solar Radiation and Time of Day
        h5 = self._hypothesis_solar_radiation(freeze_events, cold_no_freeze)
        if h5:
            hypotheses['hypotheses'].append(h5)

        # Hypothesis 6: Wind Speed Threshold Effect
        h6 = self._hypothesis_wind_speed_threshold(freeze_events, cold_no_freeze)
        if h6:
            hypotheses['hypotheses'].append(h6)

        # Calculate confidence scores
        self._calculate_confidence_scores(hypotheses)

        return hypotheses

    def _hypothesis_wind_chill_direction(self, freeze: pd.DataFrame, no_freeze: pd.DataFrame) -> Dict:
        """
        Hypothesis: Pipes freeze when wind from vulnerable direction combines
        with moderate cold, but extreme cold from any direction causes protection.
        """
        if freeze.empty:
            return None

        vulnerable_dirs = self.config['analysis']['vulnerable_wind_directions']
        tolerance = self.config['analysis']['vulnerable_direction_tolerance']

        def is_vulnerable_dir(deg):
            return any(
                abs(deg - vdir) <= tolerance or abs(deg - vdir) >= (360 - tolerance)
                for vdir in vulnerable_dirs
            )

        freeze['is_vulnerable_dir'] = freeze['wind_direction_deg'].apply(is_vulnerable_dir)
        no_freeze['is_vulnerable_dir'] = no_freeze['wind_direction_deg'].apply(is_vulnerable_dir)

        freeze_vuln_pct = freeze['is_vulnerable_dir'].mean() * 100 if not freeze.empty else 0
        no_freeze_vuln_pct = no_freeze['is_vulnerable_dir'].mean() * 100 if not no_freeze.empty else 0

        # Calculate average temps
        freeze_avg_temp = freeze['temperature_f'].mean() if not freeze.empty else 0
        no_freeze_avg_temp = no_freeze['temperature_f'].mean() if not no_freeze.empty else 0

        evidence = []

        if freeze_vuln_pct > 50:
            evidence.append(f"{freeze_vuln_pct:.0f}% of freeze events occurred with vulnerable wind direction")

        if no_freeze_vuln_pct < 30:
            evidence.append(f"Only {no_freeze_vuln_pct:.0f}% of cold no-freeze events had vulnerable wind direction")

        if not freeze.empty and not no_freeze.empty:
            freeze_with_wind = freeze[freeze['wind_speed_mph'] > 5]
            if not freeze_with_wind.empty:
                avg_wind = freeze_with_wind['wind_speed_mph'].mean()
                evidence.append(f"Average wind speed during freeze: {avg_wind:.1f} mph")

        return {
            'name': 'Wind Direction and Chill Combination',
            'description': (
                'Pipes are more likely to freeze when cold wind comes from specific '
                'vulnerable directions (e.g., north-facing exposure), creating localized '
                'wind chill effects on the pipe.'
            ),
            'evidence': evidence,
            'supporting_data': {
                'freeze_vulnerable_direction_pct': round(freeze_vuln_pct, 1),
                'no_freeze_vulnerable_direction_pct': round(no_freeze_vuln_pct, 1),
                'freeze_avg_temp': round(freeze_avg_temp, 1),
                'no_freeze_avg_temp': round(no_freeze_avg_temp, 1)
            },
            'confidence': 0.0  # Will be calculated later
        }

    def _hypothesis_duration_exposure(self, freeze: pd.DataFrame, no_freeze: pd.DataFrame) -> Dict:
        """
        Hypothesis: Moderate cold for extended periods causes freezing,
        while brief extreme cold doesn't allow heat loss.
        """
        if freeze.empty:
            return None

        # This would require time-series analysis of consecutive cold periods
        # For now, provide the framework

        evidence = [
            "Moderate temperatures (20-32°F) allow gradual heat loss from pipes",
            "Thermal mass of water in pipes requires time to freeze",
            "Extreme cold (<10°F) often triggers immediate preventive action"
        ]

        return {
            'name': 'Duration of Cold Exposure',
            'description': (
                'Pipes freeze when exposed to moderate cold (20-32°F) for extended periods '
                '(multiple hours), allowing gradual heat loss. Brief periods of extreme cold '
                'may not provide sufficient time for the thermal mass to freeze.'
            ),
            'evidence': evidence,
            'supporting_data': {
                'note': 'Requires continuous monitoring data to fully validate'
            },
            'confidence': 0.0
        }

    def _hypothesis_extreme_cold_preparation(self, freeze: pd.DataFrame, no_freeze: pd.DataFrame) -> Dict:
        """
        Hypothesis: Extreme cold prompts protective measures, moderate cold doesn't.
        """
        if freeze.empty and no_freeze.empty:
            return None

        freeze_avg_temp = freeze['temperature_f'].mean() if not freeze.empty else 32
        no_freeze_cold = no_freeze[no_freeze['temperature_f'] < 15] if not no_freeze.empty else pd.DataFrame()
        no_freeze_cold_avg = no_freeze_cold['temperature_f'].mean() if not no_freeze_cold.empty else 0

        evidence = []

        if freeze_avg_temp > 20:
            evidence.append(
                f"Average freeze temperature ({freeze_avg_temp:.1f}°F) is in the 'moderate cold' range"
            )

        if not no_freeze_cold.empty:
            evidence.append(
                f"No freezing occurred at much colder temperatures (avg: {no_freeze_cold_avg:.1f}°F)"
            )

        evidence.extend([
            "Extreme cold warnings trigger preventive actions: dripping faucets, cabinet doors open",
            "Moderate cold (20-32°F) may not trigger these precautions",
            "Human behavior adaptation is a key non-linear factor"
        ])

        return {
            'name': 'Extreme Cold Preparedness Paradox',
            'description': (
                'The non-linear pattern may be explained by human behavior: extreme cold weather '
                'triggers warnings and preventive measures (dripping faucets, opening cabinet doors, '
                'adding insulation), while moderate cold doesn\'t prompt such actions.'
            ),
            'evidence': evidence,
            'supporting_data': {
                'freeze_avg_temp': round(freeze_avg_temp, 1),
                'extreme_cold_no_freeze_avg': round(no_freeze_cold_avg, 1) if not no_freeze_cold.empty else None
            },
            'confidence': 0.0
        }

    def _hypothesis_humidity_effect(self, freeze: pd.DataFrame, no_freeze: pd.DataFrame) -> Dict:
        """
        Hypothesis: High humidity at moderate cold increases freeze risk.
        """
        if freeze.empty:
            return None

        freeze_avg_humidity = freeze['humidity'].mean() if not freeze.empty else 0
        no_freeze_avg_humidity = no_freeze['humidity'].mean() if not no_freeze.empty else 0

        evidence = []

        if freeze_avg_humidity > 65:
            evidence.append(f"Average humidity during freeze events: {freeze_avg_humidity:.0f}%")

        if abs(freeze_avg_humidity - no_freeze_avg_humidity) > 10:
            evidence.append(
                f"Humidity difference: Freeze avg {freeze_avg_humidity:.0f}% vs No-Freeze avg {no_freeze_avg_humidity:.0f}%"
            )

        evidence.extend([
            "High humidity increases convective heat transfer",
            "Moisture condensation on pipes accelerates cooling",
            "Dry air in extreme cold provides some insulation"
        ])

        return {
            'name': 'Humidity-Enhanced Heat Loss',
            'description': (
                'High relative humidity at moderate temperatures increases heat loss from pipes '
                'through enhanced convective heat transfer and condensation effects. Extremely '
                'cold air is typically very dry, reducing this effect.'
            ),
            'evidence': evidence,
            'supporting_data': {
                'freeze_avg_humidity': round(freeze_avg_humidity, 1),
                'no_freeze_avg_humidity': round(no_freeze_avg_humidity, 1)
            },
            'confidence': 0.0
        }

    def _hypothesis_solar_radiation(self, freeze: pd.DataFrame, no_freeze: pd.DataFrame) -> Dict:
        """
        Hypothesis: Nighttime moderate cold vs daytime extreme cold.
        """
        if freeze.empty:
            return None

        freeze_night = freeze[freeze['is_daytime'] == False]
        no_freeze_day = no_freeze[no_freeze['is_daytime'] == True]

        freeze_night_pct = (len(freeze_night) / len(freeze) * 100) if not freeze.empty else 0
        no_freeze_day_pct = (len(no_freeze_day) / len(no_freeze) * 100) if not no_freeze.empty else 0

        evidence = []

        if freeze_night_pct > 60:
            evidence.append(f"{freeze_night_pct:.0f}% of freeze events occurred at night")

        if no_freeze_day_pct > 40:
            evidence.append(f"{no_freeze_day_pct:.0f}% of cold no-freeze events occurred during day")

        evidence.extend([
            "Solar radiation during daytime provides passive warming",
            "Nighttime radiative cooling accelerates heat loss",
            "Even extreme cold during sunny days may not freeze pipes on sun-exposed walls"
        ])

        return {
            'name': 'Solar Radiation and Diurnal Cycle',
            'description': (
                'Pipes may freeze during moderate cold nights but not during extremely cold '
                'days due to solar radiation warming. The absence of solar input at night '
                'allows uninterrupted heat loss.'
            ),
            'evidence': evidence,
            'supporting_data': {
                'freeze_nighttime_pct': round(freeze_night_pct, 1),
                'no_freeze_daytime_pct': round(no_freeze_day_pct, 1)
            },
            'confidence': 0.0
        }

    def _hypothesis_wind_speed_threshold(self, freeze: pd.DataFrame, no_freeze: pd.DataFrame) -> Dict:
        """
        Hypothesis: Specific wind speed range causes optimal heat loss.
        """
        if freeze.empty:
            return None

        freeze_avg_wind = freeze['wind_speed_mph'].mean() if not freeze.empty else 0
        no_freeze_avg_wind = no_freeze['wind_speed_mph'].mean() if not no_freeze.empty else 0

        # Check for wind speed "sweet spot"
        freeze_moderate_wind = freeze[(freeze['wind_speed_mph'] >= 5) & (freeze['wind_speed_mph'] <= 20)]
        moderate_wind_pct = (len(freeze_moderate_wind) / len(freeze) * 100) if not freeze.empty else 0

        evidence = []

        if moderate_wind_pct > 50:
            evidence.append(
                f"{moderate_wind_pct:.0f}% of freeze events occurred with moderate wind (5-20 mph)"
            )

        evidence.extend([
            f"Average wind speed during freeze: {freeze_avg_wind:.1f} mph",
            f"Average wind speed during no-freeze cold: {no_freeze_avg_wind:.1f} mph",
            "Moderate wind speeds maximize convective heat loss without triggering protection",
            "Very high winds in extreme cold may prompt immediate protective action"
        ])

        return {
            'name': 'Optimal Wind Speed for Freezing',
            'description': (
                'There may be an optimal wind speed range (5-20 mph) that maximizes heat loss '
                'from pipes without triggering weather warnings. Extreme cold with high winds '
                'generates warnings and protective responses.'
            ),
            'evidence': evidence,
            'supporting_data': {
                'freeze_avg_wind_mph': round(freeze_avg_wind, 1),
                'no_freeze_avg_wind_mph': round(no_freeze_avg_wind, 1),
                'moderate_wind_freeze_pct': round(moderate_wind_pct, 1)
            },
            'confidence': 0.0
        }

    def _calculate_confidence_scores(self, hypotheses: Dict):
        """Calculate confidence scores for each hypothesis based on evidence"""
        for h in hypotheses['hypotheses']:
            score = 0.0
            evidence_count = len(h['evidence'])

            # Base score on amount of evidence
            score += min(evidence_count * 0.15, 0.5)

            # Check data quality
            if hypotheses['data_summary']['freeze_events'] >= 3:
                score += 0.2

            if hypotheses['data_summary']['cold_no_freeze_events'] >= 5:
                score += 0.2

            # Specific hypothesis bonuses
            if h['name'] == 'Extreme Cold Preparedness Paradox':
                score += 0.1  # Strong logical basis

            h['confidence'] = min(round(score, 2), 1.0)

    def generate_report(self) -> str:
        """Generate a comprehensive text report"""
        analysis = self.analyze_non_linear_pattern()

        if 'error' in analysis:
            return f"Error: {analysis['error']}"

        report = []
        report.append("=" * 70)
        report.append("FROZEN PIPE NON-LINEAR BEHAVIOR ANALYSIS")
        report.append("=" * 70)
        report.append(f"\nGenerated: {analysis['timestamp']}")
        report.append(f"\nData Summary:")
        report.append(f"  • Total Observations: {analysis['data_summary']['total_observations']}")
        report.append(f"  • Freeze Events: {analysis['data_summary']['freeze_events']}")
        report.append(f"  • Cold No-Freeze Events: {analysis['data_summary']['cold_no_freeze_events']}")

        report.append("\n" + "=" * 70)
        report.append("HYPOTHESES FOR NON-LINEAR FREEZING PATTERN")
        report.append("=" * 70)

        for i, h in enumerate(analysis['hypotheses'], 1):
            report.append(f"\n{i}. {h['name']}")
            report.append(f"   Confidence: {h['confidence'] * 100:.0f}%")
            report.append(f"\n   {h['description']}")

            report.append(f"\n   Evidence:")
            for evidence in h['evidence']:
                report.append(f"     • {evidence}")

            if h['supporting_data']:
                report.append(f"\n   Supporting Data:")
                for key, value in h['supporting_data'].items():
                    if value is not None:
                        report.append(f"     • {key}: {value}")

            report.append("")

        report.append("=" * 70)
        report.append("RECOMMENDATIONS")
        report.append("=" * 70)
        report.append("\n1. Continue collecting data during various weather conditions")
        report.append("2. Record freeze events with detailed notes")
        report.append("3. Document any preventive measures taken (faucet dripping, etc.)")
        report.append("4. Monitor patterns over multiple freeze/thaw cycles")
        report.append("5. Consider installing temperature sensors on the actual pipe")
        report.append("\n" + "=" * 70)

        return "\n".join(report)


if __name__ == "__main__":
    generator = HypothesisGenerator()
    report = generator.generate_report()
    print(report)

    # Save report
    report_path = Path("data/hypothesis_report.txt")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    print(f"\n✓ Report saved to {report_path}")
