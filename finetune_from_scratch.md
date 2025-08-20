Complete Guide: Fine-tuning LLaMA 3.2 with Unsloth for Document Q&A
Overview
This guide covers the complete process of fine-tuning LLaMA 3.2 using Unsloth for document-based question answering, from PDF processing to model validation.
Prerequisites

GPU with at least 16GB VRAM (RTX 4090, A100, etc.)
Python 3.8+
CUDA toolkit installed
Sufficient disk space (20+ GB for model and data)

1. Environment Setup
Install Required Libraries

```python
# Install Unsloth
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

# Additional dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers datasets accelerate bitsandbytes
pip install PyPDF2 pymupdf pandas numpy
pip install langchain ollama
pip install rouge-score bert-score
```
2. Data Preparation from PDF
Step 1: Extract Text from PDF

```python
import fitz  # PyMuPDF
import re
import json
from typing import List, Dict
import pandas as pd

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    doc = fitz.open(pdf_path)
    text = ""
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    
    doc.close()
    return text

def clean_text(text: str) -> str:
    """Clean extracted text"""
    # Remove extra whitespaces and newlines
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\.\,\?\!\-\:\;]', '', text)
    
    return text.strip()
```

Step 2: Create Training Data

```python
def create_qa_pairs_from_text(text: str, chunk_size: int = 1000) -> List[Dict]:
    """
    Create Q&A pairs from text chunks
    You'll need to manually create or use LLM to generate questions
    """
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    qa_pairs = []
    
    # This is a template - you'll need to create actual Q&A pairs
    # Option 1: Manual creation
    # Option 2: Use GPT-4/Claude to generate questions from chunks
    
    for i, chunk in enumerate(chunks):
        # Example structure - replace with your actual Q&A pairs
        qa_pair = {
            "instruction": f"Based on the following documentation, answer the question about [specific topic from chunk {i+1}]",
            "input": f"What is [specific question about the content]?",
            "output": f"[Answer derived from the chunk]: {chunk[:200]}...",
            "context": chunk
        }
        qa_pairs.append(qa_pair)
    
    return qa_pairs

def format_for_training(qa_pairs: List[Dict]) -> List[Dict]:
    """Format data for Unsloth training"""
    formatted_data = []
    
    for qa in qa_pairs:
        # Alpaca format
        formatted_data.append({
            "text": f"### Instruction:\n{qa['instruction']}\n\n### Input:\n{qa['input']}\n\n### Response:\n{qa['output']}"
        })
    
    return formatted_data

# Usage example
pdf_text = extract_text_from_pdf("your_product_documentation.pdf")
cleaned_text = clean_text(pdf_text)
qa_pairs = create_qa_pairs_from_text(cleaned_text)
training_data = format_for_training(qa_pairs)

# Save to JSON
with open("training_data.json", "w") as f:
    json.dump(training_data, f, indent=2)
```

Step 3: Advanced Data Generation (Using LLM)

```python
def generate_questions_with_llm(text_chunk: str) -> List[Dict]:
    """
    Use an LLM to generate questions from text chunks
    This is more effective than manual creation
    """
    # You can use OpenAI API, Claude API, or local models for this
    prompt = f"""
    Based on the following text, generate 3-5 relevant questions and their answers:
    
    Text: {text_chunk}
    
    Format your response as JSON with this structure:
    {{
        "qa_pairs": [
            {{
                "question": "Question here",
                "answer": "Detailed answer here"
            }}
        ]
    }}
    """
    
    # Implementation depends on your chosen LLM API
    # This is a placeholder - implement based on your preferred service
    pass
```
3. Fine-tuning with Unsloth
Step 1: Load Model and Tokenizer
```python
from unsloth import FastLanguageModel
import torch
from datasets import Dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# Model configuration
max_seq_length = 2048
dtype = None  # Auto-detection
load_in_4bit = True  # Use 4bit quantization to reduce memory usage

# Load model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3.2-3b-instruct-bnb-4bit",  # Choose appropriate size
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)

# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # Choose any number > 0, typically 8, 16, 32, 64, 128
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,  # Supports any, but = 0 is optimized
    bias="none",     # Supports any, but = "none" is optimized
    use_gradient_checkpointing="unsloth",  # True or "unsloth" for long context
    random_state=3407,
)
```

Step 2: Prepare Dataset

```python
def formatting_prompts_func(examples):
    """Format prompts for training"""
    texts = []
    for text in examples["text"]:
        # Add EOS token
        texts.append(text + tokenizer.eos_token)
    return {"text": texts}

# Load your training data
with open("training_data.json", "r") as f:
    training_data = json.load(f)

# Create dataset
dataset = Dataset.from_list(training_data)
dataset = dataset.map(formatting_prompts_func, batched=True)
```

