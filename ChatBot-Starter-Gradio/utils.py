import re, json, os

from g4f.Provider import BingCreateImages, OpenaiChat, Gemini, Bing, Liaobots
import g4f
import openai
from typing import List

def sent_purify(text):
   standard_character_regex = "a-zA-Z0-9ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ\s|_!\.\?:,;\(\)"
   text = text.strip()
   text = re.sub(f"[^{standard_character_regex}]+"," ", text)
   text = re.sub("\s+", " ", text)
   text = text.strip()
   return text

linking_word_file = open("/workspace/nlplab/quannd/scada-full-stack/ChatBot-Starter-Gradio/Vietnamese_linking_words.txt", "r")
linking_word_list = linking_word_file.read().split("\n")
linking_word_list = [word.lower() for word in linking_word_list]
linking_word_file.close()

prefix_linking_word_file = open("/workspace/nlplab/quannd/scada-full-stack/ChatBot-Starter-Gradio/Vietnamese_prefix_linking_words.txt", "r")
prefix_linking_word_list = prefix_linking_word_file.read().split("\n")
prefix_linking_word_list = [word.lower() for word in prefix_linking_word_list]
prefix_linking_word_file.close()

add_on_linking_word_list = ["và", "cùng với"]
def check_comma_segment(clause):
    word_list = linking_word_list + add_on_linking_word_list
    for linking_word in word_list:
        if clause.startswith(linking_word):
            return True
    return False

def sent_segment(	paragraph, 
					prompt:str=None, 
					max_new_tokens:int=1024, 
					temperature:float=0.1, 
					top_p:float=0.9, 
					top_k:int=50	) -> List[str]:
  """segmented by end_of_sentence punctuation"""
  sentence_punctuation_list = ".?!:,;"
  end_of_sentence_punctuation_list = ".?!:;"
  only_punc_sent_regex= f'^[{sentence_punctuation_list}\s]*$'
  paragraph = paragraph.strip(sentence_punctuation_list)
  split_regex = f'[{end_of_sentence_punctuation_list}]+'
  list_of_sentences = re.split(split_regex, paragraph)
  
  print("list_of_sentences after eos punctuation: ", list_of_sentences)

  """segmented by subsentence punctuation, followed by linking words"""
  new_list_of_sent = []
  for sent in list_of_sentences:
    sent = sent.strip(" ")
    sent = sent.strip(sentence_punctuation_list)
    if not re.match(only_punc_sent_regex, sent):
      sent_segment_index_list = [0]
      for i, char in enumerate(sent):
        if char == "," and check_comma_segment(sent[i:].strip(", ")):
          sent_segment_index_list.append(i)
      if len(sent_segment_index_list) > 1:
        for j in range(len(sent_segment_index_list) - 1):
          tmp_sent = sent[sent_segment_index_list[j]: sent_segment_index_list[j+1]].strip(" ")
          if tmp_sent != "":
            new_list_of_sent.append(tmp_sent)
        if sent[sent_segment_index_list[-1]:].strip(" ") != "":
          new_list_of_sent.append(sent[sent_segment_index_list[-1]:].strip(";").strip(" "))
      else:
        new_list_of_sent.append(sent)

    new_list_of_sent = [sent for sent in new_list_of_sent if not re.match(only_punc_sent_regex, sent)]
    if new_list_of_sent != []:
      list_of_sentences = new_list_of_sent
      new_list_of_sent = []
    
    print("list_of_sentences after subsentence punctuation: ", list_of_sentences)

    """segmented just by linking word"""
    linking_word_pattern = "|".join([re.escape(word) for word in linking_word_list])
    for sent in list_of_sentences:
      sent_list = re.split(linking_word_pattern, sent)
      new_list_of_sent = new_list_of_sent + sent_list
    
    new_list_of_sent = [sent for sent in new_list_of_sent if not re.match(only_punc_sent_regex, sent)]
    if new_list_of_sent != []:
      list_of_sentences = new_list_of_sent
      new_list_of_sent = []

    print("list_of_sentences after linking words: ", list_of_sentences)

    """segmented by prefix linking word"""
    for sent in list_of_sentences:
      check = ""
      for prefix_linking_word in prefix_linking_word_list:
        if sent.startswith(prefix_linking_word):
          check = prefix_linking_word
          break
      if check != "":
        sent_list = re.split("[,;]+", maxsplit=1)
        new_list_of_sent = new_list_of_sent + sent_list
    
    new_list_of_sent = [sent for sent in new_list_of_sent if not re.match(only_punc_sent_regex, sent)]
    if new_list_of_sent != []:
      list_of_sentences = new_list_of_sent
      new_list_of_sent = []
    print("list_of_sentences after prefix linking words: ", list_of_sentences)

  return list_of_sentences

