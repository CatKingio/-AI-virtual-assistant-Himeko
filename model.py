import torch.nn as nn


class SimpleTransformer(nn.Module):
    
    def __init__(self, vocab_size = 194 , d_model =256  , num_classes = 6 , num_heads = 4, num_layers = 2):
        super(SimpleTransformer, self).__init__()
     
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.encoder_layer = nn.TransformerEncoderLayer(d_model, num_heads)
        self.transformer_encoder = nn.TransformerEncoder(self.encoder_layer, num_layers)
        self.fc = nn.Linear(d_model, num_classes)
    
    def forward(self, src):
        src = self.embedding(src)
        src = src.permute(1, 0, 2)  
        output = self.transformer_encoder(src)
        output = output.mean(dim=0)  
        logits = self.fc(output)
        return logits
