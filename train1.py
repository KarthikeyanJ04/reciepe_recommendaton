import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import load_dataset

# Limit VRAM usage to ~5.5GB on a 6GB GPU
torch.cuda.set_per_process_memory_fraction(0.92, device=0)

print("="*80)
print("TRAINING GPT-2 FOR INDIAN RECIPES (6GB VRAM FRIENDLY)")
print("="*80)

# Load tokenizer and model (GPT-2 small)
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.gradient_checkpointing_enable()  # Saves a lot of VRAM

tokenizer.pad_token = tokenizer.eos_token  # For padding

# Use short sequence to reduce RAM/VRAM requirement
MAX_LEN = 256

dataset = load_dataset('text', data_files={'train': 'train.txt'})

def tokenize_function(examples):
    return tokenizer(
        examples['text'],
        truncation=True,
        max_length=MAX_LEN,
        padding='max_length'
    )

print("Tokenizing dataset...")
tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=['text'])

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir="./gpt2-recipe-slim",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=1,           # Tiny batch size to fit 6GB
    gradient_accumulation_steps=8,           # Accumulate gradients
    learning_rate=5e-5,
    warmup_steps=250,
    save_steps=1000,
    save_total_limit=2,
    fp16=True,  # Use half-precision for big VRAM savings
    logging_steps=100,
    report_to=None,
)

print("\nInitializing trainer...")
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=tokenized_dataset['train'],
)

print("\n🚀 Starting training...\n")
trainer.train()

print("\nSaving model...")
model.save_pretrained("./gpt2-recipe-slim-final")
tokenizer.save_pretrained("./gpt2-recipe-slim-final")

print("\n✓ Done! Model saved to ./gpt2-recipe-slim-final")
