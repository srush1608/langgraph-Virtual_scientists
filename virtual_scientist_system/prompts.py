S0_START_PROMPT = """
Hi, I am Scientist S0, leading the group to discuss and finalize the abstract.
S1, S2, and S3, please find relevant information about the topic and share your findings with me.
"""

S1_PROMPT = """
Hello, I am Scientist S1. Please search for the topic using DuckDuckGo bring 1000 words info:
1. Purpose and Scope: Define the research problem statements and objectives.
2. Methodology: Describe the research methods or experimental approach about the topic.
The information should be different from the other 2 scientists.

Ensure your findings are detailed and accurate.
"""

S2_PROMPT = """
Hi, I am Scientist S2. Please search for the topic using DuckDuckGo brin 500 words info:
1. Key Findings: Summarize the key results and insights from the research.
2. Contributions and Novelty: Highlight the unique aspects of the study and its advancements.
The information should be different from the other 2 scientists.

Ensure your findings are detailed and accurate.
"""

S3_PROMPT = """
Greetings, I am Scientist S3. Please search for the topic using DuckDuckGo bring 100 words information only:
1. Conclusions and Implications: Summarize the impact or practical applications of the research.
2. Additional Insights: Provide any other relevant information that adds value to the discussion.
The information should be different from the other 2 scientists.

Ensure your findings are detailed and accurate.
"""

S0_END_PROMPT = """
I have reviewed the findings from all three scientists. Now, let's combine our insights into a cohesive abstract.
"""
GROQ_FINAL_PROMPT = """
Based on our discussion, please combine the following responses into a concise and well-structured abstract:

S1: {S1_FINDINGS}
S2: {S2_FINDINGS}
S3: {S3_FINDINGS}

Please summarize these discussions and present a cohesive abstract that captures the key points, insights, and conclusions.

Thank you for your collaboration.
"""
