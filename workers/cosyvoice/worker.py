"""
CosyVoice TTS Worker for Vast.ai Serverless

This worker proxies TTS requests to a CosyVoice model server running
on port 8188. Compatible with neosun/cosyvoice Docker image.

Usage:
    Set BACKEND=cosyvoice in your Vast.ai template environment variables.
"""
from vastai import Worker, WorkerConfig, HandlerConfig, LogActionConfig, BenchmarkConfig

# CosyVoice model configuration
MODEL_SERVER_URL           = 'http://127.0.0.1'
MODEL_SERVER_PORT          = 8188
MODEL_LOG_FILE             = "/var/log/cosyvoice.log"
MODEL_HEALTHCHECK_ENDPOINT = "/health"

# CosyVoice-specific log messages (check actual CosyVoice logs for correct patterns)
MODEL_LOAD_LOG_MSG = [
    "Uvicorn running on",
    "Application startup complete",
]

MODEL_ERROR_LOG_MSGS = [
    "Error:",
    "Exception:",
    "Traceback (most recent call last):",
]

MODEL_INFO_LOG_MSGS = [
    "Loading model",
]


def benchmark_generator() -> dict:
    """Generate a benchmark request for capacity estimation."""
    benchmark_data = {
        "text": "Hello, this is a test of the text to speech system.",
    }
    return benchmark_data


worker_config = WorkerConfig(
    model_server_url=MODEL_SERVER_URL,
    model_server_port=MODEL_SERVER_PORT,
    model_log_file=MODEL_LOG_FILE,
    model_healthcheck_url=MODEL_HEALTHCHECK_ENDPOINT,
    handlers=[
        HandlerConfig(
            route="/api/tts",
            allow_parallel_requests=False,
            max_queue_time=120.0,
            benchmark_config=BenchmarkConfig(
                generator=benchmark_generator,
                concurrency=1,
                runs=3
            ),
            workload_calculator=lambda x: len(x.get("text", ""))
        ),
    ],
    log_action_config=LogActionConfig(
        on_load=MODEL_LOAD_LOG_MSG,
        on_error=MODEL_ERROR_LOG_MSGS,
        on_info=MODEL_INFO_LOG_MSGS
    )
)

Worker(worker_config).run()
