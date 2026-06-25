FROM vllm/vllm-openai:v0.6.6

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/models/hf \
    HUGGINGFACE_HUB_CACHE=/models/hf/hub \
    TRANSFORMERS_CACHE=/models/hf/transformers \
    VLLM_CACHE_ROOT=/models/vllm

WORKDIR /app

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "-lc"]
CMD ["vllm serve ${MODEL_NAME:-Qwen/Qwen2.5-14B-Instruct-AWQ} --host 0.0.0.0 --port 8000 --dtype ${DTYPE:-float16} ${QUANTIZATION:+--quantization ${QUANTIZATION}} --max-model-len ${MAX_MODEL_LEN:-32768} --gpu-memory-utilization ${GPU_MEMORY_UTILIZATION:-0.92} --enable-auto-tool-choice --tool-call-parser hermes ${TENSOR_PARALLEL_SIZE:+--tensor-parallel-size ${TENSOR_PARALLEL_SIZE}} ${LIMIT_MM_PER_PROMPT:+--limit-mm-per-prompt ${LIMIT_MM_PER_PROMPT}}"]
