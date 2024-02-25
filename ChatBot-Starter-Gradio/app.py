import os
from threading import Thread
from typing import Iterator, List, Tuple, Dict

import gradio as gr
# import spaces
import utils
import re
import requests, json

URL = 'http://rasa-server:5005'
AUTH_TOKEN = 'nlplab-scada-chatbot'
LAST_MESSAGE_LIST = []

SUPPORT_FN = {
	"Rule-based": utils.sent_segment,
	"Bing": utils.bing_gpt_support_segment,
	"OpenAI": utils.openai_gpt_support_segment,
	"VBD-Llama2": utils.vbd_llama2_support_segment
}

def generate_gpt_support(
    message: str,
    chat_history: List[Tuple[str, str]],
    system_prompt: str,
    executor: str = 'Rule-based',
    max_new_tokens: int = 1024,
    temperature: float = 0.6,
    top_p: float = 0.9,
    top_k: int = 50,
) -> Iterator[str]:
	message_list = SUPPORT_FN[executor](message, system_prompt, max_new_tokens, temperature, top_p, top_k)
		# message_list = utils.openai_gpt_support_segment(message, system_prompt)
	message_list = [msg for msg in message_list if msg != '']
	global LAST_MESSAGE_LIST
	LAST_MESSAGE_LIST = message_list

	ans_list = []
	for message in message_list:
		new_message = message
		match = re.search(r"(\d+)\s*x\s*(\d+)", new_message) 
		if match is not None:
			group_1 = match.group(1)
			group_2 = match.group(2)
			replaced_substr = f'{group_1} x {group_2}'
			new_message = new_message.replace(match.group(), replaced_substr)
		new_message = utils.sent_purify(new_message)
		payload = {"message": str(new_message)}
		response = requests.post(url=f"{URL}/webhooks/rest/webhook?token={AUTH_TOKEN}", json=payload)
		ans_dict = response.json()
		ans_list = ans_list + ans_dict

	# print(ans_list)
	final_ans_list = []
	for ans in ans_list:
		# print("ans: ", ans)
		if 'text' in ans:
			final_ans_list.append(ans['text'])
		elif 'custom' in ans:
			final_ans_list.append(json.dumps(ans['custom'], ensure_ascii=False, indent=2))

	final_ans = "\n\n".join(final_ans_list)
	outputs = []
	inputs = list(final_ans)
	for text in inputs:
		outputs.append(text)
		yield "".join(outputs)
        
chat_interface_gpt_sp = gr.ChatInterface(
    fn=generate_gpt_support,
    additional_inputs=[
        gr.Textbox(label="Command Analysis Prompt", lines=15, value=utils.DEFAULT_PROMPT),
        # gr.JSON(label="Command Analysis Prompt", value=json.load(open('CHAT_HISTORY.json', 'r'))),
        # gr.Textbox(label="Command Analysis Prompt", lines=6),
        gr.Dropdown(
			choices=list(SUPPORT_FN.keys()),
			value='OpenAI',
			label="Excuter",
			max_choices=1,
			multiselect=False,
			info="Choose sentence analyzer",
		),
        gr.Slider(
            label="Temperature",
            minimum=0.1,
            maximum=2.0,
            step=0.1,
            value=0.1,
        ),        
        gr.Slider(
            label="Top-p (nucleus sampling)",
            minimum=0.05,
            maximum=1.0,
            step=0.05,
            value=0.9,
        ),        
        gr.Slider(
            label="Top-k",
            minimum=1,
            maximum=1000,
            step=1,
            value=50,
        ),
	],
    stop_btn="Stop",
    examples=[
        ["Xin chào!"],
        ["Vẽ hình chữ vuông có kích thước cạnh bằng 50 pixel ở vị trí chính giữa màn hình."],
        ["Vẽ hình mũi tên có chiều rộng và chiều cao lần lượt là 70 và 30 ở vị trí chính giữa."],
        ["Tạo bản sao của hình mũi tên ở góc bên trái."],
        ["Tạo hình bình hành màu xanh dương, có chiều dài đáy là 25 đơn vị, chiều cao là 35 đơn vị, nằm ở vị trí tương đối trên cùng bên phải."],
    ],
)

with gr.Blocks(css='style.css') as demo:
    
	with gr.Column(scale=5) as chat:
		chat_interface_gpt_sp.render()
		@gr.on(triggers=[chat_interface_gpt_sp.clear_btn.click])
		def restart_rasa():
			payload = {"message": "/restart"}
			response = requests.post(url=f"{URL}/webhooks/rest/webhook?token={AUTH_TOKEN}", json=payload)
  
	with gr.Column(scale=2, visible=False) as hidden_proc:
		with gr.Row(equal_height=False):	
			show_hid_proc = gr.Button("Show hidden process")

		with gr.Row(equal_height=False, visible=True) as show_more:
			split_interface = gr.JSON(value=[], visible=False)
			@gr.on(triggers=[show_hid_proc.click], 
				# inputs=chat_interface.textbox, 
				outputs=split_interface)
			def load_split() -> List[str]:
				return gr.JSON(value=LAST_MESSAGE_LIST, visible=True, label='Last message list')

		with gr.Row(equal_height=False, visible=True) as show_more:
			tracker_interface = gr.JSON(value={}, visible=False)
			@gr.on(triggers=[show_hid_proc.click],
				# inputs=chat_interface_gpt_sp.textbox, 
				outputs=tracker_interface)
			def load_tracker() -> Dict:
				respose = requests.get(url=f'{URL}/conversations/default/tracker?token={AUTH_TOKEN}')
				if respose.status_code // 100 != 2:
					return gr.JSON(value={}, visible=True)
				tracker = respose.json()
				if "latest_message" in tracker.keys():
					if "text_tokens" in tracker['latest_message'].keys(): del tracker['latest_message']['text_tokens']
					if "response_selector" in tracker.keys(): del tracker['response_selector']
				for event in tracker['events']:
					if "text_tokens" in event.keys(): del event['text_tokens']
				retain_event_types = ['followup', 'user', 'bot', 'action']
				retained_events = []
				events = sorted(tracker['events'], key=lambda x: x['timestamp'], reverse=True)
				for event in events:
					if event['event'] in retain_event_types:
						if "parse_data" in event.keys():
							if "text_tokens" in event['parse_data']: del event['parse_data']['text_tokens']
							if "response_selector" in event['parse_data']: del event['parse_data']['response_selector']
						retained_events.append(event)
				tracker['events'] = retained_events
				return gr.JSON(value=tracker, visible=True, label='Rasa tracker store')

# if __name__ == "__main__":
#     demo.queue(max_size=50, api_open=True).launch(
#         share=True, 
#         # auth=("nlplab", "abc123"), 
#         show_error=True,
#         show_api=True,
#         server_port=7860,
#         server_name='0.0.0.0',
#         debug=True
#         # share_server_address='0.0.0.0:7860'
#     )
    