Step 3: Training Configuration

```python
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,  # Can make training 5x faster for short sequences
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=100,  # Adjust based on your data size
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="./llama-3.2-finetuned",
        save_steps=50,
        save_total_limit=2,
        dataloader_num_workers=0,
        report_to=None,  # Use "wandb" if you want to track training
    ),
)
```

Step 4: Start Training


```python
# Show current memory stats
gpu_stats = torch.cuda.get_device_properties(0)
start_gpu_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
print(f"GPU = {gpu_stats.name}. Max memory = {max_memory} GB.")
print(f"Memory before training = {start_gpu_memory} GB.")

# Train the model
trainer_stats = trainer.train()

# Show final memory and time stats
used_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
used_memory_for_lora = round(used_memory - start_gpu_memory, 3)
used_percentage = round(used_memory / max_memory * 100, 3)
lora_percentage = round(used_memory_for_lora / max_memory * 100, 3)
print(f"Memory used = {used_memory} GB ({used_percentage}%)")
print(f"Memory used for LoRA = {used_memory_for_lora} GB ({lora_percentage}%)")
```
4. Model Export and Ollama Integration
Step 1: Save Model

```ptyhon
# Save LoRA model
model.save_pretrained("./llama-3.2-lora")
tokenizer.save_pretrained("./llama-3.2-lora")

# Save to GGUF format for Ollama
model.save_pretrained_gguf("./llama-3.2-gguf", tokenizer, quantization_method="q4_k_m")
```

Step 2: Create Ollama Modelfile

```python
def create_ollama_modelfile(model_path: str, model_name: str):
    """Create Ollama modelfile"""
    modelfile_content = f"""
FROM {model_path}

TEMPLATE \"\"\"### Instruction:
{{{{ .System }}}}

### Input:
{{{{ .Prompt }}}}

### Response:
\"\"\"

PARAMETER stop "### Instruction:"
PARAMETER stop "### Input:"
PARAMETER stop "### Response:"
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
"""
    
    with open("Modelfile", "w") as f:
        f.write(modelfile_content)
    
    print(f"Modelfile created. Run: ollama create {model_name} -f Modelfile")

# Create modelfile
create_ollama_modelfile("./llama-3.2-gguf", "product-docs-llama")
```

Step 3: Import to Ollama
```bash
# In terminal
ollama create product-docs-llama -f Modelfile
ollama list  # Verify model is available
```

5. Model Validation and Testing
Step 1: Basic Functionality Test

```python
def test_basic_functionality():
    """Test basic model functionality"""
    import ollama
    
    test_questions = [
        "What is the main purpose of this product?",
        "How do I install this software?",
        "What are the system requirements?",
        "What troubleshooting steps should I follow?",
    ]
    
    for question in test_questions:
        response = ollama.chat(model='product-docs-llama', messages=[
            {'role': 'user', 'content': question}
        ])
        
        print(f"Q: {question}")
        print(f"A: {response['message']['content']}")
        print("-" * 50)

test_basic_functionality()
```
Step 2: Comprehensive Evaluation


```python
import json
from rouge_score import rouge_scorer
from bert_score import score
import numpy as np

def evaluate_model_performance(test_data: List[Dict]):
    """Comprehensive model evaluation"""
    import ollama
    
    predictions = []
    references = []
    
    # Generate predictions
    for item in test_data:
        response = ollama.chat(model='product-docs-llama', messages=[
            {'role': 'user', 'content': item['question']}
        ])
        
        predictions.append(response['message']['content'])
        references.append(item['expected_answer'])
    
    # Calculate ROUGE scores
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    rouge_scores = []
    
    for pred, ref in zip(predictions, references):
        scores = scorer.score(ref, pred)
        rouge_scores.append({
            'rouge1': scores['rouge1'].fmeasure,
            'rouge2': scores['rouge2'].fmeasure,
            'rougeL': scores['rougeL'].fmeasure,
        })
    
    # Calculate BERTScore
    P, R, F1 = score(predictions, references, lang="en", verbose=True)
    
    # Summary statistics
    avg_rouge1 = np.mean([s['rouge1'] for s in rouge_scores])
    avg_rouge2 = np.mean([s['rouge2'] for s in rouge_scores])
    avg_rougeL = np.mean([s['rougeL'] for s in rouge_scores])
    avg_bert_f1 = torch.mean(F1).item()
    
    evaluation_results = {
        'rouge1': avg_rouge1,
        'rouge2': avg_rouge2,
        'rougeL': avg_rougeL,
        'bert_f1': avg_bert_f1,
        'num_samples': len(test_data)
    }
    
    return evaluation_results, predictions, references

# Create test dataset
test_data = [
    {"question": "Test question 1", "expected_answer": "Expected answer 1"},
    # Add more test cases based on your documentation
]

results, preds, refs = evaluate_model_performance(test_data)
print("Evaluation Results:", json.dumps(results, indent=2))
```

