# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

# This is a simple example for a custom action which utters "Hello World!"
import re
from typing import Any, Text, Dict, List
import json

from rasa_sdk import Action, Tracker, FormValidationAction, ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import EventType, FollowupAction, Restarted, SlotSet, AllSlotsReset

from actions.config import get_output_api_form

# select_intent_list = ["select_all_object", "exit_select", "delete_selected_objects", "select_area"]

# edit_intent_list = [""]

decartes_position_regex = "\(\s*(\d+)\s*,\s*(\d+)\s*\)"

def validate_select_memory(keys:List, new_values:List, memory:Dict):
    print("keys: ", keys)
    print("new_values: ", new_values)
    # print("memory: ", memory)
    if memory is None:
        if None in new_values:
            return False
        else:
            return True
        
    new_values = {key:value for key, value in zip(keys, new_values)}
    for key in new_values.keys():
        if new_values[key] is None:
            continue
        elif new_values[key] != memory[key]:
            return False
    return True

def check_object_shape_size(shape:str, size_dict:dict):
    shape = shape.lower().lstrip("hình ")

    if shape.split(" ")[0] in ["đường", "đoạn"] and "tròn" not in shape and "cong" not in shape:
        if size_dict["object_destination"] is not None:
            return ["object_destination"], size_dict
        return "None", size_dict
    
    elif shape == "vuông":
        if size_dict["height"] != None:
            return ["height"], size_dict
        if size_dict["width"] != None:
            return ["width"], size_dict
        return "None", size_dict
    elif shape == "tròn":
        if size_dict["width"] != None:
            return ["width"], size_dict
        if size_dict["length"] != None:
            tmp_str = size_dict["length"].split(" ")[0]
            try: 
                size_dict["width"] = int(tmp_str)/2
                size_dict["length"] = None
                return ["width"], size_dict
            except:
                pass
        return "None", size_dict
    
    else:
        if size_dict["length"] != None and size_dict["width"] != None and size_dict["height"] != None:
            return ["length", "width", "height"], size_dict
        if (size_dict["length"] != None and size_dict["width"] != None):
            return ["length", "width"], size_dict
        if (size_dict["height"] != None and size_dict["width"] != None):
            return ["width", "height"], size_dict
        if (size_dict["length"] != None and size_dict["height"] != None):
            return ["length", "height"], size_dict
        return "None", size_dict

def check_value_shape_size(shape:str, size_dict:dict):
    shape = shape.lower().lstrip("hình ")

    if shape.split(" ")[0] in ["đường", "đoạn"] and "tròn" not in shape and "cong" not in shape:
        if size_dict["object_destination"] is not None:
            return ["object_destination"], size_dict
        return "None", size_dict
    
    elif shape == "vuông":
        if size_dict["height"] != None:
            return ["height"], size_dict
        if size_dict["width"] != None:
            return ["width"], size_dict
        return "None", size_dict
    
    elif shape == "tròn":
        if size_dict["width"] != None:
            return ["width"], size_dict
        if size_dict["width"] != None:
            return ["width"], size_dict
        if size_dict["length"] != None:
            tmp_str = size_dict["length"].split(" ")[0]
            try: 
                size_dict["width"] = int(tmp_str)/2
                size_dict["length"] = None
                return ["width"], size_dict
            except:
                pass
        return "None", size_dict
    
    elif shape == "thang":
        if (size_dict["length"] != None and size_dict["width"] != None and size_dict["height"] != None):
            return ["height", "width", "length"], size_dict
        return "None", size_dict
    else:
        if (size_dict["length"] != None and size_dict["width"] != None):
            return ["length", "width"], size_dict
        if (size_dict["height"] != None and size_dict["width"] != None):
            return ["width", "height"], size_dict
        if (size_dict["length"] != None and size_dict["height"] != None):
            return ["length", "height"], size_dict
        return "None", size_dict

#############################################################################
    
class ActionRotateLeft(Action): 

    """done"""
    def name(self) -> Text:
        return "action_rotate_left"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_rotate_left'), 
                    FollowupAction('action_select_object')
                    ]
        value_angle = tracker.get_slot('value_angle')
        # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n object_size: {tracker.get_slot('object_size')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} ")
        if value_angle is None:
            param_dict = get_output_api_form('rotate_left', response_message=f'Mình nhận ra bạn muốn xoay trái một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
                                     f'\t- Mức độ xoay vật thể.')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []

        param_dict = get_output_api_form('rotate_left', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

#############################################################################
       

#############################################################################
    
class ActionRotateRight(Action):
    def name(self) -> Text:
        return "action_rotate_right"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_rotate_right'), 
                    FollowupAction('action_select_object')
                    ]
        value_angle = tracker.get_slot('value_angle')
        if value_angle is None:
            text=f'Mình nhận ra bạn muốn xoay phải một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
                                     f'\t- Mức độ xoay vật thể.'
            param_dict = get_output_api_form('rotate_right', response_message=text)
            dispatcher.utter_custom_json(json_message=param_dict)
            return []

        param_dict = get_output_api_form('rotate_right', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]


# class ActionDeactivateLoop(Action):

#     def name(self) -> Text:
#         return "action_deactivate_loop"
    
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         dispatcher.utter_message("Oke. Bạn muốn mình thực hiện tác vụ nào khác không ?")
#         return []

#############################################################################
       
class ActionHorizontalFlip(Action):

    def name(self) -> Text:
        return "action_horizontal_flip"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
        
        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_horizontal_flip'), 
                    FollowupAction('action_select_object')
                    ]
      
        param_dict = get_output_api_form("horizontal_flip", tracker)

        
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

#############################################################################
    
