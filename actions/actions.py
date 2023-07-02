import phonenumbers
from phonenumbers import geocoder
import json
from datetime import date
from datetime import datetime
import secrets
import string

from tinydb import TinyDB, Query



from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType, SlotSet, FollowupAction
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
    "extra large" : 1450}

db = TinyDB("ordersDB.json")
query = Query()

def userName(ID):
    for user in db.search(query.userID==ID):
        return user["firstName"]


valid_pizza = list(menu.keys())
valid_sizes = list(pizza_prices.keys())
valid_status = ["confirm", "cancel", "change"]

def clean_name(name):
    return "".join([c for c in name if c.isalpha()])
    
class hi(Action):
    def name(self) -> Text:
        return "action_hi"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        
        ID = tracker.current_state()["sender_id"]
        user_name = userName(ID)
        if user_name is not None:
            
            dispatcher.utter_message(text=f"Hello {user_name.title()}, Welcome back to Lunchbox Pizzeria")
        else:
            dispatcher.utter_message(response="utter_greet")

        return []

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

        if slot_value.lower() not in valid_pizza:
            dispatcher.utter_message(text=f"Sorry, that pizza is currently unavailable.Here's what you order:",
                                     buttons=[{"title": pz, "payload": pz} for pz in valid_pizza])

            return {"pizza_kind": None}
        dispatcher.utter_message(text=f"OK! You want to have a {slot_value} pizza.")
        return {"pizza_kind": slot_value}

    def validate_pizza_size(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pizza_size` value."""

        if slot_value.lower() not in valid_sizes:
            dispatcher.utter_message(text=f"Sorry, we only accept the following sizes:",
                                     buttons=[{"title": ps, "payload": ps} for ps in valid_sizes])
            
            return {"pizza_size": None}
        selected_pizza = tracker.get_slot("pizza_kind")
        dispatcher.utter_message(text=f"Noted! A {slot_value} {selected_pizza} pizza.")
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
            dispatcher.utter_message(text="Mmmh might be a typo🙃🤪. Kindly assist me a valid name please")
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
            dispatcher.utter_message(text="I need a valid name to complete your order.")
            return {"last_name": None}
        first_name = tracker.get_slot("first_name")
        if len(first_name) + len(name) < 3:
            dispatcher.utter_message(text="That's a very short name🤨😬. Can get your name again.")
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
            dispatcher.utter_message(text="Sorry, kindly provide valid phone number")
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
            dispatcher.utter_message(text="For efficiency, please provide a detailed delivery address")
            return {"deliveryAddress": None}
        return {"deliveryAddress": slot_value}


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
        
        dispatcher.utter_message(text="I will now Order for you:")
        dispatcher.utter_message(text=f"****Order Summary****\nOrdered by: {fname} {lname}\nPizza: {selected_pizza}\nSize: {selected_size}\nPrize: KES {order_price}\n ***All prices Inc. of VAT***")
        
        return []

class showPrice(Action):
    def name(self) -> Text:
        return "action_show_price"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        dispatcher.utter_message(text=f"Our pizza prices are as follows:\n\nMedium  - KES {pizza_prices['medium']}/=\nLarge  - KES {pizza_prices['large']}/=\nExtra Large  - KES{pizza_prices['extra large']}\n\nNote prices are inclusive of VAT but not delivery fees")   

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
    

class askConfirmation(Action):
    def name(self) -> Text:
        return "action_ask_confirmation"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        dispatcher.utter_message(response="utter_ask_confirmation")   

        return [FollowupAction("action_listen")]

class askCancelOrder(Action):
    def name(self) -> Text:
        return "action_ask_cancel_order"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        dispatcher.utter_message(response="utter_ask_cancel_order")   

        return [FollowupAction("action_listen")]          

class CancelOrder(Action):
    def name(self) -> Text:
        return "action_cancelOrder"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]: 
        
        if tracker.latest_message['intent'].get('name') == "affirm":
            dispatcher.utter_message(text="Confirmed! Your Order has been cancelled.\n To order again just type: Order pizza")
            return [FollowupAction(name="action_resetSlots")]
        elif tracker.latest_message['intent'].get('name') == "deny":
            return [FollowupAction(name="order_form")]

class toDB(Action):
    def name(self) -> Text:
        return "action_toDB"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]: 
        
        if tracker.latest_message['intent'].get('name') == "affirm":

            orderID = str(''.join(secrets.choice(string.ascii_uppercase+string.digits) for i in range(7)))
            timeStamp = datetime.now().strftime("%H:%M:%S"),
            dateStamp = date.today().isoformat()

            def insert():
                db.insert({"firstName": tracker.get_slot("first_name"),
                           "lastName": tracker.get_slot("last_name"),
                           "pizzaType": tracker.get_slot("pizza_kind"),
                           "pizzaSize":  tracker.get_slot("pizza_size"),
                           "phoneNumber": "0700000000",
                           "address": tracker.get_slot("deliveryAddress"),
                           "orderID": orderID,
                           "timeStamp": timeStamp,
                           "dateStamp": dateStamp,
                           "userID": tracker.current_state()["sender_id"]})
            
            insert()
            dispatcher.utter_message(text=f"Order placed correctly! Your order ID is {orderID}.\n You will get a call once your Pizza has arrived. Delivery time 30-50 min.\n\n ❤❤Enjoy your meal❤❤")
        elif tracker.latest_message['intent'].get('name') == "deny":

            dispatcher.utter_message(text="Confirmed! Your Order has been cancelled.\n To order again just type: Order pizza")
            return [FollowupAction(name="action_resetSlots")]
