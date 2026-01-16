"""
CosyVoice TTS Worker for Vast.ai Serverless

This worker proxies TTS requests to a CosyVoice model server running
on port 18000. Supports both SFT mode (preset speakers) and zero-shot
voice cloning.

Usage:
    Set BACKEND=cosyvoice in your Vast.ai template environment variables.
"""
import os
from vastai import Worker, WorkerConfig, HandlerConfig, LogActionConfig, BenchmarkConfig

# Model server configuration
MODEL_SERVER_URL = "http://127.0.0.1"
MODEL_SERVER_PORT = int(os.environ.get("MODEL_SERVER_PORT", 18000))
MODEL_LOG_FILE = os.environ.get("MODEL_LOG", "/workspace/model.log")
MODEL_HEALTHCHECK_ENDPOINT = "/health"

# Log patterns for PyWorker detection
# CRITICAL: These must match EXACTLY what the model server prints (PREFIX match)
MODEL_LOAD_LOG_MSG = ["COSYVOICE_READY"]

MODEL_ERROR_LOG_MSGS = [
    "Traceback",
    "Error:",
    "Exception:",
    "CUDA out of memory",
    "RuntimeError",
    "ModuleNotFoundError",
]

MODEL_INFO_LOG_MSGS = [
    "Starting CosyVoice",
    "Loading CosyVoice",
    "Model loaded",
    "Warmup",
    "Available speakers",
]


def benchmark_generator() -> dict:
    """
    Generate benchmark payload for Vast.ai worker validation.

    The benchmark runs after on_load is detected to validate the worker
    is functioning correctly before joining the standby pool.
    """
    return {
        "text": "Hello, this is a benchmark test for the text to speech system.",
        "mode": "sft",
        "speaker": "english_female",
    }


def workload_calculator(request: dict) -> int:
    """Calculate workload based on text length."""
    return len(request.get("text", ""))


worker_config = WorkerConfig(
    model_server_url=MODEL_SERVER_URL,
    model_server_port=MODEL_SERVER_PORT,
    model_log_file=MODEL_LOG_FILE,
    model_healthcheck_url=MODEL_HEALTHCHECK_ENDPOINT,
    handlers=[
        HandlerConfig(
            route="/generate",
            allow_parallel_requests=False,  # TTS uses GPU, no parallelism
            max_queue_time=600.0,  # Long queue time for voice cloning
            benchmark_config=BenchmarkConfig(
                generator=benchmark_generator,
                concurrency=1,
                runs=1,  # Single run for GPU model
            ),
            workload_calculator=workload_calculator,
        ),
    ],
    log_action_config=LogActionConfig(
        on_load=MODEL_LOAD_LOG_MSG,
        on_error=MODEL_ERROR_LOG_MSGS,
        on_info=MODEL_INFO_LOG_MSGS,
    ),
)

Worker(worker_config).run()
