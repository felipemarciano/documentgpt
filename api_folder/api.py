from flask import Flask, request, jsonify
import os

import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma

import constants

os.environ["OPENAI_API_KEY"] = constants.APIKEY

PERSIST = True

app = Flask(__name__)
app.secret_key = os.urandom(24)

if PERSIST and os.path.exists("persist"):
  vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  loader = DirectoryLoader("data/")
  if PERSIST:
    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
  else:
    index = VectorstoreIndexCreator().from_loaders([loader])

chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-3.5-turbo"),
  retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
)

# Dictionary to store chat history. Keys will be the session ids.
chat_histories = {}

@app.route('/chat', methods=['POST'])
def chat():
  session_id = request.json.get('session_id')
  query = request.json.get('query')
  
  # Get the chat history for this session, or initialize a new one if it doesn't exist.
  chat_history = chat_histories.get(session_id, [])
  
  result = chain({"question": query, "chat_history": chat_history})
  answer = result['answer']
  
  chat_history.append((query, answer))
  
  # Save the updated chat history for this session.
  chat_histories[session_id] = chat_history
  
  return jsonify({'answer': answer})

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
