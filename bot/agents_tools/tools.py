import base64
import json

import aiofiles
from agents import function_tool, RunContextWrapper
from openai import AsyncOpenAI

from redis_service.connect import redis


@function_tool
async def image_gen_tool(wrapper: RunContextWrapper, prompt: str) -> str:
    """The function generates an image at the user's request. A prompt must be provided to generate the image.

    Args:
        prompt: Prompt for image generation.
    """

    client: AsyncOpenAI = wrapper.context[0]

    img = await client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_base64 = img.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    async with aiofiles.open(f"images/image_{wrapper.context[1]}.png", "wb") as f:
        await f.write(image_bytes)

    data = {'image': f"images/image_{wrapper.context[1]}.png", 'input_tokens': img.usage.input_tokens, 'output_tokens': img.usage.output_tokens}

    await redis.set(f'image_{wrapper.context[1]}', json.dumps(data))

    return 'Сгенерировано изображение'

