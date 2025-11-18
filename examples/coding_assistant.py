#!/usr/bin/env python3
"""
Coding Assistant Example
Demonstrates using Local LLM for code generation, review, and debugging
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from clients.python.client import LLMClient, Message


class CodingAssistant:
    """AI-powered coding assistant"""

    def __init__(self, base_url: str = "http://localhost:8000", model: str = "codellama"):
        self.client = LLMClient(base_url)
        self.model = model
        self.conversation_history = []

    def generate_code(self, prompt: str, language: str = "python") -> str:
        """Generate code based on prompt"""
        system_message = Message(
            role="system",
            content=f"You are an expert {language} programmer. Generate clean, "
                    f"efficient, and well-documented code."
        )

        user_message = Message(
            role="user",
            content=f"Generate {language} code for: {prompt}"
        )

        messages = [system_message, user_message]
        response = self.client.chat(messages=messages, model=self.model, temperature=0.3)

        return response['choices'][0]['message']['content']

    def review_code(self, code: str, language: str = "python") -> str:
        """Review code and provide suggestions"""
        system_message = Message(
            role="system",
            content="You are a senior code reviewer. Provide constructive feedback "
                    "on code quality, potential bugs, performance, and best practices."
        )

        user_message = Message(
            role="user",
            content=f"Review this {language} code:\n\n```{language}\n{code}\n```"
        )

        messages = [system_message, user_message]
        response = self.client.chat(messages=messages, model=self.model, temperature=0.5)

        return response['choices'][0]['message']['content']

    def debug_code(self, code: str, error: str, language: str = "python") -> str:
        """Help debug code with errors"""
        system_message = Message(
            role="system",
            content="You are an expert debugger. Analyze code errors and provide "
                    "clear explanations and fixes."
        )

        user_message = Message(
            role="user",
            content=f"Debug this {language} code:\n\n"
                    f"Code:\n```{language}\n{code}\n```\n\n"
                    f"Error:\n```\n{error}\n```"
        )

        messages = [system_message, user_message]
        response = self.client.chat(messages=messages, model=self.model, temperature=0.3)

        return response['choices'][0]['message']['content']

    def explain_code(self, code: str, language: str = "python") -> str:
        """Explain what code does"""
        system_message = Message(
            role="system",
            content="You are a technical educator. Explain code clearly and concisely."
        )

        user_message = Message(
            role="user",
            content=f"Explain this {language} code:\n\n```{language}\n{code}\n```"
        )

        messages = [system_message, user_message]
        response = self.client.chat(messages=messages, model=self.model, temperature=0.5)

        return response['choices'][0]['message']['content']

    def chat_stream(self, user_input: str):
        """Interactive chat with streaming"""
        self.conversation_history.append(Message(role="user", content=user_input))

        print("Assistant: ", end="", flush=True)
        full_response = ""

        for chunk in self.client.chat(
            messages=self.conversation_history,
            model=self.model,
            stream=True
        ):
            print(chunk, end="", flush=True)
            full_response += chunk

        print()  # New line after streaming
        self.conversation_history.append(
            Message(role="assistant", content=full_response)
        )


def main():
    """Demo the coding assistant"""
    print("=== Coding Assistant Demo ===\n")

    assistant = CodingAssistant()

    # Check if server is available
    try:
        health = assistant.client.health()
        print(f"✓ Server Status: {health['status']}")
        print(f"✓ Backend: {health['backend']}")
        print(f"✓ Models: {', '.join(health['models_loaded'])}\n")
    except Exception as e:
        print(f"✗ Server not available: {e}")
        print("Please start the server first: python -m server.main")
        return

    # Example 1: Generate code
    print("1. Generate Code")
    print("-" * 50)
    prompt = "Create a function to calculate fibonacci numbers with memoization"
    print(f"Prompt: {prompt}\n")
    code = assistant.generate_code(prompt, "python")
    print(f"Generated Code:\n{code}\n")

    # Example 2: Review code
    print("\n2. Review Code")
    print("-" * 50)
    sample_code = """
def sum_list(lst):
    total = 0
    for i in range(len(lst)):
        total = total + lst[i]
    return total
"""
    print(f"Code to review:{sample_code}")
    review = assistant.review_code(sample_code.strip(), "python")
    print(f"Review:\n{review}\n")

    # Example 3: Interactive chat
    print("\n3. Interactive Chat (type 'exit' to quit)")
    print("-" * 50)

    assistant.conversation_history = [
        Message(
            role="system",
            content="You are a helpful coding assistant for Python and Go."
        )
    ]

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break

            if not user_input:
                continue

            assistant.chat_stream(user_input)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
