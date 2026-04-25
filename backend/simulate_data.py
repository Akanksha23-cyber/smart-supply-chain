#!/usr/bin/env python
"""Simulation script for real-time data generation."""
import asyncio
import httpx
import random
from datetime import datetime, timedelta
import json

BASE_URL = "http://localhost:8000"

# Sample locations
LOCATIONS = [
    ("NYC", 40.7128, -74.0060),
    ("CHI", 41.8781, -87.6298),
    ("DEN", 39.7392, -104.9903),
    ("PHX", 33.4484, -112.0742),
    ("LA", 34.0522, -118.2437),
    ("ATL", 33.7490, -84.3880),
]

WEATHER_CONDITIONS = ["clear", "cloudy", "rainy", "stormy"]
TRAFFIC_LEVELS = ["low", "moderate", "heavy"]


async def simulate_shipment_update(client: httpx.AsyncClient, shipment_id: str):
    """Simulate a shipment location update."""
    try:
        location = random.choice(LOCATIONS)
        event_data = {
            "shipment_id": shipment_id,
            "event_type": "location_update",
            "data": {
                "location": location[0],
                "lat": location[1] + random.uniform(-0.1, 0.1),
                "lon": location[2] + random.uniform(-0.1, 0.1),
                "speed": random.uniform(40, 100),
            },
            "severity": "info",
        }

        response = await client.post(f"{BASE_URL}/events", json=event_data)
        if response.status_code == 200:
            print(f"✅ Location update for {shipment_id}: {location[0]}")
        else:
            print(f"❌ Failed to update {shipment_id}: {response.status_code}")
    except Exception as e:
        print(f"❌ Error updating shipment: {e}")


async def simulate_weather_event(client: httpx.AsyncClient, shipment_id: str):
    """Simulate a weather event."""
    try:
        event_data = {
            "shipment_id": shipment_id,
            "event_type": "weather_update",
            "data": {
                "condition": random.choice(WEATHER_CONDITIONS),
                "temperature": random.uniform(0, 35),
                "wind_speed": random.uniform(0, 50),
            },
            "severity": "info",
        }

        response = await client.post(f"{BASE_URL}/events", json=event_data)
        if response.status_code == 200:
            print(f"✅ Weather update for {shipment_id}")
    except Exception as e:
        print(f"❌ Error with weather event: {e}")


async def simulate_traffic_event(client: httpx.AsyncClient, shipment_id: str):
    """Simulate a traffic event."""
    try:
        event_data = {
            "shipment_id": shipment_id,
            "event_type": "traffic_update",
            "data": {
                "traffic_level": random.choice(TRAFFIC_LEVELS),
                "incidents": random.randint(0, 3),
            },
            "severity": "warning" if random.random() > 0.7 else "info",
        }

        response = await client.post(f"{BASE_URL}/events", json=event_data)
        if response.status_code == 200:
            print(f"✅ Traffic update for {shipment_id}")
    except Exception as e:
        print(f"❌ Error with traffic event: {e}")


async def predict_disruption(client: httpx.AsyncClient, shipment_id: str):
    """Predict disruption for a shipment."""
    try:
        prediction_data = {
            "shipment_id": shipment_id,
            "weather_condition": random.choice(WEATHER_CONDITIONS),
            "traffic_level": random.choice(TRAFFIC_LEVELS),
            "distance_remaining": random.uniform(100, 1000),
        }

        response = await client.post(
            f"{BASE_URL}/predictions/disruption",
            json=prediction_data
        )
        if response.status_code == 200:
            result = response.json()
            print(
                f"⚠️  Disruption prediction for {shipment_id}: "
                f"{result['disruption_probability']:.2%}"
            )
    except Exception as e:
        print(f"❌ Error with prediction: {e}")


async def run_simulation(duration_minutes: int = 5):
    """Run continuous simulation for specified duration."""
    print(f"\n🚀 Starting simulation for {duration_minutes} minutes...\n")

    # Sample shipments to simulate
    shipments = ["SHP-001-URGENT", "SHP-002-STANDARD", "SHP-003-EXPRESS"]

    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=duration_minutes)

    async with httpx.AsyncClient(timeout=10.0) as client:
        iteration = 0
        while datetime.utcnow() < end_time:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")

            for shipment_id in shipments:
                # Random event type
                event_type = random.choice(["location", "weather", "traffic", "prediction"])

                if event_type == "location":
                    await simulate_shipment_update(client, shipment_id)
                elif event_type == "weather":
                    await simulate_weather_event(client, shipment_id)
                elif event_type == "traffic":
                    await simulate_traffic_event(client, shipment_id)
                else:
                    await predict_disruption(client, shipment_id)

                await asyncio.sleep(0.5)

            # Sleep before next iteration
            await asyncio.sleep(5)

    print(f"\n✅ Simulation completed!")


def main():
    """Main entry point."""
    import sys

    duration = 5  # Default 5 minutes
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print("Usage: python simulate_data.py [duration_minutes]")
            sys.exit(1)

    asyncio.run(run_simulation(duration))


if __name__ == "__main__":
    main()
