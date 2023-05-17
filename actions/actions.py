import phonenumbers
from phonenumbers import geocoder
import json
from datetime import date
from datetime import datetime
import secrets
import string
import pandas as pd
import numpy as np

from tinydb import TinyDB, Query



from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.types import DomainDict

menu = {'margherita': ['mozzarella cheese'],
        'veggie lovers': ['mozzarella cheese','green pepper','mushroom','red onions','corn','black olives'], 
        'tropical vegan': ['mozzarella cheese','pepper','red onions','pineapples','red chilli'], 
        'pepperoni lovers': ['mozzarella cheese', 'beef pepperoni'], 
        'bbq beef': ['mozzarella cheese', 'beef pepperoni', 'beef crumble'],
        'bbq chicken': ['mozzarella cheese','chicken choma sausages','chicken salami','chicken crumble','green peppers','red onions'],                    
        'super supreme': ['mozzarella cheese','beef pepperoni','beef crumble','chicken choma sausages','chicken salami','green peppers','mushroom','red onions','black olives']}

pizza_prices = {
    "medium" : 890,
    "large" : 1150,
    "extra large" : 1450    
}

db = TinyDB("ordersDB.json")

def clean_name(name):
    return "".join([c for c in name if c.isalpha()])
    


class ValidateOrderForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_order_form"

    def validate_pizza_kind(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pizza_kind` value."""

        if slot_value.lower() not in menu.keys():
            dispatcher.utter_message(text=f"Sorry, that pizza is currently unavailable.Here's what you order: \n {', '.join(list(menu.keys()))}")
            return {"pizza_kind": None}
        
        return {"pizza_kind": slot_value}

    def validate_pizza_size(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pizza_size` value."""

        ALLOWED_SIZES = pizza_prices.keys()

        if slot_value.lower() not in ALLOWED_SIZES:
            dispatcher.utter_message(text=f"Sorry, we only accept the following sizes: \n",
                                     button=[{"title": P_size, "payload": P_size} for P_size in ALLOWED_SIZES])
            return {"pizza_size": None}
        
        return {"pizza_size": slot_value}


    def validate_first_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""

        name = clean_name(slot_value)
        if len(name) == 0:
            dispatcher.utter_message(text="Mmmh typo. Provide a valid name please")
            return {"first_name": None}
        return {"first_name": name}


    def validate_last_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `last_name` value."""

        name = clean_name(slot_value)
        if len(name) == 0:
            dispatcher.utter_message(text="Sorry please provide a valid name.")
            return {"last_name": None}
        first_name = tracker.get_slot("first_name")
        if len(first_name) + len(name) < 3:
            dispatcher.utter_message(text="That's a very short name. pizza_kindly provide valid name")
            return {"first_name": None, "last_name": None}
        return {"last_name": name}

    def validate_phone_number(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `phone_number` value."""

        ph_num = phonenumbers.parse(tracker.get_slot("phone_number"), "KE")
        
        if phonenumbers.is_valid_number(ph_num):
            return {"phone_number": slot_value}
        else:
            dispatcher.utter_message(text="pizza_kindly provide valid phone number")
            return {"phone_number": None}


    def validate_deliveryAddress(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `deliveryAddress` value."""

        if len(slot_value) <= 20:
            dispatcher.utter_message(text="For faster delivery, please provide a detailed address")
            return {"deliveryAddress": None}
        return {"deliveryAddress": slot_value}

    def validate_orderStatus(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `orderStatus` value."""

        if slot_value.title() not in ["Confirm", "Cancel", "Change"]:
            dispatcher.utter_message(response=f"utter_default:",
                                     button=[{"title": status, "payload": status} for status in ["Confirm", "Cancel", "Change"]])
            return {"orderStatus": None}
        
        return {"orderStatus": slot_value}    



class ShowUserCart(Action):
    def name(self) -> Text:
        return "action_show_user_cart"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        fname = tracker.get_slot("first_name").title()
        lname = tracker.get_slot("last_name").title()
        selected_pizza = tracker.get_slot("pizza_kind").title()
        selected_size = tracker.get_slot("pizza_size")
        order_price = pizza_prices[tracker.get_slot("pizza_size").lower()]
        
        dispatcher.utter_message(text=f"****Order Summary****\nName: {fname} {lname}\nPizza Type: {selected_pizza}\nSize: {selected_size}\nPrize: Ksh {order_price}\n ***All prices Inc. of VAT***")
        
        return []

class LocateUs(Action):
    def name(self) -> Text:
        return "action_locate_us"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        dispatcher.utter_message(response="utter_outlets")

        return []

class WorkHours(Action):
    def name(self) -> Text:
        return "action_office_hours"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        dispatcher.utter_message(response="utter_office_hours")

        return []

class resetSlots(Action):
    def name(self) -> Text:
        return "action_resetSlots"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        return [SlotSet('pizza_kind', None), 
                SlotSet('pizza_size', None), 
                SlotSet('first_name', None), 
                SlotSet('last_name', None), 
                SlotSet('phone_number', None), 
                SlotSet('deliveryAddress', None)]
    
class orderConfirmation(Action):
    def name(self) -> Text:
        return "action_ask_orderStatus"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        dispatcher.utter_message(response="utter_ask_orderStatus",
                                     button=[{"title": status, "payload": status} for status in ["Confirm", "Cancel", "Change"]])
        return []


class toDB(Action):
    def name(self) -> Text:
        return "action_toDB"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]: 
        
        if tracker.get_slot("orderStatus").lower() == 'confirm':
            orderID = str(''.join(secrets.choice(string.ascii_uppercase+string.digits) for i in range(7)))
            timeStamp = datetime.now().strftime("%H:%M:%S"),
            dateStamp = date.today().isoformat()

            def insert():
                db.insert({"firstName": tracker.get_slot("first_name"),
                           "lastName": tracker.get_slot("last_name"),
                           "pizzaType": tracker.get_slot("pizza_type"),
                           "pizzaSize":  tracker.get_slot("pizza_size"),
                           "phoneNumber": tracker.get_slot("phone_number"),
                           "address": tracker.get_slot("deliveryAddress"),
                           "orderID": orderID,
                           "timeStamp": timeStamp,
                           "dateStamp": dateStamp,
                           "userID": tracker.current_state()["sender_id"]})
            
            insert()

            dispatcher.utter_message(text=f"Order placed correctly! Your order ID is {orderID}.\n You will get a call once your Pizza has arrived.\n\n\n ❤❤Enjoy your meal❤❤")
        return []