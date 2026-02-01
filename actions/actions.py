from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests

# Emergency directory with country-specific numbers
EMERGENCY_DIRECTORY = {
    "India": {
        "fire": "101",
        "ambulance": "102",
        "police": "100",
        "emergency": "112"
    },
    "USA": {
        "fire": "911",
        "ambulance": "911",
        "police": "911",
        "emergency": "911"
    },
    "UK": {
        "fire": "999",
        "ambulance": "999",
        "police": "999",
        "emergency": "999"
    },
    "Germany": {
        "fire": "112",
        "ambulance": "112",
        "police": "110",
        "emergency": "112"
    },
    "France": {
        "fire": "18",
        "ambulance": "15",
        "police": "17",
        "emergency": "112"
    },
    "default": {
        "fire": "112",
        "ambulance": "112",
        "police": "112",
        "emergency": "112"
    }
}

# Location to country mapping
LOCATION_COUNTRY_MAP = {
    "mumbai": "India",
    "delhi": "India",
    "bangalore": "India",
    "pune": "India",
    "chennai": "India",
    "kolkata": "India",
    "hyderabad": "India",
    "gurgaon": "India",
    "noida": "India",
    "new york": "USA",
    "los angeles": "USA",
    "chicago": "USA",
    "seattle": "USA",
    "boston": "USA",
    "san francisco": "USA",
    "london": "UK",
    "manchester": "UK",
    "birmingham": "UK",
    "berlin": "Germany",
    "munich": "Germany",
    "hamburg": "Germany",
    "paris": "France",
    "lyon": "France",
    "marseille": "France",
}


class ActionHandleFireEmergency(Action):
    """Handle fire emergency with location validation for safe users"""
    
    def name(self) -> Text:
        return "action_handle_fire_emergency"
    
    def validate_location(self, location: str) -> bool:
        """Uses OpenStreetMap API to validate city"""
        if not location:
            return False
        try:
            url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
            headers = {"User-Agent": "RasaCrisisBot/1.0"}
            res = requests.get(url, headers=headers, timeout=5)
            return len(res.json()) > 0
        except:
            return False
    
    def get_country_from_location(self, location: str) -> str:
        """Determine country from location"""
        location_lower = location.lower()
        for city, country in LOCATION_COUNTRY_MAP.items():
            if city in location_lower:
                return country
        return "default"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # Get location from slot or entity
        location = tracker.get_slot("location")
        if not location:
            entities = tracker.latest_message.get('entities', [])
            for entity in entities:
                if entity.get('entity') == 'location':
                    location = entity.get('value')
                    break
        
        if not location:
            dispatcher.utter_message(text="📍 I need your location to send help. What city/area are you in?")
            return []
        
        # Validate location
        valid = self.validate_location(location)
        if not valid:
            dispatcher.utter_message(
                text=f"⚠️ I couldn't verify '{location}'. Please provide a nearby major city or area."
            )
            return [SlotSet("location", None)]
        
        # Get appropriate emergency numbers
        country = self.get_country_from_location(location)
        services = EMERGENCY_DIRECTORY.get(country, EMERGENCY_DIRECTORY["default"])
        
        # Send emergency information
        dispatcher.utter_message(
            text=f"🚨 **EMERGENCY SERVICES FOR {location.upper()}**"
        )
        
        dispatcher.utter_message(
            text=f"📞 **CALL IMMEDIATELY:**\n\n"
                 f"🔥 Fire Emergency: **{services['fire']}**\n"
                 f"🚑 Ambulance: **{services['ambulance']}**\n"
                 f"👮 Police: **{services['police']}**"
        )
        
        dispatcher.utter_message(
            text="⚠️ **WHILE WAITING:**\n"
                 "• Stay outside and away from smoke\n"
                 "• Do NOT re-enter the building\n"
                 "• Account for all people\n"
                 "• Warn others nearby"
        )
        
        return [
            SlotSet("location", location),
            SlotSet("risk_level", "HIGH")
        ]


class ActionHandleFireEmergencyUrgent(Action):
    """Handle fire emergency when people are trapped - CRITICAL"""
    
    def name(self) -> Text:
        return "action_handle_fire_emergency_urgent"
    
    def validate_location(self, location: str) -> bool:
        """Uses OpenStreetMap API to validate city"""
        if not location:
            return False
        try:
            url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
            headers = {"User-Agent": "RasaCrisisBot/1.0"}
            res = requests.get(url, headers=headers, timeout=5)
            return len(res.json()) > 0
        except:
            return False
    
    def get_country_from_location(self, location: str) -> str:
        """Determine country from location"""
        location_lower = location.lower()
        for city, country in LOCATION_COUNTRY_MAP.items():
            if city in location_lower:
                return country
        return "default"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # Get location
        location = tracker.get_slot("location")
        if not location:
            entities = tracker.latest_message.get('entities', [])
            for entity in entities:
                if entity.get('entity') == 'location':
                    location = entity.get('value')
                    break
        
        if not location:
            dispatcher.utter_message(text="📍 URGENT: What is your exact location? (City and address)")
            return []
        
        # Get emergency numbers
        country = self.get_country_from_location(location)
        services = EMERGENCY_DIRECTORY.get(country, EMERGENCY_DIRECTORY["default"])
        
        # Send URGENT information
        dispatcher.utter_message(
            text=f"🚨🚨 **CRITICAL EMERGENCY - {location.upper()}** 🚨🚨"
        )
        
        dispatcher.utter_message(
            text=f"📞 **CALL NOW - PEOPLE TRAPPED:**\n\n"
                 f"🔥 **{services['fire']}** ← CALL THIS NUMBER NOW\n\n"
                 f"Tell them:\n"
                 f"• Fire emergency\n"
                 f"• People trapped inside\n"
                 f"• Your exact address"
        )
        
        dispatcher.utter_message(
            text="⚠️ **IF YOU'RE TRAPPED:**\n"
                 "• Close doors between you and fire\n"
                 "• Seal cracks with cloth/towels\n"
                 "• Signal from window if possible\n"
                 "• Stay low to floor for fresh air\n"
                 "• Cover nose/mouth with wet cloth"
        )
        
        dispatcher.utter_message(
            text="🆘 Emergency services are being dispatched. Stay on the line with them!"
        )
        
        return [
            SlotSet("location", location),
            SlotSet("risk_level", "CRITICAL"),
            SlotSet("is_safe", False)
        ]