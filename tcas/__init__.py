from .model import TCASObjectClassifier
from .data_processor import SensorDataProcessor, SensorData
from .predictor import CollisionPredictor
from typing import Dict, Any

class EnhancedTCAS:
    def __init__(self):
        """Initialize the Enhanced TCAS system."""
        self.object_classifier = TCASObjectClassifier()
        self.data_processor = SensorDataProcessor()
        self.collision_predictor = CollisionPredictor()
        
    def process_sensor_data(self,
                          transponder_data: dict,
                          radar_data: dict,
                          visual_data: any) -> SensorData:
        """Process and fuse all sensor data."""
        return self.data_processor.fuse_sensor_data(
            transponder_data,
            radar_data,
            visual_data
        )
    
    def classify_object(self, sensor_data: SensorData) -> tuple:
        """Classify detected object using CNN model."""
        return self.object_classifier.classify_object(sensor_data.image_data)
    
    def assess_collision_risk(self,
                            ownship_data: SensorData,
                            intruder_data: SensorData) -> dict:
        """Assess collision risk between ownship and intruder."""
        return self.collision_predictor.detect_collision_risk(
            ownship_data,
            intruder_data
        )
    
    def generate_alert(self, risk_assessment: dict) -> dict:
        """Generate appropriate alert based on risk assessment."""
        return self.collision_predictor.generate_alert(risk_assessment)
    
    def _generate_detailed_object_info(self, 
                                    class_id: int, 
                                    confidence: float, 
                                    detailed_class: Dict) -> Dict[str, Any]:
        """Generate detailed information about a detected object."""
        return {
            "basic_info": {
                "type": self.object_classifier.get_class_name(class_id),
                "confidence": confidence
            },
            "detailed_info": {
                "main_category": detailed_class["main_category"],
                "subcategory": detailed_class["subcategory"],
                "specific_type": detailed_class["specific_type"],
                "available_types": detailed_class["available_types"]
            },
            "confidence_scores": detailed_class["confidences"]
        }
    
    def process_update(self,
                      ownship_data: dict,
                      intruder_data: dict,
                      visual_data: any) -> dict:
        """
        Process a complete update cycle of the TCAS system.
        Returns: Dictionary containing classification, risk assessment, and alerts
        """
        # Process sensor data
        ownship_processed = self.process_sensor_data(
            ownship_data['transponder'],
            ownship_data['radar'],
            visual_data
        )
        
        intruder_processed = self.process_sensor_data(
            intruder_data['transponder'],
            intruder_data['radar'],
            visual_data
        )
        
        # Classify objects with enhanced detail
        ownship_class, ownship_conf, ownship_detailed = self.classify_object(ownship_processed)
        intruder_class, intruder_conf, intruder_detailed = self.classify_object(intruder_processed)
        
        # Assess collision risk
        risk_assessment = self.assess_collision_risk(
            ownship_processed,
            intruder_processed
        )
        
        # Generate alerts
        alerts = self.generate_alert(risk_assessment)
        
        # Generate detailed object information
        ownship_info = self._generate_detailed_object_info(
            ownship_class, 
            ownship_conf, 
            ownship_detailed
        )
        
        intruder_info = self._generate_detailed_object_info(
            intruder_class, 
            intruder_conf, 
            intruder_detailed
        )
        
        return {
            "ownship": ownship_info,
            "intruder": intruder_info,
            "risk_assessment": risk_assessment,
            "alerts": alerts,
            "timestamp": ownship_processed.timestamp
        } 