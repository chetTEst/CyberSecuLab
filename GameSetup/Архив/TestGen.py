from transformers import GPT2LMHeadModel, GPT2Tokenizer

def generate_text(prompt, model_name="ai-forever/mGPT", max_length=150):
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)

    inputs = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(inputs, max_length=max_length, num_return_sequences=1)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Example usage
prompt = "Напишите статью о кибербезопасности в цифровом городе 'Киберия'. "  # Replace with your prompt
generated_text = generate_text(prompt)
print(generated_text)