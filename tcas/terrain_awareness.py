from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass

@dataclass
class TerrainData:
    """Container for terrain-related data."""
    aircraft_altitude: float  # in feet
    terrain_elevation: float  # in feet
    terrain_slope: float  # in degrees
    distance_to_terrain: float  # in meters
    terrain_type: str  # e.g., 'mountain', 'valley', 'plateau'
    terrain_roughness: float  # 0-1 scale
    terrain_obstacles: List[Dict[str, float]]  # List of obstacles with their positions and heights
    terrain_clearance: float  # in feet

class TerrainAwarenessSystem:
    def __init__(self):
        """Initialize terrain awareness parameters."""
        self.minimum_terrain_clearance = {
            'critical': 500,  # feet
            'high': 1000,
            'medium': 2000,
            'low': 3000
        }
        self.slope_thresholds = {
            'critical': 45,  # degrees
            'high': 30,
            'medium': 15,
            'low': 5
        }
        self.roughness_thresholds = {
            'critical': 0.8,
            'high': 0.6,
            'medium': 0.4,
            'low': 0.2
        }
        
    def assess_terrain_risk(self, terrain_data: TerrainData) -> Dict:
        """
        Assess terrain-related risks and their impact on collision avoidance.
        Returns a dictionary with risk assessment and recommendations.
        """
        # Calculate individual risk factors
        clearance_risk = self._calculate_clearance_risk(terrain_data.terrain_clearance)
        slope_risk = self._calculate_slope_risk(terrain_data.terrain_slope)
        roughness_risk = self._calculate_roughness_risk(terrain_data.terrain_roughness)
        obstacle_risk = self._calculate_obstacle_risk(terrain_data.terrain_obstacles)
        
        # Calculate combined risk score
        risk_factors = {
            'clearance': clearance_risk,
            'slope': slope_risk,
            'roughness': roughness_risk,
            'obstacles': obstacle_risk
        }
        
        combined_risk = np.mean(list(risk_factors.values()))
        
        # Determine overall risk level
        risk_level = self._determine_risk_level(combined_risk)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_factors, risk_level, terrain_data)
        
        return {
            'risk_level': risk_level,
            'risk_score': combined_risk,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'terrain_conditions': {
                'altitude': terrain_data.aircraft_altitude,
                'terrain_elevation': terrain_data.terrain_elevation,
                'clearance': terrain_data.terrain_clearance,
                'slope': terrain_data.terrain_slope,
                'terrain_type': terrain_data.terrain_type
            }
        }
    
    def _calculate_clearance_risk(self, clearance: float) -> float:
        """Calculate risk factor based on terrain clearance."""
        if clearance < self.minimum_terrain_clearance['critical']:
            return 1.0
        elif clearance < self.minimum_terrain_clearance['high']:
            return 0.8
        elif clearance < self.minimum_terrain_clearance['medium']:
            return 0.6
        elif clearance < self.minimum_terrain_clearance['low']:
            return 0.4
        return 0.2
    
    def _calculate_slope_risk(self, slope: float) -> float:
        """Calculate risk factor based on terrain slope."""
        if slope > self.slope_thresholds['critical']:
            return 1.0
        elif slope > self.slope_thresholds['high']:
            return 0.8
        elif slope > self.slope_thresholds['medium']:
            return 0.6
        elif slope > self.slope_thresholds['low']:
            return 0.4
        return 0.2
    
    def _calculate_roughness_risk(self, roughness: float) -> float:
        """Calculate risk factor based on terrain roughness."""
        if roughness > self.roughness_thresholds['critical']:
            return 1.0
        elif roughness > self.roughness_thresholds['high']:
            return 0.8
        elif roughness > self.roughness_thresholds['medium']:
            return 0.6
        elif roughness > self.roughness_thresholds['low']:
            return 0.4
        return 0.2
    
    def _calculate_obstacle_risk(self, obstacles: List[Dict[str, float]]) -> float:
        """Calculate risk factor based on terrain obstacles."""
        if not obstacles:
            return 0.2
            
        # Calculate risk based on number and proximity of obstacles
        risk_score = 0.0
        for obstacle in obstacles:
            # Higher risk for closer obstacles
            distance_factor = 1.0 - min(obstacle['distance'] / 5000, 1.0)
            # Higher risk for taller obstacles
            height_factor = min(obstacle['height'] / 1000, 1.0)
            risk_score = max(risk_score, (distance_factor + height_factor) / 2)
            
        return risk_score
    
    def _determine_risk_level(self, combined_risk: float) -> str:
        """Determine overall risk level based on combined risk score."""
        if combined_risk >= 0.8:
            return "CRITICAL"
        elif combined_risk >= 0.6:
            return "HIGH"
        elif combined_risk >= 0.4:
            return "MEDIUM"
        elif combined_risk >= 0.2:
            return "LOW"
        return "NONE"
    
    def _generate_recommendations(self, 
                                risk_factors: Dict[str, float], 
                                risk_level: str,
                                terrain_data: TerrainData) -> List[str]:
        """Generate specific recommendations based on risk factors and terrain data."""
        recommendations = []
        
        # Clearance-based recommendations
        if risk_factors['clearance'] >= 0.8:
            recommendations.append("IMMEDIATE CLIMB REQUIRED - Critical terrain clearance")
        elif risk_factors['clearance'] >= 0.6:
            recommendations.append("Maintain increased altitude - Low terrain clearance")
        
        # Slope-based recommendations
        if risk_factors['slope'] >= 0.8:
            recommendations.append("Avoid steep terrain areas - Critical slope detected")
        elif risk_factors['slope'] >= 0.6:
            recommendations.append("Exercise caution - Significant terrain slope")
        
        # Roughness-based recommendations
        if risk_factors['roughness'] >= 0.8:
            recommendations.append("Maintain increased separation - Rough terrain")
        elif risk_factors['roughness'] >= 0.6:
            recommendations.append("Exercise caution - Moderate terrain roughness")
        
        # Obstacle-based recommendations
        if risk_factors['obstacles'] >= 0.8:
            recommendations.append("Multiple obstacles detected - Maintain maximum clearance")
        elif risk_factors['obstacles'] >= 0.6:
            recommendations.append("Obstacles present - Maintain increased separation")
        
        # Terrain type specific recommendations
        if terrain_data.terrain_type == 'mountain':
            recommendations.append("Mountainous terrain - Maintain increased vigilance")
        elif terrain_data.terrain_type == 'valley':
            recommendations.append("Valley terrain - Monitor terrain clearance")
        
        # General recommendations based on risk level
        if risk_level == "CRITICAL":
            recommendations.append("TERRAIN TERRAIN PULL UP - Immediate action required")
        elif risk_level == "HIGH":
            recommendations.append("Increase terrain clearance and prepare for possible diversion")
        elif risk_level == "MEDIUM":
            recommendations.append("Monitor terrain proximity and maintain safe clearance")
        
        return recommendations 