import numpy as np
from tcas import EnhancedTCAS

def create_sample_data():
    """Create sample data for testing."""
    # Sample transponder data
    ownship_transponder = {
        'position': {'x': 0, 'y': 0, 'z': 10000},
        'altitude': 10000,
        'speed': 250,
        'heading': 90,
        'flight_level': 330,
        'speed_category': 'HIGH',
        'heading_cardinal': 'EAST'
    }
    
    intruder_transponder = {
        'position': {'x': 5000, 'y': 5000, 'z': 9500},
        'altitude': 9500,
        'speed': 220,
        'heading': 270,
        'flight_level': 310,
        'speed_category': 'MEDIUM',
        'heading_cardinal': 'WEST'
    }
    
    # Sample radar data
    ownship_radar = {
        'relative_velocity': {'x': 0, 'y': 0, 'z': 0},
        'target_size': {'length': 30, 'width': 30, 'height': 10},
        'closing_rate': 0,
        'aspect_angle': 0
    }
    
    intruder_radar = {
        'relative_velocity': {'x': -220, 'y': 0, 'z': -100},
        'target_size': {'length': 25, 'width': 25, 'height': 8},
        'closing_rate': 250,
        'aspect_angle': 45
    }
    
    # Sample visual data (simulated image features)
    ownship_visual = np.random.rand(224, 224, 3)
    intruder_visual = np.random.rand(224, 224, 3)
    
    # Sample weather data
    weather_data = {
        'visibility': 5000,
        'precipitation_rate': 2.5,
        'cloud_ceiling': 8000,
        'wind_speed': 25,
        'wind_direction': 45,
        'turbulence_index': 0.7,
        'icing_potential': 0.6,
        'lightning_activity': 0.8
    }
    
    # Sample terrain data
    terrain_data = {
        'aircraft_altitude': 10000,
        'terrain_elevation': 8000,
        'terrain_slope': 15,
        'distance_to_terrain': 2000,
        'terrain_type': 'mountainous',
        'terrain_roughness': 0.8,
        'terrain_obstacles': [
            {'type': 'peak', 'elevation': 8500, 'distance': 5000},
            {'type': 'ridge', 'elevation': 8200, 'distance': 3000}
        ],
        'terrain_clearance': 2000
    }
    
    return {
        'ownship': {
            'transponder': ownship_transponder,
            'radar': ownship_radar,
            'visual': ownship_visual,
            'timestamp': '2024-03-20T10:00:00Z'
        },
        'intruder': {
            'transponder': intruder_transponder,
            'radar': intruder_radar,
            'visual': intruder_visual,
            'timestamp': '2024-03-20T10:00:00Z'
        },
        'weather': weather_data,
        'terrain': terrain_data
    }

def print_detailed_object_info(obj_info: dict, prefix: str = ""):
    """Print detailed information about detected objects."""
    print(f"\n{prefix}Object Information:")
    print(f"Type: {obj_info['basic_info']['type']}")
    print(f"Confidence: {obj_info['basic_info']['confidence']:.2f}")
    print(f"Position: {obj_info['basic_info']['position']}")
    print(f"Altitude: {obj_info['basic_info']['altitude']} ft")
    print(f"Speed: {obj_info['basic_info']['speed']} knots")
    print(f"Heading: {obj_info['basic_info']['heading']}°")
    
    print("\nDetailed Classification:")
    for category, details in obj_info['detailed_classification'].items():
        print(f"- {category}: {details}")
    
    print("\nPossible Types:")
    for type_info in obj_info['possible_types']:
        print(f"- {type_info['type']} ({type_info['confidence']:.2f})")
    
    print("\nAdditional Features:")
    for feature, value in obj_info['additional_features'].items():
        print(f"- {feature}: {value}")

def print_risk_assessment(risk_assessment: dict):
    """Print risk assessment information."""
    print("\nRisk Assessment:")
    print(f"Risk Level: {risk_assessment['risk_level']}")
    print(f"Risk Score: {risk_assessment['risk_score']:.2f}")
    print(f"Time to Collision: {risk_assessment['time_to_collision']:.1f} seconds")
    print(f"Minimum Separation Required: {risk_assessment['min_separation']:.1f} meters")
    
    print("\nRisk Factors:")
    for factor, value in risk_assessment['risk_factors'].items():
        print(f"- {factor}: {value:.2f}")

def print_weather_assessment(weather_assessment: dict):
    """Print weather assessment information."""
    print("\nWeather Assessment:")
    print(f"Risk Level: {weather_assessment['risk_level']}")
    print(f"Risk Score: {weather_assessment['risk_score']:.2f}")
    
    print("\nWeather Conditions:")
    for condition, value in weather_assessment['weather_conditions'].items():
        print(f"- {condition}: {value}")
    
    print("\nRecommendations:")
    for recommendation in weather_assessment['recommendations']:
        print(f"- {recommendation}")

def print_terrain_assessment(terrain_assessment: dict):
    """Print terrain assessment information."""
    print("\nTerrain Assessment:")
    print(f"Risk Level: {terrain_assessment['risk_level']}")
    print(f"Risk Score: {terrain_assessment['risk_score']:.2f}")
    
    print("\nTerrain Conditions:")
    for condition, value in terrain_assessment['terrain_conditions'].items():
        print(f"- {condition}: {value}")
    
    print("\nRecommendations:")
    for recommendation in terrain_assessment['recommendations']:
        print(f"- {recommendation}")

def print_alerts(alerts: list):
    """Print system alerts."""
    print("\nAlerts:")
    for alert in alerts:
        print(f"\nLevel: {alert['level']}")
        print(f"Message: {alert['message']}")
        print(f"Urgency: {alert['urgency']}")
        print(f"Recommended Action: {alert['recommended_action']}")
        if 'weather_conditions' in alert:
            print("Weather Conditions:")
            for condition, value in alert['weather_conditions'].items():
                print(f"- {condition}: {value}")
        if 'terrain_conditions' in alert:
            print("Terrain Conditions:")
            for condition, value in alert['terrain_conditions'].items():
                print(f"- {condition}: {value}")

def main():
    # Initialize Enhanced TCAS
    tcas = EnhancedTCAS()
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Process update
    result = tcas.process_update(
        ownship_data=sample_data['ownship'],
        intruder_data=sample_data['intruder'],
        weather_data=sample_data['weather'],
        terrain_data=sample_data['terrain']
    )
    
    # Print results
    print("\n=== Enhanced TCAS System Output ===")
    print(f"Timestamp: {result['timestamp']}")
    
    print_detailed_object_info(result['ownship'], "Ownship")
    print_detailed_object_info(result['intruder'], "Intruder")
    
    print_risk_assessment(result['risk_assessment'])
    
    if result['weather_assessment']:
        print_weather_assessment(result['weather_assessment'])
    
    if result['terrain_assessment']:
        print_terrain_assessment(result['terrain_assessment'])
    
    print_alerts(result['alerts'])

if __name__ == "__main__":
    main() 