# S0 Start Prompt: Introduction and instruction for collaboration
S0_START_PROMPT = """
Hi, I am Scientist S0, leading the group to discuss and finalize the abstract.
S1, S2, and S3, please find relevant information about the topic and share your findings with me.
"""

# S1 Prompt: Details on purpose, scope, and methodology
S1_PROMPT = """
Hello, I am Scientist S1. Please search for the topic using DuckDuckGo and bring 1000 words of information:
1. Purpose and Scope: Define the research problem statements and objectives.
2. Methodology: Describe the research methods or experimental approach about the topic.
The information should be different from the other 2 scientists.

Ensure your findings are detailed and accurate.
"""

# S2 Prompt: Key findings, contributions, and novelty
S2_PROMPT = """
Hi, I am Scientist S2. Please search for the topic using DuckDuckGo and bring 500 words of information:
1. Key Findings: Summarize the key results and insights from the research.
2. Contributions and Novelty: Highlight the unique aspects of the study and its advancements.
The information should be different from the other 2 scientists.

Ensure your findings are detailed and accurate.
"""

# S3 Prompt: Conclusions, implications, and additional insights
S3_PROMPT = """
Greetings, I am Scientist S3. Please search for the topic using DuckDuckGo and bring 100 words of information only:
1. Conclusions and Implications: Summarize the impact or practical applications of the research.
2. Additional Insights: Provide any other relevant information that adds value to the discussion.
The information should be different from the other 2 scientists.

Ensure your findings are detailed and accurate.
"""

# S0 End Prompt: Instruction for combining the findings
S0_END_PROMPT = """
I have reviewed the findings from all three scientists. Now, let's combine our insights into a cohesive abstract.
"""

# Final Abstract Prompt: Combining the responses from S1, S2, and S3 into a final summary
GROQ_FINAL_PROMPT = """

You are a  professional summarizer. Your task is to generate a concise and well-structured abstract by summarizing the below responses:

    1. Key insights from S1: {state['s1_response']}
    2. Additional details provided by S2: {state['s2_response']}
    3. Further perspectives shared by S3: {state['s3_response']}
    4. Abstract should be only between 300-400 words. 
    5. STRICTLY provide only the abstract.
    6. Strictly rely on the provided text, without external informatioin
"""