class ActionVerticalFlip(Action):

    def name(self) -> Text:
        return "action_vertical_flip"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_vertical_flip'), 
                    FollowupAction('action_select_object')
                    ]
      

        param_dict = get_output_api_form("vertical_flip", tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

    
#############################################################################
        
class ActionMoveLeft(Action):

    def name(self) -> Text:
        return "action_move_left"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_move_left'), 
                    FollowupAction('action_select_object')
                    ]
        value_move = tracker.get_slot('value_move')        
        if value_move is None:
            param_dict = get_output_api_form('move_left', response_message=f'Mình nhận ra bạn muốn dịch chuyển một vật thể trên màn hình sang bên trái. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. '\
                                     f'Để có thể thực hiện được tác vụ này, mình cần thông tin sau: \n' \
                                     f'\t- Mức độ di chuyển của vật thể.')
            dispatcher.utter_custom_json(param_dict)
            return []
        
        param_dict = get_output_api_form('move_left', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        
        dispatcher.utter_custom_json(json_message=param_dict)
        
        try:
            position_source = tracker.get_slot("position_source")
            decartes_match = re.match(decartes_position_regex, position_source)
            if decartes_match is not None:
                move_left_value = int(value_move.split(" ")[0])

                source_x = int(decartes_match.group(1).split(" ")[0])
                source_y = int(decartes_match.group(2).split(" ")[0])
                source_x = source_x - move_left_value
                param_dict['position_source'] = f"({source_x}, {source_y})"
        except:
            pass

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

#############################################################################
        
class ActionMoveRight(Action):

    def name(self) -> Text:
        return "action_move_right"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_move_right'), 
                    FollowupAction('action_select_object')
                    ]
        value_move = tracker.get_slot('value_move')        
        if value_move is None:
            param_dict = get_output_api_form('move_right', response_message=f'Mình nhận ra bạn muốn dịch chuyển một vật thể trên màn hình sang bên phải. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. '\
                                     f'Để có thể thực hiện được tác vụ này, mình cần thông tin sau: \n' \
                                     f'\t- Mức độ di chuyển của vật thể.')
            dispatcher.utter_message(json_message=param_dict)
            return []
        
        param_dict = get_output_api_form('move_right', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        
        
        try:
            position_source = tracker.get_slot("position_source")
            decartes_match = re.match(decartes_position_regex, position_source)
            if decartes_match is not None:
                move_right_value = int(value_move.split(" ")[0])

                source_x = int(decartes_match.group(1).split(" ")[0])
                source_y = int(decartes_match.group(2).split(" ")[0])
                source_x = source_x + move_right_value
                param_dict['position_source'] = f"({source_x}, {source_y})"
        except:
            pass
        dispatcher.utter_custom_json(json_message=param_dict)
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

#############################################################################
        
class ActionMoveUp(Action):

    def name(self) -> Text:
        return "action_move_up"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_move_up'), 
                    FollowupAction('action_select_object')
                    ]
        value_move = tracker.get_slot('value_move')        
        if value_move is None:
            param_dict = get_output_api_form('move_up', response_message=f'Mình nhận ra bạn muốn dịch chuyển một vật thể trên màn hình lên trên. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. '\
                                     f'Để có thể thực hiện được tác vụ này, mình cần thông tin sau: \n' \
                                     f'\t- Mức độ di chuyển của vật thể.')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []
        
        param_dict = get_output_api_form('move_up', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        
        try:
            position_source = tracker.get_slot("position_source")
            decartes_match = re.match(decartes_position_regex, position_source)
            if decartes_match is not None:
                move_up_value = int(value_move.split(" ")[0])

                source_x = int(decartes_match.group(1).split(" ")[0])
                source_y = int(decartes_match.group(2).split(" ")[0])
                source_y = source_y + move_up_value
                param_dict['position_source'] = f"({source_x}, {source_y})"
        except:
            pass


        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

#############################################################################
        
class ActionMoveDown(Action):

    def name(self) -> Text:
        return "action_move_down"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_move_down'), 
                    FollowupAction('action_select_object')
                    ]
        value_move = tracker.get_slot('value_move')        
        if value_move is None:
            param_dict = get_output_api_form('move_down', param_dict=f'Mình nhận ra bạn muốn dịch chuyển một vật thể trên màn hình xuống dưới. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. '\
                                     f'Để có thể thực hiện được tác vụ này, mình cần thông tin sau: \n' \
                                     f'\t- Mức độ di chuyển của vật thể.')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []
        
        param_dict = get_output_api_form('move_down', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        
        try:
            position_source = tracker.get_slot("position_source")
            decartes_match = re.match(decartes_position_regex, position_source)
            if decartes_match is not None:
                move_down_value = int(value_move.split(" ")[0])

                source_x = int(decartes_match.group(1).split(" ")[0])
                source_y = int(decartes_match.group(2).split(" ")[0])
                source_y = source_y - move_down_value
                param_dict['position_source'] = f"({source_x}, {source_y})"
        except:
            pass


        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

#############################################################################
    
# class ActionAskIsAll(Action):
    
#     def name(self) -> Text:
#         return "action_ask_is_all"
    
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[EventType]:
#         dispatcher.utter_message(
#             text="Bạn muốn chọn tất cả các hình có đặc trưng này hay muốn mô tả kĩ hơn để chỉ xác định một hình ?",
#             buttons=[
#                 {"title": "có", "payload": "/affirm"},
#                 {"title": "không", "payload": "/deny"}
#             ]
#         )
#         # last_action = tracker.get_slot("last_action")
#         # if last_action is not None: return [FollowupAction(last_action)]
#         return []

#############################################################################
       
class ActionSelectObject(Action):

    def name(self) -> Text:
        return "action_select_object"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # is_all = tracker.get_slot('is_all')
        
        # if is_all is None:
        #     SlotSet('last_action', 'action_select_object')
        #     return [FollowupAction('action_ask_is_all')]
        # elif is_all == False:
        #     SlotSet('last_action', None)
        #     dispatcher.utter_message(text='Huỷ thao tác!')
        #     return [Restarted()]
        
        # return [FollowupAction('select_all_object')]

        require_keys = ['object_shape', 'position_source', 'object_color', 'object_size']
        # position_source_x = next(tracker.get_latest_entity_values("position", "source_x"), None)
        # position_source_y = next(tracker.get_latest_entity_values("position", "source_y"), None)
        # position_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)
        # dispatcher.utter_message(f"position_source_x: {str(position_source_x)}\nposition_source_y: {str(position_source_y)}\nposition_destination_y: {str(position_destination_y)}")
        require_values = [tracker.get_slot(key) for key in require_keys]
        last_memory = tracker.get_slot('last_memory')
        if validate_select_memory(require_keys, require_values, last_memory):
            last_action = tracker.get_slot('last_action')
            if last_action is not None: 
                return [
                    FollowupAction(last_action),
                    SlotSet('last_action', 'action_select_object')
                    ]
        # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} \n object_size: {tracker.get_slot('object_size')}"
        if None in require_values:
            param_dict = get_output_api_form('select_object', response_message='Mình nhận ra bạn muốn chọn một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. \n \
                                     Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n \
                                     - Hình dạng của vật thể. \n \
                                     - Kích thước của vật thể. \n \
                                     - Màu sắc của vật thể. \n \
                                     - Vị trí hiện tại của vật thể.')
            dispatcher.utter_custom_json(param_dict)
            return []

        try:
            size_dict = tracker.get_slot("object_size")
            aspect_list, size_dict = check_object_shape_size(tracker.get_slot("object_shape"), size_dict)
            if aspect_list == "None":
                param_dict = get_output_api_form('select_object', response_message='Mình nhận ra bạn muốn chọn một vật thể trên màn hình. Tuy nhiên, thông tin về kích thước của vật thể mà bạn cung cấp cho mình là chưa đủ hoặc chưa phù hợp.')
                dispatcher.utter_custom_json(param_dict)
                return []
        except:
            pass

        param_dict = get_output_api_form('select_object', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        last_action = tracker.get_slot('last_action')
        if last_action is not None: 
            return [
                FollowupAction(last_action),
                SlotSet('last_action', 'action_select_object')
                ]
        
        return [SlotSet('last_action', 'action_select_object')]
        
#############################################################################
    
class ActionSelectArea(Action):

    def name(self) -> Text:
        return "action_select_area"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_keys = ['selected_area_source', 'selected_area_destination']
        # position_source_x = next(tracker.get_latest_entity_values("position", "source_x"), None)
        # position_source_y = next(tracker.get_latest_entity_values("position", "source_y"), None)
        # position_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)
        # dispatcher.utter_message(f"position_source_x: {str(position_source_x)}\nposition_source_y: {str(position_source_y)}\nposition_destination_y: {str(position_destination_y)}")
        require_values = [tracker.get_slot(key) for key in require_keys]
        if None in require_values:
            param_dict = get_output_api_form('select_area', response_message='Mình nhận ra bạn muốn chọn một vùng chọn trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n\t- Vị trí xuất phát của vùng chọn. \n\t- Vị trí kết thúc của vùng chọn.')
            dispatcher.utter_custom_json(param_dict)
            return []
        
        object_shape = tracker.get_slot("object_shape")
        if object_shape is None:
            object_shape = "any"
        object_color = tracker.get_slot("object_color")
        if object_color is None:
            object_color = "any"
        object_size = tracker.get_slot("object_size")
        if object_size is None:
            object_size = "any"
        position_source = tracker.get_slot("position_source")
        if position_source is None:
            position_source = "any"
        
        param_dict = get_output_api_form('select_area', tracker)
        param_dict["object_shape"] = object_shape
        param_dict["object_color"] = object_color
        param_dict["object_size"] = object_size
        param_dict["position_source"] = position_source
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        # last_action = tracker.get_slot('last_action')
        # if last_action is not None: return [FollowupAction(last_action)]
        
        return [AllSlotsReset(),
                SlotSet('last_action', 'select_area'),
                SlotSet('last_memory', param_dict)]

#############################################################################
    
class ActionSelectAllObject(Action):

    def name(self) -> Text:
        return "action_select_all_object"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        current_object_shape = next(tracker.get_latest_entity_values("object", "shape"), "any")
        current_object_color = next(tracker.get_latest_entity_values("object", "color"), "any")
        current_object_size = tracker.get_slot("object_size")
        if current_object_size is None:
            current_object_size = "any"
        current_position_source = next(tracker.get_latest_entity_values("position", "source"), "any")      
        
        # param_dict = {
        #     "intent": "select_all_object",
        #     "object_shape": current_object_shape,
        #     "object_size": current_object_size,
        #     "object_color": current_object_color,
        #     "position_source": current_position_source
        # }
        param_dict = get_output_api_form('select_all_object', tracker)
        param_dict["object_shape"] = current_object_shape
        param_dict["object_size"] = current_object_size
        param_dict["object_color"] = current_object_color
        param_dict["position_source"] = current_position_source
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        
        return [
            AllSlotsReset(),
            SlotSet("last_action", "select_all_object"),
            SlotSet('last_memory', param_dict)
        ]

#############################################################################
     
class ActionExitSelect(Action):

    def name(self) -> Text:
        return "action_exit_select"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        param_dict = get_output_api_form('exit_select')
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

#############################################################################
     
class ActionDeleteSelectedObjects(Action):

    def name(self) -> Text:
        return "action_delete_selected_objects"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_delete_selected_objects'), 
                    FollowupAction('action_select_object')
                    ]
        
        param_dict = get_output_api_form('delete_selected_objects', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

    
    
#############################################################################
    
class ActionColorBackground(Action):

    def name(self) -> Text:
        return "action_color_background"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_color_background'), 
                    FollowupAction('action_select_object')
                    ]
        
        value_color = tracker.get_slot('value_color')
        if value_color is None:
            param_dict = get_output_api_form("color_background", response_message=f'Mình nhận ra bạn muốn tô màu nền cho một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                            f'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
                                            f'\t- Màu mà bạn muốn tô cho vật thể này')
            dispatcher.utter_custom_json(param_dict)
            return [] 
        param_dict = get_output_api_form('color_background', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        param_dict['object_color'] = value_color

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

    

#############################################################################

class ActionColorForeground(Action):

    def name(self) -> Text:
        return "action_color_foreground"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_color_foreground'), 
                    FollowupAction('action_select_object')
                    ]
        
        value_color = tracker.get_slot('value_color')
        if value_color is None:
            param_dict = get_output_api_form('color_foreground', response_message=f'Mình nhận ra bạn muốn tô màu cho một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                            f'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
                                            f'\t- Màu mà bạn muốn tô cho vật thể này')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []
        param_dict = get_output_api_form('color_foreground', tracker)
        # param_dict['object_color'] = tracker.get_slot("value_color")
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

##########################################################################
    
# class ActionChangeWidth(Action):

#     def name(self) -> Text:
#         return "action_change_width"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         require_keys = ['object_shape', 'position_source', 'object_color', 'object_size', 'value_change', "change_action"]
#         # position_source_x = next(tracker.get_latest_entity_values("position", "source_x"), None)
#         # position_source_y = next(tracker.get_latest_entity_values("position", "source_y"), None)
#         # position_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)
#         # dispatcher.utter_message(f"position_source_x: {str(position_source_x)}\nposition_source_y: {str(position_source_y)}\nposition_destination_y: {str(position_destination_y)}")
#         require_values = [tracker.get_slot(key) for key in require_keys]
#         # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} \n object_size: {tracker.get_slot('object_size')}"
#         if None in require_values:
#             dispatcher.utter_message(text='Mình nhận ra bạn muốn thay đổi chiều rộng của một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
#                                      'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
#                                     #  '- Hình dạng của vật thể. \n' \
#                                     #  '- Kích thước của vật thể. \n' \
#                                     #  '- Màu sắc của vật thể. \n' \
#                                     #  '- Vị trí hiện tại của vật thể. \n'
#                                     '\t- Cách thay đổi: Tăng / Giảm / Thay đổi giá trị mới' sdfasd
#                                     '\t- Giá trị phục vụ cho hành động này'
#                                      )
#             return []

#         try:
#             size_dict = tracker.get_slot("object_size")
#             aspect_list, size_dict = check_object_shape_size(tracker.get_slot("object_shape"), size_dict)
#             if aspect_list == "None":
#                 dispatcher.utter_message(text='Mình nhận ra bạn muốn thay đổi chiều rộng của một vật thể trên màn hình. Tuy nhiên, thông tin về kích thước của vật thể mà bạn cung cấp cho mình là chưa đủ hoặc chưa phù hợp.')
#                 return []
#         except:
#             pass

#         param_dict = {
#             "intent": "exit_select",
#         }
#         # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
#         dispatcher.utter_custom_json(json_message=param_dict)
#         # return [SlotSet("object_shape", None),
#         #         SlotSet("position_source", None),
#         #         SlotSet("position_source_x", None),
#         #         SlotSet("position_source_y", None),
#         #         SlotSet("position_destination", None),
#         #         SlotSet("object_color", None),
#         #         SlotSet("object_size", None),
#         #         SlotSet("object_height", None),
#         #         SlotSet("object_width", None),
#         #         SlotSet("object_length", None),
#         #         SlotSet("object_thickness", None),
#         #         SlotSet("object_destination", None),
#         #         SlotSet("position_destination_x", None),
#         #         SlotSet("position_destination_y", None),
#         #         SlotSet("selected_area_source", None),
#         #         SlotSet("selected_area_destination", None),
#         #         SlotSet("selected_area_height", None),
#         #         SlotSet("selected_area_width", None),
#         #         SlotSet("selected_area_length", None),
#         #         SlotSet("object_orientation", None),]

#         # return []
#         return [AllSlotsReset(), SlotSet('last_memory', param_dict)]


#############################################################################
     
# class ActionDeleteSelectedObjects(Action):

#     def name(self) -> Text:
#         return "action_delete_selected_objects"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         require_keys = ['object_shape', 'position_source', 'object_color', 'object_size']
#         # position_source_x = next(tracker.get_latest_entity_values("position", "source_x"), None)
#         # position_source_y = next(tracker.get_latest_entity_values("position", "source_y"), None)
#         # position_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)
#         # dispatcher.utter_message(f"position_source_x: {str(position_source_x)}\nposition_source_y: {str(position_source_y)}\nposition_destination_y: {str(position_destination_y)}")
#         require_values = [tracker.get_slot(key) for key in require_keys]
#         if None in require_values:
#             param_dict = get_output_api_form("delete_selected_objects", response_message="Mình nhận ra bạn muốn xóa vật thể mà bạn đã chọn trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. Để có thể thực hiện được tác vụ này, trước hết bạn cần chọn vật thể theo các đặc tính như hình dạng, màu sắc,.... hoặc chọn nhiều vật thể trên một vùng cố định.")
#             dispatcher.utter_custom_json(param_dict)
#             return []
        
#         try:
#             size_dict = tracker.get_slot("object_size")
#             aspect_list, size_dict = check_object_shape_size(tracker.get_slot("object_shape"), size_dict)
#             if aspect_list == "None":
#                 dispatcher.utter_message(text='Mình nhận ra bạn muốn xóa vật thể mà bạn đã chọn trên màn hình. Tuy nhiên, thông tin về kích thước của vật thể mà bạn cung cấp cho mình là chưa đủ hoặc chưa phù hợp.')
#                 return []
#         except:
#             pass
        
#         param_dict = {
#             "intent": "delete_selected_objects",
#             "object_shape": tracker.get_slot("object_shape"),
#             "object_color": tracker.get_slot("object_color"),
#             "object_size": json.dumps(size_dict),
#             "position_source": tracker.get_slot("position_source"),
#             "selected_area_source": tracker.get_slot("selected_area_source"),
#             "selected_area_destination": tracker.get_slot("selected_area_destination"),
#         }
#         # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
#         dispatcher.utter_custom_json(json_message=param_dict)

#         # return [SlotSet("object_shape", None),
#         #         SlotSet("object_color", None),
#         #         SlotSet("object_size", None),
#         #         SlotSet("object_height", None),
#         #         SlotSet("object_width", None),
#         #         SlotSet("object_length", None),
#         #         SlotSet("object_thickness", None),
#         #         SlotSet("object_orientation", None),
#         #         SlotSet("position_source", None),
#         #         SlotSet("position_source_x", None),
#         #         SlotSet("position_source_y", None),
#         #         SlotSet("position_destination", None),
#         #         SlotSet("object_destination", None),
#         #         SlotSet("position_destination_x", None),
#         #         SlotSet("position_destination_y", None),
#         #         SlotSet("selected_area_source", None),
#         #         SlotSet("selected_area_destination", None),
#         #         SlotSet("selected_area_height", None),
#         #         SlotSet("selected_area_width", None),
#         #         SlotSet("selected_area_length", None),]

#         # return []
#         return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

    
    
#############################################################################
    
# class ActionColorBackground(Action):

#     def name(self) -> Text:
#         return "action_color_background"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         require_keys = ['object_shape', 'object_size', 'object_color', 'position_source', 'value_color']
#         # position_source_x = next(tracker.get_latest_entity_values("position", "source_x"), None)
#         # position_source_y = next(tracker.get_latest_entity_values("position", "source_y"), None)
#         # position_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)
#         # dispatcher.utter_message(f"position_source_x: {str(position_source_x)}\nposition_source_y: {str(position_source_y)}\nposition_destination_y: {str(position_destination_y)}")
#         require_values = [tracker.get_slot(key) for key in require_keys]
#         if None in require_values:
#             dispatcher.utter_message(text='Mình nhận ra bạn muốn tô màu nên cho một đối tượng. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \
#                                      \n - Hình dạng của vật thể \
#                                      \n - Màu sắc của vật thể \
#                                      \n - Kích thước của vật thể \
#                                      \n - Vị trí của vật thể. \
#                                      \n - Màu mà bạn muốn tô cho nền của vật thể đó.')
#             return []
        
#         try:
#             size_dict = tracker.get_slot("object_size")
#             aspect_list, size_dict = check_object_shape_size(tracker.get_slot("object_shape"), size_dict)
#             if aspect_list == "None":
#                 dispatcher.utter_message(text='Mình nhận ra bạn muốn tô màu nền cho một vật thể trên màn hình. Tuy nhiên, thông tin về kích thước của vật thể mà bạn cung cấp cho mình là chưa đủ hoặc chưa phù hợp.')
#                 return []
#         except:
#             pass

#         param_dict = {
#             "intent": "color_background",
#             "position_source": tracker.get_slot("position_source"),
#             "object_shape": tracker.get_slot("object_shape"),
#             "object_size": json.dumps(size_dict),
#             "object_color": tracker.get_slot("object_color"),
#             "selected_area_source": tracker.get_slot("selected_area_source"),
#             "selected_area_destination": tracker.get_slot("selected_area_destination"),
#             "value_color": tracker.get_slot("value_color")
#         }
#         # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
#         dispatcher.utter_custom_json(json_message=param_dict)
#         # return [SlotSet("value_color", None),
#         #         SlotSet("position_source", None),
#         #         SlotSet("position_source_x", None),
#         #         SlotSet("position_source_y", None),
#         #         SlotSet("position_destination", None),
#         #         SlotSet("object_shape", None),
#         #         SlotSet("object_size", None),
#         #         SlotSet("object_height", None),
#         #         SlotSet("object_width", None),
#         #         SlotSet("object_length", None),
#         #         SlotSet("object_thickness", None),
#         #         SlotSet("object_orientation", None),
#         #         SlotSet("object_color", None),
#         #         SlotSet("object_destination", None),
#         #         SlotSet("position_destination_x", None),
#         #         SlotSet("position_destination_y", None),
#         #         SlotSet("selected_area_source", None),
#         #         SlotSet("selected_area_destination", None),
#         #         SlotSet("selected_area_height", None),
#         #         SlotSet("selected_area_width", None),
#         #         SlotSet("selected_area_length", None),]

#         # return []
#         return [AllSlotsReset(), SlotSet('last_memory', param_dict)]


    

# #############################################################################


# class ActionColorForeground(Action):

#     def name(self) -> Text:
#         return "action_color_foreground"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         require_keys = ['object_shape', 'position_source', 'object_color', 'object_size', 'value_color']
#         # position_source_x = next(tracker.get_latest_entity_values("position", "source_x"), None)
#         # position_source_y = next(tracker.get_latest_entity_values("position", "source_y"), None)
#         # position_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)
#         # dispatcher.utter_message(f"position_source_x: {str(position_source_x)}\nposition_source_y: {str(position_source_y)}\nposition_destination_y: {str(position_destination_y)}")
#         require_values = [tracker.get_slot(key) for key in require_keys]
#         # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} \n object_size: {tracker.get_slot('object_size')}"
#         if None in require_values:
#             dispatcher.utter_message(text='Mình nhận ra bạn muốn tô màu một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. '\
#                                      'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
#                                     #  '\t- Hình dạng của vật thể. \n' \
#                                     #  '\t- Kích thước của vật thể. \n' \
#                                     #  '\t- Màu sắc hiện tại của vật thể. \n' \
#                                     #  '\t- Vị trí hiện tại của vật thể. \n' \
#                                      '\t- Màu mà bạn muốn tô cho vật thể này')
#             return []

#         try:
#             size_dict = tracker.get_slot("object_size")
#             aspect_list, size_dict = check_object_shape_size(tracker.get_slot("object_shape"), size_dict)
#             if aspect_list == "None":
#                 dispatcher.utter_message(text='Mình nhận ra bạn muốn tô màu một vật thể trên màn hình. Tuy nhiên, thông tin về kích thước của vật thể mà bạn cung cấp cho mình là chưa đủ hoặc chưa phù hợp.')
#                 return []
#         except:
#             pass

#         param_dict = {
#             "intent": "color_foreground",
#             "position_source": tracker.get_slot("position_source"),
#             "object_shape": tracker.get_slot("object_shape"),
#             "object_size": json.dumps(size_dict),
#             "object_color": tracker.get_slot("object_color"),
#             "selected_area_source": tracker.get_slot("selected_area_source"),
#             "selected_area_destination": tracker.get_slot("selected_area_destination"),
#             "value_color": tracker.get_slot("value_color")
#         }
#         # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
#         dispatcher.utter_custom_json(json_message=param_dict)
#         # return [SlotSet("object_height", None),
#         #         SlotSet("object_width", None),
#         #         SlotSet("object_length", None),
#         #         SlotSet("object_thickness", None),
#         #         SlotSet("object_orientation", None),
#         #         SlotSet("object_size", None),
#         #         SlotSet("object_shape", None),
#         #         SlotSet("object_color", None),
#         #         SlotSet("position_source", None),
#         #         SlotSet("position_source_x", None),
#         #         SlotSet("position_source_y", None),
#         #         SlotSet("position_destination", None),
#         #         SlotSet("object_destination", None),
#         #         SlotSet("position_destination_x", None),
#         #         SlotSet("position_destination_y", None),
#         #         SlotSet("selected_area_source", None),
#         #         SlotSet("selected_area_destination", None),
#         #         SlotSet("selected_area_height", None),
#         #         SlotSet("selected_area_width", None),
#         #         SlotSet("selected_area_length", None),
#         #         SlotSet("value_color", None)]

#         # return []
#         return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

##########################################################################
    
class ActionChangeWidth(Action):

    def name(self) -> Text:
        return "action_change_width"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_change_width'), 
                    FollowupAction('action_select_object')
                    ]
        require_keys = ['value_angle', 'change_action']
        require_values = [tracker.get_slot(key) for key in require_keys]
        # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n object_size: {tracker.get_slot('object_size')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} ")
        if None in require_values:
            param_dict = get_output_api_form("change_width", response_message=f'Mình nhận ra bạn muốn thay đổi chiều rộng của một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần thông tin sau: ' \
                                     f'\t- Giá trị chiều rộng mà bạn muốn thay đổi' \
                                     f'\t- Kiểu thay đổi kích thước mà bạn mong muốn')
            dispatcher.utter_custom_json(param_dict)
            return []  

        param_dict = get_output_api_form('change_width', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

class ActionChangeHeight(Action):

    def name(self) -> Text:
        return "action_change_height"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_change_height'), 
                    FollowupAction('action_select_object')
                    ]
        require_keys = ['value_angle', 'change_action']
        require_values = [tracker.get_slot(key) for key in require_keys]
        # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n object_size: {tracker.get_slot('object_size')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} ")
        if None in require_values:
            param_dict = get_output_api_form("change_height", response_message=f'Mình nhận ra bạn muốn thay đổi chiều cao của một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần thông tin sau: ' \
                                     f'\t- Giá trị chiều rộng mà bạn muốn thay đổi' \
                                     f'\t- Kiểu thay đổi kích thước mà bạn mong muốn')
            
            return []  

        param_dict = get_output_api_form('change_height', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

class ActionChangeLength(Action):

    def name(self) -> Text:
        return "action_change_length"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_change_length'), 
                    FollowupAction('action_select_object')
                    ]
        require_keys = ['value_angle', 'change_action']
        require_values = [tracker.get_slot(key) for key in require_keys]
        # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n object_size: {tracker.get_slot('object_size')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} ")
        if None in require_values:
            param_dict = get_output_api_form("change_length", response_message=f'Mình nhận ra bạn muốn thay đổi chiều dài của một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần thông tin sau: ' \
                                     f'\t- Giá trị chiều rộng mà bạn muốn thay đổi' \
                                     f'\t- Kiểu thay đổi kích thước mà bạn mong muốn')
            dispatcher.utter_custom_json(param_dict)
            return []  

        param_dict = get_output_api_form('change_length', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

class ActionChangeRadius(Action):

    def name(self) -> Text:
        return "action_change_radius"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_change_radius'), 
                    FollowupAction('action_select_object')
                    ]
        require_keys = ['value_angle', 'change_action']
        require_values = [tracker.get_slot(key) for key in require_keys]
        # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n object_size: {tracker.get_slot('object_size')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} ")
        if None in require_values:
            param_dict = get_output_api_form("change_radius", response_message=f'Mình nhận ra bạn muốn thay đổi bán kính của một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần thông tin sau: ' \
                                     f'\t- Giá trị chiều rộng mà bạn muốn thay đổi' \
                                     f'\t- Kiểu thay đổi kích thước mà bạn mong muốn')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []  

        param_dict = get_output_api_form('change_radius', tracker)

        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]
        

