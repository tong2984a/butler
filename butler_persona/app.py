import streamlit as st
import faiss
from fastapi import FastAPI
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import (
    StreamingStdOutCallbackHandler,
)  # for streaming resposne
import pickle
from langchain import LLMChain
from langchain.prompts import Prompt
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model = AutoModelForSeq2SeqLM.from_pretrained('t5-base')
tokenizer = AutoTokenizer.from_pretrained('t5-base')

app = FastAPI()

def abs_sum(text, model, tokenizer):
    tokens_input = tokenizer.encode("summarize: "+text, return_tensors='pt',
                                    max_length=tokenizer.model_max_length,
                                    truncation=True)

    summary_ids = model.generate(tokens_input, min_length=80, max_length=150,
                                length_penalty=15, num_beams=2)

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary

def generate_response(question):
    index = faiss.read_index("training.index")

    with open("faiss.pkl", "rb") as f:
        store = pickle.load(f)

    store.index = index

    with open("training/master.txt", "r") as f:
        promptTemplate = f.read()

    model_path = "/home/aleung/rag/Knowledgebase-embedding/llama-2-7b-chat.Q2_K.gguf" # <-------- enter your model path here
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    n_gpu_layers = 40  # Change this value based on your model and your GPU VRAM pool.
    n_batch = 512  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
    llm = LlamaCpp(
        model_path=model_path,
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        callback_manager=callback_manager,
        verbose=True,
        n_ctx=2048,
        # temperature=1
    )
    prompt = Prompt(template=promptTemplate, input_variables=["history", "context", "question"])

    llmChain = LLMChain(llm=llm, prompt=prompt)
    docs = store.similarity_search(question)
    contexts = []
    for i, doc in enumerate(docs):
        summary = abs_sum(doc.page_content, model, tokenizer)
        contexts.append(f"Context {i}:\n{summary}")
    answer = llmChain.predict(question=question, context="\n\n".join(contexts), history=[])
    return answer

# REST API
@app.post("/ask")
def ask(input:str):
    result = generate_response(input)
    return result

# Build an app with streamlit
def main():
    st.set_page_config(
        page_title="AI-Brian response generator", page_icon=":bird:")

    st.header("AI-Brian response generator :bird:")
    message = st.text_area("Your message")

    if message:
        st.write("Generating response...")
        result = generate_response(message)
        st.info(result)

if __name__ == '__main__':
    main()