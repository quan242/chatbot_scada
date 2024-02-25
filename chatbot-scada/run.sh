# train and test NLU model with config-fasttext (best config until now)
# rasa train nlu --config="/workspace/nlplab/quannd/scada-full-stack/chatbot-scada/config_fasttext.yml" --out="/workspace/nlplab/quannd/scada-full-stack/chatbot-scada/models/NLU" --nlu="/workspace/nlplab/quannd/scada-full-stack/chatbot-scada/train_test_split/training_data.yml"

# train fulll
TF_GPU_MEMORY_ALLOC="0:3000" rasa train --config="/workspace/nlplab/quannd/scada-full-stack/chatbot-scada/config_bert.yml" --out="/workspace/nlplab/quannd/scada-full-stack/chatbot-scada/models/NLU_NLG/vncorenlp/phobert/quannd/add_last_memory"

TF_GPU_MEMORY_ALLOC="0:3000" rasa train --config="/workspace/nlplab/quannd/scada-full-stack/chatbot-scada/config_bert_1.yml" --out="/workspace/nlplab/quannd/scada-full-stack/chatbot-scada/models/NLU_NLG/vncorenlp/phobert/quannd/add_relative_for_bert_config"

# TF_GPU_MEMORY_ALLOC="0:3000" rasa train --config="/workspace/nlplab/quannd/scada-full-stack/chatbot-scada/config_bert.yml" --out="/workspace/nlplab/quannd/scada-full-stack/chatbot-scada/models/NLU_NLG/vncorenlp/phobert/quannd/add_last_memory"

# TF_GPU_MEMORY_ALLOC="0:3000" rasa train --config="/workspace/nlplab/quannd/scada-full-stack/chatbot-scada/config_bert.yml" --out="/workspace/nlplab/quannd/scada-full-stack/chatbot-scada/models/NLU_NLG/vncorenlp/phobert/quannd/add_last_memory"