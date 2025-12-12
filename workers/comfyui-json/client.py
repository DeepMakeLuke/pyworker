import uuid
import random
import asyncio
import random

from vastai import Serverless

async def main():
    async with Serverless() as client:
        endpoint = await client.get_endpoint(name="my-comfy-endpoint") # Change this to your endpoint name

        payload = {
            "input": {
                "request_id": str(uuid.uuid4()),
                "modifier": "Text2Image",
                "modifications": {
                    "prompt": "a beautiful landscape with mountains and lakes",
                    "width": 1024,
                    "height": 1024,
                    "steps": 20,
                    "seed": random.randint(0, 2**32 - 1)
                },
                "workflow_json": {}  # Empty since using modifier approach
            }
        }
        
        response = await endpoint.request("/generate/sync", payload, cost=100)

        # Get the file from the path on the local machine using SCP or SFTP
        # or configure S3 to upload to cloud storage.
        print(response["response"]["output"][0]["local_path"])

if __name__ == "__main__":
    asyncio.run(main())