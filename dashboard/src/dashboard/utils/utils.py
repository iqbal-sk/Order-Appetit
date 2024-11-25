from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
summarizer = OpenAI()

def summarize_text(text):
    response = summarizer.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant that summarizes text into a single concise statement."},
            {"role": "user",
             "content": f"Summarize the following text into a single statement with precision with max of 15 words in present continuous tense: {text}"}
        ],
        max_tokens=512,
        temperature=0.2
    )
    return response.choices[0].message.content.strip()


def summarize_task(task):
    response = summarizer.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant that summarizes text into a single concise statement."},
            {"role": "user",
             "content": f"Summarize the following text into a single statement with precision with max of 15 words in past tense: {task}"}
        ],
        max_tokens=512,
        temperature=0.2
    )
    return response.choices[0].message.content.strip()