import asyncio
from groq import Groq
from prompts import S1_PROMPT, S2_PROMPT, S3_PROMPT, GROQ_FINAL_PROMPT, S0_START_PROMPT, S0_END_PROMPT  # Import prompts
from dotenv import load_dotenv
load_dotenv()

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

    def get_response(self):
        return self.response

class ScientistS0:
    def start_conversation(self, topic, scientists):
        tasks = [scientist.query_tool(topic) for scientist in scientists]
        for task in tasks:
            task  # Execute synchronously
        return "All tasks complete"

    def gather_responses(self, topic, scientists):
        responses = {}
        for scientist in scientists:
            print(f"S0: {scientist.name}, can you provide detailed information on your topic?")
            scientist.query_tool(topic)  # Fetch detailed information
            responses[scientist.name] = scientist.get_response()  # Store the response
        return responses

    def format_response(self, topic, scientists):
        # Print S0 introduction from prompts
        print(S0_START_PROMPT)

        # Simulate a discussion among the scientists
        print("Discussion on the topic:", topic)
        print("\n--- Discussion Begins ---\n")

        # Gather detailed responses from each scientist
        detailed_responses = self.gather_responses(topic, scientists)

        # Display responses as a discussion
        print("S0: S1, can you please summarize the purpose and scope of the research?")
        s1_response = detailed_responses.get("S1", "No response found.")
        print(f"S1: {s1_response}\n")

        print("S0: S2, what are your key findings and contributions?")
        s2_response = detailed_responses.get("S2", "No response found.")
        print(f"S2: {s2_response}\n")

        print("S0: S3, could you summarize the conclusions and implications?")
        s3_response = detailed_responses.get("S3", "No response found.")
        print(f"S3: {s3_response}\n")

        # Conclude the discussion
        print(S0_END_PROMPT)


        # Create the final abstract using the GROQ_FINAL_PROMPT
        final_abstract = GROQ_FINAL_PROMPT.format(
            S1_FINDINGS=s1_response,
            S2_FINDINGS=s2_response,
            S3_FINDINGS=s3_response
        )

        # Print the final abstract
        client = Groq()
        completion = client.chat.completions.create(
        model="llama3-8b-8192",  # Use the appropriate model
        messages=[
            {"role": "system", "content": final_abstract}
        ],
        temperature=0.7,
    )

    # Extract and print the final abstract response
        final_abstract = completion.choices[0].message.content
        print("Final Abstract:\n")
        print(final_abstract)

def main():
    while True:
        # Get user input for the query
        topic = input("Enter the topic for query (or 'exit' to quit): ").strip()

        if topic.lower() == 'exit':
            print("Exiting the program.")
            break

        if not topic:
            print("Error: Topic cannot be empty. Please enter a valid topic.")
            continue

        # Initialize the Groq agent
        groq_agent = Groq()

        # Initialize scientists with Groq agent and their respective prompts
        scientist_s1 = Scientist("S1", groq_agent, S1_PROMPT)
        scientist_s2 = Scientist("S2", groq_agent, S2_PROMPT)
        scientist_s3 = Scientist("S3", groq_agent, S3_PROMPT)
        scientist_s0 = ScientistS0()

        # Query each tool and collect responses
        scientists = [scientist_s1, scientist_s2, scientist_s3]
        scientist_s0.start_conversation(topic, scientists)

        # Format the combined response
        scientist_s0.format_response(topic, scientists)

if __name__ == "__main__":
    main()
