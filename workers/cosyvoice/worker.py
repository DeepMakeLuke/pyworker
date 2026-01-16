"""
CosyVoice TTS Worker for Vast.ai Serverless

This worker proxies TTS requests to a CosyVoice model server
(dragontamer80085/cosyvoice-serverless) running on port 18000.

Usage:
    Set BACKEND=cosyvoice in your Vast.ai template environment variables.
"""
from vastai import Worker, WorkerConfig, HandlerConfig, LogActionConfig, BenchmarkConfig

# CosyVoice model configuration (dragontamer80085/cosyvoice-serverless image)
MODEL_SERVER_URL           = 'http://127.0.0.1'
MODEL_SERVER_PORT          = 18000
MODEL_LOG_FILE             = "/workspace/model.log"
MODEL_HEALTHCHECK_ENDPOINT = "/health"

# Log patterns for PyWorker detection
MODEL_LOAD_LOG_MSG = ["COSYVOICE_READY"]

MODEL_ERROR_LOG_MSGS = [
    "Traceback",
    "Error:",
    "Exception:",
    "CUDA out of memory",
    "RuntimeError",
]

MODEL_INFO_LOG_MSGS = [
    "Starting CosyVoice",
    "Loading CosyVoice",
    "Model loaded",
    "Warmup",
]


def benchmark_generator() -> dict:
    """Generate benchmark payload for worker validation."""
    return {
        "text": "Hello, this is a benchmark test.",
        "mode": "sft",
        "speaker": "english_female",
    }


worker_config = WorkerConfig(
    model_server_url=MODEL_SERVER_URL,
    model_server_port=MODEL_SERVER_PORT,
    model_log_file=MODEL_LOG_FILE,
    model_healthcheck_url=MODEL_HEALTHCHECK_ENDPOINT,
    handlers=[
        HandlerConfig(
            route="/generate",
            allow_parallel_requests=False,
            max_queue_time=120.0,
            benchmark_config=BenchmarkConfig(
                generator=benchmark_generator,
                concurrency=1,
                runs=1,
            ),
            workload_calculator=lambda x: len(x.get("text", ""))
        ),
    ],
    log_action_config=LogActionConfig(
        on_load=MODEL_LOAD_LOG_MSG,
        on_error=MODEL_ERROR_LOG_MSGS,
        on_info=MODEL_INFO_LOG_MSGS,
    ),
)

Worker(worker_config).run()
