from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai_llm = OpenAI()

def summarize_text(text):
    response = openai_llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant that summarizes text into a single concise statement."},
            {"role": "user",
             "content": f"Summarize the following text into a single statement with precision with max of 15 words in present continuous tense with out any subject: {text}"}
        ],
        max_tokens=512,
        temperature=0.2
    )
    return response.choices[0].message.content.strip()


def summarize_task(task):
    response = openai_llm.chat.completions.create(
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


def extract_last_meaningful_query(conversation_history):
    # Prepare the conversation history for the OpenAI model


    prompt = f"""
                Given the following conversation history, 
                1. First Identify whether the most recent user request is normal conversational user prompt or not, if yes simply return No meaningful query found
                
                If most recent user request is about unresolved query or inaccurate query results then 
                identify and extract the meaningful user query about retrieving
                data from a database (about sales) with having detailed query about something over database. Ignore messages having
                "retry", "try again" or something similar to them. If user provides with few suggestions on what to do, then mention them as well in query.
                If no meaningful query was found,
                the model might return "No meaningful query found"

                Conversation history:
                {conversation_history}

                Most recent meaningful query:"""

    try:
        response = openai_llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant that extracts the meaningful 'User' query from a conversation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=16384,
            temperature=0.0
        )

        extracted_query = response.choices[0].message.content.strip()

        # If no meaningful query was found, the model might return something like "No meaningful query found"
        if "no meaningful query" in extracted_query.lower():
            return None

        return extracted_query

    except Exception as e:
        print(f"Error in extracting query: {str(e)}")
        return None