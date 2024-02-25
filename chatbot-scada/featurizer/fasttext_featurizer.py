import numpy as np
import logging
from typing import Any, Optional, Text, Dict, List, Tuple, Type

from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.graph import ExecutionContext, GraphComponent
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.nlu.featurizers.dense_featurizer.dense_featurizer import DenseFeaturizer
from rasa.nlu.tokenizers.tokenizer import Tokenizer, Token
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.features import Features
from rasa.shared.nlu.training_data.message import Message

from huggingface_hub import hf_hub_download
import fasttext

from tqdm import tqdm

from rasa.nlu.constants import (
    DENSE_FEATURIZABLE_ATTRIBUTES,
    FEATURIZER_CLASS_ALIAS,
    TOKENS_NAMES,
    NUMBER_OF_SUB_TOKENS,
    NO_LENGTH_RESTRICTION,
    SEQUENCE_FEATURES,
    SENTENCE_FEATURES,

)

from rasa.shared.nlu.constants import (
    TEXT,
    TEXT_TOKENS,
    FEATURE_TYPE_SENTENCE,
    FEATURE_TYPE_SEQUENCE,
    ACTION_TEXT
)

logger = logging.getLogger(__name__)

@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_FEATURIZER, is_trainable=False
)
class FastTextFeaturizer(DenseFeaturizer, GraphComponent):
    @classmethod
    def required_components(cls) -> List[Type]:
        return [Tokenizer]

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        return {
            **DenseFeaturizer.get_default_config(),
            'config': "facebook/fasttext-vi-vectors",
            'max_len_restriction': False,
            'max_len': None,
            'dimension': 300,
        }
    
    def __init__(self, 
                 config: Dict[Text, Any],
                 name: Text, 
                 ) -> None:
        
        super().__init__(name, config)
        
        model_path = hf_hub_download(repo_id=self._config['config'], filename="model.bin")
        self.model = fasttext.load_model(model_path)

    # def train(self, training_data: TrainingData) -> Resource:
    #     pass

    @classmethod
    def create(cls, 
               config: Dict[Text, Any], 
               model_storage: ModelStorage, 
               resource: Resource, 
               execution_context: ExecutionContext) -> GraphComponent:
        return cls(config, execution_context.node_name)
        # return cls(config)
   
    # def _extract_sequence_lengths(
    #         self, batch_tokens: List[List[Token]]
    #     ) -> Tuple[List[int], int]:
    #     max_input_sequence_length = 0
    #     actual_sequence_lengths = []

    #     for example_token_ids in batch_tokens:
    #         sequence_length = len(example_token_ids)
    #         actual_sequence_lengths.append(sequence_length)
    #         max_input_sequence_length = max(
    #             max_input_sequence_length, len(example_token_ids)
    #         )

    #     # Take into account the maximum sequence length the model can handle
    #     max_input_sequence_length = (
    #         max_input_sequence_length
    #         if self.max_model_sequence_length == NO_LENGTH_RESTRICTION
    #         else min(max_input_sequence_length, self.max_model_sequence_length)
    #     )
        
    #     return actual_sequence_lengths, max_input_sequence_length
    
    # def _validate_sequence_lengths(
    #         self,
    #         actual_sequence_lengths: List[int],
    #         batch_examples: List[Message],
    #         attribute: Text,
    #         inference_mode: bool = False,
    # ) -> None:
    #     if self.max_model_sequence_length == NO_LENGTH_RESTRICTION:
    #         # There is no restriction on sequence length from the model
    #         return

    #     for sequence_length, example in zip(actual_sequence_lengths, batch_examples):
    #         if sequence_length > self.max_model_sequence_length:
    #             if not inference_mode:
    #                 raise RuntimeError(
    #                     f"The sequence length of '{example.get(attribute)[:20]}...' "
    #                     f"is too long({sequence_length} tokens) for the "
    #                     f"model chosen {self.model_name} which has a maximum "
    #                     f"sequence length of {self.max_model_sequence_length} tokens. "
    #                     f"Either shorten the message or use a model which has no "
    #                     f"restriction on input sequence length like XLNet."
    #                 )
    #             logger.debug(
    #                 f"The sequence length of '{example.get(attribute)[:20]}...' "
    #                 f"is too long({sequence_length} tokens) for the "
    #                 f"model chosen {self.model_name} which has a maximum "
    #                 f"sequence length of {self.max_model_sequence_length} tokens. "
    #                 f"Downstream model predictions may be affected because of this."
    #             )

    def _compute_sequence_embedding(
            self, message: Message, attribute: Text
        ) -> np.ndarray:
        
        tokens_in = message.get(TOKENS_NAMES[attribute])

        token_feature_list = []
        for token in tqdm(tokens_in):

            final_token = token.text.lower().replace(" ", "_")
            token_vector = self.model[final_token]
            token_feature_list.append(token_vector)
        token_feature = np.array(token_feature_list)
            
        return token_feature

    def _compute_batch_sequence_embeddings(
            self, batch_tokens: List[Message], attribute: Text
        ) -> List[np.ndarray]:

        token_feature_list = []
        for message in batch_tokens:
            token_feature = self._compute_sequence_embedding(message, attribute)
            token_feature_list.append(token_feature)

        return token_feature_list
    
    def _post_process_sequence_embeddings(
            self, 
            sequence_embedding: List[np.ndarray]
        ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        sentence_embeddings = []

        for example_embeddings in sequence_embedding:
            sentence_embedding  = np.mean(example_embeddings, axis=0)

            sentence_embeddings.append(sentence_embedding)

            # print(sentence_embedding.shape, example_embeddings.shape)
        
        return sentence_embeddings, sequence_embedding


    def _get_model_features_for_batch(
            self,
            batch_examples: List[Message],
            attribute: Text,
    ) -> Tuple[np.ndarray, np.ndarray]:


        token_feature_list = self._compute_batch_sequence_embeddings(
            batch_examples, attribute=attribute
        )

        # print(sequence_hidden_states.shape)

        # for nonpadded_embed in sequence_nonpadded_embeddings:
        #     print(nonpadded_embed.shape)
        
        (
            sentence_embeddings,
            sequence_embeddings,
        ) = self._post_process_sequence_embeddings(sequence_embedding=token_feature_list)

        sentence_embeddings = np.array(sentence_embeddings)
        try:
            final_embeddings = np.array(sequence_embeddings)
        except:
            final_embeddings = np.array(sequence_embeddings, dtype=object)    
        return sentence_embeddings, final_embeddings
    
    def _get_docs_for_batch(
            self,
            batch_examples: List[Message],
            attribute: Text,
            inference_mode: bool = False,
        ) -> List[Dict[Text, Any]]:

        (
            batch_sentence_features,
            batch_sequence_features,
        ) = self._get_model_features_for_batch(
            batch_examples, attribute
        )

        batch_docs = []
        for index in range(len(batch_examples)):
            doc = {
                SEQUENCE_FEATURES: batch_sequence_features[index],
                SENTENCE_FEATURES: np.reshape(batch_sentence_features[index], (1, -1)),
            }
            # print(doc[SEQUENCE_FEATURES].shape, doc[SENTENCE_FEATURES].shape)
            batch_docs.append(doc)

        return batch_docs
    
    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        batch_size = len(training_data.training_examples)

        for i, attribute in enumerate(DENSE_FEATURIZABLE_ATTRIBUTES):
            # print(i)
            non_empty_examples = list(
                filter(lambda x: x.get(attribute), training_data.training_examples)
            )

            batch_start_index = 0

            while batch_start_index < len(non_empty_examples):

                batch_end_index = min(
                    batch_start_index + batch_size, len(non_empty_examples)
                )
                # Collect batch examples
                batch_messages = non_empty_examples[batch_start_index:batch_end_index]

                # Construct a doc with relevant features
                # extracted(tokens, dense_features)
                batch_docs = self._get_docs_for_batch(batch_messages, attribute)

                for index, ex in enumerate(batch_messages):
                    self._set_lm_features(batch_docs[index], ex, attribute)
                batch_start_index += batch_size

            
            # Collect batch examples
            # batch_messages = non_empty_examples

            # Construct a doc with relevant features
            # extracted(tokens, dense_features)
            # batch_docs = self._get_docs_for_batch(batch_messages, attribute)

            # for index, ex in enumerate(batch_messages):
            #     self._set_lm_features(batch_docs[index], ex, attribute)
            

        return training_data
    
    def process(self, messages: List[Message]) -> List[Message]:
        """Processes messages by computing tokens and dense features."""
        for message in messages:
            self._process_message(message)
        return messages

    def _process_message(self, message: Message) -> Message:
        """Processes a message by computing tokens and dense features."""
        # processing featurizers operates only on TEXT and ACTION_TEXT attributes,
        # because all other attributes are labels which are featurized during
        # training and their features are stored by the model itself.
        for attribute in {TEXT, ACTION_TEXT}:
            if message.get(attribute):
                self._set_lm_features(
                    self._get_docs_for_batch(
                        [message], attribute=attribute, inference_mode=True
                    )[0],
                    message,
                    attribute,
                )
        return message

    def _set_lm_features(
        self, doc: Dict[Text, Any], message: Message, attribute: Text = TEXT
    ) -> None:
        """Adds the precomputed word vectors to the messages features."""
        sequence_features = doc[SEQUENCE_FEATURES]
        sentence_features = doc[SENTENCE_FEATURES]

        self.add_features_to_message(
            sequence=sequence_features,
            sentence=sentence_features,
            attribute=attribute,
            message=message,
        )
    @classmethod
    def validate_config(cls, config: Dict[Text, Any]) -> None:
        # if not config["config"]:
        #     raise ValueError("Phobert featurizer need config setting via `config`.")
        pass