class ActionChangeTop(Action):

    def name(self) -> Text:
        return "action_change_top"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_change_top'), 
                    FollowupAction('action_select_object')
                    ]
        require_keys = ['position_destination']
        require_values = [tracker.get_slot(key) for key in require_keys]
        # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n object_size: {tracker.get_slot('object_size')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} ")
        if None in require_values:
            param_dict = get_output_api_form("change_top", response_message=f'Mình nhận ra bạn muốn thay đổi vị trí dựa trên góc trên của một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần thông tin sau: ' \
                                     f'\t- Ví trí mà bạn muốn vật thể di chuyển đến')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []  

        param_dict = get_output_api_form('change_top', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]


class ActionChangeLeft(Action):

    def name(self) -> Text:
        return "action_change_left"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_change_left'), 
                    FollowupAction('action_select_object')
                    ]
        require_keys = ['position_destination']
        require_values = [tracker.get_slot(key) for key in require_keys]
        # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n object_size: {tracker.get_slot('object_size')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} ")
        if None in require_values:
            param_dict = get_output_api_form("change_left", response_message=f'Mình nhận ra bạn muốn thay đổi vị trí dựa trên góc trái của một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần thông tin sau: ' \
                                     f'\t- Ví trí mà bạn muốn vật thể di chuyển đến')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []  

        param_dict = get_output_api_form('change_left', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]
        

