
#============================================segmented and normalized by underthesea=================================================
# from __future__ import annotations

# import re
# from typing import Any, Dict, List, Text, Type
# import json
# from rasa.nlu.tokenizers.tokenizer import Token, Tokenizer
# from rasa.shared.nlu.training_data.message import Message

# from rasa.engine.recipes.default_recipe import DefaultV1Recipe


# from rasa.nlu.constants import TOKENS_NAMES, MESSAGE_ATTRIBUTES
# from rasa.engine.graph import ExecutionContext
# from rasa.engine.storage.resource import Resource
# from rasa.engine.storage.storage import ModelStorage

# from underthesea import word_tokenize

# @DefaultV1Recipe.register(
#     component_types=[DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER],
#     is_trainable=False
# )


# class VietnameseTokenizer(Tokenizer):

#     # provides = [TOKENS_NAMES[attribute] for attribute in MESSAGE_ATTRIBUTES]
#     # @classmethod
#     # def required_components(cls) -> List[Type]:
#     #     """Components that should be included in the pipeline before this component."""
#     #     return []
    
#     # @classmethod
#     # def create(
#     #     cls,
#     #     config: Dict[Text, Any],
#     #     model_storage: ModelStorage,
#     #     resource: Resource,
#     #     execution_context: ExecutionContext,
#     # ) -> VietnameseTokenizer:
#     #     return cls.create(config, model_storage, resource, execution_context)
    
#     # @classmethod
#     # def load(
#     #     cls,
#     #     config: Dict[Text, Any],
#     #     model_storage: ModelStorage,
#     #     resource: Resource,
#     #     execution_context: ExecutionContext,
#     #     **kwargs: Any,
#     # ) -> VietnameseTokenizer:
#     #     try:
#     #         with model_storage.read_from(resource) as directory_path:
#     #             with open(directory_path / "artifact.json", "r") as file:
#     #                 training_artifact = json.load(file)
#     #                 return cls(
#     #                     model_storage, resource, training_artifact=training_artifact
#     #                 )
#     #     except ValueError:
#     #         return cls.create(config, model_storage, resource, execution_context)
        

#     @staticmethod
#     def get_default_config() -> Dict[Text, Any]:
#         return {
#             # This *must* be added due to the parent class.
#             "intent_tokenization_flag": False,
#             # This *must* be added due to the parent class.
#             "intent_split_symbol": ".",
#             # This is the spaCy language setting.
#             "case_sensitive": False,
#         }

#     def __init__(self, component_config: Dict[Text, Any]) -> None:
#         # config = {**self.get_default_config(), **config}
#         super().__init__(component_config)
#         # self.case_sensitive = config["case_sensitive"]
    
#     @classmethod
#     def create(
#         cls,
#         config: Dict[Text, Any],
#         model_storage: ModelStorage,
#         resource: Resource,
#         execution_context: ExecutionContext,
#     ) -> VietnameseTokenizer:
#         return cls(config)

#     def tokenize(self, message: Message, attribute: Text) -> List[Token]:
#         text = message.get(attribute)
#         words = word_tokenize(text)
#         return self._convert_words_to_tokens(words, text)




#========================================segmented by vncorenlp, normalized by underthesea===========================================
from __future__ import annotations

import re
from typing import Any, Dict, List, Text, Type
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


class VietnameseTokenizer(Tokenizer):
    
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
    ) -> VietnameseTokenizer:
        return cls(config, model_storage, resource)
    
    @classmethod
    def load(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
        **kwargs: Any,
    ) -> VietnameseTokenizer:
        return cls(config, model_storage, resource)

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)
        payload = {"text": text}
        response = requests.post(url="http://192.168.16.5:9091/vncorenlp", json=payload)
        words = response.json()['tokens']
        return self._convert_words_to_tokens(words, text)
    
    # def infer_message(self, message: Message, attribute: Text) -> List[Token]:
    #     text = message.get(attribute)
    #     match = re.search(r"(\d+)x(\d+)", text)
    #     if match:
    #         group_1 = match.group(1)
    #         group_2 = match.group(2)
    #         replaced_substr = f'{group_1} x {group_2}'
    #         text = text.replace(match.group(), replaced_substr)
    #     payload = {"text": text}
    #     response = requests.post(url="http://192.168.16.5:9091/vncorenlp", json=payload)
    #     words = response.json()['tokens']
    #     return self._convert_words_to_tokens(words, text)
    
    # def process(self, messages: List[Message]) -> List[Message]:
    #     """Tokenize the incoming messages."""
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