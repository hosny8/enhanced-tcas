from typing import Dict, List, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class WeatherData:
    """Container for weather-related data."""
    visibility: float  # in meters
    precipitation_rate: float  # in mm/hour
    cloud_ceiling: float  # in meters
    wind_speed: float  # in knots
    wind_direction: float  # in degrees
    turbulence_index: float  # 0-1 scale
    icing_potential: float  # 0-1 scale
    lightning_activity: float  # 0-1 scale

class WeatherRiskAssessor:
    def __init__(self):
        """Initialize weather risk assessment parameters."""
        self.visibility_thresholds = {
            'critical': 1000,  # meters
            'high': 3000,
            'medium': 5000,
            'low': 8000
        }
        self.precipitation_thresholds = {
            'critical': 10,  # mm/hour
            'high': 5,
            'medium': 2,
            'low': 0.5
        }
        self.wind_thresholds = {
            'critical': 50,  # knots
            'high': 35,
            'medium': 25,
            'low': 15
        }
        
    def assess_weather_risk(self, weather_data: WeatherData) -> Dict:
        """
        Assess weather-related risks and their impact on collision avoidance.
        Returns a dictionary with risk assessment and recommendations.
        """
        # Calculate individual risk factors
        visibility_risk = self._calculate_visibility_risk(weather_data.visibility)
        precipitation_risk = self._calculate_precipitation_risk(weather_data.precipitation_rate)
        wind_risk = self._calculate_wind_risk(weather_data.wind_speed)
        turbulence_risk = weather_data.turbulence_index
        icing_risk = weather_data.icing_potential
        lightning_risk = weather_data.lightning_activity
        
        # Calculate combined risk score
        risk_factors = {
            'visibility': visibility_risk,
            'precipitation': precipitation_risk,
            'wind': wind_risk,
            'turbulence': turbulence_risk,
            'icing': icing_risk,
            'lightning': lightning_risk
        }
        
        combined_risk = np.mean(list(risk_factors.values()))
        
        # Determine overall risk level
        risk_level = self._determine_risk_level(combined_risk)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_factors, risk_level)
        
        return {
            'risk_level': risk_level,
            'risk_score': combined_risk,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'weather_conditions': {
                'visibility': weather_data.visibility,
                'precipitation': weather_data.precipitation_rate,
                'wind_speed': weather_data.wind_speed,
                'wind_direction': weather_data.wind_direction,
                'cloud_ceiling': weather_data.cloud_ceiling
            }
        }
    
    def _calculate_visibility_risk(self, visibility: float) -> float:
        """Calculate risk factor based on visibility."""
        if visibility < self.visibility_thresholds['critical']:
            return 1.0
        elif visibility < self.visibility_thresholds['high']:
            return 0.8
        elif visibility < self.visibility_thresholds['medium']:
            return 0.6
        elif visibility < self.visibility_thresholds['low']:
            return 0.4
        return 0.2
    
    def _calculate_precipitation_risk(self, precipitation: float) -> float:
        """Calculate risk factor based on precipitation rate."""
        if precipitation > self.precipitation_thresholds['critical']:
            return 1.0
        elif precipitation > self.precipitation_thresholds['high']:
            return 0.8
        elif precipitation > self.precipitation_thresholds['medium']:
            return 0.6
        elif precipitation > self.precipitation_thresholds['low']:
            return 0.4
        return 0.2
    
    def _calculate_wind_risk(self, wind_speed: float) -> float:
        """Calculate risk factor based on wind speed."""
        if wind_speed > self.wind_thresholds['critical']:
            return 1.0
        elif wind_speed > self.wind_thresholds['high']:
            return 0.8
        elif wind_speed > self.wind_thresholds['medium']:
            return 0.6
        elif wind_speed > self.wind_thresholds['low']:
            return 0.4
        return 0.2
    
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
    
    def _generate_recommendations(self, risk_factors: Dict[str, float], risk_level: str) -> List[str]:
        """Generate specific recommendations based on risk factors and level."""
        recommendations = []
        
        # Visibility-based recommendations
        if risk_factors['visibility'] >= 0.8:
            recommendations.append("Consider alternate routing due to low visibility")
        elif risk_factors['visibility'] >= 0.6:
            recommendations.append("Increase separation distances due to reduced visibility")
        
        # Precipitation-based recommendations
        if risk_factors['precipitation'] >= 0.8:
            recommendations.append("Activate weather radar and maintain increased separation")
        elif risk_factors['precipitation'] >= 0.6:
            recommendations.append("Monitor precipitation intensity and adjust speed accordingly")
        
        # Wind-based recommendations
        if risk_factors['wind'] >= 0.8:
            recommendations.append("Consider altitude change due to strong winds")
        elif risk_factors['wind'] >= 0.6:
            recommendations.append("Adjust speed and heading for wind compensation")
        
        # Turbulence-based recommendations
        if risk_factors['turbulence'] >= 0.8:
            recommendations.append("Activate turbulence mode and increase separation")
        elif risk_factors['turbulence'] >= 0.6:
            recommendations.append("Maintain increased separation in turbulent conditions")
        
        # Icing-based recommendations
        if risk_factors['icing'] >= 0.8:
            recommendations.append("Activate anti-ice systems and consider altitude change")
        elif risk_factors['icing'] >= 0.6:
            recommendations.append("Monitor icing conditions and activate anti-ice as needed")
        
        # Lightning-based recommendations
        if risk_factors['lightning'] >= 0.8:
            recommendations.append("Maintain maximum separation from storm cells")
        elif risk_factors['lightning'] >= 0.6:
            recommendations.append("Monitor lightning activity and adjust route if necessary")
        
        # General recommendations based on risk level
        if risk_level == "CRITICAL":
            recommendations.append("Consider immediate diversion or holding pattern")
        elif risk_level == "HIGH":
            recommendations.append("Increase situational awareness and prepare for possible diversion")
        elif risk_level == "MEDIUM":
            recommendations.append("Maintain increased vigilance and monitor weather conditions")
        
        return recommendations 