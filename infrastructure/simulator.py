import random
import time
import json
import requests
from datetime import datetime
from enum import Enum

class WeatherCondition(Enum):
    CLEAR = "clear"
    RAIN = "rain"
    SNOW = "snow"
    FOG = "fog"

class TrafficDensity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CONGESTED = "congested"

class TransportSensorSimulator:
    def __init__(self, infrastructure_id, infrastructure_type, location, server_url):
        self.infrastructure_id = infrastructure_id
        self.infrastructure_type = infrastructure_type
        self.location = location
        self.server_url = server_url
        
        # Define sensor configurations based on infrastructure type
        self.sensors = self._initialize_sensors()
        
    def _initialize_sensors(self):
        """Initialize sensors based on infrastructure type"""
        base_sensors = {
            'traffic_flow': {'min': 0, 'max': 2000, 'unit': 'vehicles/hour'},
            'average_speed': {'min': 0, 'max': 120, 'unit': 'km/h'},
            'weather': {'conditions': [e.value for e in WeatherCondition], 'unit': None},
            'temperature': {'min': -20, 'max': 50, 'unit': '°C'},
        }
        
        infrastructure_specific_sensors = {
            'road': {
                'surface_temperature': {'min': -20, 'max': 60, 'unit': '°C'},
                'surface_moisture': {'min': 0, 'max': 100, 'unit': '%'},
                'surface_condition': {'conditions': ['dry', 'wet', 'icy', 'snow_covered'], 'unit': None}
            },
            'highway': {
                'surface_temperature': {'min': -20, 'max': 60, 'unit': '°C'},
                'surface_moisture': {'min': 0, 'max': 100, 'unit': '%'},
                'weight_load': {'min': 0, 'max': 50000, 'unit': 'kg'},
                'emergency_lane_status': {'conditions': ['clear', 'occupied'], 'unit': None}
            },
            'tunnel': {
                'air_quality': {'min': 0, 'max': 500, 'unit': 'ppm'},
                'visibility': {'min': 0, 'max': 100, 'unit': '%'},
                'ventilation_status': {'conditions': ['off', 'low', 'medium', 'high'], 'unit': None},
                'emergency_lighting': {'conditions': ['off', 'on'], 'unit': None}
            },
            'bridge': {
                'structural_stress': {'min': 0, 'max': 100, 'unit': 'MPa'},
                'vibration': {'min': 0, 'max': 50, 'unit': 'Hz'},
                'expansion_joint_status': {'min': 0, 'max': 100, 'unit': '%'},
                'weight_load': {'min': 0, 'max': 100000, 'unit': 'kg'}
            },
            'traffic_signal': {
                'signal_status': {'conditions': ['red', 'yellow', 'green'], 'unit': None},
                'queue_length': {'min': 0, 'max': 50, 'unit': 'vehicles'},
                'wait_time': {'min': 0, 'max': 120, 'unit': 'seconds'},
                'operational_status': {'conditions': ['normal', 'flashing', 'off'], 'unit': None}
                },
            'streetlight': {
                'light_status': {'conditions': ['off', 'on', 'dimmed'], 'unit': None},
                'light_intensity': {'min': 0, 'max': 100, 'unit': '%'},
                'power_consumption': {'min': 0, 'max': 400, 'unit': 'W'},
                'bulb_health': {'min': 0, 'max': 100, 'unit': '%'}
            }
        }
        
        # Combine base sensors with infrastructure-specific sensors
        return {**base_sensors, **infrastructure_specific_sensors.get(self.infrastructure_type, {})}
    
    def generate_sensor_reading(self, sensor_name, sensor_config):
        """Generate a realistic sensor reading based on sensor type and configuration"""
        if 'conditions' in sensor_config:
            return random.choice(sensor_config['conditions'])
        else:
            base_value = random.uniform(sensor_config['min'], sensor_config['max'])
            noise = random.uniform(-0.05 * (sensor_config['max'] - sensor_config['min']), 
                                 0.05 * (sensor_config['max'] - sensor_config['min']))
            return round(base_value + noise, 2)
    
    def generate_payload(self):
        """Generate a complete sensor data payload"""
        payload = {
            'infrastructure_id': self.infrastructure_id,
            'infrastructure_type': self.infrastructure_type,
            'location': self.location,
            'timestamp': datetime.utcnow().isoformat(),
            'readings': {}
        }
        
        for sensor_name, sensor_config in self.sensors.items():
            payload['readings'][sensor_name] = {
                'value': self.generate_sensor_reading(sensor_name, sensor_config),
                'unit': sensor_config.get('unit')
            }
        
        return payload
    
    def send_data(self):
        """Send data to the server"""
        try:
            payload = self.generate_payload()
            response = requests.post(
                self.server_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            print(f"Data sent successfully: {json.dumps(payload, indent=2)}")

            return response.status_code == 200
            # print(payload)
        except requests.exceptions.RequestException as e:
            print(f"Error sending data: {e}")
            return False

    def run(self, interval=5, duration=None):
        """Run the simulator for a specified duration or indefinitely"""
        start_time = time.time()
        iteration = 1
        
        print(f"Starting {self.infrastructure_type} sensor simulator (ID: {self.infrastructure_id})")
        print(f"Sending data every {interval} seconds")
        
        while True:
            self.send_data()
            print(f"Iteration {iteration} completed")
            
            if duration and (time.time() - start_time) >= duration:
                print("Simulation duration completed")
                break
                
            iteration += 1
            time.sleep(interval)

# Example usage
if __name__ == "__main__":
    # Server configuration
    SERVER_URL = "http://localhost:8000/api/data"
    
    # Example infrastructure configurations
    infrastructures = [
        {
            'id': 'ROAD_001',
            'type': 'road',
            'location': {'lat': 40.7128, 'lng': -74.0060}
        },
        {
            'id': 'TUNNEL_001',
            'type': 'tunnel',
            'location': {'lat': 40.7131, 'lng': -74.0089}
        },
        {
            'id': 'BRIDGE_001',
            'type': 'bridge',
            'location': {'lat': 40.7064, 'lng': -73.9969}
        }
    ]
    
    # Create and run simulators
    simulators = []
    for infra in infrastructures:
        simulator = TransportSensorSimulator(
            infrastructure_id=infra['id'],
            infrastructure_type=infra['type'],
            location=infra['location'],
            server_url=SERVER_URL
        )
        simulators.append(simulator)
    
    # Run each simulator in sequence for demonstration
    for simulator in simulators:
        # Run for 10 minutes (600 seconds) with 5-second intervals
        simulator.run(interval=5, duration=6)