class ActionChangeRight(Action):

    def name(self) -> Text:
        return "action_change_right"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_change_right'), 
                    FollowupAction('action_select_object')
                    ]
        require_keys = ['position_destination']
        require_values = [tracker.get_slot(key) for key in require_keys]
        # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n object_size: {tracker.get_slot('object_size')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} ")
        if None in require_values:
            param_dict = get_output_api_form("change_left", response_message=f'Mình nhận ra bạn muốn thay đổi vị trí dựa trên góc phải của một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                             f'Để có thể thực hiện được tác vụ này, mình cần thông tin sau: ' \
                                             f'\t- Ví trí mà bạn muốn vật thể di chuyển đến')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []  

        param_dict = get_output_api_form('change_right', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]


class ActionChangeBottom(Action):

    def name(self) -> Text:
        return "action_change_bottom"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_select_keys = ['object_shape', 'object_size', 'position_source', 'object_color']
        require_select_values = [tracker.get_slot(key) for key in require_select_keys]
        
        if require_select_values != [None] * len(require_select_values):
            last_action = tracker.get_slot('last_action')
            if last_action is None:
                return [
                    SlotSet('last_action', 'action_change_bottom'), 
                    FollowupAction('action_select_object')
                    ]
        require_keys = ['position_destination']
        require_values = [tracker.get_slot(key) for key in require_keys]
        # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n object_size: {tracker.get_slot('object_size')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} ")
        if None in require_values:
            param_dict = get_output_api_form("change_bottom", response_message=f'Mình nhận ra bạn muốn thay đổi vị trí dựa trên góc dưới của một vật thể trên màn hình. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần thông tin sau: ' \
                                     f'\t- Ví trí mà bạn muốn vật thể di chuyển đến')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []

            return []  

        param_dict = get_output_api_form('change_bottom', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        

        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]



class ActionDrawCircle(Action):

    def name(self) -> Text:
        return "action_draw_circle"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_keys = ['object_size', "position_source"]
        # position_source_x = next(tracker.get_latest_entity_values("position", "source_x"), None)
        # position_source_y = next(tracker.get_latest_entity_values("position", "source_y"), None)
        # position_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)
        # dispatcher.utter_message(f"position_source_x: {str(position_source_x)}\nposition_source_y: {str(position_source_y)}\nposition_destination_y: {str(position_destination_y)}")
        require_values = [tracker.get_slot(key) for key in require_keys]
        # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} \n object_size: {tracker.get_slot('object_size')}"
        if None in require_values:
            param_dict = get_output_api_form("draw_circle", 
                    response_message=f'Mình nhận ra bạn muốn vẽ một hình tròn. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
                                     f'\t- Kích thước của hình tròn. \n' \
                                     f'\t- Vị trí mà bạn muốn vẽ hình tròn này. \n')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []

        try:
            size_dict = tracker.get_slot("object_size")
            aspect_list = check_value_shape_size("tròn", size_dict)
            if aspect_list == "None":
                text='Mình nhận ra bạn muốn vẽ một hình tròn. Tuy nhiên, thông tin về kích thước của hình tròn mà bạn cung cấp cho mình là chưa đủ hoặc chưa phù hợp.'
                param_dict = get_output_api_form(intent='draw_circle', response_message=text)
                dispatcher.utter_custom_json(json_message=param_dict)
                return []
        except:
            pass

        param_dict = get_output_api_form("draw_circle", tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)

        # return [SlotSet("value_height", None),
        #         SlotSet("value_width", None),
        #         SlotSet("value_length", None),
        #         SlotSet("value_thickness", None),
        #         SlotSet("value_orientation", None),
        #         SlotSet("value_size", None),
        #         SlotSet("value_shape", None),
        #         SlotSet("value_color", None),
        #         SlotSet("position_source", None)]
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

    
class ActionDrawEllipse(Action):

    def name(self) -> Text:
        return "action_draw_ellipse"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
        require_keys = ['object_size', "position_source"]
        # position_source_x = next(tracker.get_latest_entity_values("position", "source_x"), None)
        # position_source_y = next(tracker.get_latest_entity_values("position", "source_y"), None)
        # position_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)
        # dispatcher.utter_message(f"position_source_x: {str(position_source_x)}\nposition_source_y: {str(position_source_y)}\nposition_destination_y: {str(position_destination_y)}")
        require_values = [tracker.get_slot(key) for key in require_keys]
        # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} \n object_size: {tracker.get_slot('object_size')}"
        if None in require_values:
            param_dict = get_output_api_form("draw_ellipse", 
                    response_message=f'Mình nhận ra bạn muốn vẽ một hình ê-líp. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
                                     f'\t- Kích thước của hình ê-líp. \n' \
                                     f'\t- Vị trí mà bạn muốn vẽ hình ê-líp này. \n')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []

        try:
            size_dict = tracker.get_slot("object_size")
            aspect_list = check_value_shape_size("ê-líp", size_dict)
            if aspect_list == "None":
                text='Mình nhận ra bạn muốn vẽ một hình ê-líp. Tuy nhiên, thông tin về kích thước của hình ê-líp mà bạn cung cấp cho mình là chưa đủ hoặc chưa phù hợp.'
                param_dict = get_output_api_form('draw_ellipse', response_message=text)
                dispatcher.utter_custom_json(json_message=param_dict)
                return []
        except:
            pass

        param_dict = get_output_api_form("draw_ellipse", tracker)
        
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)

        # return [SlotSet("value_height", None),
        #         SlotSet("value_width", None),
        #         SlotSet("value_length", None),
        #         SlotSet("value_thickness", None),
        #         SlotSet("value_orientation", None),
        #         SlotSet("value_size", None),
        #         SlotSet("value_shape", None),
        #         SlotSet("value_color", None),
        #         SlotSet("position_source", None)]
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]
        


