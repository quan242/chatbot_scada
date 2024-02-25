#============================segmented by vncorenlp, normalized by underthesea============================\
#(can only be used in NLU training & testing and full training, still cannot be used in full inference)
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

from underthesea import text_normalize
import py_vncorenlp
import vietokenizer

@DefaultV1Recipe.register(
    component_types=[DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER],
    is_trainable=False
)


class NewVietnameseTokenizer(Tokenizer):

    # provides = [TOKENS_NAMES[attribute] for attribute in MESSAGE_ATTRIBUTES]
    # @classmethod
    # def required_components(cls) -> List[Type]:
    #     """Components that should be included in the pipeline before this component."""
    #     return []
    
    # @classmethod
    # def create(
    #     cls,
    #     config: Dict[Text, Any],
    #     model_storage: ModelStorage,
    #     resource: Resource,
    #     execution_context: ExecutionContext,
    # ) -> NewVietnameseTokenizer:
    #     return cls.create(config, model_storage, resource, execution_context)
    
    # @classmethod
    # def load(
    #     cls,
    #     config: Dict[Text, Any],
    #     model_storage: ModelStorage,
    #     resource: Resource,
    #     execution_context: ExecutionContext,
    #     **kwargs: Any,
    # ) -> NewVietnameseTokenizer:
    #     try:
    #         with model_storage.read_from(resource) as directory_path:
    #             with open(directory_path / "artifact.json", "r") as file:
    #                 training_artifact = json.load(file)
    #                 return cls(
    #                     model_storage, resource, training_artifact=training_artifact
    #                 )
    #     except ValueError:
    #         return cls.create(config, model_storage, resource, execution_context)
        

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        return {
            # This *must* be added due to the parent class.
            "intent_tokenization_flag": False,
            # This *must* be added due to the parent class.
            "intent_split_symbol": ".",
            # This is the spaCy language setting.
            "case_sensitive": False,
        }

    def __init__(self, 
                 config: Dict[Text, Any],
                 model_storage: ModelStorage,
                 resource: Resource) -> None:
        super().__init__(config)
        self._model_storage = model_storage
        self._resource = resource
        self.segmenter = vietokenizer.vntokenizer()
    
    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
        **kwargs: Any,
    ) -> NewVietnameseTokenizer:
        # cls._load_segmenter()
        # cls.segmenter = py_vncorenlp.VnCoreNLP(save_dir="/workspace/nlplab/quannd/vncorenlp")
        return cls(config, model_storage, resource)
    
    @classmethod
    def load(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
        **kwargs: Any,
    )-> NewVietnameseTokenizer:
        return cls(config, model_storage, resource)

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)
        normalized_text = text_normalize(text)
        words = self.segmenter(normalized_text)
        words = [word.replace("_", " ") for word in words.split(" ")]
        words = [text_normalize(word) for word in words]

        return self._convert_words_to_tokens(words, text)
    
    # @staticmethod
    # def _load_segmenter(cls):
    #     cls.segmeter = py_vncorenlp.VnCoreNLP(save_dir="/workspace/nlplab/quannd/vncorenlp")