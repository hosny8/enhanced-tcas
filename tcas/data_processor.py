import numpy as np
import cv2
from dataclasses import dataclass
from typing import Tuple, List, Dict, Any

@dataclass
class SensorData:
    """Container for processed sensor data."""
    image_data: np.ndarray
    transponder_data: Dict
    radar_data: Dict
    timestamp: float
    additional_features: Dict[str, Any] = None

class SensorDataProcessor:
    def __init__(self):
        self.sensor_fusion_weights = {
            'transponder': 0.4,
            'radar': 0.4,
            'visual': 0.2
        }
        self.feature_extractors = {
            'size': self._extract_size_features,
            'motion': self._extract_motion_features,
            'shape': self._extract_shape_features
        }
    
    def process_transponder_data(self, raw_data: Dict) -> Dict:
        """Process transponder data into standardized format."""
        processed = {
            'altitude': raw_data.get('altitude', 0),
            'speed': raw_data.get('speed', 0),
            'heading': raw_data.get('heading', 0),
            'position': raw_data.get('position', {'lat': 0, 'lon': 0}),
            'identifier': raw_data.get('identifier', ''),
            'flight_level': self._calculate_flight_level(raw_data.get('altitude', 0)),
            'speed_category': self._categorize_speed(raw_data.get('speed', 0)),
            'heading_cardinal': self._get_cardinal_heading(raw_data.get('heading', 0))
        }
        return processed
    
    def process_radar_data(self, raw_data: Dict) -> Dict:
        """Process radar data into standardized format."""
        processed = {
            'range': raw_data.get('range', 0),
            'bearing': raw_data.get('bearing', 0),
            'elevation': raw_data.get('elevation', 0),
            'strength': raw_data.get('strength', 0),
            'relative_velocity': raw_data.get('relative_velocity', 0),
            'target_size': raw_data.get('target_size', 0),
            'closing_rate': self._calculate_closing_rate(raw_data),
            'aspect_angle': self._calculate_aspect_angle(raw_data)
        }
        return processed
    
    def process_visual_data(self, image_data: np.ndarray) -> np.ndarray:
        """Process visual sensor data with enhanced features."""
        # Convert to grayscale if needed
        if len(image_data.shape) == 3:
            image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        
        # Apply basic image processing
        image_data = cv2.GaussianBlur(image_data, (5, 5), 0)
        image_data = cv2.Canny(image_data, 50, 150)
        
        # Apply morphological operations for better feature extraction
        kernel = np.ones((3,3), np.uint8)
        image_data = cv2.morphologyEx(image_data, cv2.MORPH_CLOSE, kernel)
        
        # Convert back to 3 channels for CNN input
        image_data = cv2.cvtColor(image_data, cv2.COLOR_GRAY2BGR)
        
        return image_data
    
    def _calculate_flight_level(self, altitude: float) -> str:
        """Calculate flight level from altitude."""
        if altitude >= 18000:
            return f"FL{int(altitude/100)}"
        return f"{int(altitude)}ft"
    
    def _categorize_speed(self, speed: float) -> str:
        """Categorize aircraft speed."""
        if speed >= 400:
            return "high"
        elif speed >= 250:
            return "medium"
        return "low"
    
    def _get_cardinal_heading(self, heading: float) -> str:
        """Convert heading to cardinal direction."""
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        index = round(heading / 45) % 8
        return directions[index]
    
    def _calculate_closing_rate(self, radar_data: Dict) -> float:
        """Calculate closing rate from radar data."""
        return radar_data.get('relative_velocity', 0)
    
    def _calculate_aspect_angle(self, radar_data: Dict) -> float:
        """Calculate aspect angle from radar data."""
        return radar_data.get('aspect_angle', 0)
    
    def _extract_size_features(self, image_data: np.ndarray) -> Dict[str, float]:
        """Extract size-related features from image."""
        contours, _ = cv2.findContours(image_data, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return {'area': 0, 'perimeter': 0, 'aspect_ratio': 0}
        
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        return {
            'area': cv2.contourArea(largest_contour),
            'perimeter': cv2.arcLength(largest_contour, True),
            'aspect_ratio': float(w)/h if h != 0 else 0
        }
    
    def _extract_motion_features(self, image_data: np.ndarray) -> Dict[str, float]:
        """Extract motion-related features from image."""
        # Placeholder for motion features
        return {
            'velocity_magnitude': 0.0,
            'direction': 0.0,
            'acceleration': 0.0
        }
    
    def _extract_shape_features(self, image_data: np.ndarray) -> Dict[str, float]:
        """Extract shape-related features from image."""
        contours, _ = cv2.findContours(image_data, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return {'circularity': 0, 'convexity': 0, 'solidity': 0}
        
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Calculate shape features
        area = cv2.contourArea(largest_contour)
        perimeter = cv2.arcLength(largest_contour, True)
        hull = cv2.convexHull(largest_contour)
        hull_area = cv2.contourArea(hull)
        
        return {
            'circularity': 4 * np.pi * area / (perimeter * perimeter) if perimeter != 0 else 0,
            'convexity': perimeter / cv2.arcLength(hull, True) if cv2.arcLength(hull, True) != 0 else 0,
            'solidity': area / hull_area if hull_area != 0 else 0
        }
    
    def extract_features(self, sensor_data: SensorData) -> np.ndarray:
        """Extract relevant features from sensor data."""
        # Combine numerical features
        numerical_features = np.array([
            sensor_data.transponder_data['altitude'],
            sensor_data.transponder_data['speed'],
            sensor_data.transponder_data['heading'],
            sensor_data.radar_data['range'],
            sensor_data.radar_data['bearing'],
            sensor_data.radar_data['elevation'],
            sensor_data.radar_data['closing_rate'],
            sensor_data.radar_data['aspect_angle']
        ])
        
        # Normalize numerical features
        numerical_features = (numerical_features - np.mean(numerical_features)) / np.std(numerical_features)
        
        return numerical_features
    
    def fuse_sensor_data(self, 
                        transponder_data: Dict,
                        radar_data: Dict,
                        visual_data: np.ndarray) -> SensorData:
        """Fuse different sensor data sources with enhanced features."""
        # Process each data source
        processed_transponder = self.process_transponder_data(transponder_data)
        processed_radar = self.process_radar_data(radar_data)
        processed_visual = self.process_visual_data(visual_data)
        
        # Extract additional features
        additional_features = {}
        for feature_name, extractor in self.feature_extractors.items():
            additional_features[feature_name] = extractor(processed_visual)
        
        # Create timestamp
        timestamp = np.datetime64('now').astype(float)
        
        # Create SensorData object with additional features
        return SensorData(
            image_data=processed_visual,
            transponder_data=processed_transponder,
            radar_data=processed_radar,
            timestamp=timestamp,
            additional_features=additional_features
        ) 