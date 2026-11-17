import os
import time

from dotenv import load_dotenv
from litellm import completion

load_dotenv()

start = time.perf_counter()

resp = completion(
    model=os.environ["LLM_MODEL"],
    messages=[{"role": "user", "content": "Ek line mein batao: tum kaun ho?"}],
    reasoning_effort="minimal",
)
elapsed = time.perf_counter() - start

print(resp.choices[0].message.content)
print(resp.model_dump_json(indent=2))
print(f"tokens:{resp.usage.total_tokens}, time: {elapsed:.2f}s")
