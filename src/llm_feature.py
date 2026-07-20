from ollama import chat
from schemas import LLMOutput

# Step 1: Convert the email text to lowercase
# Step 2: Look for words associated with each category
# Step 3: Return the matching category and a summary

# Billing keywords: 
# 1. "invoice"
# 2. "payment"
# 3. "billing"
# 4. "charge"
# 5. "refund"

# Technical keywords:
# 1. "error"
# 2. "bug"
# 3. "connection"
# 4. "disconnect"
# 5. "crash"

# Account keywords:
# 1. "account"
# 2. "login"
# 3. "password"
# 4. "security"
# 5. "profile"

def classify_email_baseline(email_text: str) -> LLMOutput:
    normalized_email = email_text.lower()

    billing_keywords = ["invoice", "payment", "billing", "charge", "refund"]
    
    technical_keywords = ["error", "bug", "connection", "disconnect", "crash"]

    account_keywords = ["account", "login", "password", "security", "profile"]

    has_billing_keyword = any(keyword in normalized_email for keyword in billing_keywords)
    has_technical_keyword = any(keyword in normalized_email for keyword in technical_keywords)
    has_account_keyword = any(keyword in normalized_email for keyword in account_keywords)

    if has_billing_keyword:
        return LLMOutput(
            category="billing",
            summary="The customer is inquiring about billing or payment issues."
        )

    if has_technical_keyword:
        return LLMOutput(
            category="technical",
            summary="The customer is reporting a technical issue."
        )

    if has_account_keyword:
        return LLMOutput(
            category="account",
            summary="The customer is seeking assistance with account-related matters."
        )

    return LLMOutput(
        category="general",
        summary="The customer is requesting help with an order."
    )


def classify_email_ollama(email_text: str, system_prompt: str) -> LLMOutput:
    print("USING OLLAMA CLASSIFIER")
    
    
    response = chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": email_text
            }
        ],
        format=LLMOutput.model_json_schema(),
        options={
            "temperature": 0
        }
    )

    return LLMOutput.model_validate_json(
        response.message.content
    )


def classify_email(email_text: str, system_prompt: str) -> LLMOutput:
    return classify_email_ollama(email_text, system_prompt)

