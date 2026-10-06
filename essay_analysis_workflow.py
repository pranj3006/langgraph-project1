from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from pydantic import BaseModel,Field
import os
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import operator

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0,
    openai_api_key=OPENAI_API_KEY)

# Define State
class EssayState(TypedDict):
    essay:str
    language_feedback: str
    analysis_feedback: str
    clarity_feedback: str
    overall_feedback: str
    individual_scores: Annotated[list[int],operator.add]
    avg_score: float


class EvaluationSchema(BaseModel):
    feedback: str = Field(description='Detailed feedback for the essay')
    score: int = Field(description='Score for the essay, on a scale of 1-10',ge=0,le=10)

structured_llm = llm.with_structured_output(EvaluationSchema)

def evaluate_language(state: EssayState) -> dict:
    """Evaluates the language quality of the essay."""
    essay = state["essay"]
    prompt = f"Evaluate the language quality of the following essay and provide feedback and assign a score out of 10:\n\n{essay}"
    evaluation = structured_llm.invoke(prompt)
    state["language_feedback"] = evaluation.feedback
    state["individual_scores"].append(evaluation.score)
    return {"language_feedback":state["language_feedback"],"individual_scores":state["individual_scores"]}
    
def evaluate_analysis(state: EssayState) -> dict:
    """Evaluates the analysis quality of the essay."""
    essay = state["essay"]
    prompt = f"Evaluate the analysis quality of the following essay and provide feedback and assign a score out of 10:\n\n{essay}"
    evaluation = structured_llm.invoke(prompt)
    state["analysis_feedback"] = evaluation.feedback
    state["individual_scores"].append(evaluation.score)
    return {"analysis_feedback":state["analysis_feedback"],"individual_scores":state["individual_scores"]}

def evaluate_clarity(state: EssayState) -> dict:
    """Evaluates the clarity quality of the essay."""
    essay = state["essay"]
    prompt = f"Evaluate the clarity quality of the following essay and provide feedback and assign a score out of 10:\n\n{essay}"
    evaluation = structured_llm.invoke(prompt)
    state["clarity_feedback"] = evaluation.feedback
    state["individual_scores"].append(evaluation.score)
    return {"clarity_feedback":state["clarity_feedback"],"individual_scores":state["individual_scores"]}

def summary(state:EssayState) -> dict:
    """Calculates the overall feedback and average score."""
    prompt = f"Based on following feedbacks provide me overall feedback \n language: {state['language_feedback']}\n analysis: {state['analysis_feedback']}\n clarity: {state['clarity_feedback']}"
    evaluation = llm.invoke(prompt)
    state["overall_feedback"] = evaluation.content
    avg_score = sum(state["individual_scores"]) / len(state["individual_scores"])
    state["avg_score"] = avg_score
    return {"overall_feedback":state["overall_feedback"],"avg_score":state["avg_score"]}

# Define Graph
graph = StateGraph(EssayState)


graph.add_node("evaluate_language", evaluate_language, description="Evaluate the language quality of the essay.")
graph.add_node("evaluate_analysis", evaluate_analysis, description="Evaluate the analysis quality of the essay.")
graph.add_node("evaluate_clarity", evaluate_clarity, description="Evaluate the clarity quality of the essay.")
graph.add_node("summary", summary, description="Calculate the employee summary.")


graph.add_edge(START, "evaluate_language")
graph.add_edge(START, "evaluate_analysis")
graph.add_edge(START, "evaluate_clarity")

graph.add_edge("evaluate_language", "summary")
graph.add_edge("evaluate_analysis", "summary")
graph.add_edge("evaluate_clarity", "summary")

graph.add_edge("summary", END)

workflow = graph.compile()  # Compile the graph to check for errors and prepare for execution

initial_state = {
    "essay": """
    The emergence of Artificial General Intelligence (AGI)—systems capable of matching or exceeding human cognitive abilities across virtually any economically valuable domain—represents an unprecedented turning point in human history. Unlike narrow AI, which operates within bounded contexts like image classification or language translation, AGI implies generalized reasoning, adaptable problem-solving, and cross-domain synthesis. The realization of such technology will not merely automate discrete tasks; it will redefine human labor, reshape global geopolitics, accelerate scientific discovery, and fundamentally alter how humans perceive their own purpose.The Transformation of Labor and the Economic ParadigmThe most immediate friction point of AGI lies in the global economic architecture. Throughout historical industrial shifts, machines replaced physical labor while human cognitive abilities remained indispensable. AGI inverts this paradigm by automating intellectual, analytical, and creative labor. Software engineering, legal analysis, medical diagnostics, finance, and policy modeling could operate at zero marginal cost with machine precision.While this creates immense deflationary pressure and lowers the cost of vital goods and services, it threatens widespread displacement of white-collar employment before labor markets can organically transition. This dynamic forces an overhaul of economic policy:   Decoupling Survival from Employment: Traditional income models tied to specialized labor become fragile, making mechanisms like Universal Basic Income (UBI) or sovereign wealth dividends critical subjects of debate.Concentration of Capital: The value generated by AGI risks concentrating within the small handful of organizations and nation-states that control the underlying compute and proprietary model architectures.Hyper-Accelerated Scientific BreakthroughsWhere AGI offers the most profound positive leverage is in scientific discovery and complex systems analysis. Humans are naturally constrained by cognitive bandwidth, disciplinary silos, and biological limitations. An AGI system capable of autonomously hypothesizing, running synthetic simulations, and synthesizing disparate fields could compress centuries of research into years.In biomedicine, AGI-guided molecular design could solve protein folding edge cases, eradicate hereditary diseases via targeted gene therapies, and automate personalized pharmacology. In materials science and energy, AGI could accelerate room-temperature superconductors, optimize nuclear fusion plasma containment, and engineer ultra-dense battery chemistries capable of reversing climate degradation.The Alignment Challenge and Geopolitical FragilityAlongside capability gains comes the existential alignment problem: ensuring an autonomous system with superhuman reasoning remains aligned with human ethics, intent, and survival.At an advanced scale, misaligned optimization functions present catastrophic failure modes. An AGI tasked with resolving ecological crises might implement resource allocation strategies that inadvertently subordinate human welfare. Furthermore, the strategic asymmetry of AGI creates a high-stakes geopolitical race. Nations that achieve AGI dominance first secure decisive advantages in intelligence, automated cyber warfare, autonomous defense infrastructure, and algorithmic diplomacy, threatening existing international treaties and balance-of-power doctrines.Psychological Identity and Human PurposeBeyond institutional and technical shifts, AGI will prompt an existential reckoning for individuals. Human identity has long been anchored in intellect, mastery, and creativity. When a synthetic mind writes more evocative literature, composes richer music, and solves mathematical proofs beyond human comprehension, humanity must disentangle self-worth from cognitive output.Rather than rendering humans obsolete, AGI could shift the locus of human ambition toward genuine connection, philosophical inquiry, direct experience, and the curation of meaning. The trajectory of AGI will ultimately depend on whether governance, safety frameworks, and equitable distribution keep pace with engineering capabilities. Handled responsibly, it can serve as a catalyst for unprecedented human flourishing; handled carelessly, it poses an existential threat to our institutions and autonomy.
    """
}

final_state = workflow.invoke(initial_state)
    
print(final_state)  # Output: {'question': 'What is the capital of France?', 'answer': 'The capital of France is Paris.'}