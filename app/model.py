"""
NLP Model for Product Description Generation using GPT-2
"""
import pandas as pd
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge import Rouge
import warnings

warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

class ProductDescriptionGenerator:
    def __init__(self, model_name="gpt2", device=None):
        self.model_name = model_name
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading model {model_name} on device: {self.device}")
        
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        
        self.model.to(self.device)
        self.model.eval()
        
        self.rouge = Rouge()
        self.smoothing = SmoothingFunction().method1
        print("Model loaded successfully!")
    
    def generate_text(self, prompt, max_new_tokens=150, temperature=0.7, top_k=50, top_p=0.95):
        try:
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            max_input_length = 1024
            input_length = inputs.shape[1]
            if input_length > max_input_length:
                inputs = inputs[:, -max_input_length:]
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=max_new_tokens,
                    num_return_sequences=1,
                    do_sample=True,
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p,
                    pad_token_id=self.tokenizer.eos_token_id,
                    attention_mask=torch.ones(inputs.shape, device=self.device)
                )
            full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            if full_text.startswith(prompt):
                generated_text = full_text[len(prompt):].strip()
            else:
                generated_text = full_text.strip()
            return generated_text
        except Exception as e:
            print(f"Error generating text: {str(e)}")
            return ""
    
    def reward_function(self, generated_text, reference_text):
        try:
            reference_tokens = reference_text.split()
            generated_tokens = generated_text.split()
            
            if len(reference_tokens) == 0 or len(generated_tokens) == 0:
                bleu_score = 0.0
            else:
                bleu_score = sentence_bleu(
                    [reference_tokens],
                    generated_tokens,
                    smoothing_function=self.smoothing
                )
            try:
                rouge_scores = self.rouge.get_scores(generated_text, reference_text)
                rouge_l_score = rouge_scores[0]['rouge-l']['f']
                rouge_1_score = rouge_scores[0]['rouge-1']['f']
                rouge_2_score = rouge_scores[0]['rouge-2']['f']
            except:
                rouge_l_score = 0.0
                rouge_1_score = 0.0
                rouge_2_score = 0.0
            
            combined_score = 0.5 * bleu_score + 0.5 * rouge_l_score
            return {
                'bleu': bleu_score,
                'rouge_1': rouge_1_score,
                'rouge_2': rouge_2_score,
                'rouge_l': rouge_l_score,
                'combined': combined_score
            }
        except Exception as e:
            print(f"Error calculating reward: {str(e)}")
            return {'bleu': 0.0, 'rouge_1': 0.0, 'rouge_2': 0.0, 'rouge_l': 0.0, 'combined': 0.0}
