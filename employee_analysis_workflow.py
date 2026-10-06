from langgraph.graph import StateGraph, START, END
from typing import TypedDict
import os
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# load_dotenv(override=True)

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# llm = ChatOpenAI(
#     model_name="gpt-3.5-turbo",
#     temperature=0,
#     openai_api_key=OPENAI_API_KEY)

# Define State
class EmployeeState(TypedDict):
    employee_name: str
    monthly_salary: float
    working_days: int
    completed_projects: int

    yearly_salary: float
    bonus: float
    project_status: str
    summary: str
    
def calculate_bonus(state: EmployeeState) -> dict:
    """Calculates the employee bonus."""
    # Placeholder implementation - replace with actual bonus calculation logic
    state["bonus"] = state["monthly_salary"] * 0.1  # Example bonus calculation
    return {"bonus":state["bonus"]}

def calculate_yearly_salary(state: EmployeeState) -> EmployeeState:
    """Calculates the employee yearly salary."""
    # Placeholder implementation - replace with actual yearly salary calculation logic
    state["yearly_salary"] = state["monthly_salary"] * 12  # Example yearly salary calculation
    return {"yearly_salary":state["yearly_salary"]}

def calculate_project_status(state: EmployeeState) -> EmployeeState:
    """Calculates the employee project status."""
    # Placeholder implementation - replace with actual project status calculation logic
    if state["completed_projects"] >= 5:
        state["project_status"] = "Excellent"
    elif state["completed_projects"] >= 3:
        state["project_status"] = "Good"
    else:
        state["project_status"] = "Needs Improvement"
    return {"project_status":state["project_status"]}

def summary(state: EmployeeState) -> EmployeeState:
    """Generates a summary of the employee's performance."""
    state["summary"] = (
        f"Employee: {state['employee_name']}\n"
        f"Yearly Salary: ${state['yearly_salary']:.2f}\n"
        f"Bonus: ${state['bonus']:.2f}\n"
        f"Project Status: {state['project_status']}"
    )
    return {"summary":state["summary"]}

# Define Graph
graph = StateGraph(EmployeeState)


graph.add_node("calculate_bonus", calculate_bonus, description="Calculate the employee bonus.")
graph.add_node("calculate_yearly_salary", calculate_yearly_salary, description="Calculate the employee yearly salary.")
graph.add_node("calculate_project_status", calculate_project_status, description="Calculate the employee project status.")
graph.add_node("summary", summary, description="Calculate the employee summary.")


graph.add_edge(START, "calculate_bonus")
graph.add_edge(START, "calculate_yearly_salary")
graph.add_edge(START, "calculate_project_status")

graph.add_edge("calculate_bonus", "summary")
graph.add_edge("calculate_yearly_salary", "summary")
graph.add_edge("calculate_project_status", "summary")

graph.add_edge("summary", END)

workflow = graph.compile()  # Compile the graph to check for errors and prepare for execution

initial_state = {
    "employee_name": "John Doe",
    "monthly_salary": 5000.0,
    "working_days": 20,
    "completed_projects": 4
}

final_state = workflow.invoke(initial_state)
    
print(final_state)  # Output: {'question': 'What is the capital of France?', 'answer': 'The capital of France is Paris.'}