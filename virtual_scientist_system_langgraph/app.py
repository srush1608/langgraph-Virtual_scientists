from flask import Flask, render_template, request
from groq import Groq
from prompts import S1_PROMPT, S2_PROMPT, S3_PROMPT, GROQ_FINAL_PROMPT,S0_START_PROMPT
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import TypedDict
from database import store_query_response


from dotenv import load_dotenv
load_dotenv()

class ScientistState(TypedDict):
    topic: str
    s1_response: str
    s2_response: str
    s3_response: str
    final_abstract: str
    additional_notes: str

class Scientist:
    def __init__(self, name, agent, prompt):
        self.name = name
        self.agent = agent
        self.prompt = prompt
        self.response = None

    def query_tool(self, topic):
        print(f"{self.name} is querying the agent for the topic '{topic}'...")
        completion = self.agent.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": self.prompt}, {"role": "user", "content": topic}],
            temperature=1,
            max_tokens=1500,  
            top_p=1,
            stream=False,  
            stop=None,
        )
        self.response = completion.choices[0].message.content  
        print(f"Response from {self.name}: {self.response}")
        return self.response

def start(state: ScientistState):
    print("Starting the process...")
    return state

def query_agent_s0(state: ScientistState):
    # S0 is now asking the topic question
    groq_agent = Groq()
    scientist_s0 = Scientist("S0", groq_agent, S0_START_PROMPT)
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
    final_abstract_prompt = f"""
    You professional summarizer. Your task is to generate a concise and well-structured abstract by summarizing the below responses:

    1. Key insights from S1: {state['s1_response']}
    2. Additional details provided by S2: {state['s2_response']}
    3. Further perspectives shared by S3: {state['s3_response']}
    4. Abstract should be only between 300-400 words. 
    5. STRICTLY provide only the abstract.
    6. Strictly rely on the provided text, without external information.
    7. Your response should directly start with the abstract without any external metadata.
    """

    client = Groq()
    completion = client.chat.completions.create(
        model="llama3-8b-8192",  
        messages=[{"role": "system", "content": final_abstract_prompt}],
        temperature=0.7,
        max_tokens=500,  
    )

    final_abstract_response = completion.choices[0].message.content.strip()

    store_query_response(state['topic'], final_abstract_response)

    print(f"Generated Abstract: {final_abstract_response}")

    return {'final_abstract': final_abstract_response}

def create_workflow():
    workflow = StateGraph(ScientistState)

    workflow.add_node("start", start)
    workflow.add_node("query_s0", query_agent_s0)
    workflow.add_node("query_s1", query_agent_s1)
    workflow.add_node("query_s2", query_agent_s2)
    workflow.add_node("query_s3", query_agent_s3)
    workflow.add_node("abstract_generation", abstract_generation)

    workflow.add_edge(START, "start")
    workflow.add_edge("start", "query_s0")  
    workflow.add_edge("query_s0", "query_s1") 
    workflow.add_edge("query_s0", "query_s2")  
    workflow.add_edge("query_s0", "query_s3")  
    workflow.add_edge("query_s1", "abstract_generation")  
    workflow.add_edge("query_s2", "abstract_generation")  
    workflow.add_edge("query_s3", "abstract_generation") 
    workflow.add_edge("abstract_generation", END)

    return workflow

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    final_abstract = ""
    
    if request.method == "POST":
        topic = request.form.get("topic")
        
        if topic:
            workflow = create_workflow()

            state_obj = {
                'topic': topic,
                's1_response': '',
                's2_response': '',
                's3_response': '',
                'final_abstract': '',
                'additional_notes': ''
            }

            app_flow = workflow.compile()
            result = app_flow.invoke(state_obj)

            final_abstract = result['final_abstract']
    
    return render_template("index.html", final_abstract=final_abstract)

if __name__ == "__main__":
    app.run(debug=True)
