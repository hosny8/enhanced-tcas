from typing import Dict, List, Optional, Any
import numpy as np
from .model import ObjectClassifier
from .data_processor import SensorDataProcessor, SensorData
from .predictor import CollisionPredictor
from .weather_integration import WeatherRiskAssessor, WeatherData
from .terrain_awareness import TerrainAwarenessSystem, TerrainData

class EnhancedTCAS:
    def __init__(self):
        """Initialize the Enhanced TCAS system."""
        self.classifier = ObjectClassifier()
        self.data_processor = SensorDataProcessor()
        self.predictor = CollisionPredictor()
        self.weather_assessor = WeatherRiskAssessor()
        self.terrain_assessor = TerrainAwarenessSystem()
        
    def process_update(self,
                      ownship_data: Dict[str, Any],
                      intruder_data: Dict[str, Any],
                      weather_data: Optional[Dict[str, Any]] = None,
                      terrain_data: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Process sensor data and generate alerts.
        Args:
            ownship_data: Dictionary containing ownship sensor data
            intruder_data: Dictionary containing intruder sensor data
            weather_data: Optional dictionary containing weather data
            terrain_data: Optional dictionary containing terrain data
        Returns:
            Dictionary containing processed results and alerts
        """
        # Process sensor data
        ownship_processed = self.data_processor.process_sensor_data(ownship_data)
        intruder_processed = self.data_processor.process_sensor_data(intruder_data)
        
        # Classify objects with enhanced detail
        ownship_classification = self.classifier.classify_object(ownship_processed)
        intruder_classification = self.classifier.classify_object(intruder_processed)
        
        # Generate detailed object information
        ownship_info = self._generate_detailed_object_info(ownship_processed, ownship_classification)
        intruder_info = self._generate_detailed_object_info(intruder_processed, intruder_classification)
        
        # Detect collision risks
        risk_assessment = self.predictor.detect_collision_risk(ownship_processed, intruder_processed)
        
        # Process weather data if available
        weather_assessment = None
        if weather_data:
            weather_data_obj = WeatherData(
                visibility=weather_data.get('visibility', 10000),
                precipitation_rate=weather_data.get('precipitation_rate', 0),
                cloud_ceiling=weather_data.get('cloud_ceiling', 10000),
                wind_speed=weather_data.get('wind_speed', 0),
                wind_direction=weather_data.get('wind_direction', 0),
                turbulence_index=weather_data.get('turbulence_index', 0),
                icing_potential=weather_data.get('icing_potential', 0),
                lightning_activity=weather_data.get('lightning_activity', 0)
            )
            weather_assessment = self.weather_assessor.assess_weather_risk(weather_data_obj)
            
            # Adjust risk assessment based on weather conditions
            risk_assessment = self._adjust_risk_for_weather(risk_assessment, weather_assessment)
        
        # Process terrain data if available
        terrain_assessment = None
        if terrain_data:
            terrain_data_obj = TerrainData(
                aircraft_altitude=terrain_data.get('aircraft_altitude', 0),
                terrain_elevation=terrain_data.get('terrain_elevation', 0),
                terrain_slope=terrain_data.get('terrain_slope', 0),
                distance_to_terrain=terrain_data.get('distance_to_terrain', 10000),
                terrain_type=terrain_data.get('terrain_type', 'unknown'),
                terrain_roughness=terrain_data.get('terrain_roughness', 0),
                terrain_obstacles=terrain_data.get('terrain_obstacles', []),
                terrain_clearance=terrain_data.get('terrain_clearance', 10000)
            )
            terrain_assessment = self.terrain_assessor.assess_terrain_risk(terrain_data_obj)
            
            # Adjust risk assessment based on terrain conditions
            risk_assessment = self._adjust_risk_for_terrain(risk_assessment, terrain_assessment)
        
        # Generate alerts
        alerts = self.predictor.generate_alert(risk_assessment)
        
        # Add weather-related alerts if available
        if weather_assessment:
            alerts.extend(self._generate_weather_alerts(weather_assessment))
            
        # Add terrain-related alerts if available
        if terrain_assessment:
            alerts.extend(self._generate_terrain_alerts(terrain_assessment))
        
        return {
            'ownship': ownship_info,
            'intruder': intruder_info,
            'risk_assessment': risk_assessment,
            'weather_assessment': weather_assessment,
            'terrain_assessment': terrain_assessment,
            'alerts': alerts,
            'timestamp': ownship_data.get('timestamp', '')
        }
    
    def _generate_detailed_object_info(self, 
                                    sensor_data: SensorData,
                                    classification: Dict) -> Dict:
        """Generate detailed information about detected objects."""
        return {
            'basic_info': {
                'type': classification['type'],
                'confidence': classification['confidence'],
                'position': sensor_data.transponder_data['position'],
                'altitude': sensor_data.transponder_data['altitude'],
                'speed': sensor_data.transponder_data['speed'],
                'heading': sensor_data.transponder_data['heading']
            },
            'detailed_classification': classification['detailed_classification'],
            'possible_types': classification['possible_types'],
            'confidence_scores': classification['confidence_scores'],
            'additional_features': sensor_data.additional_features
        }
    
    def _adjust_risk_for_weather(self, 
                               risk_assessment: Dict,
                               weather_assessment: Dict) -> Dict:
        """Adjust risk assessment based on weather conditions."""
        # Increase risk level if weather conditions are severe
        if weather_assessment['risk_level'] == "CRITICAL":
            risk_assessment['risk_level'] = "CRITICAL"
        elif weather_assessment['risk_level'] == "HIGH" and risk_assessment['risk_level'] != "CRITICAL":
            risk_assessment['risk_level'] = "HIGH"
        
        # Adjust separation requirements based on visibility
        visibility_factor = weather_assessment['risk_factors']['visibility']
        if visibility_factor >= 0.8:
            risk_assessment['min_separation'] *= 1.5
        elif visibility_factor >= 0.6:
            risk_assessment['min_separation'] *= 1.2
        
        return risk_assessment
    
    def _adjust_risk_for_terrain(self,
                               risk_assessment: Dict,
                               terrain_assessment: Dict) -> Dict:
        """Adjust risk assessment based on terrain conditions."""
        # Increase risk level if terrain conditions are severe
        if terrain_assessment['risk_level'] == "CRITICAL":
            risk_assessment['risk_level'] = "CRITICAL"
        elif terrain_assessment['risk_level'] == "HIGH" and risk_assessment['risk_level'] != "CRITICAL":
            risk_assessment['risk_level'] = "HIGH"
        
        # Adjust separation requirements based on terrain clearance
        clearance_factor = terrain_assessment['risk_factors']['clearance']
        if clearance_factor >= 0.8:
            risk_assessment['min_separation'] *= 2.0
        elif clearance_factor >= 0.6:
            risk_assessment['min_separation'] *= 1.5
        
        return risk_assessment
    
    def _generate_weather_alerts(self, weather_assessment: Dict) -> List[Dict]:
        """Generate weather-related alerts."""
        alerts = []
        
        # Add weather-specific alerts based on risk level
        if weather_assessment['risk_level'] == "CRITICAL":
            alerts.append({
                "level": "WEATHER_ALERT",
                "message": "CRITICAL WEATHER CONDITIONS DETECTED",
                "urgency": "CRITICAL",
                "recommended_action": "IMMEDIATE WEATHER AVOIDANCE REQUIRED",
                "weather_conditions": weather_assessment['weather_conditions']
            })
        elif weather_assessment['risk_level'] == "HIGH":
            alerts.append({
                "level": "WEATHER_ALERT",
                "message": "SEVERE WEATHER CONDITIONS DETECTED",
                "urgency": "HIGH",
                "recommended_action": "PREPARE FOR WEATHER AVOIDANCE",
                "weather_conditions": weather_assessment['weather_conditions']
            })
        
        # Add specific weather-related recommendations
        for recommendation in weather_assessment['recommendations']:
            alerts.append({
                "level": "WEATHER_ADVISORY",
                "message": recommendation,
                "urgency": "MEDIUM",
                "recommended_action": recommendation
            })
        
        return alerts
    
    def _generate_terrain_alerts(self, terrain_assessment: Dict) -> List[Dict]:
        """Generate terrain-related alerts."""
        alerts = []
        
        # Add terrain-specific alerts based on risk level
        if terrain_assessment['risk_level'] == "CRITICAL":
            alerts.append({
                "level": "TERRAIN_ALERT",
                "message": "CRITICAL TERRAIN PROXIMITY",
                "urgency": "CRITICAL",
                "recommended_action": "IMMEDIATE TERRAIN AVOIDANCE REQUIRED",
                "terrain_conditions": terrain_assessment['terrain_conditions']
            })
        elif terrain_assessment['risk_level'] == "HIGH":
            alerts.append({
                "level": "TERRAIN_ALERT",
                "message": "SEVERE TERRAIN PROXIMITY",
                "urgency": "HIGH",
                "recommended_action": "PREPARE FOR TERRAIN AVOIDANCE",
                "terrain_conditions": terrain_assessment['terrain_conditions']
            })
        
        # Add specific terrain-related recommendations
        for recommendation in terrain_assessment['recommendations']:
            alerts.append({
                "level": "TERRAIN_ADVISORY",
                "message": recommendation,
                "urgency": "MEDIUM",
                "recommended_action": recommendation
            })
        
        return alerts 