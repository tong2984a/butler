import faiss
import pickle
import json
import streamlit as st
import os

index = faiss.read_index("training.index")

with open("faiss.pkl", "rb") as f:
    store = pickle.load(f)

store.index = index

def runPrompt():
    def onMessage(question):
        docs_and_scores = store.similarity_search_with_score(question, k=1)
        for i, doc in enumerate(docs_and_scores):
            print("page content:", doc[0].page_content, "score:", doc[1])
            json_object = json.loads(doc[0].page_content)
            print("file:", json_object['File'])

    while True:
        question = input("Ask a question > ")
        answer = onMessage(question)
        print(f"Bot: {answer}")

st.info('Sample Prompt 1 : What are the most rewarding aspects of your journey in the restaurant business that you hold close to your heart?')
st.info('Sample Prompt 2 : Could you provide some background on your upbringing and the place that shaped you into the person you are today?')
st.info('Sample Prompt 3 : Tell us about yourself.') 
st.info("Sample Prompt 4 : Tell me about Larry La's journey in the restaurant business.")

if user_input := st.chat_input():
    st.chat_message("user").write(user_input)
    with st.chat_message("assistant"):
        docs_and_scores = store.similarity_search_with_score(user_input, k=1)
        for i, doc in enumerate(docs_and_scores):
            print("page content:", doc[0].page_content, "score:", doc[1])
            json_object = json.loads(doc[0].page_content)
            mp4 = json_object['File']
            print("mp4:", mp4)
            subfolder = "mp4_files"
            file_path = os.path.join(subfolder, mp4)
            video_file = open(file_path, 'rb') #enter the filename with filepath
            video_bytes = video_file.read() #reading the file
            st.video(video_bytes) #displaying the video
