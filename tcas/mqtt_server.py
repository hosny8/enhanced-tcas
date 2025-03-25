import paho.mqtt.client as mqtt
import json
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from .data_processor import SensorData, SensorDataProcessor
from .predictor import CollisionPredictor
from .weather_integration import WeatherRiskAssessor, WeatherData
from .terrain_awareness import TerrainAwarenessSystem, TerrainData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MQTTConfig:
    """Configuration for MQTT server."""
    broker_address: str = "localhost"
    broker_port: int = 1883
    keepalive: int = 60
    client_id: str = "tcas_server"
    username: Optional[str] = None
    password: Optional[str] = None
    topics: Dict[str, str] = None

    def __post_init__(self):
        if self.topics is None:
            self.topics = {
                'sensor_data': 'tcas/sensors/data',
                'alerts': 'tcas/alerts',
                'status': 'tcas/status',
                'config': 'tcas/config'
            }

class TCASMQTTServer:
    def __init__(self, config: MQTTConfig):
        """
        Initialize MQTT server for TCAS sensor data processing.
        Args:
            config: MQTT configuration parameters
        """
        self.config = config
        self.client = mqtt.Client(client_id=config.client_id)
        self.connected = False
        self.callbacks = {}
        
        # Initialize TCAS components
        self.data_processor = SensorDataProcessor()
        self.predictor = CollisionPredictor()
        self.weather_assessor = WeatherRiskAssessor()
        self.terrain_assessor = TerrainAwarenessSystem()
        
        # Set up authentication if provided
        if config.username and config.password:
            self.client.username_pw_set(config.username, config.password)
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Set up QoS levels for different topics
        self.qos_levels = {
            'sensor_data': 1,  # At least once delivery
            'alerts': 2,       # Exactly once delivery
            'status': 0,       # At most once delivery
            'config': 1        # At least once delivery
        }
        
        # Store latest sensor data
        self.latest_sensor_data: Dict[str, SensorData] = {}
    
    def connect(self) -> bool:
        """Connect to MQTT broker."""
        try:
            self.client.connect(
                self.config.broker_address,
                self.config.broker_port,
                self.config.keepalive
            )
            self.client.loop_start()
            logger.info(f"Connected to MQTT broker at {self.config.broker_address}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        logger.info("Disconnected from MQTT broker")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker."""
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker")
            # Subscribe to relevant topics
            for topic in self.config.topics.values():
                self.client.subscribe(topic, qos=self.qos_levels.get(topic, 0))
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker."""
        self.connected = False
        if rc != 0:
            logger.warning("Unexpected disconnection from MQTT broker")
        else:
            logger.info("Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, message):
        """Callback for when a message is received."""
        try:
            topic = message.topic
            payload = json.loads(message.payload.decode())
            
            # Process message based on topic
            if topic == self.config.topics['sensor_data']:
                self._process_sensor_data(payload)
            elif topic == self.config.topics['status']:
                self._process_status_update(payload)
            elif topic == self.config.topics['config']:
                self._process_config_update(payload)
            
            # Call registered callback if exists
            if topic in self.callbacks:
                self.callbacks[topic](payload)
            
            logger.debug(f"Processed message on topic {topic}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
    
    def _process_sensor_data(self, payload: Dict[str, Any]):
        """Process incoming sensor data."""
        try:
            # Extract aircraft identifier
            aircraft_id = payload.get('transponder_data', {}).get('identifier', 'unknown')
            
            # Create SensorData object
            sensor_data = SensorData(
                image_data=None,  # Image data not included in MQTT payload
                transponder_data=payload.get('transponder_data', {}),
                radar_data=payload.get('radar_data', {}),
                timestamp=payload.get('timestamp', 0),
                additional_features=payload.get('additional_features', {})
            )
            
            # Store latest sensor data
            self.latest_sensor_data[aircraft_id] = sensor_data
            
            # Process collision risks if we have data for multiple aircraft
            if len(self.latest_sensor_data) >= 2:
                self._process_collision_risks()
            
            logger.info(f"Processed sensor data for aircraft {aircraft_id}")
            
        except Exception as e:
            logger.error(f"Error processing sensor data: {str(e)}")
    
    def _process_collision_risks(self):
        """Process collision risks between aircraft."""
        try:
            # Get the two most recent aircraft
            aircraft_ids = list(self.latest_sensor_data.keys())[-2:]
            ownship_id = aircraft_ids[0]
            intruder_id = aircraft_ids[1]
            
            # Get sensor data
            ownship_data = self.latest_sensor_data[ownship_id]
            intruder_data = self.latest_sensor_data[intruder_id]
            
            # Detect collision risks
            risk_assessment = self.predictor.detect_collision_risk(ownship_data, intruder_data)
            
            # Generate alert
            alert = self.predictor.generate_alert(risk_assessment)
            
            # Publish alert
            self._publish_alert(alert)
            
            logger.info(f"Processed collision risk between {ownship_id} and {intruder_id}")
            
        except Exception as e:
            logger.error(f"Error processing collision risks: {str(e)}")
    
    def _process_status_update(self, payload: Dict[str, Any]):
        """Process status updates."""
        try:
            aircraft_id = payload.get('aircraft_id', 'unknown')
            status = payload.get('status', {})
            
            logger.info(f"Received status update for aircraft {aircraft_id}: {status}")
            
        except Exception as e:
            logger.error(f"Error processing status update: {str(e)}")
    
    def _process_config_update(self, payload: Dict[str, Any]):
        """Process configuration updates."""
        try:
            # Update system configuration based on payload
            logger.info(f"Received configuration update: {payload}")
            
        except Exception as e:
            logger.error(f"Error processing configuration update: {str(e)}")
    
    def _publish_alert(self, alert: Dict[str, Any]):
        """Publish alert to MQTT broker."""
        if not self.connected:
            logger.warning("Not connected to MQTT broker")
            return False
        
        try:
            result = self.client.publish(
                self.config.topics['alerts'],
                json.dumps(alert),
                qos=self.qos_levels['alerts']
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published alert: {alert.get('message', 'No message')}")
                return True
            else:
                logger.error(f"Failed to publish alert: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing alert: {str(e)}")
            return False
    
    def register_callback(self, topic: str, callback: Callable):
        """Register a callback function for a specific topic."""
        self.callbacks[topic] = callback 