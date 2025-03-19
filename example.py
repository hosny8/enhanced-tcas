import numpy as np
from tcas import EnhancedTCAS

def create_sample_data():
    """Create sample sensor data for demonstration."""
    # Sample transponder data
    ownship_transponder = {
        'altitude': 35000,  # feet
        'speed': 450,      # knots
        'heading': 90,     # degrees
        'position': {'lat': 40.7128, 'lon': -74.0060},
        'identifier': 'N12345'
    }
    
    intruder_transponder = {
        'altitude': 35000,
        'speed': 400,
        'heading': 270,
        'position': {'lat': 40.7128, 'lon': -74.0061},
        'identifier': 'N67890'
    }
    
    # Sample radar data
    ownship_radar = {
        'range': 0,
        'bearing': 0,
        'elevation': 0,
        'strength': 1.0
    }
    
    intruder_radar = {
        'range': 1000,  # meters
        'bearing': 180,  # degrees
        'elevation': 0,
        'strength': 0.8
    }
    
    # Sample visual data (dummy image)
    visual_data = np.zeros((64, 64, 3), dtype=np.uint8)
    
    return {
        'ownship': {
            'transponder': ownship_transponder,
            'radar': ownship_radar
        },
        'intruder': {
            'transponder': intruder_transponder,
            'radar': intruder_radar
        },
        'visual': visual_data
    }

def print_detailed_object_info(obj_info: dict, prefix: str = ""):
    """Print detailed information about a detected object."""
    print(f"\n{prefix}Object Information:")
    print("-" * 50)
    
    # Basic Information
    print(f"Type: {obj_info['basic_info']['type']}")
    print(f"Confidence: {obj_info['basic_info']['confidence']:.2f}")
    
    # Detailed Information
    print("\nDetailed Classification:")
    print(f"Main Category: {obj_info['detailed_info']['main_category'].title()}")
    print(f"Subcategory: {obj_info['detailed_info']['subcategory'].title()}")
    print(f"Specific Type: {obj_info['detailed_info']['specific_type'].title()}")
    
    # Available Types
    print("\nPossible Types:")
    for type_name in obj_info['detailed_info']['available_types']:
        print(f"- {type_name}")
    
    # Confidence Scores
    print("\nConfidence Scores:")
    for category, score in obj_info['confidence_scores'].items():
        print(f"{category}: {score:.2f}")

def main():
    # Initialize Enhanced TCAS
    tcas = EnhancedTCAS()
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Process update cycle
    result = tcas.process_update(
        sample_data['ownship'],
        sample_data['intruder'],
        sample_data['visual']
    )
    
    # Print results
    print("\nEnhanced TCAS System Results:")
    print("=" * 50)
    
    # Print ownship information
    print_detailed_object_info(result['ownship'], "Ownship")
    
    # Print intruder information
    print_detailed_object_info(result['intruder'], "Intruder")
    
    # Print risk assessment
    print("\nRisk Assessment:")
    print("-" * 50)
    print(f"Risk Level: {result['risk_assessment']['risk_level']}")
    print(f"Minimum Separation: {result['risk_assessment']['min_separation']:.1f}m")
    print(f"Time to Closest: {result['risk_assessment']['time_to_closest']:.1f}s")
    
    # Print alerts
    print("\nAlerts:")
    print("-" * 50)
    print(f"Level: {result['alerts']['level']}")
    print(f"Message: {result['alerts']['message']}")
    print(f"Urgency: {result['alerts']['urgency']}")
    print(f"Recommended Action: {result['alerts']['recommended_action']}")
    
    # Print timestamp
    print(f"\nTimestamp: {result['timestamp']}")

if __name__ == "__main__":
    main() 