# app/utils/extractor_async.py

import openai
import asyncio

async def extract_data(prompt):
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content": prompt}]
    )
    return response.choices[0].message['content']
