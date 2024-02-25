# from tensorflow.python.client import device_lib
# print(device_lib.list_local_devices())

# import tensorflow as tf
# print(tf.config.list_physical_devices())
# from rasa.core.agent import Agent
# import asyncio
# agent = Agent.load(model_path="/workspace/nlplab/quannd/scada-full-stack/chatbot-scada/models/20230926-153722-isobaric-alley.tar.gz")
# text = 'Chào bạn'
# response = asyncio.run(agent.parse_message(message_data=text))
# print(response)

# from tensorflow.python.client import device_lib
# print(device_lib.list_local_devices())

import tensorflow as tf
print(tf.__version__)
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

import subprocess

subprocess.run()