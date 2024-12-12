import asyncio
from groq import Groq
from prompts import S1_PROMPT, S2_PROMPT, S3_PROMPT, GROQ_FINAL_PROMPT, S0_START_PROMPT, S0_END_PROMPT
from dotenv import load_dotenv
from langgraph.graph import Graph, StateGraph, START, END
from pydantic import BaseModel, Field
from typing import TypedDict, List, Any

load_dotenv()

class ScientistState(TypedDict):
    topic: str
    s1_response: str
    s2_response: str
    s3_response: str
    final_abstract: str
    additional_notes: str

# Define Scientist class
class Scientist:
    def __init__(self, name, agent, prompt):
        self.name = name
        self.agent = agent
        self.prompt = prompt
        self.response = None

    def query_tool(self, topic):
        print(f"{self.name} is querying the agent for the topic '{topic}'...")
        # Use Groq's chat completion for querying (assuming it's synchronous)
        completion = self.agent.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": self.prompt}, {"role": "user", "content": topic}],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,  # Disable streaming for a direct response
            stop=None,
        )
        self.response = completion.choices[0].message.content  # Access the response directly
        print(f"Response from {self.name}: {self.response}")
        return self.response

# Define the task functions for each node in the workflow
def start(state: ScientistState):
    print("Starting the process...")
    return state

def query_agent_s1(state: ScientistState):
    groq_agent = Groq()
    scientist_s1 = Scientist("S1", groq_agent, S1_PROMPT)
    response = scientist_s1.query_tool(state['topic'])
    return {'s1_response': response}

def query_agent_s2(state: ScientistState):
    groq_agent = Groq()
    scientist_s2 = Scientist("S2", groq_agent, S2_PROMPT)
    response = scientist_s2.query_tool(state['topic'])
    return {'s2_response': response}

def query_agent_s3(state: ScientistState):
    groq_agent = Groq()
    scientist_s3 = Scientist("S3", groq_agent, S3_PROMPT)
    response = scientist_s3.query_tool(state['topic'])
    return {'s3_response': response}

def abstract_generation(state: ScientistState):
    # Format the final abstract using the responses gathered from the scientists
    final_abstract = GROQ_FINAL_PROMPT.format(
        S1_FINDINGS=state['s1_response'],
        S2_FINDINGS=state['s2_response'],
        S3_FINDINGS=state['s3_response']
    )

    # Generate the final abstract with Groq
    client = Groq()
    completion = client.chat.completions.create(
        model="llama3-8b-8192",  # Use the appropriate model
        messages=[{"role": "system", "content": final_abstract}],
        temperature=0.7,
    )
    
    final_abstract_response = completion.choices[0].message.content
    return {'final_abstract': final_abstract_response}

# Define the graph and workflow
def create_workflow():
    # Create the state graph for managing the flow
    workflow = StateGraph(ScientistState)

    # Add nodes (functions) to the graph
    workflow.add_node("start", start)
    workflow.add_node("query_s1", query_agent_s1)
    workflow.add_node("query_s2", query_agent_s2)
    workflow.add_node("query_s3", query_agent_s3)
    workflow.add_node("abstract_generation", abstract_generation)

    # Add edges to define the flow of tasks
    workflow.add_edge(START, "start")
    
    # Use conditional edges to handle concurrent processing
    workflow.add_conditional_edges(
        "start", 
        lambda _: ["query_s1", "query_s2", "query_s3"],
        {
            "query_s1": "query_s1",
            "query_s2": "query_s2",
            "query_s3": "query_s3"
        }
    )

    # Connect agent query nodes to abstract generation
    workflow.add_edge("query_s1", "abstract_generation")
    workflow.add_edge("query_s2", "abstract_generation")
    workflow.add_edge("query_s3", "abstract_generation")
    
    # End the process after abstract generation
    workflow.add_edge("abstract_generation", END)

    return workflow

def main():
    while True:
        # Get user input for the query
        topic = input("Enter the topic for query (or 'exit' to quit: ").strip()

        if topic.lower() == 'exit':
            print("Exiting the program.")
            break

        if not topic:
            print("Error: Topic cannot be empty. Please enter a valid topic.")
            continue

        # Initialize the workflow
        workflow = create_workflow()

        # Initialize the state object
        state_obj = {
            'topic': topic,
            's1_response': '',
            's2_response': '',
            's3_response': '',
            'final_abstract': '',
            'additional_notes': ''
        }

        # Execute the workflow
        app = workflow.compile()
        result = app.invoke(state_obj)

        # Print the final abstract
        print("Final Abstract:\n")
        print(result['final_abstract'])

if __name__ == "__main__":
    main()