DEFAULT_PROMPT = open('PROMPT', 'r').read()
	# f"""USER: Trong vai trợ lý phân tích ý định, hãy phân tích và chia nhỏ đoạn lệnh thành các câu lệnh đơn (nếu có) để phần mềm có thể thực hiện tuần tự: "Hãy vẽ hình vuông có kích thước cạnh bằng 50 pixel ở vị trí chính giữa màn hình rồi nghiêng nó sang phải khoảng 15 độ.".""" \
	# f"""Bạn có thể tham khảo các ví dụ dưới đây để có thể tách được câu được yêu cầu:""" \
	# f"""\n- Đầu vào: "vẽ hình tròn màu đen ở vị trí (20, 40) rồi tô màu đen cho nó". => Đầu ra: ["vẽ hình tròn màu đen ở vị trí (20, 40)", "tô màu đen cho hình tròn ở vị trí (20, 40)"]""" \
	# f"""\n- Đầu vào : "vẽ hình vuông và hình tròn với cùng kích thước 40 x 40 tại 2 vị trí là (24,14) và góc trên bên trái màn hình" => Đầu ra: ["vẽ hình vuông có kích thước 40 x 40 tại vị trí (24, 14)", "Vẽ hình tròn có kích thước 40 x 40 tại vị trí góc trên bên trái màn hình"].""" \
	# f"""\n- Đầu vào: "xoay hình vuông có cạnh dài 50 pixel sang phải 15 độ rồi tô màu đen cho nó  => Đầu ra: ["xoay hình vuông có cạnh dài 50 pixel sang phải 15 độ", "tô màu đen cho hình vuông có cạnh dài 50 pixel"].""" \
	# f"""\nChú ý: bạn chỉ cần đưa ra kết quả có bố cục tương tự đầu ra trong các ví dụ trên, không cần đưa ra thông tin nào khác. Đồng thời hãy để ý đến các quan hệ từ và xác định vai trò của chúng trong việc tách câu. """ \
	# f"""\nASSISTANT:""" \
	# f"""\n- Vẽ hình vuông có kích thước cạnh bằng 50 pixel ở vị trí chính giữa màn hình.""" \
	# f"""\n- Nghiêng hình vuông sang phải khoảng 15 độ.""" \
	# f"""\nUSER: Vẽ hình mũi tên có chiều rộng và chiều cao lần lượt là 70 và 30 ở chính giữa sau đó tạo bản sao của nó ở góc bên trái. """ \
	# f"""\nASSISTANT:""" \
 	# f"""\n- Vẽ hình mũi tên có chiều rộng và chiều cao lần lượt là 70 và 30 ở vị trí chính giữa""" \
	# f"""\n- Sao chép""" \
	# f"""\n- Dán vào góc bên trái""" \
	# f"""\nUSER: Tạo hình bình hành màu xanh dương , có chiều dài đáy là 25 đơn vị , chiều cao là 35 đơn vị , nằm ở vị trí tương đối trên cùng bên phải . """ \
	# f"""\nASSISTANT:""" \
	# f"""\n- Tạo hình bình hành màu xanh dương có chiều dài đáy là 25 đơn vị và chiều cao là 35 đơn vị , nằm ở vị trí tương đối trên cùng bên phải .""" \
	# [
    #     {
	# 	"role": "user",
	# 	"content": 
	# 			'Trong vai trợ lý phân tích ý định, hãy phân tích và chia nhỏ đoạn lệnh thành các câu lệnh đơn (nếu có) để phần mềm có thể thực hiện độc lập. \n' \
	# 			'Ví dụ: Đầu vào: \"vẽ hình chữ nhật màu xanh có chiều dài 70 và chiều rộng 40, đặt góc bên trái sau đó di chuyển nó lên góc bên trên\" \n' \
	# 			'+ Vẽ hình chữ nhật màu xanh có chiều dài 70 và chiều rộng 40, đặt góc bên trái \n' \
	# 			'+ Di chuyển hình chữ nhật màu xanh có chiều dài 70 và chiều rộng 40, đặt ở góc bên trái lên góc bên trên \n' \
	# 			'Tuân thủ cách viết trên hãy áp dụng để phân tích câu: \"Hãy vẽ hình vuông có kích thước cạnh bằng 50 pixel ở vị trí chính giữa màn hình rồi nghiêng nó sang phải khoảng 15 độ.\"'
	# 	},
	# 	{
	# 	"role": "assistant",
	# 	"content": 
	# 			'- Vẽ hình vuông có kích thước cạnh bằng 50 pixel ở vị trí chính giữa màn hình. \n' \
	# 			'- Nghiêng hình vuông sang phải khoảng 15 độ.'
	# 	},
	# 	{
	# 	"role": "user",
	# 	"content": f'\"Vẽ hình mũi tên có chiều rộng và chiều cao lần lượt là 70 và 30 ở chính giữa sau đó tạo bản sao của nó ở góc bên trái\"\n'
	# 	},
	# 	{
	# 	"role": "assistant",
	# 	"content": 
	# 			'- Vẽ hình mũi tên có chiều rộng và chiều cao lần lượt là 70 và 30 ở vị trí chính giữa \n' \
	# 			'- Sao chép \n' \
	# 			'- Dán ở góc bên trái'
	# 	},                
	# 	{
	# 	"role": "user",
	# 	"content": f'\"Tạo hình bình hành màu xanh dương , có chiều dài đáy là 25 đơn vị , chiều cao là 35 đơn vị , nằm ở vị trí tương đối trên cùng bên phải .\"\n'
	# 	},
	# 	{
	# 	"role": "assistant",
	# 	"content":  \
	# 			'- Tạo hình bình hành màu xanh dương , có chiều dài đáy là 25 đơn vị , chiều cao là 35 đơn vị , nằm ở vị trí tương đối trên cùng bên phải .'
	# 	}
   	# ]

