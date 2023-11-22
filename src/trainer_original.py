from transformers import Trainer
from torch.nn import BCEWithLogitsLoss, CrossEntropyLoss
from focal_loss.focal_loss import FocalLoss
import torch
import torch.nn.functional as F
import numpy as np

class CustomTrainer(Trainer):
    '''
    #class_weights --> loss gets weighted by the ground truth class -- inverse probabiity weighting
    e.g. def __init__(self, use_hierarchical_classifier=False, class_weights, *args, **kwargs): 

    Or find other weight loss and combine with comepute_loss!

    Or BCEWithLogitsLoss + pos_weight arg  --> Binary classification
    
    '''
    def __init__(self, use_hierarchical_classifier, prediction_target_uids, use_focal_loss, class_weights, *args, **kwargs): 
        super().__init__( *args, **kwargs)
        self.loss_fn = CrossEntropyLoss()
        self.use_hierarchical_classifier = use_hierarchical_classifier
        self.prediction_target_uids = prediction_target_uids
        self.use_focal_loss = use_focal_loss
        self.target_to_dimension = {target:idx for idx,target in enumerate(self.prediction_target_uids)}
        self.class_weights = class_weights
        # self.uid_to_dimension = uid_to_dimension
        # self.num_labels = len(uid_to_dimension)

    # def one_hot_encode(self, labels):
    #     # print("labels:",labels)
    #     one_hot_encoded = []
    #     for label in labels:
    #         one_hot = [0] * self.num_labels
    #         one_hot[self.uid_to_dimension[label]] = 1
    #         one_hot_encoded.append(one_hot)  
    #     return one_hot_encoded

    def mapping_cwe_to_label(self, cwe_label):
        # Convert each tensor element to its corresponding dictionary value
        mapped_labels = [self.target_to_dimension[int(cwe_id.item())] for cwe_id in cwe_label]
        return torch.tensor(mapped_labels)
    
    # For multilabel classification, need to define the Custom Loss Function
    def compute_loss(self, model, inputs, return_outputs=False):
        # print("THIS IS COMPUTE LOSS IN TRAINER")
        if self.use_hierarchical_classifier:
            # loss, logits = model(inputs['input_ids'], attention_mask=inputs['attention_mask'], labels=inputs['labels'])
            logits = model(inputs['input_ids'], attention_mask=inputs['attention_mask'])
            # print("logits",logits)
            logits = F.softmax(logits, dim=-1)  # ----> remove??????
            # print("logits",logits)
            loss = model.loss(logits, inputs['labels'])
            # print("logits, inputs['labels']", logits.shape,  inputs['labels'].shape)
        
        else:
            logits = model(inputs['input_ids'], attention_mask=inputs['attention_mask'])
            logits = logits.logits.cpu() #[batch_size, sequence_length, num_classes] logits, inputs['labels'] torch.Size([6, 21]) torch.Size([6])
            # print("logits", logits)
            # Apply softmax to logits to get probabilities
            logits = F.softmax(logits, dim=-1)
            labels = self.mapping_cwe_to_label(inputs['labels'].cpu())
            # print("logits, inputs['labels']", logits.shape,  inputs['labels'].shape)
            if self.use_focal_loss:
                gamma = 2.0
                self.loss_fn = FocalLoss(gamma=gamma, weights=self.class_weights.cpu()) #https://pypi.org/project/focal-loss-torch/
                loss = self.loss_fn(logits, labels)
         

            else:
                loss = self.loss_fn(logits, labels)

        return (loss, (loss,logits)) if return_outputs else loss
