from langgraph.graph import StateGraph, START, END
from typing import TypedDict
import os
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=OPENAI_API_KEY)

# Define State
class BlogCreatorState(TypedDict):
    topic: str
    outline: str
    content: str
    
    
def create_outline(state: BlogCreatorState) -> BlogCreatorState:
    """Uses the LLM to create a blog outline."""
    topic = state["topic"]
    prompt = f"Create an outline for a blog post about {topic}."
    outline = llm.invoke(prompt).content
    state["outline"] = outline
    return state

def create_content(state: BlogCreatorState) -> BlogCreatorState:
    """Uses the LLM to create blog content."""
    topic = state["topic"]
    outline = state["outline"]
    prompt = f"Write a detailed blog post about {topic} based on the following outline: {outline}"
    content = llm.invoke(prompt).content
    state["content"] = content
    return state

# Define Graph
graph = StateGraph(BlogCreatorState)


graph.add_node("create_outline", create_outline, description="Create a blog outline.")
graph.add_node("create_content", create_content, description="Create a blog content.")


graph.add_edge(START, "create_outline")
graph.add_edge("create_outline", "create_content")
graph.add_edge("create_content", END)

workflow = graph.compile()  # Compile the graph to check for errors and prepare for execution

initial_state = {
    "topic": "Python Programming",
    "outline": "",
    "content": ""
}

final_state = workflow.invoke(initial_state)
    
print(final_state)  # Output: {'question': 'What is the capital of France?', 'answer': 'The capital of France is Paris.'}