import torch
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, T5Config, T5ForConditionalGeneration
from torch import nn
import indexing
from t5 import T5RecogsModule
import __main__

# needed to recognize our T5 model outside of main
setattr(__main__, "T5RecogsModule", T5RecogsModule)


def get_model(path, config_path):
    # note, from pretrained requires internet access
    enc_tokenizer = AutoTokenizer.from_pretrained("t5-large", padding=True, truncation=True)
    dec_tokenizer = enc_tokenizer
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load in weights from pt file.
    sd = torch.load(path, map_location=torch.device(device)).encdec

    # Load config
    config = T5Config.from_json_file(config_path)

    # Init empty T5 model based on the configuration
    model = T5ForConditionalGeneration(config)

    # Load weights to model
    model.load_state_dict(sd.state_dict())

    model.to(device)

    return model, enc_tokenizer

def infer(model, tokenizer, text):
    #split into resonably sized chunks for t5
    chunks = indexing.split_string(text, 800)

    # for demo we run model local
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    predictions = []
    # note, inference would be much faster if batched
    # ran this way since didn't want memory issues on my local machine
    for chunk in chunks:
        input_text = chunk
        input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
        input_ids = input_ids.to(device)
        model.eval()
        with torch.no_grad():
            # want greedy generation for this task
            output = model.generate(input_ids, max_new_tokens=512, num_beams=1, do_sample = False)
            prediction = tokenizer.decode(output[0], skip_special_tokens=True)
        predictions.append(prediction)
    output = ''.join(predictions)
    return output
