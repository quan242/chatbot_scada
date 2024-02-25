import torch
from transformers import AutoModel, AutoTokenizer
import yaml
import requests

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Text

import torch.nn.functional as F

device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
model = AutoModel.from_pretrained("vinai/phobert-base-v2").to(device)

def raw_embedding_update(file_path: Text):
    f = open(file_path, "r")
    raw_nlu_data = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
    for intent in raw_nlu_data.keys():
        raw_intent_sent = raw_nlu_data[intent]
        raw_intent_sent_id_list = []
        for i in range(len(raw_intent_sent)):
            line = raw_intent_sent[i]
            payload = {"text": line}
            response = requests.post(url="http://192.168.16.5:9091/vncorenlp", json=payload)
            words = response.json()['tokens']
            words = [word.replace(" ", "_") for word in words]
            sent = " ".join(words)
            raw_intent_sent_id_list.append(tokenizer.encode(sent))
    
        raw_intent_sent_vector_list = []

        with torch.no_grad():
            for id in raw_intent_sent_id_list:
                inputs = torch.tensor([id])
                inputs = inputs.to(device)
                features = model(inputs)

                pooler_output = features[1]
                if device == "cuda":
                    pooler_output = pooler_output.cpu().detach().numpy()
                raw_intent_sent_vector_list.append(pooler_output)
            raw_intent_sent_vector_np = np.concatenate(raw_intent_sent_vector_list, axis=0)
            np.save(f"/workspace/nlplab/quannd/scada-full-stack/raw_nlu_embedding_by_intent/{intent}.npy", raw_intent_sent_vector_np)


def cosine_sim_check(sent_list: List[Text], intent: Text, upper_threshold, lower_threshold) -> Dict[Text, List[Text]]:
   
    raw_intent_sent_vector_list = np.load(f"/workspace/nlplab/quannd/scada-full-stack/raw_nlu_embedding_by_intent/{intent}.npy", mmap_mode="r")

    sent_id_list = []
    for tmp_line in sent_list:
        line = tmp_line
        payload = {"text": line}
        if line.startswith("<i> "):
            payload = {"text": line[4:]}

        response = requests.post(url="http://192.168.16.5:9091/vncorenlp", json=payload)
        words = response.json()['tokens']
        words = [word.replace(" ", "_") for word in words]
        sent = " ".join(words)
        sent_id_list.append(tokenizer.encode(sent))

    sent_vector_list = []

    with torch.no_grad():
        for id in sent_id_list:
            inputs = torch.tensor([id])
            inputs = inputs.to(device)
            features = model(inputs)

            pooler_output = features[1]
            if device == "cuda":
                pooler_output = pooler_output.cpu().detach().numpy()
            sent_vector_list.append(pooler_output)
        
        sent_vector_np = np.concatenate(sent_vector_list, axis=0)

        cos = cosine_similarity(sent_vector_np, raw_intent_sent_vector_list)

        print(cos)
        good_sentences_check = [False] *  len(cos)
        for i, sim_list in enumerate(cos):
            if  np.mean(sim_list) <= upper_threshold and np.mean(sim_list) >= lower_threshold:
                good_sentences_check[i] = True
    
        
        accepted_sent_list = []
        denied_sent_list = []
        for check, line in zip(good_sentences_check, sent_list):
            if check:
                accepted_sent_list.append(line)
            else:
                denied_sent_list.append(line)
        
        return {"accepted": accepted_sent_list,
                "denied": denied_sent_list}
    

intent = "draw_parallelogram"
sent_list = []
f = open(f"/workspace/nlplab/quannd/scada-full-stack/raw_data_by_intent/{intent}.txt", "r")
for line in f.readlines():
    sent_list.append(line.rstrip(" \n"))
f.close()

upper_threshold = 0.9
lower_threshold = 0.65
print(cosine_sim_check(sent_list, intent, upper_threshold, lower_threshold))