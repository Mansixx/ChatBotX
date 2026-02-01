from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests

# Emergency directory
EMERGENCY_DIRECTORY = {
    "default": {
        "police": "112",
        "ambulance": "112", 
        "fire": "112",
        "shelter": "Nearest community shelter"
    }
}

class ActionHandleEmergency(Action):
    
    def name(self) -> Text:
        return "action_handle_emergency"
    
    def validate_location(self, location: str) -> bool:
        """Uses OpenStreetMap API to validate city"""
        if not location:
            return False
        try:
            url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
            headers = {"User-Agent": "RasaCrisisBot"}
            res = requests.get(url, headers=headers, timeout=5)
            return len(res.json()) > 0
        except:
            return False
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # Get intent to determine emergency type
        intent = tracker.latest_message['intent'].get('name')
        
        # Extract location from slot or entity
        location = tracker.get_slot("location")
        if not location:
            # Try to get from entity
            entities = tracker.latest_message.get('entities', [])
            for entity in entities:
                if entity.get('entity') == 'location':
                    location = entity.get('value')
                    break
        
        # Map intent to incident type
        incident_map = {
            'emergency_fire': 'fire',
            'emergency_medical': 'medical',
            'emergency_flood': 'flood',
            'emergency_earthquake': 'earthquake'
        }
        
        incident = incident_map.get(intent, 'unknown')
        
        # If no location yet, ask for it
        if not location:
            dispatcher.utter_message(response="utter_ask_location")
            return [SlotSet("incident_type", incident)]
        
        # Validate location
        valid = self.validate_location(location)
        if not valid:
            dispatcher.utter_message(
                text="I couldn't find this location. Please try a nearby city."
            )
            return []
        
        # Determine risk level
        high_risk = ['fire', 'medical']
        medium_risk = ['flood', 'earthquake']
        
        if incident in high_risk:
            risk = "HIGH"
        elif incident in medium_risk:
            risk = "MEDIUM"
        else:
            risk = "UNKNOWN"
        
        # Get emergency services
        services = EMERGENCY_DIRECTORY["default"]
        
        # Send appropriate response based on risk
        if risk == "HIGH":
            dispatcher.utter_message(text="⚠️ This is a HIGH RISK situation.")
            dispatcher.utter_message(
                text=f"📞 Call immediately:\n"
                     f"• Ambulance: {services['ambulance']}\n"
                     f"• Police: {services['police']}\n"
                     f"• Fire: {services['fire']}"
            )
            dispatcher.utter_message(
                text=f"🏥 Nearest safe place: {services['shelter']}"
            )
        elif risk == "MEDIUM":
            dispatcher.utter_message(text="⚠️ Stay alert - MEDIUM RISK situation.")
            dispatcher.utter_message(
                text=f"📞 Emergency services:\n"
                     f"• Emergency: {services['police']}\n"
                     f"• Shelter: {services['shelter']}"
            )
            dispatcher.utter_message(
                text="Follow local safety guidance and evacuation orders."
            )
        else:
            dispatcher.utter_message(text="Stay alert and follow local safety guidance.")
        
        dispatcher.utter_message(text="I am here if you need further help.")
        
        return [
            SlotSet("risk_level", risk),
            SlotSet("location", location),
            SlotSet("incident_type", incident)
        ]