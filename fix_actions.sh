#!/bin/bash

echo "=== FIXING ACTION SERVER ==="

echo "1. Stopping containers..."
docker compose down

echo "2. Creating correct actions.py..."
cat > actions/actions.py << 'EOF'
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests

class ActionHandleEmergency(Action):
    def name(self) -> Text:
        return "action_handle_emergency"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        intent = tracker.latest_message.get("intent", {}).get("name", "")
        location = tracker.get_slot("location")
        
        # Simple location extraction
        if not location:
            message = tracker.latest_message.get("text", "").lower()
            cities = ["mumbai", "delhi", "london", "new york"]
            for city in cities:
                if city in message:
                    location = city
                    break
        
        if not location:
            dispatcher.utter_message("Please tell me your city or area.")
            return []
        
        # Emergency info
        emergencies = {
            "emergency_fire": "Fire Emergency",
            "emergency_medical": "Medical Emergency", 
            "emergency_flood": "Flood Emergency",
            "emergency_earthquake": "Earthquake Emergency"
        }
        
        if intent not in emergencies:
            dispatcher.utter_message("I didn't understand. Please specify: fire, flood, earthquake, or medical.")
            return []
        
        # Send response
        dispatcher.utter_message(f"🚨 {emergencies[intent]} 🚨")
        dispatcher.utter_message(f"📍 Location: {location}")
        dispatcher.utter_message("📞 Emergency number: 112")
        dispatcher.utter_message("Please stay on the line for further instructions.")
        
        return [SlotSet("location", location)]
EOF

echo "3. Creating requirements.txt..."
cat > requirements.txt << 'EOF'
rasa-sdk>=3.6.0
requests>=2.28.0
EOF

echo "4. Rebuilding action server..."
docker compose build actions

echo "5. Starting action server..."
docker compose up actions -d

echo "6. Waiting for action server..."
sleep 5

echo "7. Checking action server..."
curl -s http://localhost:5055/health
echo ""

echo "8. Starting all services..."
docker compose up -d

echo "9. Waiting for services..."
sleep 10

echo "10. Testing..."
curl -X POST http://localhost:5005/model/parse \
  -H "Content-Type: application/json" \
  -d '{"text":"fire"}' 2>/dev/null || echo "Test failed"

echo ""
echo "=== FIX COMPLETE ==="