def bing_gpt_support_segment(	paragraph, 
								prompt:str=None, 
								max_new_tokens:int=1024, 
								temperature:float=0.1, 
								top_p:float=0.9, 
								top_k:int=50	) -> List[str]:
    
	# response = await g4f.ChatCompletion.create_async(
    sys_prompt = DEFAULT_PROMPT
    if prompt is not None and prompt != sys_prompt:
        sys_prompt = prompt
        # f = open("PROMPT", "w")
        # f.write(sys_prompt)
        # f.close()
        
    # sys_prompt += \
    # f"""USER: {paragraph}""" \
	# f"""ASSISTANT:"""
    # print(sys_prompt)
    
    response = g4f.ChatCompletion.create(
		model="gpt-4",
		messages=[
      		{
				"role": "system",
				"content": sys_prompt
			},
			{
				"role": "user",
				"content": paragraph
			}	
        ],
		# provider=Liaobots,
		provider=Bing,
		max_tokens=max_new_tokens,
		tone='Precise',
		top_p=top_p,
		temperature=temperature
		# stream=True,
	)
    
    result = ''
    for token in response:
        result += str(token)
    sent_list = result.strip().split('\n')
    sent_list = [sent.strip("- ") for sent in sent_list]
    return sent_list

def openai_gpt_support_segment(	paragraph, 
								prompt:str=None, 
								max_new_tokens:int=1024, 
								temperature:float=0.1, 
								top_p:float=0.9, 
								top_k:int=50	) -> List[str]:
    
    API_KEY = os.getenv('API_KEY', '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')
    
    client = openai.OpenAI(
		api_key=API_KEY
	)
    
    sys_prompt = DEFAULT_PROMPT
    if prompt is not None and prompt != sys_prompt:
        sys_prompt = prompt
        # f = open("PROMPT", "w")
        # f.write(sys_prompt)
        # f.close()
        
    # sys_prompt += \
    # f"""USER: {paragraph}""" \
	# f"""ASSISTANT:"""
    # print(sys_prompt)
    
    response = client.chat.completions.create(
		model="gpt-3.5-turbo",
		messages=[
      		{
				"role": "system",
				"content": sys_prompt
			},
			{
				"role": "user",
				"content": paragraph
			}	
        ],
		n=1,
		temperature=temperature,
		max_tokens=max_new_tokens,
		top_p=top_p,
		frequency_penalty=0,
		presence_penalty=0
	)
    
    result = response.choices[0].message.content
    # print(result)
    
    sent_list = result.strip().split('\n')
    sent_list = [sent.lstrip("- ") for sent in sent_list]
    return sent_list
    
    
def vbd_llama2_support_segment(paragraph, 
								prompt:str=None, 
								max_new_tokens:int=1024, 
								temperature:float=0.1, 
								top_p:float=0.9, 
								top_k:int=50) -> List[str]:
    
    from gradio_client import Client
    client = Client("http://nmtuet.ddns.net:9104/chat/")
    
    sys_prompt = DEFAULT_PROMPT
    if prompt is not None and prompt != sys_prompt:
        sys_prompt = prompt
        # f = open("PROMPT", "w")
        # f.write(sys_prompt)
        # f.close()
        
    # sys_prompt += \
    # f"""USER: {paragraph}""" \
	# f"""ASSISTANT:"""
    # print(sys_prompt)
    
    sys_prompt = "\n".join(sys_prompt.split("\n")[1:])
    sys_prompt = "SYSTEM: A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions based on previous responses of assistant." \
            "\nAs the intent analysis assistant, analyze and break down the script into single statements (if any) so that the software can execute sequentially. " \
            "Note: you only need to provide results with a similar layout to the output in the below examples, no other information is needed. " \
            "At the same time, pay attention to linking words and determine their role in separating sentences. You can refer to the examples below to be able to separate the required sentence:\n"   \
            + sys_prompt
    
    result = client.predict(
			paragraph,	# str  in 'Message' Textbox component
			sys_prompt,	# str  in 'Command Analysis Prompt' Textbox component
			max_new_tokens,	# int in 'Max new tokens' Slider component
			temperature,	# float (numeric value between 0.1 and 2.0) in 'Temperature' Slider component
			top_p, 	# float (numeric value between 0.1 and 2.0) in 'Top-p (nucleus sampling)' Slider component
			top_k,		# int in 'Top-k' Slider component
			1.2,	# float (numeric value between 0.1 and 2.0) in 'Repetition penalty' Slider component
			api_name="/chat"
	)
    
    sent_list = result.strip().split('\n')
    sent_list = [sent.lstrip("- ") for sent in sent_list]
    return sent_list