Step 3: Domain-Specific Validation

```python
def domain_specific_validation():
    """Validate domain-specific knowledge"""
    import ollama
    
    # Test categories based on your documentation
    test_categories = {
        "installation": [
            "How do I install the product?",
            "What are the installation requirements?",
        ],
        "configuration": [
            "How do I configure the basic settings?",
            "What configuration options are available?",
        ],
        "troubleshooting": [
            "How do I resolve common issues?",
            "What should I do if the product doesn't start?",
        ],
        "features": [
            "What are the key features of this product?",
            "How do I use feature X?",
        ]
    }
    
    results = {}
    
    for category, questions in test_categories.items():
        category_results = []
        
        for question in questions:
            response = ollama.chat(model='product-docs-llama', messages=[
                {'role': 'user', 'content': question}
            ])
            
            # Evaluate response quality (you can add more sophisticated metrics)
            answer = response['message']['content']
            
            # Basic quality checks
            quality_score = 0
            if len(answer) > 50:  # Reasonable length
                quality_score += 1
            if any(keyword in answer.lower() for keyword in ["install", "configure", "step", "process"]):
                quality_score += 1
            if "I don't know" not in answer and "cannot" not in answer:
                quality_score += 1
            
            category_results.append({
                'question': question,
                'answer': answer,
                'quality_score': quality_score / 3
            })
        
        results[category] = category_results
    
    return results

domain_results = domain_specific_validation()
for category, results in domain_results.items():
    avg_quality = np.mean([r['quality_score'] for r in results])
    print(f"{category.capitalize()} - Average Quality: {avg_quality:.2f}")


```

Step 4: LangChain Integration Test

```python
from langchain.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

def test_langchain_integration():
    """Test LangChain integration"""
    
    # Initialize Ollama LLM
    llm = Ollama(model="product-docs-llama")
    
    # Create conversation chain with memory
    memory = ConversationBufferMemory()
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )
    
    # Test conversation flow
    test_conversation = [
        "What is this product about?",
        "How do I install it?",
        "What if I encounter problems during installation?",
        "Can you summarize what we discussed?"
    ]
    
    for question in test_conversation:
        response = conversation.predict(input=question)
        print(f"Q: {question}")
        print(f"A: {response}")
        print("-" * 50)

test_langchain_integration()
```
6. Additional Considerations
Performance Optimization

Batch Size: Start with smaller batch sizes (1-2) and increase if GPU memory allows
Sequence Length: Match your typical document Q&A length requirements
LoRA Rank: Higher rank (32-64) for complex domains, lower (8-16) for simpler ones
Learning Rate: Start with 2e-4, adjust based on loss curves

Data Quality Guidelines

Diversity: Include various question types (factual, procedural, conceptual)
Coverage: Ensure all important topics from PDF are covered
Quality: Manual review of generated Q&A pairs is crucial
Balance: Equal representation of different document sections

Monitoring and Maintenance

Track model performance over time
Collect user feedback for continuous improvement
Regular retraining with new documentation updates
Version control for different model iterations

Industry Best Practices

A/B Testing: Compare fine-tuned model with base model
Human Evaluation: Manual assessment of answer quality
Retrieval Augmentation: Consider RAG for factual accuracy
Safety Filters: Implement content filtering for production use
Monitoring: Track inference latency, accuracy, and user satisfaction

7. Troubleshooting Common Issues
Memory Issues
```python
# Reduce model size or use more aggressive quantization
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3.2-1b-instruct-bnb-4bit",  # Smaller model
    load_in_4bit=True,
    use_gradient_checkpointing=True
)
```
Training Instability

```python
# Adjust learning rate and add warmup
args = TrainingArguments(
    learning_rate=1e-4,  # Lower learning rate
    warmup_steps=100,    # More warmup steps
    gradient_clipping=1.0,
    # ... other parameters
)
```

Poor Performance

Check data quality and formatting
Increase training steps
Adjust LoRA parameters
Validate prompt templates