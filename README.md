# RobustMasking
T5 based masking system

I trained a T5-small model to mask names and dates of birth of birth out of text.  The model was trained on a custom sythetic dataset.
The dataset is generated with notebooks in the Data folder.  The dataset is a mix of of openai api generated examples and programatically generated examples.
For programatically generated examples, I used a amazon product review dataset for natural english tokens that don't have names or dates of birth in them.
The programmatic data is generated randomly, in a very ad-hoc manner, in order to expose the T5 model to different types of examples.

The T5 training setup can be found in the t5_training notebook.  The remainder of the files are for pre-processing and post-processing on top of the model. 
This code, found in indexing.py and extraction.py, takes care of splitting the input before sending it to the T5 model, post-processig the mask tokens in order
to enforce consistency in the numbering of names, saving the (mask-token, content) pairs so that we can recover the original input if needed. 

The model weights are not on this repo as the file is too large.

