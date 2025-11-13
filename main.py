#!/usr/bin/env python3
"""
Main script for Frozen Pipe Analyzer
Provides easy interface for data collection and analysis
"""

import argparse
import sys
import time
from pathlib import Path
import json

from frozen_pipe_analyzer import FrozenPipeAnalyzer
from hypothesis_generator import HypothesisGenerator
from weather_data_collector import WeatherDataCollector


def collect_data(args):
    """Collect current weather data"""
    analyzer = FrozenPipeAnalyzer(args.config)

    if args.freeze:
        notes = args.notes or input("Notes about freeze event: ")
        success = analyzer.collect_and_store(pipe_frozen=True, notes=notes)
    else:
        success = analyzer.collect_and_store(pipe_frozen=False, notes=args.notes or "")

    if success:
        print("✓ Data collected successfully")
        return 0
    else:
        print("✗ Failed to collect data")
        return 1


def analyze_current(args):
    """Analyze current weather conditions for freeze risk"""
    analyzer = FrozenPipeAnalyzer(args.config)
    weather = analyzer.collector.collect_current_weather()

    if not weather:
        print("✗ Failed to fetch weather data")
        return 1

    analysis = analyzer.analyze_conditions(weather)

    print("\n" + "="*60)
    print("CURRENT WEATHER ANALYSIS")
    print("="*60)
    print(f"\nTimestamp: {analysis['timestamp']}")
    print(f"\nCurrent Conditions:")
    print(f"  Temperature: {weather['temperature_f']}°F")
    print(f"  Wind Chill: {weather['wind_chill_f']}°F")
    print(f"  Wind: {weather['wind_speed_mph']} mph from {weather['wind_direction_name']}")
    print(f"  Humidity: {weather['humidity']}%")
    print(f"  Conditions: {weather['weather_description']}")

    print(f"\n🎯 FREEZE RISK SCORE: {analysis['freeze_risk_score']:.1%}")

    if analysis['risk_factors']:
        print(f"\n⚠️  Risk Factors:")
        for factor in analysis['risk_factors']:
            print(f"  • {factor['factor']}: {factor['value']}")
            print(f"    Risk contribution: {factor['risk_contribution']:.1%}")

    if analysis['protective_factors']:
        print(f"\n✓ Protective Factors:")
        for factor in analysis['protective_factors']:
            print(f"  • {factor['factor']}: {factor['value']}")
            print(f"    {factor['note']}")

    print("="*60 + "\n")

    # Risk level interpretation
    risk = analysis['freeze_risk_score']
    if risk < 0.3:
        print("Assessment: LOW freeze risk")
    elif risk < 0.6:
        print("Assessment: MODERATE freeze risk - Monitor conditions")
    else:
        print("Assessment: HIGH freeze risk - Consider protective measures!")

    return 0


def generate_hypotheses(args):
    """Generate hypothesis report"""
    generator = HypothesisGenerator(args.config)
    report = generator.generate_report()
    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report)
        print(f"\n✓ Report saved to {output_path}")

    return 0


def show_summary(args):
    """Show data summary"""
    analyzer = FrozenPipeAnalyzer(args.config)
    analyzer.print_summary()
    return 0


def monitor_continuous(args):
    """Continuously monitor and collect data"""
    analyzer = FrozenPipeAnalyzer(args.config)
    interval = args.interval or analyzer.config['data_collection']['interval_minutes']

    print(f"Starting continuous monitoring (interval: {interval} minutes)")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Collecting data...")
            analyzer.collect_and_store()

            print(f"Next collection in {interval} minutes...")
            time.sleep(interval * 60)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Frozen Pipe Analyzer - Analyze weather patterns for pipe freezing"
    )
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect current weather data')
    collect_parser.add_argument(
        '--freeze', '-f',
        action='store_true',
        help='Mark this as a freeze event'
    )
    collect_parser.add_argument(
        '--notes', '-n',
        help='Notes about the observation'
    )

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze current conditions')

    # Hypotheses command
    hypo_parser = subparsers.add_parser('hypotheses', help='Generate hypothesis report')
    hypo_parser.add_argument(
        '--output', '-o',
        help='Output file path for report'
    )

    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show data summary')

    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Continuously monitor and collect')
    monitor_parser.add_argument(
        '--interval', '-i',
        type=int,
        help='Collection interval in minutes'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        'collect': collect_data,
        'analyze': analyze_current,
        'hypotheses': generate_hypotheses,
        'summary': show_summary,
        'monitor': monitor_continuous
    }

    handler = handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
