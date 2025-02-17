from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
import random


class State(TypedDict):
    state: str

def first(state):
    print("========= Node: first =========")
    return {'state': state['state'] + "I am "}

def second(state):
    print("========= Node: second =========")
    return {'state': state['state'] + "happy :)"}

def third(state):
    print("========= Node: third =========")
    return {'state': state['state'] + "sad :("}

def mood(state) -> Literal["second", "third"]:
    if random.random() < 0.5:
        return "second"
    return "third"


if __name__ == '__main__':

    builder = StateGraph(State)

    builder.add_node("first", first)
    builder.add_node("second", second)
    builder.add_node("third", third)


    builder.add_edge(START, "first")
    builder.add_conditional_edges("first", mood)
    builder.add_edge("second", END)
    builder.add_edge("third", END)

    graph = builder.compile()

    graph.invoke({'state': "hey there! "})