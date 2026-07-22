from ollama import chat


response = chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: connection successful"
        }
    ]
)

print(response.message.content)