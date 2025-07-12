from transformers import AutoModelForCausalLM, AutoTokenizer
import os

model_name = os.environ.get("MODEL_NAME")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.save_pretrained("./local_model", max_shard_size="1GB")
tokenizer.save_pretrained("./local_model", max_shard_size="1GB")
