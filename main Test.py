import os
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken
from langchain_community.document_loaders import TextLoader
from helper_functions import llm
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings


filename_list = [
    'Energy Efficient Interior Design Tips.txt',
    'Tips on Buying Energy-Efficient Appliances.txt',
    'Energy Saving Tips.txt'    
]

# load the documents
list_of_documents_loaded = []

for filename in filename_list:
    print(filename)
    try:
        # try to load the document
        markdown_path = os.path.join('data', filename)
        loader = TextLoader(markdown_path)

        # load() returns a list of Document objects
        data = loader.load()

        # use extend() to add to the list_of_documents_loaded
        list_of_documents_loaded.extend(data)
        print(f"Loaded {filename}")

    except Exception as e:
        # if there is an error loading the document, print the error and continue to the next document
        print(f"Error loading {filename}: {e}")
        continue

# print("Total documents loaded:", len(list_of_documents_loaded))
def count_tokens(text):
    encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    return len(encoding.encode(text))

i = 0
for doc in list_of_documents_loaded:
    i += 1
    print(f'Document {i} - "{doc.metadata.get("source")}" has {count_tokens(doc.page_content)} tokens')




# In this case, we intentionally set the chunk_size to 1100 tokens, to have the smallest document (document 2) intact
text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=10, length_function=count_tokens)

# Split the documents into smaller chunks
splitted_documents = text_splitter.split_documents(list_of_documents_loaded)

# Print the number of documents after splitting
print(f"Number of documents after splitting: {len(splitted_documents)}")

# embedding model that we will use for the session
embeddings_model = OpenAIEmbeddings(model='text-embedding-3-small')

# llm to be used in RAG pipeplines in this notebook
llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, seed=42)

# Create the vector database
vectordb = Chroma.from_documents(
    documents = splitted_documents,
    embedding = embeddings_model,
    collection_name = "naive_splitter", # one database can have multiple collections
    persist_directory = "./vector_db"
)
print(vectordb._collection.count())
from langchain.chains import RetrievalQA

# The `llm` is defined earlier in the notebook (using GPT-4o-mini)
rag_chain = RetrievalQA.from_llm(
    retriever = vectordb.as_retriever(search_type='mmr',
                                      search_kwargs={'k': 4, 'fetch_k': 5}), 
                                      llm = llm
)

#llm_response = rag_chain.invoke('What are tips for saving energy with air conditioners?')
#print(llm_response['result'])


# Compared to the rag pipelines that we used above, this cell allows a custom prompt to be used
# This is useful for customizing the prompt to be used in the retrieval QA chain
# The prompt below is the standard template that is used in the retrieval QA chain
# It also includes the "documents" that are used in the prompt
from langchain.prompts import PromptTemplate

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
print(llm_response['result'])
