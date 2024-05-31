# Model-Agents of Change (original codebase)
This is the original codebase of my master's thesis in computer science at Miami University.

## Note Regarding Models
The project is currently configured to use locally hosted models in the large_models/ directory within the thesisapp/ directory.  

SciBERT can be imported using the code:

```
model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')
```
