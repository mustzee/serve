#!/usr/bin/env python3
"""
Daily Logic Agent Example
Demonstrates building an intelligent agent for daily tasks and reasoning
Similar to Claude's capabilities but running locally and offline
"""
import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from clients.python.client import LLMClient, Message


class DailyAgent:
    """Intelligent agent for daily tasks and logical reasoning"""

    def __init__(self, base_url: str = "http://localhost:8000", model: str = "llama2"):
        self.client = LLMClient(base_url)
        self.model = model
        self.memory = []  # Agent's memory of interactions

    def think(self, task: str, context: str = "") -> str:
        """
        Think about a task using chain-of-thought reasoning
        """
        system_prompt = """You are an intelligent reasoning agent. When given a task:
1. Break down the problem into steps
2. Think through each step logically
3. Provide a clear, actionable answer
4. Explain your reasoning process"""

        user_prompt = f"Task: {task}"
        if context:
            user_prompt += f"\n\nContext: {context}"

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt)
        ]

        response = self.client.chat(messages=messages, model=self.model, temperature=0.7)
        return response['choices'][0]['message']['content']

    def plan_day(self, tasks: List[str], constraints: List[str] = None) -> str:
        """Plan and prioritize daily tasks"""
        system_prompt = """You are a productivity expert. Help plan and prioritize tasks
considering time constraints, dependencies, and optimal workflow."""

        tasks_str = "\n".join(f"- {task}" for task in tasks)
        user_prompt = f"Plan these tasks:\n{tasks_str}"

        if constraints:
            constraints_str = "\n".join(f"- {c}" for c in constraints)
            user_prompt += f"\n\nConstraints:\n{constraints_str}"

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt)
        ]

        response = self.client.chat(messages=messages, model=self.model, temperature=0.6)
        return response['choices'][0]['message']['content']

    def analyze_decision(self, decision: str, options: List[str], criteria: List[str]) -> str:
        """Help analyze decisions with multiple options"""
        system_prompt = """You are a decision analysis expert. Evaluate options against
criteria, identify pros and cons, and provide a recommendation with reasoning."""

        options_str = "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options))
        criteria_str = "\n".join(f"- {c}" for c in criteria)

        user_prompt = f"""Decision: {decision}

Options:
{options_str}

Criteria:
{criteria_str}

Please analyze each option and provide a recommendation."""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt)
        ]

        response = self.client.chat(messages=messages, model=self.model, temperature=0.5)
        return response['choices'][0]['message']['content']

    def research_topic(self, topic: str, questions: List[str] = None) -> str:
        """Research and explain a topic"""
        system_prompt = """You are a knowledgeable researcher. Provide comprehensive,
accurate information on topics with clear explanations."""

        user_prompt = f"Research topic: {topic}"

        if questions:
            questions_str = "\n".join(f"- {q}" for q in questions)
            user_prompt += f"\n\nSpecific questions:\n{questions_str}"

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt)
        ]

        response = self.client.chat(messages=messages, model=self.model, temperature=0.6)
        return response['choices'][0]['message']['content']

    def problem_solve(self, problem: str, known_facts: List[str] = None) -> str:
        """Solve problems using logical reasoning"""
        system_prompt = """You are a logical problem solver. Use step-by-step reasoning:
1. Understand the problem
2. Identify what you know
3. Determine what you need to find
4. Work through the solution logically
5. Verify your answer"""

        user_prompt = f"Problem: {problem}"

        if known_facts:
            facts_str = "\n".join(f"- {fact}" for fact in known_facts)
            user_prompt += f"\n\nKnown facts:\n{facts_str}"

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt)
        ]

        response = self.client.chat(messages=messages, model=self.model, temperature=0.4)
        return response['choices'][0]['message']['content']

    def interactive_assistant(self):
        """Run interactive assistant mode"""
        system_message = Message(
            role="system",
            content="""You are a helpful personal assistant similar to Claude.
You help with reasoning, planning, research, and daily tasks.
Be friendly, clear, and thorough in your responses."""
        )

        conversation = [system_message]

        print("\nInteractive Assistant Mode")
        print("Type 'exit' to quit, 'clear' to reset conversation")
        print("-" * 50)

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == 'exit':
                    print("Goodbye!")
                    break

                if user_input.lower() == 'clear':
                    conversation = [system_message]
                    print("Conversation cleared.")
                    continue

                conversation.append(Message(role="user", content=user_input))

                print("\nAssistant: ", end="", flush=True)

                full_response = ""
                for chunk in self.client.chat(
                    messages=conversation,
                    model=self.model,
                    stream=True,
                    temperature=0.7
                ):
                    print(chunk, end="", flush=True)
                    full_response += chunk

                print()  # New line
                conversation.append(Message(role="assistant", content=full_response))

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")


def main():
    """Demo the daily agent"""
    print("=== Daily Logic Agent Demo ===")
    print("(Similar to Claude, but local and offline)\n")

    agent = DailyAgent()

    # Check server health
    try:
        health = agent.client.health()
        print(f"✓ Server Status: {health['status']}")
        print(f"✓ Backend: {health['backend']}\n")
    except Exception as e:
        print(f"✗ Server not available: {e}")
        print("Please start the server first")
        return

    # Example 1: Logical reasoning
    print("1. Logical Reasoning")
    print("-" * 50)
    task = "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?"
    print(f"Task: {task}\n")
    result = agent.think(task)
    print(f"Answer:\n{result}\n")

    # Example 2: Day planning
    print("\n2. Day Planning")
    print("-" * 50)
    tasks = [
        "Write project report (2 hours)",
        "Team meeting (1 hour)",
        "Code review (1.5 hours)",
        "Workout (1 hour)",
        "Lunch break",
    ]
    constraints = [
        "Team meeting is at 2 PM",
        "Need to submit report by end of day",
        "Prefer to workout in the morning"
    ]
    print(f"Tasks: {', '.join(tasks)}")
    print(f"Constraints: {', '.join(constraints)}\n")
    plan = agent.plan_day(tasks, constraints)
    print(f"Plan:\n{plan}\n")

    # Example 3: Decision analysis
    print("\n3. Decision Analysis")
    print("-" * 50)
    decision = "Choose a backend for local LLM serving"
    options = ["Ollama", "llama.cpp", "vLLM"]
    criteria = ["Ease of setup", "Performance", "Offline capability", "Memory usage"]
    result = agent.analyze_decision(decision, options, criteria)
    print(f"Analysis:\n{result}\n")

    # Example 4: Interactive mode
    print("\n4. Interactive Assistant")
    print("-" * 50)
    agent.interactive_assistant()


if __name__ == "__main__":
    main()
