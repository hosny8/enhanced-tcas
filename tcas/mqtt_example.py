import time
import json
from mqtt_client import TCASMQTTClient, MQTTConfig as ClientConfig
from mqtt_server import TCASMQTTServer, MQTTConfig as ServerConfig
from data_processor import SensorData

def main():
    # Configure MQTT server
    server_config = ServerConfig(
        broker_address="localhost",
        broker_port=1883,
        client_id="tcas_server"
    )
    
    # Configure MQTT client
    client_config = ClientConfig(
        broker_address="localhost",
        broker_port=1883,
        client_id="tcas_sensor_client"
    )
    
    # Initialize server and client
    server = TCASMQTTServer(server_config)
    client = TCASMQTTClient(client_config)
    
    # Connect to MQTT broker
    if not server.connect():
        print("Failed to connect server to MQTT broker")
        return
    
    if not client.connect():
        print("Failed to connect client to MQTT broker")
        server.disconnect()
        return
    
    try:
        # Example sensor data for ownship
        ownship_data = SensorData(
            image_data=None,
            transponder_data={
                'identifier': 'AIRCRAFT001',
                'altitude': 35000,
                'speed': 450,
                'heading': 90,
                'position': {'lat': 40.7128, 'lon': -74.0060}
            },
            radar_data={
                'range': 5000,
                'bearing': 45,
                'elevation': 0,
                'strength': 0.8,
                'relative_velocity': 100
            },
            timestamp=time.time(),
            additional_features={
                'classification_confidence': 0.95,
                'object_type': 'aircraft'
            }
        )
        
        # Example sensor data for intruder
        intruder_data = SensorData(
            image_data=None,
            transponder_data={
                'identifier': 'AIRCRAFT002',
                'altitude': 35000,
                'speed': 400,
                'heading': 270,
                'position': {'lat': 40.7128, 'lon': -74.0060}
            },
            radar_data={
                'range': 4500,
                'bearing': 135,
                'elevation': 0,
                'strength': 0.85,
                'relative_velocity': -80
            },
            timestamp=time.time(),
            additional_features={
                'classification_confidence': 0.92,
                'object_type': 'aircraft'
            }
        )
        
        # Publish sensor data from client
        print("Publishing ownship data...")
        client.publish_sensor_data(ownship_data)
        
        time.sleep(1)  # Wait for server to process
        
        print("Publishing intruder data...")
        client.publish_sensor_data(intruder_data)
        
        # Wait for processing and alerts
        time.sleep(2)
        
        # Publish status updates
        status_data = {
            'aircraft_id': 'AIRCRAFT001',
            'status': {
                'system_health': 'normal',
                'sensor_status': 'operational',
                'last_update': time.time()
            }
        }
        client.publish_status(status_data)
        
        # Keep the connection alive for a while to receive alerts
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("\nStopping MQTT communication...")
    finally:
        # Clean up
        client.disconnect()
        server.disconnect()

if __name__ == "__main__":
    main() 