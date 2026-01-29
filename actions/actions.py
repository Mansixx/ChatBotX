# from typing import Any, Text, Dict, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.events import SlotSet

# # Mock emergency directory
# EMERGENCY_DIRECTORY = {
#     "berlin": {
#         "police": "110",
#         "ambulance": "112",
#         "fire": "112",
#         "shelter": "Berlin Community Shelter"
#     },
#     "mumbai": {
#         "police": "100",
#         "ambulance": "108",
#         "fire": "101",
#         "shelter": "Mumbai Municipal Shelter"
#     },
#     "default": {
#         "police": "112",
#         "ambulance": "112",
#         "fire": "112",
#         "shelter": "Nearest community shelter"
#     }
# }

# # -------- NEW ACTION (CRITICAL FIX) --------
# class ActionSetIncidentType(Action):

#     def name(self) -> Text:
#         return "action_set_incident_type"

#     def run(self, dispatcher, tracker, domain):
#         intent = tracker.latest_message["intent"]["name"]

#         mapping = {
#             "report_fire": "fire",
#             "report_flood": "flood",
#             "report_earthquake": "earthquake",
#             "medical_emergency": "medical"
#         }

#         incident = mapping.get(intent)
#         return [SlotSet("incident_type", incident)]


# # -------- EXISTING RISK ACTION --------
# class ActionAssessRisk(Action):

#     def name(self) -> Text:
#         return "action_assess_risk"

#     def run(self, dispatcher, tracker, domain):

#         incident_type = tracker.get_slot("incident_type")
#         location = tracker.get_slot("location")

#         location_key = location.lower() if location else "default"
#         services = EMERGENCY_DIRECTORY.get(location_key, EMERGENCY_DIRECTORY["default"])

#         if incident_type in ["fire", "medical"]:
#             risk = "HIGH"
#         elif incident_type in ["flood", "earthquake"]:
#             risk = "MEDIUM"
#         else:
#             risk = "UNKNOWN"

#         if risk == "HIGH":
#             dispatcher.utter_message(text="⚠️ This is a HIGH RISK situation.")
#             dispatcher.utter_message(
#                 text=f"Call immediately:\n"
#                      f"Ambulance: {services['ambulance']}\n"
#                      f"Police: {services['police']}\n"
#                      f"Fire: {services['fire']}"
#             )
#             dispatcher.utter_message(
#                 text=f"Nearest safe place: {services['shelter']}"
#             )

#         elif risk == "MEDIUM":
#             dispatcher.utter_message(text="This is a MEDIUM risk situation.")
#             dispatcher.utter_message(
#                 text="Stay alert. Prepare to evacuate if conditions worsen."
#             )

#         else:
#             dispatcher.utter_message(
#                 text="I need more clarity. Are you facing fire, flood, earthquake, or medical emergency?"
#             )

#         return [
#             SlotSet("risk_level", risk),
#             SlotSet("escalated", risk == "HIGH")
#         ]

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