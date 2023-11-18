from transformers import T5ForConditionalGeneration
from torch import nn

'''
Class definition of our model needed to load in t5 module. 
'''
class T5RecogsModule(nn.Module):
    def __init__(self):
        super().__init__()
        self.encdec = T5ForConditionalGeneration.from_pretrained("t5-small")

    def forward(self, X_pad, X_mask, y_pad, y_mask, labels=None):
        outputs = self.encdec(
            input_ids=X_pad,
            attention_mask=X_mask,
            decoder_attention_mask=y_mask,
            labels=y_pad)
        return outputs
