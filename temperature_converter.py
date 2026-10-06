from langgraph.graph import StateGraph, START, END

from typing import TypedDict


# Define State
class TemperatureState(TypedDict):
    input_temperature: float
    input_unit: str
    output_unit: str
    output_temperature: float
    weather_status: str


def convert_temperature(state: TemperatureState) -> TemperatureState:
    """Converts temperature from one unit to another."""
    if state["input_unit"] == state["output_unit"]:
        state["output_temperature"] = state["input_temperature"]
        return state

    # Convert input temperature to Celsius
    if state["input_unit"] == "C":
        celsius = state["input_temperature"]
    elif state["input_unit"] == "F":
        celsius = (state["input_temperature"] - 32) * 5.0 / 9.0
    elif state["input_unit"] == "K":
        celsius = state["input_temperature"] - 273.15
    else:
        raise ValueError(f"Unsupported input unit: {state['input_unit']}")

    # Convert Celsius to output unit
    if state["output_unit"] == "C":
        state["output_temperature"] = celsius
    elif state["output_unit"] == "F":
        state["output_temperature"] = (celsius * 9.0 / 5.0) + 32
    elif state["output_unit"] == "K":
        state["output_temperature"] = celsius + 273.15
    else:
        raise ValueError(f"Unsupported output unit: {state['output_unit']}")
    return state

def label_weather(state: TemperatureState) -> TemperatureState:
    """Labels the weather based on the output temperature."""
    temp = state["output_temperature"]
    if temp < 0:
        state["weather_status"] = "Freezing"
    elif 0 <= temp < 10:
        state["weather_status"] = "Cold"
    elif 10 <= temp < 20:
        state["weather_status"] = "Cool"
    elif 20 <= temp < 30:
        state["weather_status"] = "Warm"
    else:
        state["weather_status"] = "Hot"
    return state

# Define Graph
temperature_graph = StateGraph(TemperatureState)


temperature_graph.add_node("convert_temperature", convert_temperature, description="Convert the temperature from input unit to output unit.")
temperature_graph.add_node("label_weather",label_weather, description="Label the weather based on the temperature.")


temperature_graph.add_edge(START, "convert_temperature")
temperature_graph.add_edge("convert_temperature", "label_weather")
temperature_graph.add_edge("label_weather", END)

workflow = temperature_graph.compile()  # Compile the graph to check for errors and prepare for execution

initial_state = {
    "input_temperature": 35.0,
    "input_unit": "C",
    "output_unit": "F",
    "output_temperature": 0.0,
    "weather_status": ""
}

final_state = workflow.invoke(initial_state)

print(final_state)  # Output: {'input_temperature': 100.0, 'input_unit': 'C', 'output_unit': 'F', 'output_temperature': 212.0}