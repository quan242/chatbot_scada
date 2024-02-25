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

import torch
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer

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
class PhobertFeaturizer(DenseFeaturizer, GraphComponent):
    @classmethod
    def required_components(cls) -> List[Type]:
        return [Tokenizer]

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        return {
            **DenseFeaturizer.get_default_config(),
            'config': 'vinai/phobert-base-v2',
            'max_len_restriction': False,
            'max_len': None
        }
    
    def __init__(self, 
                 config: Dict[Text, Any],
                 name: Text, 
                 ) -> None:
        
        super().__init__(name, config)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(self._config['config'], cache_dir="./phobert_cache")
        self.model = AutoModel.from_pretrained(self._config['config'], cache_dir="./phobert_cache").to(self.device)
        self.max_model_sequence_length = 512
        # if type(self._config) == dict and 'config' in self._config:
        #     self.tokenizer = AutoTokenizer.from_pretrained(self._config['config'])
        #     self.model = AutoModel.from_pretrained(self._config['config']).to(self.device)
        # elif type(name) == dict and 'config' in name:
        #     self.tokenizer = AutoTokenizer.from_pretrained(name['config'])
        #     self.model = AutoModel.from_pretrained(name['config']).to(self.device)
        # else:
        #     self.tokenizer = AutoTokenizer.from_pretrained('vinai/phobert-base-v2')
        #     self.model = AutoModel.from_pretrained('vinai/phobert-base-v2').to(self.device)

        # self._model_storage = model_storage
        # self._resource = resource
        # self.tokenizer = AutoTokenizer.from_pretrained('vinai/phobert-base-v2')
        # self.model = AutoModel.from_pretrained('vinai/phobert-base-v2').to(self.device)

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
   
    def _lm_tokenize(self, text: Text) -> Tuple[List[int], List[Text]]:
        split_token_ids = self.tokenizer.encode(text, add_special_tokens=False)

        split_token_string = self.tokenizer.convert_ids_to_tokens(split_token_ids)

        return split_token_ids, split_token_string
    
    def _add_lm_specific_special_tokens(
            self, token_ids: List[List[int]]
    ) -> List[List[int]]:
        bos_token_id = self.tokenizer.bos_token_id
        eos_token_id = self.tokenizer.eos_token_id
        augmented_token_ids = [
            [bos_token_id] + example_token_ids + [eos_token_id] for example_token_ids in token_ids
        ]
        # print(augmented_token_ids[3])
        return augmented_token_ids
    
    def _lm_specific_token_cleanup(
            self, token_ids_string: List[Tuple[int, Text]], delimiter: Text        
    ) -> Tuple[List[int], List[Text]]:
        token_ids_string = [
            (id, string.replace(delimiter, "")) for id, string in token_ids_string
        ]  

        token_ids_string =[(id, string) for id, string in token_ids_string if string]

        token_ids, token_strings = zip(*token_ids_string)

        return token_ids, token_strings
    
    def _tokenize_example(
            self, message: Message, attribute: Text
    )-> Tuple[List[Token], List[int]]:
        
        tokens_in = message.get(TOKENS_NAMES[attribute])
        tokens_out = []
        token_ids_out = []

        for token in tokens_in:

            split_token_ids, split_token_strings = self._lm_tokenize(token.text)

            if not split_token_ids:
                continue

            token_ids_string = list(zip(split_token_ids, split_token_strings))
            split_token_ids, split_token_strings = self._lm_specific_token_cleanup(token_ids_string, "@@")

            token_ids_out += split_token_ids
            token.set(NUMBER_OF_SUB_TOKENS, len(split_token_strings))

            tokens_out.append(token)
        
        return tokens_out, token_ids_out
    
    def _get_token_ids_for_batch(
            self, batch_examples: List[Message], attribute: Text
    )-> Tuple[List[List[Token]], List[List[int]]]:
        batch_token_ids = []
        batch_tokens = []
        for example in batch_examples:

            example_tokens, example_token_ids = self._tokenize_example(
                example, attribute
            )
            batch_tokens.append(example_tokens)
            batch_token_ids.append(example_token_ids)

        return batch_tokens, batch_token_ids

    @staticmethod
    def _compute_attention_mask(
            actual_sequence_lengths: List[int], max_input_sequence_length: int
    ) -> List[List[int]]:
        attention_mask = []

        for actual_sequence_length in actual_sequence_lengths:
            # add 1s for present tokens, fill up the remaining space up to max
            # sequence length with 0s (non-existing tokens)
            padded_sequence = [1] * min(
                actual_sequence_length, max_input_sequence_length
            ) + [0] * (
                max_input_sequence_length
                - min(actual_sequence_length, max_input_sequence_length)
            )
            attention_mask.append(padded_sequence)

        return attention_mask

    def _extract_sequence_lengths(
            self, batch_token_ids: List[List[int]]
        ) -> Tuple[List[int], int]:
        max_input_sequence_length = 0
        actual_sequence_lengths = []

        for example_token_ids in batch_token_ids:
            sequence_length = len(example_token_ids)
            actual_sequence_lengths.append(sequence_length)
            max_input_sequence_length = max(
                max_input_sequence_length, len(example_token_ids)
            )

        # Take into account the maximum sequence length the model can handle
        max_input_sequence_length = (
            max_input_sequence_length
            if self.max_model_sequence_length == NO_LENGTH_RESTRICTION
            else min(max_input_sequence_length, self.max_model_sequence_length)
        )
        
        return actual_sequence_lengths, max_input_sequence_length
    
    def _add_padding_to_batch(
            self, batch_token_ids: List[List[int]], max_sequence_length_model: int  
    ) -> List[List[int]]:
        padded_token_ids = []

        for example_token_ids in batch_token_ids:
            if len(example_token_ids) > max_sequence_length_model:
                example_token_ids = example_token_ids[:max_sequence_length_model]

            padded_token_ids.append(
                example_token_ids
                + [self.tokenizer.pad_token_id] * (max_sequence_length_model - len(example_token_ids))
            )

        return padded_token_ids
    
    def _validate_sequence_lengths(
            self,
            actual_sequence_lengths: List[int],
            batch_examples: List[Message],
            attribute: Text,
            inference_mode: bool = False,
    ) -> None:
        if self.max_model_sequence_length == NO_LENGTH_RESTRICTION:
            # There is no restriction on sequence length from the model
            return

        for sequence_length, example in zip(actual_sequence_lengths, batch_examples):
            if sequence_length > self.max_model_sequence_length:
                if not inference_mode:
                    raise RuntimeError(
                        f"The sequence length of '{example.get(attribute)[:20]}...' "
                        f"is too long({sequence_length} tokens) for the "
                        f"model chosen {self.model_name} which has a maximum "
                        f"sequence length of {self.max_model_sequence_length} tokens. "
                        f"Either shorten the message or use a model which has no "
                        f"restriction on input sequence length like XLNet."
                    )
                logger.debug(
                    f"The sequence length of '{example.get(attribute)[:20]}...' "
                    f"is too long({sequence_length} tokens) for the "
                    f"model chosen {self.model_name} which has a maximum "
                    f"sequence length of {self.max_model_sequence_length} tokens. "
                    f"Downstream model predictions may be affected because of this."
                )

    def _compute_batch_sequence_features(
            self, batch_attention_mask: List[List[int]], padded_token_ids: List[List[int]]
        ) -> np.ndarray:
        batch_size = 32
        inputs = torch.tensor(padded_token_ids)
        attn_masks = torch.tensor(batch_attention_mask)
        
        data = TensorDataset(inputs, attn_masks)
        sampler = SequentialSampler(data)
        dataloader = DataLoader(data, sampler=sampler, batch_size=batch_size)

        out_features = []
        with torch.no_grad():
            for i, batch in enumerate(tqdm(dataloader)):
                inputs, attn_masks = batch
                inputs = inputs.to(self.device)
                attn_masks = attn_masks.to(self.device)
                features = self.model(inputs, attn_masks)

                hidden_states = features[0]
                if self.device == "cuda":
                    hidden_states = hidden_states.cpu()

                out_features.append(hidden_states)

        out_features = torch.cat(out_features, dim=0).numpy()
        return out_features
    
    def _extract_nonpadded_embeddings(
            self, embeddings: np.ndarray, actual_sequence_lengths: List[int]
    ) -> List[np.ndarray]:
        
        nonpadded_sequence_embeddings = []
        for index, embedding in enumerate(embeddings):
            unmasked_embedding = embedding[: actual_sequence_lengths[index]]
            nonpadded_sequence_embeddings.append(unmasked_embedding)
        
        return nonpadded_sequence_embeddings
    
    def _post_process_sequence_embeddings(
            self, sequence_embeddings: List[np.ndarray]
        ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        sentence_embeddings = []
        post_processed_sequence_embeddings = []

        for example_embedding in sequence_embeddings:
            
            example_sentence_embedding = example_embedding[0]
            
            example_post_processed_embedding = example_embedding[1:-1]

            # print(example_sentence_embedding.shape, example_post_processed_embedding.shape)
            sentence_embeddings.append(example_sentence_embedding)
            post_processed_sequence_embeddings.append(example_post_processed_embedding)

        return sentence_embeddings, post_processed_sequence_embeddings
    
    def _add_extra_padding(
            self,
            sequence_embeddings: List[np.ndarray],
            actual_sequence_lengths: List[int]
    ) -> List[np.ndarray]:
        if self.max_model_sequence_length == NO_LENGTH_RESTRICTION:
            # No extra padding needed because there wouldn't have been any
            # truncation in the first place
            return sequence_embeddings

        reshaped_sequence_embeddings = []
        for index, embedding in enumerate(sequence_embeddings):
            embedding_size = embedding.shape[-1]
            if actual_sequence_lengths[index] > self.max_model_sequence_length:
                embedding = np.concatenate(
                    [
                        embedding,
                        np.zeros(
                            (
                                actual_sequence_lengths[index]
                                - self.max_model_sequence_length,
                                embedding_size,
                            ),
                            dtype=np.float32,
                        ),
                    ]
                )
            reshaped_sequence_embeddings.append(embedding)

        return reshaped_sequence_embeddings
    
    def align_token_features(
            self,
            list_of_tokens: List[List["Token"]],
            in_token_features: List[np.ndarray],
            shape: Optional[Tuple] = None,
    ) -> np.ndarray:
        if shape is None:
            shape = in_token_features.shape
        out_token_features = np.zeros(shape)

        for example_idx, example_tokens in enumerate(list_of_tokens):
            offset = 0
            for token_idx, token in enumerate(example_tokens):
                number_sub_words = token.get(NUMBER_OF_SUB_TOKENS, 1)

                if number_sub_words > 1:
                    token_start_idx = token_idx + offset
                    token_end_idx = token_idx + offset + number_sub_words

                    mean_vec = np.mean(
                        in_token_features[example_idx][token_start_idx:token_end_idx],
                        axis=0,
                    )

                    offset += number_sub_words - 1

                    out_token_features[example_idx][token_idx] = mean_vec
                else:
                    out_token_features[example_idx][token_idx] = in_token_features[
                        example_idx
                    ][token_idx + offset]

        return out_token_features


    def _get_model_features_for_batch(
            self,
            batch_token_ids: List[List[int]],
            batch_tokens: List[List[Token]],
            batch_examples: List[Message],
            attribute: Text,
            inference_mode: bool = False,
    ) -> Tuple[np.ndarray, np.ndarray]:
        batch_token_ids_augmented = self._add_lm_specific_special_tokens(batch_token_ids)

        (
            actual_sequence_lengths,
            max_input_sequence_length,
        ) = self._extract_sequence_lengths(batch_token_ids_augmented)

        self._validate_sequence_lengths(
            actual_sequence_lengths, batch_examples, attribute, inference_mode
        )

        padded_token_ids = self._add_padding_to_batch(
            batch_token_ids_augmented, max_input_sequence_length
        )

        batch_attention_mask = self._compute_attention_mask(
            actual_sequence_lengths, max_input_sequence_length
        )

        sequence_hidden_states = self._compute_batch_sequence_features(
            batch_attention_mask, padded_token_ids
        )

        # print(sequence_hidden_states.shape)

        sequence_nonpadded_embeddings = self._extract_nonpadded_embeddings(
            sequence_hidden_states, actual_sequence_lengths
        )

        # for nonpadded_embed in sequence_nonpadded_embeddings:
        #     print(nonpadded_embed.shape)
        
        (
            sentence_embeddings,
            sequence_embeddings,
        ) = self._post_process_sequence_embeddings(sequence_nonpadded_embeddings)

        sequence_embeddings = self._add_extra_padding(sequence_embeddings, actual_sequence_lengths)

        batch_dim = len(sequence_embeddings)
        seq_dim = max(e.shape[0] for e in sequence_embeddings)
        # seq_dim = max([len(batch_tokens[i]) for i in range(len(batch_tokens))])
        feature_dim = sequence_embeddings[0].shape[1]
        shape = (batch_dim, seq_dim, feature_dim)

        # print(shape)
        sequence_embeddings = self.align_token_features(
            batch_tokens, sequence_embeddings, shape
        )
        # for i, sentence_embed in enumerate(sentence_embeddings):
        #     print(i, sentence_embed.shape)
        sentence_embeddings = np.array(sentence_embeddings)

        sequence_final_embeddings = []
        for embeddings, tokens in zip(sequence_embeddings, batch_tokens):
            sequence_final_embeddings.append(embeddings[: len(tokens)])

        final_embeddings = None
        try:
            final_embeddings = np.array(sequence_final_embeddings)
        except:
            final_embeddings = np.array(sequence_final_embeddings, dtype=object)    
        return sentence_embeddings, final_embeddings
    
    def _get_docs_for_batch(
            self,
            batch_examples: List[Message],
            attribute: Text,
            inference_mode: bool = False,
        ) -> List[Dict[Text, Any]]:

        batch_tokens, batch_token_ids = self._get_token_ids_for_batch(batch_examples, attribute)

        (
            batch_sentence_features,
            batch_sequence_features,
        ) = self._get_model_features_for_batch(
            batch_token_ids, batch_tokens, batch_examples, attribute, inference_mode
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
            print(i)
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