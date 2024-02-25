from rasa_sdk import Tracker

COLOR_LIST = {
    "trắng" : "#ffffff",
    "đen"   : "#000000",
    "đỏ"    : "#ff0000",
    "cam"   : "#ff8000", 
    "vàng"  : "#ffff00", 
    "lục"   : "#40ff00", 
    "lam"   : "#0080ff", 
    "chàm"  : "#0000ff",
    "tím"   : "#bf00ff",
    "hồng"  : "#ff80bf",
    "xanh lá cây"       : "#00ff40",
    "xanh dương"        : "#0040ff",
    "nâu"               : "#8b4513",
    "hổ phách"          : "#ffcf73",
    "xám"               : "#808080",
    "vàng chanh"        : "#ffdb58",
    "xanh ngọc"         : "#00ffcc",
    "xanh cobalt"       : "#0047ab",
    "đậm hồng"          : "#ff1493",
    "hồng đậm"          : "#ff1493"
}

def size2int(size:str):
    size = size.strip().split(" ")[0]
    num = ''
    for i in range(len(size)):
        if size[i] in ['0123456789']:
            num += size[i]
        else:
            try: 
                num = int(num)
                return num
            except:
                pass
            break
    return size
    
    

def get_output_api_form(intent:str, tracker:Tracker=None, response_message:str="Cảm ơn bạn đã cung cấp đầy đủ thông tin. Tác vụ sẽ được hoàn thành sau vài giây tới."):
    form = {
        "intent": intent,
        "response_message": response_message,
        "object_shape": None,
        # "object_width": None,
        # "object_height": None,
        # "object_length": None,
        "object_color": None,
        # "object_orientation": None,
        # "object_thickness": None,
        # "object_angle": None,
        "position_source": None,
        # "position_source_x": None,
        # "position_source_y": None,
        "position_destination": None,
        # "position_destination_x": None,
        # "position_destination_y": None,
        # "position_center": None,
        # "position_center_x": None,
        # "position_center_y": None,
        # "object_destination": None,
        "object_size": None,
        "value_angle": None,
        "value_color": None,
        "value_change": None,
        "value_move": None,
        "change_action": None,
        "selected_area_source": None,
        "selected_area_destination": None,
        # "selected_area_width": None,
        # "selected_area_length": None,
        # "selected_area_height": None,
        "comparison": None,
        # "session_started_metadata": None
    }
    if tracker is not None:
        form["object_size"] = tracker.get_slot("object_size")
        try:
            import json
            form["object_size"] = json.loads(form["object_size"])
        except Exception: pass
        form['object_shape'] = tracker.get_slot("object_shape")
        form["object_color"] = tracker.get_slot("object_color")
        form["position_source"] = tracker.get_slot("position_source")
        form["position_destination"] = tracker.get_slot("position_destination")
        
    try: 
        if intent == 'draw_line' or form['object_shape'].lower().lstrip('hình ') in ['đường thẳng', 'đoạn thẳng', 'đường chỉ', 'đường chéo']:
            if form['object_size']['length'] is None:
                if form['object_size']['width'] is not None: 
                    form['object_size']['length'] = form['object_size']['width']
                elif form['object_size']['height'] is not None: 
                    form['object_size']['length'] = form['object_size']['height']
            form['object_size']['width'] = None
            form['object_size']['height'] = None
            
        elif intent == 'draw_circle' or form['object_shape'].lower().lstrip('hình ') in ['đường tròn', 'đường cong', 'tròn']:
            if form['object_size']['width'] is None:
                if form['object_size']['length'] is not None:
                    try:
                        length = form['object_size']['length'].split(" ")[0]
                        form['object_size']['width'] = str( int(length) // 2 )
                    except:
                        form['object_size']['width'] = form['object_size']['length']
                elif form['object_size']['height'] is not None: 
                    form['object_size']['width'] = form['object_size']['height']
            form['object_size']['length'] = None
            form['object_size']['height'] = None
            
        elif intent =='draw_square' or form['object_shape'].lower().lstrip('hình ') in ['vuông', 'chữ vuông']:
            if form['object_size']['width'] is None:
                if form['object_size']['length'] is not None:
                    form['object_size']['width'] = form['object_size']['length']
                elif form['object_size']['height'] is not None: 
                    form['object_size']['width'] = form['object_size']['height']
            form['object_size']['length'] = None
            form['object_size']['height'] = None
                
        elif intent == 'draw_rectangle' or form['object_shape'].lower().lstrip('hình ') in ['nhật', 'chữ nhật', 'chữ điền', 'thoi', 'ê-líp', 'ê líp', 'ellipse', 'bầu dục']:
            if form['object_size']['width'] is None:
                if form['object_size']['height'] is not None: 
                    form['object_size']['width'] = form['object_size']['height']
                
            elif form['object_size']['length'] is None:
                if form['object_size']['height'] is not None: 
                    form['object_size']['length'] = form['object_size']['height']

            form['object_size']['height'] = None
            
        elif intent =='draw_parallelogram' or form['object_shape'].lower().lstrip('hình ') in ['bình hành']:
            if form['object_size']['length'] is None:
                if form['object_size']['width'] is not None: 
                    form['object_size']['length'] = form['object_size']['width']
                
            elif form['object_size']['height'] is None:
                if form['object_size']['width'] is not None: 
                    form['object_size']['height'] = form['object_size']['width']
            form['object_size']['width'] = None
    except Exception as e:
        print(e)
        
    return form

    
def get_size_dict_form():
    return {
                "height": None,
                "width": None,
                "length": None,
                "thickness": None,
                "object_destination": None,
                "orientation": None
            }
    
# def get_position_dict_form():
#     return {
        
#     }

# class ValidateRotateLeftForm(FormValidationAction):
#     """done"""
#     def name(self) -> Text:
#         return "validate_rotate_left_form"
    
#     def validate_object_shape(
#             self,
#             slot_value: Text,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         if slot_value.lower() not in OBJECT_LIST:
#             dispatcher.utter_message(text="Xin lỗi bạn, tớ không thể vẽ được hình này. Bạn hãy đưa ra một hình khác đơn giản hơn.")
#             return {"object_shape": None}
#         return {"object_shape": slot_value}
    
#     def validate_position_source(
#             self,
#             slot_value: Text,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         if slot_value is None:
#             # position_source_x = tracker.get_slot("position_source_x")
#             position_source_x = next(tracker.get_latest_entity_values("position", "source_x"), None)

#             # position_source_y = tracker.get_slot("position_source_y")
#             position_source_y = next(tracker.get_latest_entity_values("position", "source_y"), None)

#             # position_destination_y = tracker.get_slot("position_destination_y")
#             position_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)

#             if position_source_x is not None:
#                 if position_source_y is not None:
#                     slot_value = f"({position_source_x}, {position_source_y})"
#                 elif position_destination_y is not None:
#                     slot_value = f"({position_source_x}, {position_destination_y})"

#         return {"position_source": slot_value}
    
#     def validate_object_color(
#             self,
#             slot_value: Text,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         # if slot_value.lower() not in COLOR_LIST:
#         #     dispatcher.utter_message(text="Xin lỗi bạn, màu này không có trong danh sách. Bạn hãy vẽ bằng màu khác.")
#         #     return {"object_color": None}
#         return {"object_color": slot_value}
    
#     def validate_value_angle(
#             self,
#             slot_value: Text,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         return {"value_angle": slot_value}

# class ValidateRotateRightForm(FormValidationAction):
#     """done"""
#     def name(self) -> Text:
#         return "validate_rotate_right_form"
    
#     def validate_object_shape(
#             self,
#             slot_value: Text,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         if slot_value.lower() not in OBJECT_LIST:
#             dispatcher.utter_message(text="Xin lỗi bạn, tớ không thể vẽ được hình này. Bạn hãy đưa ra một hình khác đơn giản hơn.")
#             return {"object_shape": None}
#         return {"object_shape": slot_value}
    
#     def validate_position_source(
#             self,
#             slot_value: Text,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         if slot_value is None:
#             # position_source_x = tracker.get_slot("position_source_x")
#             position_source_x = next(tracker.get_latest_entity_values("position", "source_x"), None)

#             # position_source_y = tracker.get_slot("position_source_y")
#             position_source_y = next(tracker.get_latest_entity_values("position", "source_y"), None)

#             # position_destination_y = tracker.get_slot("position_destination_y")
#             position_destination_y = next(tracker.get_latest_entity_values("position", "destination_y"), None)

#             if position_source_x is not None:
#                 if position_source_y is not None:
#                     slot_value = f"({position_source_x}, {position_source_y})"
#                 elif position_destination_y is not None:
#                     slot_value = f"({position_source_x}, {position_destination_y})"

#         return {"position_source": slot_value}
    
#     def validate_object_color(
#             self,
#             slot_value: Text,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         if slot_value.lower() not in COLOR_LIST:
#             dispatcher.utter_message(text="Xin lỗi bạn, màu này không có trong danh sách. Bạn hãy vẽ bằng màu khác.")
#             return {"object_color": None}
#         return {"object_color": slot_value}
    
#     def validate_value_angle(
#             self,
#             slot_value: Text,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         return {"value_angle": slot_value}


        # return [SlotSet("object_shape", None),
        # SlotSet("position_source", None),
        # SlotSet("position_source_x", None),
        # SlotSet("position_source_y", None),
        # SlotSet("position_destination", None),
        # SlotSet("object_color", None),
        # SlotSet("object_size", None),
        # SlotSet("object_height", None),
        # SlotSet("object_width", None),
        # SlotSet("object_length", None),
        # SlotSet("object_thickness", None),
        # SlotSet("object_orientation", None),
        # SlotSet("object_destination", None),
        # SlotSet("position_destination_x", None),
        # SlotSet("position_destination_y", None),
        # SlotSet("selected_area_source", None),
        # SlotSet("selected_area_destination", None),
        # SlotSet("selected_area_height", None),
        # SlotSet("selected_area_width", None),
        # SlotSet("selected_area_length", None),
        # SlotSet("value_move", None)]
        
        
        # exit_select
        # return [SlotSet("object_shape", None),
        #         SlotSet("position_source", None),
        #         SlotSet("position_source_x", None),
        #         SlotSet("position_source_y", None),
        #         SlotSet("position_destination", None),
        #         SlotSet("object_color", None),
        #         SlotSet("object_size", None),
        #         SlotSet("object_height", None),
        #         SlotSet("object_width", None),
        #         SlotSet("object_length", None),
        #         SlotSet("object_thickness", None),
        #         SlotSet("object_destination", None),
        #         SlotSet("position_destination_x", None),
        #         SlotSet("position_destination_y", None),
        #         SlotSet("selected_area_source", None),
        #         SlotSet("selected_area_destination", None),
        #         SlotSet("selected_area_height", None),
        #         SlotSet("selected_area_width", None),
        #         SlotSet("selected_area_length", None),
        #         SlotSet("object_orientation", None),]
        
        # delete
        # return [SlotSet("object_shape", None),
        #         SlotSet("object_color", None),
        #         SlotSet("object_size", None),
        #         SlotSet("object_height", None),
        #         SlotSet("object_width", None),
        #         SlotSet("object_length", None),
        #         SlotSet("object_thickness", None),
        #         SlotSet("object_orientation", None),
        #         SlotSet("position_source", None),
        #         SlotSet("position_source_x", None),
        #         SlotSet("position_source_y", None),
        #         SlotSet("position_destination", None),
        #         SlotSet("object_destination", None),
        #         SlotSet("position_destination_x", None),
        #         SlotSet("position_destination_y", None),
        #         SlotSet("selected_area_source", None),
        #         SlotSet("selected_area_destination", None),
        #         SlotSet("selected_area_height", None),
        #         SlotSet("selected_area_width", None),
        #         SlotSet("selected_area_length", None),]
        
        
        
        # select area
        # width = tracker.get_slot('selected_area_width')
        # height = tracker.get_slot('selected_area_height')
        # length = tracker.get_slot('selected_area_length')
        
        # src_post = tracker.get_slot('position_source')
        # if src_post is None:
        #     src_x = tracker.get_slot('position_source_x')
        #     src_y = tracker.get_slot('position_source_y')
        #     if src_x is not None and src_y is not None:
        #         src_post = f'({src_x},{src_y})'
                
        # dst_post = tracker.get_slot('position_destination')
        # if dst_post is None:
        #     dst_x = tracker.get_slot('position_destination_x')
        #     dst_y = tracker.get_slot('position_destination_y')
        #     if dst_x is not None and dst_y is not None:
        #         dst_post = f'({dst_x},{dst_y})'

        
        # if src_post is not None and dst_post is not None:
        #     dispatcher.utter_message(text=f'Chọn theo vùng bắt đầu từ {src_post} đến {dst_post}!')
        # elif src_post is not None and width is not None and height is not None:
        #     dispatcher.utter_message(text=f'Chọn theo vùng bắt đầu từ {src_post} với kích thước {width}x{height}!')
        # elif src_post is not None and length is not None and height is not None:
        #     dispatcher.utter_message(text=f'Chọn theo vùng bắt đầu từ {src_post} với kích thước {length}x{height}!')
        # elif src_post is not None and width is not None and length is not None:
        #     dispatcher.utter_message(text=f'Chọn theo vùng bắt đầu từ {src_post} với kích thước {width}x{length}!')
        # else:
        #     dispatcher.utter_message(text='Xin vui lòng nêu cụ thể các thuộc tính của vùng bạn muốn chọn!')
        #     # return [Restarted()]

        # # last_action = tracker.get_slot('last_action')
        # # if last_action is not None: 
        # #     return [SlotSet('position_source', src_post),
        # #             SlotSet('position_destination', dst_post),
        # #             FollowupAction(last_action)]
        # return [SlotSet('position_source', src_post),
        #         SlotSet('position_destination', dst_post)]
        
        
        # flip 
                # return [
        # SlotSet("position_source", None),
        # SlotSet("position_source_x", None),
        # SlotSet("position_source_y", None),
        # SlotSet("position_destination", None),
        # SlotSet("position_destination_x", None),
        # SlotSet("position_destination_y", None),
        # SlotSet("object_shape", None),
        # SlotSet("object_color", None),
        # SlotSet("object_size", None),
        # SlotSet("object_height", None),
        # SlotSet("object_width", None),
        # SlotSet("object_length", None),
        # SlotSet("object_thickness", None),
        # SlotSet("object_destination", None),
        # SlotSet("object_orientation", None),
        # SlotSet("selected_area_source", None),
        # SlotSet("selected_area_destination", None),
        # SlotSet("selected_area_height", None),
        # SlotSet("selected_area_width", None),
        # SlotSet("selected_area_length", None),]
        
        # rotate
                # return [
        # SlotSet("position_source", None),
        # SlotSet("position_source_x", None),
        # SlotSet("position_source_y", None),
        # SlotSet("position_destination", None),
        # SlotSet("position_destination_x", None),
        # SlotSet("position_destination_y", None),
        # SlotSet("selected_area_source", None),
        # SlotSet("selected_area_destination", None),
        # SlotSet("selected_area_height", None),
        # SlotSet("selected_area_width", None),
        # SlotSet("selected_area_length", None),
        # SlotSet("object_shape", None),
        # SlotSet("object_color", None),
        # SlotSet("object_size", None),
        # SlotSet("object_length", None),
        # SlotSet("object_width", None),
        # SlotSet("object_height", None),
        # SlotSet("object_thickness", None),
        # SlotSet("object_orientation", None),
        # SlotSet("object_destination", None),
        # SlotSet("value_angle", None)]
        
                # return [SlotSet("position_source", None),
        # SlotSet("position_source_x", None),
        # SlotSet("position_source_y", None),
        # SlotSet("position_destination", None),
        # SlotSet("position_destination_x", None),
        # SlotSet("position_destination_y", None),
        # SlotSet("selected_area_source", None),
        # SlotSet("selected_area_destination", None),
        # SlotSet("selected_area_height", None),
        # SlotSet("selected_area_width", None),
        # SlotSet("selected_area_length", None),
        # SlotSet("object_shape", None),
        # SlotSet("object_color", None),
        # SlotSet("object_size", None),
        # SlotSet("object_length", None),
        # SlotSet("object_width", None),
        # SlotSet("object_height", None),
        # SlotSet("object_destination", None),
        # SlotSet("object_thickness", None),
        # SlotSet("object_orientation", None),
        # SlotSet("value_angle", None),]