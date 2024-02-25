from __future__ import annotations

import re
from typing import Any, Dict, List, Text

import json
from rasa.nlu.tokenizers.tokenizer import Token, Tokenizer
from rasa.shared.nlu.training_data.message import Message

from rasa.engine.recipes.default_recipe import DefaultV1Recipe


from rasa.nlu.constants import TOKENS_NAMES, MESSAGE_ATTRIBUTES
from rasa.engine.graph import ExecutionContext
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.constants import (
    INTENT,
    INTENT_RESPONSE_KEY,
    RESPONSE_IDENTIFIER_DELIMITER,
    ACTION_NAME
)

from underthesea import text_normalize, word_tokenize
import requests, json

@DefaultV1Recipe.register(
    component_types=[DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER],
    is_trainable=False
)

class MultiIntentHandler(Tokenizer):
    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        return {
            # This *must* be added due to the parent class.
            "intent_tokenization_flag": False,
            # This *must* be added due to the parent class.
            "intent_split_symbol": "+",
            # This is the spaCy language setting.
            "case_sensitive": False,
        }

    def __init__(self, 
                 config: Dict[Text, Any],
                 model_storage: ModelStorage,
                 resource: Resource) -> None:
        super().__init__(config)
    
    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> MultiIntentHandler:
        return cls(config, model_storage, resource)
    
    @classmethod
    def load(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
        **kwargs: Any,
    ) -> MultiIntentHandler:
        return cls(config, model_storage, resource)

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)
        payload = {"text": text}
        response = requests.post(url="http://192.168.16.5:9091/vncorenlp", json=payload)
        words = response.json()['tokens']
        return self._convert_words_to_tokens(words, text)
    
    # def infer_message(self, message: Message, attribute: Text) -> List[Token]:
    #     text = message.get(attribute)
    #     text = text_normalize(text)
    #     payload = {"text": text}
    #     response = requests.post(url="http://192.168.16.5:9091/vncorenlp", json=payload)
    #     words = response.json()['tokens']
    #     return self._convert_words_to_tokens(words, text)


    # def process_training_data(self, training_data: TrainingData) -> TrainingData:
    #     for example in training_data.training_examples:
    #         for attribute in MESSAGE_ATTRIBUTES:
    #             if example.get(attribute) is not None and not example.get(attribute) == "" :
    #                 if attribute in [INTENT, ACTION_NAME, INTENT_RESPONSE_KEY]:
    #                     tokens = self._split_name(example, attribute)
    #                 else:
    #                     tokens = self.tokenize(example, attribute)
                    
    #                 example.set(TOKENS_NAMES[attribute], tokens)

    #     return training_data
    
    # def process(self, messages: List[Message]) -> List[Message]:
    #     for message in messages:
    #         for attribute in MESSAGE_ATTRIBUTES:
    #             if isinstance(message.get(attribute), str):
    #                 if attribute in [
    #                     INTENT,
    #                     ACTION_NAME,
    #                     RESPONSE_IDENTIFIER_DELIMITER,
    #                 ]:
    #                     tokens = self._split_name(message, attribute)
    #                 else:
    #                     tokens = self.infer_message(message, attribute)
                    
    #                 message.set(TOKENS_NAMES[attribute], tokens)

    #     return messages