class ActionDrawRectangle(Action):

    def name(self) -> Text:
        return "action_draw_rectangle"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_keys = ['object_size', 'position_source']
        require_values = [tracker.get_slot(key) for key in require_keys]
        if None in require_values:
            param_dict = get_output_api_form("draw_rectangle", 
                    response_message=f'Mình nhận ra bạn muốn vẽ một hình chữ nhật. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
                                     f'\t- Kích thước của hình chữ nhật. \n' \
                                     f'\t- Vị trí mà bạn muốn vẽ hình chữ nhật này. \n')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []

        try:
            size_dict = tracker.get_slot("object_size")
            aspect_list = check_value_shape_size("chữ nhật", size_dict)
            if aspect_list == "None":
                text='Mình nhận ra bạn muốn vẽ một hình chữ nhật. Tuy nhiên, thông tin về kích thước của hình chữ nhật mà bạn cung cấp cho mình là chưa đủ hoặc chưa phù hợp.'
                param_dict = get_output_api_form('draw_rectangle', response_message=text)
                dispatcher.utter_custom_json(json_message=param_dict)
                return []
        except:
            pass
        
        param_dict = get_output_api_form('draw_rectangle', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)      
        # return [SlotSet("value_height", None),
        #         SlotSet("value_width", None),
        #         SlotSet("value_length", None),
        #         SlotSet("value_thickness", None),
        #         SlotSet("value_orientation", None),
        #         SlotSet("value_size", None),
        #         SlotSet("value_shape", None),
        #         SlotSet("value_color", None),
        #         SlotSet("position_source", None)]
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]
        

class ActionDrawSquare(Action):

    def name(self) -> Text:
        return "action_draw_square"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_keys = ['object_size', 'position_source']
        require_values = [tracker.get_slot(key) for key in require_keys]
        if None in require_values:
            param_dict = get_output_api_form("draw_square", 
                    response_message=f'Mình nhận ra bạn muốn vẽ một hình vuông. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
                                     f'\t- Kích thước của hình vuông. \n' \
                                     f'\t- Vị trí mà bạn muốn vẽ hình vuông này. \n')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []

        try:
            size_dict = tracker.get_slot("object_size")
            aspect_list = check_value_shape_size("vuông", size_dict)
            if aspect_list == "None":
                text='Mình nhận ra bạn muốn vẽ một hình vuông. Tuy nhiên, thông tin về kích thước của hình vuông mà bạn cung cấp cho mình là chưa đủ hoặc chưa phù hợp.'
                param_dict = get_output_api_form('draw_square', response_message=text)
                dispatcher.utter_custom_json(json_message=param_dict)
                return []
        except:
            pass
        
        param_dict = get_output_api_form('draw_square', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)      
        # return [SlotSet("value_height", None),
        #         SlotSet("value_width", None),
        #         SlotSet("value_length", None),
        #         SlotSet("value_thickness", None),
        #         SlotSet("value_orientation", None),
        #         SlotSet("value_size", None),
        #         SlotSet("value_shape", None),
        #         SlotSet("value_color", None),
        #         SlotSet("position_source", None)]
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]
        

class ActionDrawRhombus(Action):

    def name(self) -> Text:
        return "action_draw_rhombus"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_keys = ['object_size', 'position_source']
        require_values = [tracker.get_slot(key) for key in require_keys]
        if None in require_values:
            param_dict = get_output_api_form("draw_rhombus", 
                    response_message=f'Mình nhận ra bạn muốn vẽ một hình thoi. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
                                     f'\t- Kích thước của hình thoi. \n' \
                                     f'\t- Vị trí mà bạn muốn vẽ hình thoi này. \n')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []

        try:
            size_dict = tracker.get_slot("object_size")
            aspect_list = check_value_shape_size("thoi", size_dict)
            if aspect_list == "None":
                text='Mình nhận ra bạn muốn vẽ một hình thoi. Tuy nhiên, thông tin về kích thước của hình thoi mà bạn cung cấp cho mình là chưa đủ hoặc chưa phù hợp.'
                param_dict = get_output_api_form('draw_rhombus', response_message=text)
                dispatcher.utter_custom_json(json_message=param_dict)
                return []
        except:
            pass
        
        dispatcher.utter_custom_json(json_message=param_dict)      
        # return [SlotSet("value_height", None),
        #         SlotSet("value_width", None),
        #         SlotSet("value_length", None),
        #         SlotSet("value_thickness", None),
        #         SlotSet("value_orientation", None),
        #         SlotSet("value_size", None),
        #         SlotSet("value_shape", None),
        #         SlotSet("value_color", None),
        #         SlotSet("position_source", None)]
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]
        

class ActionDrawParallelogram(Action):

    def name(self) -> Text:
        return "action_draw_parallelogram"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        require_keys = ['object_size', 'position_source']
        require_values = [tracker.get_slot(key) for key in require_keys]
        if None in require_values:
            param_dict = get_output_api_form("draw_parallelogram", 
                    response_message=f'Mình nhận ra bạn muốn vẽ một hình bình hành. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
                                     f'\t- Kích thước của hình bình hành. \n' \
                                     f'\t- Vị trí mà bạn muốn vẽ hình bình hành này. \n')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []

        try:
            size_dict = tracker.get_slot("object_size")
            aspect_list = check_value_shape_size("bình hành", size_dict)
            if aspect_list == "None":
                text='Mình nhận ra bạn muốn vẽ một hình bình hành. Tuy nhiên, thông tin về kích thước của hình bình hành mà bạn cung cấp cho mình là chưa đủ hoặc chưa phù hợp.'
                param_dict = get_output_api_form('draw_parallelogram', response_message=text)
                dispatcher.utter_custom_json(json_message=param_dict)
                return []
        except:
            pass
        
        param_dict = get_output_api_form('draw_parallelogram', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)      
        # return [SlotSet("value_height", None),
        #         SlotSet("value_width", None),
        #         SlotSet("value_length", None),
        #         SlotSet("value_thickness", None),
        #         SlotSet("value_orientation", None),
        #         SlotSet("value_size", None),
        #         SlotSet("value_shape", None),
        #         SlotSet("value_color", None),
        #         SlotSet("position_source", None)]
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]
        

class ActionDrawTrapezoid(Action):

    def name(self) -> Text:
        return "action_draw_trapezoid"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_keys = ['object_size', 'position_source']
        require_values = [tracker.get_slot(key) for key in require_keys]
        if None in require_values:
            param_dict = get_output_api_form("draw_trapezoid", 
                    response_message=f'Mình nhận ra bạn muốn vẽ một hình thang. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
                                     f'\t- Kích thước của hình thang. \n' \
                                     f'\t- Vị trí mà bạn muốn vẽ hình thang này. \n')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []

        try:
            size_dict = tracker.get_slot("object_size")
            aspect_list = check_value_shape_size("thang", size_dict)
            if aspect_list == "None":
                text='Mình nhận ra bạn muốn vẽ một hình thang. Tuy nhiên, thông tin về kích thước của hình thang mà bạn cung cấp cho mình là chưa đủ hoặc chưa phù hợp.'
                param_dict = get_output_api_form('draw_trapezoid', response_message=text)
                dispatcher.utter_custom_json(json_message=param_dict)
                return []
        except:
            pass
        
        param_dict = get_output_api_form('draw_trapezoid', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)      
        # return [SlotSet("value_height", None),
        #         SlotSet("value_width", None),
        #         SlotSet("value_length", None),
        #         SlotSet("value_thickness", None),
        #         SlotSet("value_orientation", None),
        #         SlotSet("value_size", None),
        #         SlotSet("value_shape", None),
        #         SlotSet("value_color", None),
        #         SlotSet("position_source", None)]
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]

class ActionDrawLine(Action):

    def name(self) -> Text:
        return "action_draw_line"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_keys = ['object_size', "position_source"]
        # position_source_x = next(tracker.get_latest_entity_values("position", "source_x"), None)
        # position_source_y = next(tracker.get_latest_entity_values("position", "source_y"), None)
        # position_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)
        # dispatcher.utter_message(f"position_source_x: {str(position_source_x)}\nposition_source_y: {str(position_source_y)}\nposition_destination_y: {str(position_destination_y)}")
        require_values = [tracker.get_slot(key) for key in require_keys]
        # dispatcher.utter_message(text=f"object_shape: {tracker.get_slot('object_shape')} \n  position_source: {tracker.get_slot('position_source')} \n object_color: {tracker.get_slot('object_color')} \n value_angle: {tracker.get_slot('value_angle')} \n object_size: {tracker.get_slot('object_size')}"
        if None in require_values:
            param_dict = get_output_api_form("draw_line", 
                    response_message=f'Mình nhận ra bạn muốn vẽ một đường thẳng. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
                                     f'\t- Kích thước của đường thẳng. \n' \
                                     f'\t- Vị trí mà bạn muốn vẽ đường thẳng này. \n')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []

        try:
            size_dict = tracker.get_slot("object_size")
            aspect_list = check_value_shape_size("đường thẳng", size_dict)
            if aspect_list == "None":
                text='Mình nhận ra bạn muốn vẽ một đường thẳng. Tuy nhiên, thông tin về kích thước của đường thẳng mà bạn cung cấp cho mình là chưa đủ hoặc chưa phù hợp.'
                param_dict = get_output_api_form('draw_line', response_message=text)
                dispatcher.utter_custom_json(json_message=param_dict)
                return []
        except:
            pass

        param_dict = get_output_api_form('draw_line', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)
        # return [SlotSet("value_height", None),
        #         SlotSet("value_width", None),
        #         SlotSet("value_length", None),
        #         SlotSet("value_thickness", None),
        #         SlotSet("value_orientation", None),
        #         SlotSet("value_size", None),
        #         SlotSet("value_shape", None),
        #         SlotSet("value_color", None),
        #         SlotSet("position_source", None),
        #         SlotSet("position_source_x", None),
        #         SlotSet("position_source_y", None),
        #         SlotSet("position_destination", None),
        #         SlotSet("position_destination_x", None),
        #         SlotSet("position_destination_y", None),
        #         SlotSet("object_destination", None)]
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]
    

