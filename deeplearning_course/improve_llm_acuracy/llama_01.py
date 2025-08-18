import lamini
llm = lamini.Lamini(model_name="meta-llama/Meta-Llama-3-8B-Instruct")
prompt = """\
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful assistant.<|eot_id|><|start_header_id|>user<|end_header_id|>

Please write a birthday card for my good friend Andrew\
<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
result = llm.generate(prompt, max_new_tokens=200)
print(result)