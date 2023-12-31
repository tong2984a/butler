from langchain.document_loaders import CSVLoader
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import (
    AgentTokenBufferMemory,
)
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.prompts import MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain.tools import tool
import streamlit as st
import json
import os

api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key

# Create a csv retriever
subfolder = "mp4_files"
csv_filepath = os.path.join(subfolder, "index.csv")
loader = CSVLoader(csv_filepath)
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
embeddings = HuggingFaceEmbeddings()
db = FAISS.from_documents(texts, embeddings)
retriever = db.as_retriever()

# Create a retriever tool
tool_name = "Larry_La_life_stories"
tool_description = "This tool retrieves from a collection of mp4 files"
retriever_tool = create_retriever_tool(retriever, tool_name, tool_description)
tools = [retriever_tool]

# Create a custom mp4 tool
@tool
def play_mp4(query: str) -> str:
    """Play a specific mp4 file."""
    subfolder = "mp4_files"
    file_path = os.path.join(subfolder, query)
    if os.path.exists(file_path):
        video_file = open(file_path, 'rb') #enter the filename with filepath
        video_bytes = video_file.read() #reading the file
        st.video(video_bytes) #displaying the video
        return json.dumps({"file_path": file_path})
    else:
        return json.dumps({"file_path": None})

tools.append(play_mp4)

# Create conversational retrieval agent
llm = ChatOpenAI(temperature=0)
memory_key = "history"
memory = AgentTokenBufferMemory(memory_key=memory_key, llm=llm)
system_message = SystemMessage(
    content=(
        "You are now Larry La, a captivating individual whose life stories have been meticulously documented in a collection of mp4 files."
        "As you engage in conversation, you will draw upon Larry's personal experiences to answer questions."
        "Your goal is to provide a specific mp4 file name that relates to the topic at hand."
        "Utilize your intimate knowledge of Larry's life to share the most fitting story from the collection."
        "While responding, you can leverage any relevant tools or references at your disposal to ensure accuracy and depth in your storytelling."
        "Let the richness of Larry La's life unfold through the mp4 files as you captivate and inspire through your answers."
    )
)
prompt = OpenAIFunctionsAgent.create_prompt(
        system_message=system_message,
        extra_prompt_messages=[MessagesPlaceholder(variable_name=memory_key)]
    )
agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    return_intermediate_steps=True,
)

# main streamlit app
if user_input := st.chat_input():
    st.chat_message("user").write(user_input)
    with st.chat_message("assistant"):
        result = agent_executor({"input": user_input})
        st.write(result['output'])