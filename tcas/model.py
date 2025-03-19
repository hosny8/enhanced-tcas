import tensorflow as tf
from tensorflow.keras import layers, models
from typing import Dict, Tuple, List
import numpy as np

class TCASObjectClassifier:
    def __init__(self):
        self.model = self._build_model()
        self.class_hierarchy = self._build_class_hierarchy()
        
    def _build_model(self):
        """Build a CNN model optimized for real-time object classification."""
        model = models.Sequential([
            # Input layer - expecting 64x64x3 sensor data
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
            layers.MaxPooling2D((2, 2)),
            
            # First convolutional block
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            
            # Second convolutional block
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            
            # Additional convolutional block for better feature extraction
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            
            # Flatten and dense layers
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            
            # Output layer - expanded number of classes
            layers.Dense(12, activation='softmax')  # Increased from 4 to 12 classes
        ])
        
        # Compile with appropriate loss and optimizer
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_class_hierarchy(self) -> Dict:
        """Build a hierarchical classification system."""
        return {
            "aircraft": {
                "commercial": {
                    "narrow_body": ["B737", "A320", "B757"],
                    "wide_body": ["B777", "A350", "B787"],
                    "regional": ["CRJ", "ERJ", "ATR"]
                },
                "business": {
                    "light": ["Citation", "Phenom", "Learjet"],
                    "medium": ["Gulfstream", "Global", "Falcon"],
                    "heavy": ["BBJ", "ACJ", "VIP"]
                },
                "military": {
                    "fighter": ["F-16", "F-18", "F-35"],
                    "transport": ["C-130", "C-17", "A400M"],
                    "helicopter": ["Blackhawk", "Apache", "Chinook"]
                }
            },
            "ground_vehicle": {
                "airport": {
                    "service": ["fuel_truck", "catering_truck", "baggage_cart"],
                    "maintenance": ["tug", "pushback", "deicer"],
                    "emergency": ["fire_truck", "ambulance", "police"]
                },
                "military": {
                    "combat": ["tank", "apc", "artillery"],
                    "support": ["logistics", "command", "recovery"]
                }
            },
            "terrain": {
                "natural": {
                    "mountain": ["peak", "ridge", "valley"],
                    "water": ["ocean", "lake", "river"],
                    "forest": ["dense", "sparse", "clearing"]
                },
                "man_made": {
                    "urban": ["city", "suburb", "industrial"],
                    "infrastructure": ["bridge", "dam", "power_plant"]
                }
            },
            "runway": {
                "surface": {
                    "paved": ["concrete", "asphalt", "composite"],
                    "unpaved": ["grass", "gravel", "dirt"]
                },
                "markings": {
                    "precision": ["ILS", "PAPI", "touchdown"],
                    "non_precision": ["threshold", "centerline", "taxiway"]
                }
            }
        }
    
    def preprocess_input(self, sensor_data):
        """Preprocess sensor data for model input."""
        # Resize to 64x64x3 if needed
        if sensor_data.shape != (64, 64, 3):
            sensor_data = tf.image.resize(sensor_data, (64, 64))
        
        # Normalize pixel values
        sensor_data = sensor_data / 255.0
        
        # Add batch dimension
        return tf.expand_dims(sensor_data, 0)
    
    def classify_object(self, sensor_data) -> Tuple[int, float, Dict]:
        """
        Classify object from sensor data.
        Returns: (class_id, confidence_score, detailed_classification)
        """
        # Preprocess input
        processed_data = self.preprocess_input(sensor_data)
        
        # Get prediction
        predictions = self.model.predict(processed_data, verbose=0)
        
        # Get class with highest confidence
        class_id = tf.argmax(predictions[0]).numpy()
        confidence = tf.reduce_max(predictions[0]).numpy()
        
        # Get detailed classification
        detailed_class = self.get_detailed_classification(class_id, predictions[0])
        
        return class_id, confidence, detailed_class
    
    def get_detailed_classification(self, class_id: int, predictions: np.ndarray) -> Dict:
        """Get detailed classification information including subcategories."""
        # Map class_id to hierarchical classification
        class_mapping = {
            0: ("aircraft", "commercial", "narrow_body"),
            1: ("aircraft", "commercial", "wide_body"),
            2: ("aircraft", "commercial", "regional"),
            3: ("aircraft", "business", "light"),
            4: ("aircraft", "business", "medium"),
            5: ("aircraft", "business", "heavy"),
            6: ("ground_vehicle", "airport", "service"),
            7: ("ground_vehicle", "airport", "maintenance"),
            8: ("ground_vehicle", "airport", "emergency"),
            9: ("terrain", "natural", "mountain"),
            10: ("terrain", "man_made", "urban"),
            11: ("runway", "surface", "paved")
        }
        
        main_cat, sub_cat, specific = class_mapping.get(class_id, ("unknown", "unknown", "unknown"))
        
        # Get confidence scores for subcategories
        subcategory_confidences = {
            "main_category": predictions[class_id],
            "subcategory": predictions[class_id],
            "specific_type": predictions[class_id]
        }
        
        return {
            "main_category": main_cat,
            "subcategory": sub_cat,
            "specific_type": specific,
            "confidences": subcategory_confidences,
            "available_types": self.class_hierarchy.get(main_cat, {}).get(sub_cat, [])
        }
    
    def get_class_name(self, class_id: int) -> str:
        """Convert class ID to human-readable name."""
        class_names = {
            0: "Commercial Aircraft - Narrow Body",
            1: "Commercial Aircraft - Wide Body",
            2: "Commercial Aircraft - Regional",
            3: "Business Aircraft - Light",
            4: "Business Aircraft - Medium",
            5: "Business Aircraft - Heavy",
            6: "Airport Service Vehicle",
            7: "Airport Maintenance Vehicle",
            8: "Airport Emergency Vehicle",
            9: "Mountain Terrain",
            10: "Urban Terrain",
            11: "Paved Runway"
        }
        return class_names.get(class_id, "Unknown Object")
    
    def get_object_details(self, detailed_class: Dict) -> str:
        """Generate human-readable object details."""
        return f"{detailed_class['main_category'].title()} - {detailed_class['subcategory'].title()} ({detailed_class['specific_type'].title()})"
    
    def load_weights(self, weights_path):
        """Load pre-trained weights."""
        self.model.load_weights(weights_path) 