class ActionDrawArrow(Action):

    def name(self) -> Text:
        return "action_draw_arrow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        require_keys = ['object_size', 'position_source']
        require_values = [tracker.get_slot(key) for key in require_keys]
        if None in require_values:
            param_dict = get_output_api_form("draw_arrow", 
                    response_message=f'Mình nhận ra bạn muốn vẽ một hình mũi tên. Tuy nhiên, bạn chưa cung cấp đủ các thông tin cần thiết. ' \
                                     f'Để có thể thực hiện được tác vụ này, mình cần các thông tin sau: \n' \
                                     f'\t- Kích thước của hình mũi tên. \n' \
                                     f'\t- Vị trí mà bạn muốn vẽ hình mũi tên này. \n')
            dispatcher.utter_custom_json(json_message=param_dict)
            return []

        try:
            size_dict = tracker.get_slot("object_size")
            aspect_list = check_value_shape_size("mũi tên", size_dict)
            if aspect_list == "None":
                text='Mình nhận ra bạn muốn vẽ một hình mũi tên. Tuy nhiên, thông tin về kích thước của hình mũi tên mà bạn cung cấp cho mình là chưa đủ hoặc chưa phù hợp.'
                param_dict = get_output_api_form('draw_arrow', response_message=text)
                dispatcher.utter_custom_json(json_message=param_dict)
                return []
        except:
            pass
        
        param_dict = get_output_api_form('draw_arrow', tracker)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)      
        # return [SlotSet("value_height", None),
        #         SlotSet("value_width", None),
        #         SlotSet("value_length", None),
        #         SlotSet("value_thickness", None),
        #         SlotSet("value_orientation", None),
        #         SlotSet("value_size", None),
        #         SlotSet("value_shape", None),
        #         SlotSet("value_color", None),
        #         SlotSet("position_source", None)]
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]


class ActionCopySelectedObject(Action):

    def name(self) -> Text:
        return "action_copy_selected_objects"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        text="Sao chép các đối tượng đã được chọn!"
        param_dict = get_output_api_form('copy_selected_objects', tracker=None, response_message=text)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)     
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]
    
class ActionCutSelectedObject(Action):

    def name(self) -> Text:
        return "action_cut_selected_objects"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        text="Cut các đối tượng đã được chọn!"
        param_dict = get_output_api_form('cut_selected_objects', tracker=None, response_message=text)
        # dispatcher.utter_message(text=json.dumps(param_dict, ensure_ascii=False))
        dispatcher.utter_custom_json(json_message=param_dict)     
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]    

class ActionPaste(Action):

    def name(self) -> Text:
        return "action_paste"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dst_post = tracker.get_slot('position_destination')
        if dst_post is None:
            param_dict = get_output_api_form('paste', tracker=None, response_message="Bạn muốn dán vào vị trí nào?")
            dispatcher.utter_custom_json(param_dict)
            return []
        else:
            param_dict = get_output_api_form('paste', tracker=None, response_message='Dán các đối tượng đã chọn!')
            param_dict['position_destination'] = dst_post
            dispatcher.utter_custom_json(json_message=param_dict)   
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]    
    
class ActionUndo(Action):

    def name(self) -> Text:
        return "action_undo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        param_dict = get_output_api_form('undo', tracker=None, response_message='Hoàn tác!')
        dispatcher.utter_custom_json(json_message=param_dict)   
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]    

class ActionRedo(Action):

    def name(self) -> Text:
        return "action_redo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        param_dict = get_output_api_form('redo', tracker=None, response_message='Quay lại trước khi hoàn tác!')
        dispatcher.utter_custom_json(json_message=param_dict)   
        # return []
        return [AllSlotsReset(), SlotSet('last_memory', param_dict)]    
    
"""action customization for slot mapping"""
# class ActionSetSourcePosition(Action):
#     def name(self) -> Text:
#         return "action_set_position_source"
#     def run(self,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         current_value = tracker.get_slot("position_source")
#         if current_value is None:
#             entities_list_x = tracker.get_latest_entity_values(entity_type="position", entity_role="source_x")
#             entities_list_y = tracker.get_latest_entity_values(entity_type="position", entity_role="source_y")

#             if len(entities_list_x) > 0 and len(entities_list_y) > 0:
#                 new_value = "({}, {})".format(str(entities_list_x[0]), str(entities_list_y[0]))
#                 return [
#                 SlotSet("position_source", new_value)
#                 ]
#             else:
#                 return [
#                 SlotSet("position_source", None)
#                 ]
#         else:
#             return [
#                 SlotSet("position_source", None)
#                 ]



