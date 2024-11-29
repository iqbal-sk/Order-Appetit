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


def extract_last_meaningful_query(conversation_history, user_query):
    # Prepare the conversation history for the OpenAI model

    prompt = f"""
    Given a conversation about data analysis, transform user query by:
    
    1. Context Understanding:
        - Previous analysis context: {conversation_history}
        - Current question: {user_query}
        - Related metrics mentioned earlier
        
    If current query has no relevance to the previous conversation, then don't make any assumptions based on previous current history
    
    2. Query Enhancement:
        - If query is conversational, simply return No meaningful query found
        - Extract specific KPIs and metrics needed
        - Identify time periods and frequencies
        - Determine required data dimensions
        - Add business context
    
    3. Generate Analysis Request:
    "Based on our discussion about Previous analysis context, please analyze:
    - Primary metrics: [specific metrics]
    - Time period: [specified timeframe] (If no time specified, consider it as "till now"
    - Analysis goal: [business objective]
    - Additional context: [relevant background]"
    """

    print(prompt)

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