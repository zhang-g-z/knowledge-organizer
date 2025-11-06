# app/utils/extractor.py

def extract_data(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content": prompt}]
    )
    return response.choices[0].message['content']
