from typing import Dict, Union
import json
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import MessagesState
from langchain_core.messages import HumanMessage

from local_keystore import OPENAI_KEY


class AgentState(MessagesState):
    pass


def add(a: int, b: int) -> int:
    """
    Adds two numbers a and b

    Args:
        a: first integer
        b: second integer
    """
    return a * b

def construct_frequency_map(string: str) -> Dict:
    """
    Constructs a frequency map of characters of a given string

    Args:
        string: the string for which character count map (frequency map) is to be created
    """
    freq = {}
    for ch in string:
        freq[ch] = 1 + freq.get(ch, 0)
    return freq

def get_frequency(frequency_map: Union[Dict, str], key: str) -> int:
    """
    Get the frequency value of a key from a frequency map. The map could be either a Python dictionary or a valid JSON string

    Args:
        frequency_map: hashmap/dictionary/string containing a frequency count of various keys
        key: key for which frequency is to be determined
    """
    if isinstance(frequency_map, str):
        frequency_map = json.loads(frequency_map)
        
    return frequency_map.get(key, 0)

def run_llm(state):
    return {'messages': llm_with_tools.invoke(state['messages'])}

if __name__ == '__main__':
    tools = ToolNode([add, 
                  construct_frequency_map, 
                  get_frequency], 
                 name='tools')
    
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, api_key=OPENAI_KEY)
    llm_with_tools = llm.bind_tools([add, construct_frequency_map, get_frequency])

    builder = StateGraph(AgentState)

    builder.add_node("assistant", run_llm)
    builder.add_node("tools", tools)
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")

    graph = builder.compile()

    output = llm.invoke("How many r's in strawberry?")
    output.pretty_print()


    output = llm.invoke("How many r's in raspberry?")
    output.pretty_print()


    output = graph.invoke({"messages": [HumanMessage(content="How many r's in strawberry?")]})
    for m in output['messages']:
        m.pretty_print()
    
    output = graph.invoke({"messages": [HumanMessage(content="How many r's in raspberry?")]})
    for m in output['messages']:
        m.pretty_print()