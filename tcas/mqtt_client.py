import paho.mqtt.client as mqtt
import json
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from .data_processor import SensorData
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MQTTConfig:
    """Configuration for MQTT client."""
    broker_address: str = "localhost"
    broker_port: int = 1883
    keepalive: int = 60
    client_id: str = "tcas_sensor_client"
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

class TCASMQTTClient:
    def __init__(self, config: MQTTConfig):
        """
        Initialize MQTT client for TCAS sensor data transmission.
        Args:
            config: MQTT configuration parameters
        """
        self.config = config
        self.client = mqtt.Client(client_id=config.client_id)
        self.connected = False
        self.callbacks = {}
        
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
            
            # Call registered callback if exists
            if topic in self.callbacks:
                self.callbacks[topic](payload)
            
            logger.debug(f"Received message on topic {topic}: {payload}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
    
    def register_callback(self, topic: str, callback: Callable):
        """Register a callback function for a specific topic."""
        self.callbacks[topic] = callback
    
    def publish_sensor_data(self, sensor_data: SensorData):
        """Publish sensor data to MQTT broker."""
        if not self.connected:
            logger.warning("Not connected to MQTT broker")
            return False
        
        try:
            # Convert SensorData to dictionary
            data_dict = {
                'timestamp': sensor_data.timestamp,
                'transponder_data': sensor_data.transponder_data,
                'radar_data': sensor_data.radar_data,
                'additional_features': sensor_data.additional_features
            }
            
            # Publish with QoS 1 for reliable delivery
            result = self.client.publish(
                self.config.topics['sensor_data'],
                json.dumps(data_dict),
                qos=self.qos_levels['sensor_data']
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug("Published sensor data successfully")
                return True
            else:
                logger.error(f"Failed to publish sensor data: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing sensor data: {str(e)}")
            return False
    
    def publish_alert(self, alert_data: Dict[str, Any]):
        """Publish alert data to MQTT broker."""
        if not self.connected:
            logger.warning("Not connected to MQTT broker")
            return False
        
        try:
            # Add timestamp to alert data
            alert_data['timestamp'] = time.time()
            
            # Publish with QoS 2 for exactly once delivery
            result = self.client.publish(
                self.config.topics['alerts'],
                json.dumps(alert_data),
                qos=self.qos_levels['alerts']
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published alert: {alert_data.get('message', 'No message')}")
                return True
            else:
                logger.error(f"Failed to publish alert: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing alert: {str(e)}")
            return False
    
    def publish_status(self, status_data: Dict[str, Any]):
        """Publish status information to MQTT broker."""
        if not self.connected:
            logger.warning("Not connected to MQTT broker")
            return False
        
        try:
            # Add timestamp to status data
            status_data['timestamp'] = time.time()
            
            # Publish with QoS 0 for status updates
            result = self.client.publish(
                self.config.topics['status'],
                json.dumps(status_data),
                qos=self.qos_levels['status']
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug("Published status update successfully")
                return True
            else:
                logger.error(f"Failed to publish status: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing status: {str(e)}")
            return False 