class ValidateCustomSlotMappings(ValidationAction):

    # async def extract_object_shape(self,
    #                                   dispatcher: CollectingDispatcher,
    #                                   tracker: Tracker,
    #                                   domain: Dict) -> Dict[Text, Any]:
        
    #     old_object_shape = tracker.get_slot("object_shape")
    #     object_shape = next(tracker.get_latest_entity_values("object", "shape"), None)
    #     if object_shape is not None:
    #         return {"object_shape": object_shape}
    #     return {"object_shape": old_object_shape}

    def validate_object_shape(self,
                              slot_value,
                              dispatcher: CollectingDispatcher,
                              tracker: Tracker,
                              domain: DomainDict) -> Dict[Text, Any]:
        if isinstance(slot_value, str):
            return {"object_shape": slot_value.lstrip("hình ")}
        else:
            return {"object_shape": None}
    
    # def validate_value_shape(self,
    #                          slot_value,
    #                          dispatcher: CollectingDispatcher,
    #                          tracker: Tracker,
    #                          domain: DomainDict) -> Dict[Text, Any]:
    #     if isinstance(slot_value, str):
    #         return {"value_shape": slot_value.lstrip("hình ")}
    #     else:
    #         return {"value_shape": None}
    
    async def extract_position_source(self,
                                      dispatcher: CollectingDispatcher,
                                      tracker: Tracker,
                                      domain: Dict) -> Dict[Text, Any]:
        old_position_source = tracker.get_slot("position_source")
        position_source = next(tracker.get_latest_entity_values("position", "source"), None)
        position_source_x = next(tracker.get_latest_entity_values("position", "source_x"), None)
        if position_source_x is None:
            position_source_x = tracker.get_slot("position_source_x")

        position_source_y = next(tracker.get_latest_entity_values("position", "source_y"), None)
        if position_source_y is None:
            position_source_y = tracker.get_slot("position_source_y")

        position_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)
        if position_destination_y is None:
            position_destination_y = tracker.get_slot("position_destination_y")

        if position_source_x is not None:
            if position_source_y is not None:
                return {"position_source": f"({str(position_source_x)}, {str(position_source_y)})"}
            if position_destination_y is not None:
                return {"position_source": f"({str(position_source_x)}, {str(position_destination_y)})"}
        
        if position_source is not None:
            return {"position_source": position_source}
        
        current_position_destination = tracker.get_slot("object_destination")
        
        if current_position_destination is not None and current_position_destination.startswith("("):
            position_destination_x, position_destination_y = current_position_destination[1:-1].split(", ")
            position_destination_x = int(position_destination_x)
            position_destination_y = int(position_destination_y)

            object_length = tracker.get_slot("object_length")
            if object_length is None:
                object_length = next(tracker.get_latest_entity_values("value", "length"), None)
            if (tracker.get_slot("object_shape") is not None and tracker.get_slot("object_shape") in ["đường", "đường thẳng", "đường chéo", "đoạn thẳng"]) and object_length is not None:

                object_length = int(object_length.split(" ")[0])
                if next(tracker.get_latest_entity_values("object", "orientation"), None) != None and next(tracker.get_latest_entity_values("object", "orientation"), None) in ["dọc", "thẳng đứng", "đứng"]:
                    source_y = position_destination_y - object_length
                    source_x = position_destination_x
                    return {"position_source": f"({source_x}, {source_y})"}
                else:
                    source_x = position_destination_x - object_length
                    source_y = position_destination_y
                    return {"position_source": f"({source_x}, {source_y})"}
                

                
            if tracker.get_intent_of_latest_message() == "draw_line" and tracker.get_slot("value_length") is not None:
                value_length = int(tracker.get_slot("value_length").split(" ")[0])
                if next(tracker.get_latest_entity_values("value", "orientation"), None) != None and next(tracker.get_latest_entity_values("value", "orientation"), None) in ["dọc", "thẳng đứng", "đứng"]:
                    source_y = position_destination_y - value_length
                    source_x = position_destination_x
                    return {"position_source": f"({source_x}, {source_y})"}
                else:
                    source_x = position_destination_x - value_length
                    source_y = position_destination_y
                    return {"position_source": f"({source_x}, {source_y})"}

        return {"position_source": old_position_source}
       
    async def extract_position_destination(self,
                                           dispatcher: CollectingDispatcher,
                                           tracker: Tracker,
                                           domain: Dict) -> Dict[Text, Any]:
        old_position_destination = tracker.get_slot("position_destination")
        intent = tracker.get_intent_of_latest_message()

        if intent in ["change_top", "change_left", "change_right", "change_bottom", "paste"]:

            position_destination = next(tracker.get_latest_entity_values("position", "destination"), None)
            position_destination_x = list(tracker.get_latest_entity_values("position", "destination_x"))
            # position_destination_x = tracker.get_slot("position_destination_x")

            position_source_y = list(tracker.get_latest_entity_values("position", "source_y"))
            # position_source_y = tracker.get_slot("position_source_y")

            position_destination_y = list(tracker.get_latest_entity_values("position", "destination_y"))
            # position_destination_y = tracker.get_slot("position_destination_y")

            position_source = list(tracker.get_latest_entity_values("position", "source"))
            if len(position_source) == 0:
                position_source = list(tracker.get_latest_entity_values("position", "source_x"))
            if len(position_source) > 0:
                entity_list = tracker.latest_message['entities']
                destination = None
                destination_x = None
                destination_y = None
                for i, entity in enumerate(entity_list):
                    if entity['entity'] == 'position' and entity['role'] in ['source', 'source_x']:
                        for new_entity in entity_list[:i]:
                            if new_entity['entity'] == 'position' and new_entity['role'] == 'destination':
                                destination = new_entity['value']
                            if new_entity['entity'] == 'position' and new_entity['role'] == 'destination_x':
                                destination_x = new_entity['value']
                            if new_entity['entity'] == 'position' and new_entity['role'] == 'destination_y':
                                destination_y = new_entity['value']
                            if destination is not None:
                                return {"position_destination": destination}
                            if destination_x is not None and destination_y is not None:
                                return {"position_destination": f"({destination_x}, {destination_y})"}
                        break
                

            if len(position_destination_x) > 0:
                destination_x = position_destination_x[-1]
                if len(position_destination_y) > 0:
                    destination_y = position_destination_y[-1]
                    return {"position_destination": f"({destination_x}, {destination_y})"}
                if len(position_source_y) > 1:
                    source_y = position_source_y[-1]
                    return {"position_destination": f"({destination_x}, {source_y})"}
        
        
            if position_destination is not None:
                return {"position_destination": position_destination}
                    
            # if tracker.get_intent_of_latest_message() == "draw_line" and tracker.get_slot("value_length") is not None:
            #     value_length = int(tracker.get_slot("value_length").split(" ")[0])
            #     if next(tracker.get_latest_entity_values("value", "orientation"), None) != None and next(tracker.get_latest_entity_values("value", "orientation"), None) in ["dọc", "thẳng đứng", "đứng"]:
            #         destination_y = position_source_y + value_length
            #         destination_x = position_source_x
            #         return {"position_destination": f"({destination_x}, {destination_y})"}
            #     else:
            #         destination_x = position_source_x + value_length
            #         destination_y = position_source_y
            #         return {"position_destination": f"({destination_x}, {destination_y})"}
                
            
        return {"position_destination": old_position_destination}
    
    async def extract_object_destination(self,
                                         dispatcher: CollectingDispatcher,
                                         tracker: Tracker,
                                         domain: Dict) -> Dict[Text, Any]:
        
        old_object_destination = tracker.get_slot("object_destination")
        intent = tracker.get_intent_of_latest_message(skip_fallback_intent=False)

        object_shape = next(tracker.get_latest_entity_values("object", "shape"), None)
        if object_shape is None:
            object_shape = next(tracker.get_latest_entity_values("value", "shape"), None)

        if object_shape is not None and object_shape.split(" ")[0] in ["đường", "đoạn"] and "tròn" not in object_shape and "cong" not in object_shape:
            if intent not in ["change_top", "change_left", "change_right", "change_bottom"]:
                # object_destination = next(tracker.get_latest_entity_values("position", "destination"), None)
                # if not object_destination:
                #     object_destination = tracker.get_slot("position_destination")
                # if object_destination:                                  
                #     return {"object_destination": object_destination}

                # return {"object_destination": old_object_destination}
        
                current_position_source = tracker.get_slot("position_source")

                if current_position_source is not None and current_position_source.startswith("("):
                    position_source_x, position_source_y = current_position_source[1:-1].split(", ")
                    position_source_x = int(position_source_x)
                    position_source_y = int(position_source_y)

                    object_length = next(tracker.get_latest_entity_values("object", "length"), None)
                    if object_length is None:
                        object_length = tracker.get_slot("object", "length")

                    if object_length is not None:
                        object_length = int(object_length.split(" ")[0])

                        object_angle = next(tracker.get_latest_entity_values("object", "angle"), None)
                        if object_angle is None:
                            object_angle = tracker.get_slot("object_angle")
                            
                        object_orientation = next(tracker.get_latest_entity_values("object", "orientation"), None)
                        if object_orientation is None:
                            object_orientation = tracker.get_slot("object_orientation")

                        if object_orientation != None:
                            if object_orientation in ["dọc", "thẳng đứng", "đứng"]:
                                destination_x = position_source_y + object_length
                                destination_y = position_source_x
                                return {"object_destination": f"({destination_x}, {destination_y})"}
                            else:
                                destination_x = position_source_x + object_length
                                destination_y = position_source_y
                                return {"object_destination": f"({destination_x}, {destination_y})"}
                        else:
                            import math
                            if object_angle != None:
                                angle = float(object_angle.split(" ")[0])
                                destination_x = position_source_x + int(math.cos(angle)*object_length)
                                destination_y = position_source_y + int(math.sin(angle)*object_length)
                                return {"object_destination": f"({destination_x}, {destination_y})"}
                            else:
                                destination_x = position_source_x + object_length
                                destination_y = position_source_y
                                return {"object_destination": f"({destination_x}, {destination_y})"}
                        
                old_object_destination = tracker.get_slot("object_destination")
                object_destination = next(tracker.get_latest_entity_values("position", "destination"), None)
                # object_destination_x = next(tracker.get_latest_entity_values("position", "destination_x"), None)
                object_destination_x = tracker.get_slot("position_destination_x")

                object_source_y = list(tracker.get_latest_entity_values("position", "source_y"))
                # object_source_y = tracker.get_slot("position_source_y")

                # object_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)
                object_destination_y = tracker.get_slot("position_destination_y")

                if object_destination_x is not None:
                    if object_destination_y is not None:
                        return {"object_destination": f"({object_destination_x}, {object_destination_y})"}
                    if len(object_source_y) >= 2:
                        source_y = object_source_y[1]
                        return {"object_destination": f"({object_destination_x}, {source_y})"}
                    
                if object_destination is not None:
                    return {"object_destination": object_destination}
                    
            # if tracker.get_intent_of_latest_message() == "draw_line" and tracker.get_slot("value_length") is not None:
            #     value_length = int(tracker.get_slot("value_length").split(" ")[0])
            #     if next(tracker.get_latest_entity_values("value", "orientation"), None) != None and next(tracker.get_latest_entity_values("value", "orientation"), None) in ["dọc", "thẳng đứng", "đứng"]:
            #         destination_y = position_source_y + value_length
            #         destination_x = position_source_x
            #         return {"position_destination": f"({destination_x}, {destination_y})"}
            #     else:
            #         destination_x = position_source_x + value_length
            #         destination_y = position_source_y
            #         return {"position_destination": f"({destination_x}, {destination_y})"}
                
            
                return {"object_destination": old_object_destination}
        
            else:  
                object_length = next(tracker.get_latest_entity_values("object", "length"), None)
                if object_length is None:
                    object_length = next(tracker.get_latest_entity_values("value", "length"), None)

                if object_length is not None:
                    current_position_source = tracker.get_slot("position_source")

                    if current_position_source is not None and current_position_source.startswith("("):
                        position_source_x, position_source_y = current_position_source[1:-1].split(", ")
                        position_source_x = int(position_source_x)
                        position_source_y = int(position_source_y)

                        object_orientation = next(tracker.get_latest_entity_values("object", "orientation"), None)
                        if object_orientation is None:
                            object_orientation = next(tracker.get_latest_entity_values("value", "orientation"), None)

                        object_length = int(object_length.split(" ")[0])
                        if object_orientation != None and object_orientation in ["dọc", "thẳng đứng", "đứng"]:
                            destination_x = position_source_y + object_length
                            destination_y = position_source_x
                            return {"object_destination": f"({destination_x}, {destination_y})"}
                        else:
                            destination_x = position_source_x + object_length
                            destination_y = position_source_y
                            return {"object_destination": f"({destination_x}, {destination_y})"}
                        
                entity_list = tracker.latest_message['entities']
                
                for i, entity in enumerate(entity_list):
                    if entity['entity'] == 'position' and entity['role'] in ['source', 'source_x']:
                        # index = entity['end']
                        # entity_index = i
                        destination = None
                        destination_x = None
                        destination_y = None
                        for new_entity in entity_list[i:]:
                            if new_entity['entity'] == 'position' and new_entity['role'] == 'destination':
                                destination = new_entity['value']
                            if new_entity['entity'] == 'position' and new_entity['role'] == 'destination_x':
                                destination_x = new_entity['value']
                            if new_entity['entity'] == 'position' and new_entity['role'] == 'destination_y':
                                destination_y = new_entity['value']
                            if destination is not None:
                                return {"object_destination": destination}
                            if destination_x is not None and  destination_y is not None:
                                return {"object_destination": f"({destination_x}, {destination_y})"}         
                        break
                
      
            return {"object_destination": old_object_destination}
         
    async def extract_selected_area_source(self,
                                      dispatcher: CollectingDispatcher,
                                      tracker: Tracker,
                                      domain: Dict) -> Dict[Text, Any]:
        old_selected_area_source = tracker.get_slot("selected_area_source")

        if tracker.get_intent_of_latest_message() == "select_area":
            selected_area_height = tracker.get_slot("selected_area_height")
            selected_area_width = tracker.get_slot("selected_area_width")
            selected_area_length = tracker.get_slot("selected_area_length")

            position_source = tracker.get_slot("position_source")
            if position_source is None:
                position_source = next(tracker.get_latest_entity_values("position", "source"), None)
            
            # position_source_x = tracker.get_slot("position_source_x")
            # position_source_y = tracker.get_slot("position_source_y")

            # position_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)

            if position_source is not None:
                return {"selected_area_source": position_source}
            
            # if position_source_x is not None:
            #     if position_source_y is not None:
            #         return {"position_source": f"({str(position_source_x)}, {str(position_source_y)})"}
            #     if position_destination_y is not None:
            #         return {"position_source": f"({str(position_source_x)}, {str(position_destination_y)})"}
            
            current_position_destination = tracker.get_slot("selected_area_destination")
            if current_position_destination is not None and current_position_destination.startswith("("):
                position_destination_x, position_destination_y = current_position_destination[1:-1].split(", ")
                position_destination_x = int(position_destination_x)
                position_destination_y = int(position_destination_y)

                if selected_area_height is not None and selected_area_length is not None:
                    selected_area_height = int(selected_area_height.split(" ")[0])
                    selected_area_length = int(selected_area_length.split(" ")[0])

                    source_x = position_destination_x - selected_area_length
                    source_y = position_destination_y - selected_area_height

                    return {"selected_area_source": f"({str(source_x)}, {str(source_y)})"}
                
                if selected_area_width is not None and selected_area_length is not None:
                    selected_area_width = int(selected_area_width.split(" ")[0])
                    selected_area_length = int(selected_area_length.split(" ")[0])

                    source_x = position_destination_x - selected_area_length
                    source_y = position_destination_y - selected_area_width

                    return {"selected_area_source": f"({str(source_x)}, {str(source_y)})"}
                
                if selected_area_height is not None and selected_area_width is not None:
                    selected_area_height = int(selected_area_height.split(" ")[0])
                    selected_area_width = int(selected_area_width.split(" ")[0])

                    source_x = position_destination_x - selected_area_width
                    source_y = position_destination_y - selected_area_height

                    return {"selected_area_source": f"({str(source_x)}, {str(source_y)})"}
            
            return {"selected_area_source": old_selected_area_source}
        return {"selected_area_source": old_selected_area_source}
    
    async def extract_selected_area_destination(self,
                                      dispatcher: CollectingDispatcher,
                                      tracker: Tracker,
                                      domain: Dict) -> Dict[Text, Any]:
        old_selected_area_destination = tracker.get_slot("selected_area_destination")

        if tracker.get_intent_of_latest_message() == "select_area":
            selected_area_height = tracker.get_slot("selected_area_height")
            selected_area_width = tracker.get_slot("selected_area_width")
            selected_area_length = tracker.get_slot("selected_area_length")

            position_destination = tracker.get_slot("position_destination")
            if position_destination is None:
                position_destination = next(tracker.get_latest_entity_values("position", "destination"), None)
            
            position_destination_x = list(tracker.get_latest_entity_values("position", "destination_x"))
            position_destination_y = list(tracker.get_latest_entity_values("position", "destination_y"))

            position_source_y = list(tracker.get_latest_entity_values("position", "source_y"))
            # position_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)

            if position_destination is not None:
                return {"selected_area_destination": position_destination}
            
            if len(position_destination_x) > 0:
                if len(position_destination_y) > 0:
                    return {"selected_area_destination": f"({str(position_destination_x[-1])}, {str(position_destination_y[-1])})"}
                if  len(position_source_y) > 1:
                    return {"selected_area_destination": f"({str(position_destination_x[-1])}, {str(position_source_y[-1])})"}
            
            current_position_source = tracker.get_slot("position_source")
            if current_position_source is not None and current_position_source.startswith("("):
                position_source_x, position_source_y = current_position_source[1:-1].split(", ")
                position_source_x = int(position_source_x)
                position_source_y = int(position_source_y)

                if selected_area_height is not None and selected_area_length is not None:
                    selected_area_height = int(selected_area_height.split(" ")[0])
                    selected_area_length = int(selected_area_length.split(" ")[0])

                    destination_x = position_source_x + selected_area_length
                    destination_y = position_source_y + selected_area_height

                    return {"selected_area_destination": f"({str(destination_x)}, {str(destination_y)})"}
                
                if selected_area_width is not None and selected_area_length is not None:
                    selected_area_width = int(selected_area_width.split(" ")[0])
                    selected_area_length = int(selected_area_length.split(" ")[0])

                    destination_x = position_source_x + selected_area_length
                    destination_y = position_source_y + selected_area_width

                    return {"selected_area_destination": f"({str(destination_x)}, {str(destination_y)})"}
                
                if selected_area_height is not None and selected_area_width is not None:
                    selected_area_height = int(selected_area_height.split(" ")[0])
                    selected_area_width = int(selected_area_width.split(" ")[0])

                    destination_x = position_source_x - selected_area_width
                    destination_y = position_source_y - selected_area_height

                    return {"selected_area_destination": f"({str(destination_x)}, {str(destination_y)})"}
            
            return {"selected_area_destination": old_selected_area_destination}
        return {"selected_area_destination": old_selected_area_destination}

    async def extract_object_size(self,
                                  dispatcher: CollectingDispatcher,
                                  tracker: Tracker,
                                  domain: Dict) -> Dict[Text, Any]:
        
        old_object_size = tracker.get_slot("object_size")

        object_size = next(tracker.get_latest_entity_values("object", "size"), None)
        # if object_size is None:
        #     object_size = next(tracker.get_latest_entity_values("value", "size"), None)
 
        # object_height = next(tracker.get_latest_entity_values("object", "height"), None)
        object_height = tracker.get_slot("object_height")
        # if object_height is None and tracker.get_intent_of_latest_message() is not None:
        #     # object_height = tracker.get_slot("value_height")
        #     object_height = next(tracker.get_latest_entity_values("value", "height"), None)

        # object_width = next(tracker.get_latest_entity_values("object", "width"), None)
        object_width = tracker.get_slot("object_width")
        # if object_width is None and tracker.get_intent_of_latest_message() is not None:
        #     # object_width = tracker.get_slot("value_width")
        #     object_width = next(tracker.get_latest_entity_values("value", "width"), None)

        # object_length = next(tracker.get_latest_entity_values("object", "length"), None)
        object_length = tracker.get_slot("object_length")
        # if object_length is None and tracker.get_intent_of_latest_message() is not None:
        #     # object_length = tracker.get_slot("value_length")
        #     object_length = next(tracker.get_latest_entity_values("value", "length"), None)
        
        # object_thickness = next(tracker.get_latest_entity_values("object", "thickness"), None)
        object_thickness = tracker.get_slot("object_thickness")
        # if object_thickness is None and tracker.get_intent_of_latest_message() is not None: 
        #     # object_thickness = tracker.get_slot("value_thickness")
        #     object_thickness = next(tracker.get_latest_entity_values("value", "thickness"), None)
        
        object_destination = tracker.get_slot("object_destination")

        object_angle = tracker.get_slot("object_angle")

        if object_height is not None or object_width is not None or object_length is not None or object_destination is not None:

            param_size = {
                "height": object_height,
                "width": object_width,
                "length": object_length,
                "thickness": object_thickness,
                "destination": object_destination,
                "angle": object_angle
            }

            # return {"object_size": json.dumps(param_size, ensure_ascii=False)}
            return {"object_size": param_size}
        
        if object_size is not None:
            return {"object_size": object_size}
                    
        return {"object_size": old_object_size}


    # async def extract_value_size(self,
    #                               dispatcher: CollectingDispatcher,
    #                               tracker: Tracker,
    #                               domain: Dict) -> Dict[Text, Any]:
        
    #     old_value_size = tracker.get_slot("value_size")
    #     value_size = next(tracker.get_latest_entity_values("value", "size"), None)

    #     # value_height = next(tracker.get_latest_entity_values("value", "height"), None)
    #     value_height = tracker.get_slot("value_height")
    #     if value_height is None and (tracker.get_intent_of_latest_message() is not None and tracker.get_intent_of_latest_message().startswith("draw")):
    #         # value_height = tracker.get_slot("value_height")
    #         value_height = next(tracker.get_latest_entity_values("object", "height"), None)

    #     # value_width = next(tracker.get_latest_entity_values("value", "width"), None)
    #     value_width = tracker.get_slot("value_width")
    #     if value_width is None and (tracker.get_intent_of_latest_message() is not None and tracker.get_intent_of_latest_message().startswith("draw")):
    #         # value_width = tracker.get_slot("value_width")  
    #         value_width = next(tracker.get_latest_entity_values("object", "width"), None)

    #     # value_length = next(tracker.get_latest_entity_values("value", "length"), None)
    #     value_length = tracker.get_slot("value_length")
    #     if value_length is None and (tracker.get_intent_of_latest_message() is not None and tracker.get_intent_of_latest_message().startswith("draw")):
    #         # value_length = tracker.get_slot("value_length")
    #         value_length = next(tracker.get_latest_entity_values("object", "length"), None)

    #     # value_thickness = next(tracker.get_latest_entity_values("value", "thickness"), None)
    #     value_thickness = tracker.get_slot("value_thickness")
    #     if value_thickness is None and (tracker.get_intent_of_latest_message() is not None and tracker.get_intent_of_latest_message().startswith("draw")):
    #         # value_thickness = tracker.get_slot("value_thickness")
    #         value_thickness = next(tracker.get_latest_entity_values("object", "thickness"), None)
        
    #     object_destination = tracker.get_slot("object_destination")

    #     if value_height is not None or value_width is not None or value_length is not None or object_destination is not None:

    #         param_size = {
    #             "height": value_height,
    #             "width": value_width,
    #             "length": value_length,
    #             "thickness": value_thickness,
    #             "object_destination": object_destination
    #         }
        
    #         return {"value_size": json.dumps(param_size)}
        
    #     if value_size is not None:
    #         return {"value_size": value_size}
                    
    #     return {"value_size": old_value_size}
    
    # async def extract_object_color(self,
    #                                   dispatcher: CollectingDispatcher,
    #                                   tracker: Tracker,
    #                                   domain: Dict) -> Dict[Text, Any]:
    #     old_object_color = tracker.get_slot("object_color")
    #     object_color = next(tracker.get_latest_entity_values("object", "color"), None)
    #     if object_color is not None:
    #         print("set object color")
    #         return {"object_color": object_color}
    #     return {"object_color": old_object_color}

