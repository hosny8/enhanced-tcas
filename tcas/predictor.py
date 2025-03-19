import numpy as np
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from .data_processor import SensorData

@dataclass
class Trajectory:
    """Container for object trajectory data."""
    positions: List[Tuple[float, float, float]]  # x, y, z coordinates
    velocities: List[Tuple[float, float, float]]  # vx, vy, vz
    timestamps: List[float]
    confidence_scores: List[float] = None
    risk_factors: List[Dict[str, float]] = None

class CollisionPredictor:
    def __init__(self, prediction_window: float = 60.0):
        """
        Initialize collision predictor.
        prediction_window: Time window for prediction in seconds
        """
        self.prediction_window = prediction_window
        self.history_size = 10  # Number of historical points to consider
        self.min_separation_distance = 500  # Minimum safe separation in meters
        self.risk_thresholds = {
            'critical': 300,  # meters
            'high': 500,      # meters
            'medium': 1000,   # meters
            'low': 2000       # meters
        }
        self.velocity_thresholds = {
            'high': 400,      # knots
            'medium': 250,    # knots
            'low': 100        # knots
        }
        
    def predict_trajectory(self, 
                         current_position: Tuple[float, float, float],
                         current_velocity: Tuple[float, float, float],
                         time_steps: int = 60,
                         confidence: float = 1.0) -> Trajectory:
        """Predict future trajectory based on current state with confidence scoring."""
        positions = []
        velocities = []
        timestamps = []
        confidence_scores = []
        risk_factors = []
        
        # Current state
        pos = np.array(current_position)
        vel = np.array(current_velocity)
        t = 0.0
        
        # Predict future positions
        for _ in range(time_steps):
            # Simple constant velocity model with confidence decay
            pos = pos + vel * (self.prediction_window / time_steps)
            
            # Calculate confidence decay based on time
            time_factor = 1.0 - (t / self.prediction_window)
            current_confidence = confidence * time_factor
            
            # Calculate risk factors
            current_risk = self._calculate_risk_factors(pos, vel)
            
            positions.append(tuple(pos))
            velocities.append(tuple(vel))
            timestamps.append(t)
            confidence_scores.append(current_confidence)
            risk_factors.append(current_risk)
            
            t += self.prediction_window / time_steps
        
        return Trajectory(
            positions=positions,
            velocities=velocities,
            timestamps=timestamps,
            confidence_scores=confidence_scores,
            risk_factors=risk_factors
        )
    
    def _calculate_risk_factors(self, position: np.ndarray, velocity: np.ndarray) -> Dict[str, float]:
        """Calculate various risk factors for a given position and velocity."""
        speed = np.linalg.norm(velocity)
        
        return {
            'speed_factor': min(speed / self.velocity_thresholds['high'], 1.0),
            'altitude_factor': 1.0 - (position[2] / 50000),  # Normalize by typical max altitude
            'proximity_factor': 1.0 - (np.linalg.norm(position) / 5000)  # Normalize by typical max range
        }
    
    def calculate_separation(self, 
                           traj1: Trajectory,
                           traj2: Trajectory) -> List[Dict[str, Any]]:
        """Calculate separation distances and risk metrics between two trajectories."""
        separations = []
        
        for i, (pos1, pos2) in enumerate(zip(traj1.positions, traj2.positions)):
            # Calculate Euclidean distance
            dist = np.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(pos1, pos2)))
            
            # Combine risk factors
            combined_risk = self._combine_risk_factors(
                traj1.risk_factors[i],
                traj2.risk_factors[i]
            )
            
            # Calculate confidence in separation prediction
            confidence = min(
                traj1.confidence_scores[i],
                traj2.confidence_scores[i]
            )
            
            separations.append({
                'distance': dist,
                'risk_factors': combined_risk,
                'confidence': confidence,
                'timestamp': traj1.timestamps[i]
            })
        
        return separations
    
    def _combine_risk_factors(self, risk1: Dict[str, float], risk2: Dict[str, float]) -> Dict[str, float]:
        """Combine risk factors from two objects."""
        return {
            'speed_factor': max(risk1['speed_factor'], risk2['speed_factor']),
            'altitude_factor': max(risk1['altitude_factor'], risk2['altitude_factor']),
            'proximity_factor': max(risk1['proximity_factor'], risk2['proximity_factor']),
            'combined_risk': np.mean([
                risk1['speed_factor'],
                risk1['altitude_factor'],
                risk1['proximity_factor'],
                risk2['speed_factor'],
                risk2['altitude_factor'],
                risk2['proximity_factor']
            ])
        }
    
    def detect_collision_risk(self,
                            ownship_data: SensorData,
                            intruder_data: SensorData) -> Dict:
        """
        Detect potential collision risks between ownship and intruder.
        Returns: Dictionary with risk assessment and prediction details
        """
        # Extract current positions and velocities
        own_pos = (
            ownship_data.transponder_data['position']['lat'],
            ownship_data.transponder_data['position']['lon'],
            ownship_data.transponder_data['altitude']
        )
        
        own_vel = (
            ownship_data.transponder_data['speed'] * np.cos(np.radians(ownship_data.transponder_data['heading'])),
            ownship_data.transponder_data['speed'] * np.sin(np.radians(ownship_data.transponder_data['heading'])),
            0  # Assuming constant altitude for simplicity
        )
        
        intruder_pos = (
            intruder_data.transponder_data['position']['lat'],
            intruder_data.transponder_data['position']['lon'],
            intruder_data.transponder_data['altitude']
        )
        
        intruder_vel = (
            intruder_data.transponder_data['speed'] * np.cos(np.radians(intruder_data.transponder_data['heading'])),
            intruder_data.transponder_data['speed'] * np.sin(np.radians(intruder_data.transponder_data['heading'])),
            0
        )
        
        # Get confidence scores from classification
        own_conf = ownship_data.additional_features.get('classification_confidence', 1.0)
        intr_conf = intruder_data.additional_features.get('classification_confidence', 1.0)
        
        # Predict trajectories
        own_trajectory = self.predict_trajectory(own_pos, own_vel, confidence=own_conf)
        intruder_trajectory = self.predict_trajectory(intruder_pos, intruder_vel, confidence=intr_conf)
        
        # Calculate separations with risk metrics
        separations = self.calculate_separation(own_trajectory, intruder_trajectory)
        
        # Find minimum separation and associated metrics
        min_sep_idx = min(range(len(separations)), key=lambda i: separations[i]['distance'])
        min_separation = separations[min_sep_idx]
        
        # Determine risk level
        risk_level = self._determine_risk_level(min_separation['distance'])
        
        return {
            "risk_level": risk_level,
            "min_separation": min_separation['distance'],
            "time_to_closest": min_separation['timestamp'],
            "confidence": min_separation['confidence'],
            "risk_factors": min_separation['risk_factors'],
            "predicted_trajectories": {
                "ownship": own_trajectory,
                "intruder": intruder_trajectory
            },
            "separation_history": separations
        }
    
    def _determine_risk_level(self, separation: float) -> str:
        """Determine risk level based on separation distance."""
        if separation < self.risk_thresholds['critical']:
            return "CRITICAL"
        elif separation < self.risk_thresholds['high']:
            return "HIGH"
        elif separation < self.risk_thresholds['medium']:
            return "MEDIUM"
        elif separation < self.risk_thresholds['low']:
            return "LOW"
        return "NONE"
    
    def generate_alert(self, risk_assessment: Dict) -> Dict:
        """Generate appropriate alert based on risk assessment."""
        risk_level = risk_assessment["risk_level"]
        min_separation = risk_assessment["min_separation"]
        time_to_closest = risk_assessment["time_to_closest"]
        confidence = risk_assessment["confidence"]
        risk_factors = risk_assessment["risk_factors"]
        
        # Generate alert based on risk level and factors
        if risk_level == "CRITICAL":
            return {
                "level": "RA",
                "message": f"RESOLUTION ADVISORY! Critical separation: {min_separation:.1f}m in {time_to_closest:.1f}s",
                "urgency": "CRITICAL",
                "recommended_action": "IMMEDIATE EVASIVE ACTION REQUIRED",
                "confidence": confidence,
                "risk_factors": risk_factors
            }
        elif risk_level == "HIGH":
            return {
                "level": "TA",
                "message": f"TRAFFIC ALERT! Minimum separation: {min_separation:.1f}m in {time_to_closest:.1f}s",
                "urgency": "HIGH",
                "recommended_action": "PREPARE FOR EVASIVE ACTION",
                "confidence": confidence,
                "risk_factors": risk_factors
            }
        elif risk_level == "MEDIUM":
            return {
                "level": "ADVISORY",
                "message": f"Traffic advisory: Separation: {min_separation:.1f}m in {time_to_closest:.1f}s",
                "urgency": "MEDIUM",
                "recommended_action": "MONITOR AND MAINTAIN SEPARATION",
                "confidence": confidence,
                "risk_factors": risk_factors
            }
        else:
            return {
                "level": "INFO",
                "message": f"Traffic information: Separation: {min_separation:.1f}m in {time_to_closest:.1f}s",
                "urgency": "LOW",
                "recommended_action": "CONTINUE MONITORING",
                "confidence": confidence,
                "risk_factors": risk_factors
            } 