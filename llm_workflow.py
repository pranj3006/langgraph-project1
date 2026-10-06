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
class QAState(TypedDict):
    question: str
    answer: str
    
def llm_qa(state: QAState) -> QAState:
    """Uses the LLM to answer the question."""
    question = state["question"]
    prompt = f"Answer the following question: {question}"
    answer = llm.invoke(prompt).content
    state["answer"] = answer
    return state

# Define Graph
graph = StateGraph(QAState)


graph.add_node("llm_qa", llm_qa, description="Answer the question using the LLM.")


graph.add_edge(START, "llm_qa")
graph.add_edge("llm_qa", END)

workflow = graph.compile()  # Compile the graph to check for errors and prepare for execution

initial_state = {
    "question": "What is the capital of France?",
    "answer": ""
}

final_state = workflow.invoke(initial_state)
    
print(final_state)  # Output: {'question': 'What is the capital of France?', 'answer': 'The capital of France is Paris.'}