from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import datetime
import random


class ActionSaveLocation(Action):
    """Save the location provided by user"""

    def name(self) -> Text:
        return "action_save_location"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Get location from message text
        location = tracker.latest_message.get('text', '').strip()
        
        # Also check entities
        entities = tracker.latest_message.get('entities', [])
        for entity in entities:
            if entity.get('entity') == 'location':
                location = entity.get('value')
                break

        if not location or len(location) < 3:
            dispatcher.utter_message(
                text="⚠️ I need a valid location. Please provide your address or a nearby landmark."
            )
            return []

        # Confirm location received
        dispatcher.utter_message(
            text=f"✓ Location recorded: {location}"
        )
        
        return [SlotSet("location", location)]


class ActionSavePeopleCount(Action):
    """Save the number of people in danger"""

    def name(self) -> Text:
        return "action_save_people_count"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Get the message text
        message = tracker.latest_message.get('text', '').lower().strip()
        
        # Try to extract number
        people_count = None
        
        # Look for digits
        import re
        numbers = re.findall(r'\d+', message)
        if numbers:
            people_count = numbers[0]
        # Look for text numbers
        elif 'one' in message or 'just me' in message:
            people_count = "1"
        elif 'two' in message:
            people_count = "2"
        elif 'three' in message:
            people_count = "3"
        elif 'four' in message:
            people_count = "4"
        elif 'five' in message:
            people_count = "5"
        elif 'many' in message or 'several' in message:
            people_count = "10+"

        if not people_count:
            dispatcher.utter_message(
                text="⚠️ Please specify the number of people (e.g., '3 people' or 'just me')"
            )
            return []

        # Confirm
        dispatcher.utter_message(
            text=f"✓ Number of people recorded: {people_count}"
        )
        
        return [SlotSet("people_count", people_count)]


class ActionSaveInjuryStatus(Action):
    """Save injury information - handles multiple intent types"""

    def name(self) -> Text:
        return "action_save_injury_status"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent'].get('name')
        
        # Handle specific injury intents
        if intent == 'inform_injured_yes':
            injury_status = "YES - Injuries reported"
            dispatcher.utter_message(text="✓ Injury status: YES - Medical assistance will be prioritized")
        elif intent == 'inform_injured_no':
            injury_status = "NO - No injuries"
            dispatcher.utter_message(text="✓ Injury status: NO injuries reported")
        elif intent == 'inform_injured_unsure':
            injury_status = "UNKNOWN - Unsure"
            dispatcher.utter_message(text="✓ Injury status: Unsure - Medical team will be on standby")
        # Handle generic affirm/deny (common when users say "yes"/"no")
        elif intent == 'affirm':
            injury_status = "YES - Injuries reported"
            dispatcher.utter_message(text="✓ Injury status: YES - Medical assistance will be prioritized")
        elif intent == 'deny':
            injury_status = "NO - No injuries"
            dispatcher.utter_message(text="✓ Injury status: NO injuries reported")
        else:
            injury_status = "NOT PROVIDED"
            
        return [SlotSet("has_injuries", injury_status)]


class ActionProcessEmergencyAlert(Action):
    """Process and dispatch emergency alert"""

    def name(self) -> Text:
        return "action_process_emergency_alert"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Get all collected information
        location = tracker.get_slot("location")
        people_count = tracker.get_slot("people_count")
        has_injuries = tracker.get_slot("has_injuries")

        # Get fire spreading status
        intent = tracker.latest_message['intent'].get('name')
        if intent == 'fire_spreading_yes' or intent == 'affirm':
            fire_spreading = "YES - Rapidly spreading"
        else:
            fire_spreading = "NO - Contained"

        # Generate emergency ID
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        emergency_id = f"FIRE-{timestamp}-{random.randint(1000, 9999)}"

        # Create emergency summary
        dispatcher.utter_message(
            text=f"📋 **EMERGENCY REPORT SUMMARY**\n\n"
                 f"🆔 Emergency ID: {emergency_id}\n"
                 f"📍 Location: {location}\n"
                 f"👥 People affected: {people_count}\n"
                 f"🏥 Injuries: {has_injuries}\n"
                 f"🔥 Fire spreading: {fire_spreading}\n"
                 f"⏰ Reported: {datetime.datetime.now().strftime('%I:%M %p')}"
        )

        # In a real system, this would:
        # 1. Send alert to fire department API
        # 2. Send SMS to emergency services
        # 3. Log in emergency database
        # 4. Notify nearby hospitals if injuries
        # 5. Alert police if needed

        dispatcher.utter_message(
            text="🚨 **ALERT TRANSMITTED TO:**\n"
                 "✓ Fire Department\n"
                 "✓ Emergency Medical Services\n"
                 "✓ Police (for crowd control)\n"
                 "✓ Local Emergency Command Center"
        )

        return [
            SlotSet("emergency_id", emergency_id),
            SlotSet("fire_spreading", fire_spreading)
        ]