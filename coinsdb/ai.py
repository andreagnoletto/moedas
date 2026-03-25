import json

from django.conf import settings
from openai import OpenAI


def ask_openai(system_prompt, user_prompt):
    """Chama a OpenAI e retorna o JSON parseado. Levanta exceção em caso de erro."""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-5.2",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )
    return json.loads(response.choices[0].message.content)


def has_api_key():
    return bool(settings.OPENAI_API_KEY)
