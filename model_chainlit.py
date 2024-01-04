# from langchain import PromptTemplate 
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings 
from langchain.vectorstores import FAISS 
from langchain.llms import CTransformers 
from langchain.chains import RetrievalQA
import chainlit as cl 

DB_FAISS_PATH = "vectorstores/db_faiss"

# custom_prompt_template = """ Use the following pieces of information to answer the user's question. 
# If you don't know the answer, please just say that don't know the answer, don't try to make up
# an answer.

# Context : {}
# Question : {question}

# only return the helpful answer below and nothing else.
# Helpful answer: 
# """

# def set_custom_prompt():
#     """propmet template for QA retrieval for each vector stores
#     """
    
#     prompt = PromptTemplate(template=custom_prompt_template,input_variable=['context','question'])
#     return prompt


# def load_llm():
#     llm = CTransformers(
#         model="llama-2-7b-chat.ggmlv3.q8_0.bin",
#         model_type = "llama",
#         max_new_tokens = 512,
#         temperature = 0.5
#     )
#     return llm

# def retrieval_qa_chain(llm,prompt,db):
#     qa_chain = RetrievalQA.from_chain_type(
#         llm=llm,
#         chain_type="stuff",
#         retriever = db.as_retriever(search_kwargs={'k':2}),
#         return_source_documents = True,
#         chain_type_kwargs={'prompt': prompt}
#     )
#     return qa_chain

# def qa_bot():
#     embeddings = HuggingFaceEmbeddings(model_name = 'sentence-transformers/all-MiniLM-L6-v2',
#                                        model_kwargs = {'device':'cpu'})
#     db = FAISS.load_local(DB_FAISS_PATH,embeddings)
#     llm = load_llm()
#     qa_prompt = set_custom_prompt()
#     qa = retrieval_qa_chain(llm,qa_prompt,db)
    
#     return qa 


# def final_result(query):
#     qa_result = qa_bot()
#     response = qa_result({'query': query})
#     return response

# ## chainlit app 

# @cl.on_chat_start
# async def start():
#     chain = qa_bot()
#     msg = cl.Message(content = "starting the bot....")
#     await msg.send()
#     msg.content = "Hi, Welcome to Cons bot, What is your Query??"
#     await msg.update()
#     cl.user_session.set("chain",chain)
    
    
    
# @cl.on_message 
# async def main(message: cl.Message):
#     chain = cl.user_session.set("chain")
#     cb = cl.AsyncLangchainCallbackHandler(
#         stream_final_answer = True, answer_prefix_tokens = ["FINAL","ANSWER"]
#     )
#     cb.answer_reached = True 
#     res = await chain.acall(message, callbacks = [cb])
#     answer = res["result"]
#     source = res["source_documents"]
    
#     if source:
#         answer += f"\nSources:" + str(source)
#     else:
#         answer += f"\nNo Source Found"
        
#     await cl.Message(content = answer).send()


######################################### Different code ##############################################



custom_prompt_template = """Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}
Question: {question}

Only return the helpful answer below and nothing else.
Helpful answer:
"""

def set_custom_prompt():
    """
    Prompt template for QA retrieval for each vectorstore
    """
    prompt = PromptTemplate(template=custom_prompt_template,
                            input_variables=['context', 'question'])
    return prompt

#Retrieval QA Chain
def retrieval_qa_chain(llm, prompt, db):
    qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                       chain_type='stuff',
                                       retriever=db.as_retriever(search_kwargs={'k': 2}),
                                       return_source_documents=True,
                                       chain_type_kwargs={'prompt': prompt}
                                       )
    return qa_chain

#Loading the model
def load_llm():
    # Load the locally downloaded model here
    llm = CTransformers(
        model = "TheBloke/Llama-2-7B-Chat-GGML",
        model_type="llama",
        max_new_tokens = 512,
        temperature = 0.5
    )
    return llm

#QA Model Function
def qa_bot():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                       model_kwargs={'device': 'cpu'})
    db = FAISS.load_local(DB_FAISS_PATH, embeddings)
    llm = load_llm()
    qa_prompt = set_custom_prompt()
    qa = retrieval_qa_chain(llm, qa_prompt, db)

    return qa

#output function
def final_result(query):
    qa_result = qa_bot()
    response = qa_result({'query': query})
    return response

#chainlit code
@cl.on_chat_start
async def start():
    chain = qa_bot()
    msg = cl.Message(content="Starting the bot...")
    await msg.send()
    msg.content = "Hi, Welcome to Medical Bot. What is your query?"
    await msg.update()

    cl.user_session.set("chain", chain)

@cl.on_message
async def main(message: cl.Message):
    chain = cl.user_session.get("chain") 
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
    )
    cb.answer_reached = True
    res = await chain.acall(message.content, callbacks=[cb])
    answer = res["result"]
    sources = res["source_documents"]

    if sources:
        answer += f"\nSources:" + str(sources)
    else:
        answer += "\nNo sources found"

    await cl.Message(content=answer).send()