from pathlib import Path
from langchain.text_splitter import CharacterTextSplitter
import faiss
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import pickle

def train():
    trainingData = list(Path("training/facts/").glob("**/*.*"))

    data = []
    for training in trainingData:
        with open(training) as f:
            print(f"Add {f.name} to dataset")
            data.append(f.read())

    textSplitter = CharacterTextSplitter(chunk_size=2000, separator="\n")
    docs = []
    for sets in data:
        docs.extend(textSplitter.split_text(sets))

    EMBEDDINGS_MODEL_NAME="all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL_NAME)

    store = FAISS.from_texts(docs, embeddings)
    faiss.write_index(store.index, "training.index")
    store.index = None

    with open("faiss.pkl", "wb") as f:
        pickle.dump(store, f)

if __name__ == '__main__':
    #runPrompt()
    train()
