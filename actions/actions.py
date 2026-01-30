

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
        """Uses OpenStreetMap free API to validate city"""
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

        incident = tracker.get_slot("incident_type")
        location = tracker.get_slot("location")

        if not incident:
            dispatcher.utter_message("What emergency are you facing? (fire, flood, earthquake, medical)")
            return []

        if not location:
            dispatcher.utter_message("Please tell me your city or area.")
            return []

        # Validate location via external API
        valid = self.validate_location(location)

        if not valid:
            dispatcher.utter_message("I couldn't find this location. Please try a nearby city.")
            return []

        # Risk logic
        high_risk = ["fire", "medical"]
        medium_risk = ["flood", "earthquake"]

        if incident in high_risk:
            risk = "HIGH"
        elif incident in medium_risk:
            risk = "MEDIUM"
        else:
            risk = "UNKNOWN"

        services = EMERGENCY_DIRECTORY["default"]

        if risk == "HIGH":
            dispatcher.utter_message("⚠️ This is a HIGH RISK situation.")
            dispatcher.utter_message(
                f"Call immediately:\n"
                f"• Ambulance: {services['ambulance']}\n"
                f"• Police: {services['police']}\n"
                f"• Fire: {services['fire']}"
            )
            dispatcher.utter_message(f"Nearest safe place: {services['shelter']}")
        else:
            dispatcher.utter_message("Stay alert and follow local safety guidance.")

        dispatcher.utter_message("I am here if you need further help.")

        return [
            SlotSet("risk_level", risk)
        ]