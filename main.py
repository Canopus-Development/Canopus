import torch
from datasets import load_dataset
from transformers import ElectraTokenizer, ElectraForMaskedLM, Trainer, TrainingArguments
from torch.utils.data import DataLoader
from accelerate import Accelerator, DistributedDataParallelKwargs
from transformers import get_linear_schedule_with_warmup

# Function to tokenize and preprocess the dataset
def preprocess_dataset(dataset, tokenizer, max_length, code_column_name):
    def tokenize_function(examples):
        outputs = tokenizer(examples[code_column_name], padding="max_length", truncation=True, max_length=max_length, return_tensors="pt")
        return outputs

    dataset = dataset.map(tokenize_function, batched=True, remove_columns=code_column_name)
    dataset.set_format(type='torch', columns=['input_ids', 'attention_mask'])
    return dataset

# Load the code_search_net dataset with trust_remote_code=True
code_search_dataset = load_dataset("code_search_net", trust_remote_code=True)

# Update the column name based on the dataset structure
code_column_name = "whole_func_string" # Replace with the correct column name

# Preprocess dataset
tokenizer = ElectraTokenizer.from_pretrained("google/electra-base-generator")
max_length = 128
train_dataset = preprocess_dataset(code_search_dataset["train"], tokenizer, max_length, code_column_name)
val_dataset = preprocess_dataset(code_search_dataset["validation"], tokenizer, max_length, code_column_name)

# Initialize ELECTRA model
model = ElectraForMaskedLM.from_pretrained("google/electra-base-generator")

# Define training arguments
# Define training arguments
training_args = TrainingArguments(
    per_device_train_batch_size=16,  # Decreased to fit GPU memory
    per_device_eval_batch_size=16,   # Decreased to fit GPU memory
    num_train_epochs=5,
    logging_dir="./logs",
    output_dir="./results",
    evaluation_strategy="epoch",
    logging_strategy="epoch",
    save_strategy="epoch",
    overwrite_output_dir=True,
    gradient_accumulation_steps=4,  # Increased to effectively use GPU memory
    fp16=False,  # Disable mixed-precision training
    fp16_full_eval=False,  # Disable half precision evaluation
)

# Initialize accelerator
accelerator = Accelerator(
    gradient_accumulation_steps=training_args.gradient_accumulation_steps,
    kwargs_handlers=[DistributedDataParallelKwargs(find_unused_parameters=True)]
)

# Create dataloaders
train_dataloader = DataLoader(train_dataset, batch_size=training_args.per_device_train_batch_size)
val_dataloader = DataLoader(val_dataset, batch_size=training_args.per_device_eval_batch_size)

# Initialize optimizer and scheduler
optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=len(train_dataloader)*training_args.num_train_epochs)

# Prepare models, optimizers, and dataloaders for distributed training
model, optimizer, train_dataloader, val_dataloader, scheduler = accelerator.prepare(
    model, optimizer, train_dataloader, val_dataloader, scheduler
)

# Training loop
for epoch in range(training_args.num_train_epochs):
    model.train()
    for batch in train_dataloader:
        optimizer.zero_grad()
        input_ids = batch["input_ids"]
        attention_mask = batch["attention_mask"]
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=input_ids)
        loss = outputs.loss
        accelerator.backward(loss)
        optimizer.step()
        scheduler.step()

    # Validation loop
    model.eval()
    eval_loss = 0
    for batch in val_dataloader:
        with torch.no_grad():
            input_ids = batch["input_ids"]
            attention_mask = batch["attention_mask"]
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=input_ids)
            eval_loss += outputs.loss.item()
    eval_loss /= len(val_dataloader)

    print(f"Epoch {epoch + 1}: Eval Loss {eval_loss}")

    # Save model checkpoint
    if accelerator.is_main_process:
        accelerator.wait_for_everyone()
        model = accelerator.unwrap_model(model)
        model.save_pretrained(f"./canopus_epoch_{epoch}")

# Save final trained model
if accelerator.is_main_process:
    accelerator.wait_for_everyone()
    model = accelerator.unwrap_model(model)
    model.save_pretrained("./canopus_final")
