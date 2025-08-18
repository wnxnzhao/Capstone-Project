import os
import json
import openai
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

if load_dotenv('.env'):
   # for local development
   OPENAI_KEY = os.getenv('OPENAI_API_KEY')
else:
   OPENAI_KEY = st.secrets['OPENAI_API_KEY']

# Pass the API Key to the OpenAI Client
client = OpenAI(api_key=OPENAI_KEY)

def get_embedding(input, model='text-embedding-3-small'):
    response = client.embeddings.create(
        input=input,
        model=model
    )
    return [x.embedding for x in response.data]


# This is the "Updated" helper function for calling LLM
def get_completion(prompt, model="gpt-4o-mini", temperature=0, top_p=1.0, max_tokens=1024, n=1, json_output=False):
    if json_output == True:
      output_json_structure = {"type": "json_object"}
    else:
      output_json_structure = None

    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create( #originally was openai.chat.completions
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=1,
        response_format=output_json_structure,
    )
    return response.choices[0].message.content


# Note that this function directly take in "messages" as the parameter.
def get_completion_by_messages(messages, model="gpt-4o-mini", temperature=0, top_p=1.0, max_tokens=1024, n=1):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=1
    )
    return response.choices[0].message.content


# This function is for calculating the tokens given the "message"
# ⚠️ This is simplified implementation that is good enough for a rough estimation
def count_tokens(text):
    encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    return len(encoding.encode(text))


def count_tokens_from_message(messages):
    encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    value = ' '.join([x.get('content') for x in messages])
    return len(encoding.encode(value))

filename_list = [
    'Energy Efficient Interior Design Tips.txt',
    'Tips on Buying Energy-Efficient Appliances.txt',
    'Energy Saving Tips.txt'    
]

# load the documents
list_of_documents_loaded = []

for filename in filename_list:
    try:
        # try to load the document
        markdown_path = os.path.join('data', filename)
        loader = TextLoader(markdown_path)

        # load() returns a list of Document objects
        data = loader.load()

        # use extend() to add to the list_of_documents_loaded
        list_of_documents_loaded.extend(data)

    except Exception as e:
        # if there is an error loading the document, print the error and continue to the next document
        print(f"Error loading {filename}: {e}")
        continue

# In this case, we intentionally set the chunk_size to 1100 tokens, to have the smallest document (document 2) intact
text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=10, length_function=count_tokens)

# Split the documents into smaller chunks
splitted_documents = text_splitter.split_documents(list_of_documents_loaded)

# embedding model that we will use for the session
embeddings_model = OpenAIEmbeddings(model='text-embedding-3-small')

# llm to be used in RAG pipeplines in this notebook
llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, seed=42)

# Create the vector database
vectordb = Chroma.from_documents(
    documents = splitted_documents,
    embedding = embeddings_model,
    collection_name = "naive_splitter", # one database can have multiple collections
    persist_directory = "./vector_db")
# Load existing vector database
# vectordb = Chroma(persist_directory = "./vector_db")

def process_user_message(user_message):
    # Build prompt
    template = """Use the following pieces of context to answer the question at the end.
    Determine if the question is relevant to the context or not.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Answer the user in a friendly tone.
    You must only rely on the facts or information in the database. Your response should be as detail as possible and
    include information that is useful for the user to make informed decisions on energy saving and efficiency.
    Make sure the statements are factually accurate.
    Use Neural Linguistic Programming to construct your response.

    {context}
    Question: {question}
    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

# Run chain
    qa_chain = RetrievalQA.from_chain_type(
        ChatOpenAI(model='gpt-4o-mini'),
        retriever=vectordb.as_retriever(search_type="similarity_score_threshold",
                                        # There is no universal threshold, it depends on the use case
                                        search_kwargs={'score_threshold': 0.20}),
        # return_source_documents=True, # Make inspection of document possible
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )

    llm_response = qa_chain.invoke('What are some genral tips for some general tips for purchaisng of electrical applicances?')
    return llm_response['result']


