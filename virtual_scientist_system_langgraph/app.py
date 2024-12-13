from flask import Flask, render_template, request
from groq import Groq
from prompts import S1_PROMPT, S2_PROMPT, S3_PROMPT, GROQ_FINAL_PROMPT
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import TypedDict
from database import store_query_response

# Load environment variables (if any)
from dotenv import load_dotenv
load_dotenv()

# Define the state class for managing the scientist's state
class ScientistState(TypedDict):
    topic: str
    s0_response: str
    s1_response: str
    s2_response: str
    s3_response: str
    final_abstract: str
    additional_notes: str

# Define the Scientist class for querying the tools
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
            max_tokens=1500,
            top_p=1,
            stream=False,  # Disable streaming for a direct response
            stop=None,
        )
        self.response = completion.choices[0].message.content  # Access the response directly
        print(f"Response from {self.name}: {self.response}")
        return self.response

# Task functions for each part of the process
def start(state: ScientistState):
    print("Starting the process...")
    return state

def query_agent_s0(state: ScientistState):
    # S0 is now asking the topic question
    groq_agent = Groq()
    scientist_s0 = Scientist("S0", groq_agent, "Ask the team for their insights on the topic: {state['topic']}.")
    s0_response = scientist_s0.query_tool(state['topic'])
    return {'additional_notes': s0_response}

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
    final_abstract = f"""
    This is the final abstract generated from all thorough discussion with the team:

    S1 Findings:
    {state['s1_response']}

    S2 Findings:
    {state['s2_response']}

    S3 Findings:
    {state['s3_response']}

    Summary:
    {state['s1_response']} {state['s2_response']} {state['s3_response']}
    """

    # Generate the final abstract with Groq
    client = Groq()
    completion = client.chat.completions.create(
        model="llama3-8b-8192",  # Use the appropriate model
        messages=[{"role": "system", "content": final_abstract}],
        temperature=0.7,
    )
    
    final_abstract_response = completion.choices[0].message.content
    store_query_response(state['topic'], final_abstract_response)

    return {'final_abstract': final_abstract_response}

# Define the graph and workflow
def create_workflow():
    workflow = StateGraph(ScientistState)

    workflow.add_node("start", start)
    workflow.add_node("query_s0", query_agent_s0)
    workflow.add_node("query_s1", query_agent_s1)
    workflow.add_node("query_s2", query_agent_s2)
    workflow.add_node("query_s3", query_agent_s3)
    workflow.add_node("abstract_generation", abstract_generation)

    workflow.add_edge(START, "start")
    workflow.add_edge("start", "query_s0")  # S0 starts the conversation
    workflow.add_edge("query_s0", "query_s1")  # S0 talks to S1
    workflow.add_edge("query_s0", "query_s2")  # S0 talks to S2
    workflow.add_edge("query_s0", "query_s3")  # S0 talks to S3
    workflow.add_edge("query_s1", "abstract_generation")  # After S1, generate abstract
    workflow.add_edge("query_s2", "abstract_generation")  # After S2, generate abstract
    workflow.add_edge("query_s3", "abstract_generation")  # After S3, generate abstract
    workflow.add_edge("abstract_generation", END)

    return workflow

app = Flask(__name__)

# Define the endpoint for the form
@app.route("/", methods=["GET", "POST"])
def index():
    final_abstract = ""
    
    if request.method == "POST":
        topic = request.form.get("topic")
        
        if topic:
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
            app_flow = workflow.compile()
            result = app_flow.invoke(state_obj)

            # Get the final abstract response
            final_abstract = result['final_abstract']
    
    return render_template("index.html", final_abstract=final_abstract)

if __name__ == "__main__":
    app.run(debug=True)
