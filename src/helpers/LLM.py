from groq import Groq
from langchain_groq import ChatGroq
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.chains import LLMChain, SequentialChain, RetrievalQA
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from typing import Dict, Literal, Optional
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain,RouterOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.agent_toolkits.load_tools import load_tools 
from langchain.agents import AgentType

# Basic index creator
from langchain.indexes import VectorstoreIndexCreator
import pandas as pd
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

class LLM:
    def __init__(self,type:str='groq', model:str='llama3-8b-8192',  api_key: str = os.environ.get("GROQ_API_KEY")):
        if type == "groq":
            self.client: ChatGroq = ChatGroq(
                groq_api_key=api_key,
                model=model
            )
        elif type == "openai":
            self.client = OpenAI(api_key)
        self.model = model
        self.agent_tools = []

    def chat_completions(self, prompt: str, model: Optional[str] = None) -> str:
        print(prompt)
        completion = self.client.invoke(
            [{"role": "user", "content": prompt}])
        print(completion.content)
        return completion.content
    

class Chains:
    def __init__(self, client):
       self.client = client 

    def create_sequential_chain(self, llm: ChatGroq, prompt_sequences: list[Dict[str, str]], input_variable: list[str], output_variable: list[str]):
        """
        This function creates a sequential chain of LLM chains based on the provided prompt sequences, input variables, and output variables.

        Parameters:
        llm (ChatGroq): The Groq API client.
        prompt_sequences (list[Dict[str, str]]): A list of dictionaries containing the prompt and output key for each sequence.
        input_variable (list[str]): A list of input variables for the overall chain.
        output_variable (list[str]): A list of output variables for the overall chain.
        Example: 
        prompt_sequences = [
            {'prompt': 'You are a helpful assistant.{input} Answer the user\'s question. {user_input}', 'output_key': 'prompt1'},
            {'prompt': 'You are a helpful assistant. Answer the user\'s question. {user_input}', 'output_key': 'prompt2'},
            {'prompt': 'You are a helpful assistant. Answer the user\'s question. {user_input}', 'output_key': 'final'}
        ]
        input_variable = ['input']
        output_variable = ['prompt1', 'prompt2', 'final']

        Returns:
        SequentialChain: An overall chain that combines all the individual chains.
        """
        chains = []
        for sequence in prompt_sequences:
            prompt = sequence['prompt']
            output_key = sequence['output_key']
            template = ChatPromptTemplate.from_template(prompt)
            chain = LLMChain(llm=llm or self.client, prompt=template, output_key=output_key)
            chains.append(chain)
        overall_chain = SequentialChain(
            chains=chains,
            input_variables=input_variable,
            output_variables=output_variable,
            verbose=True
        )
        return overall_chain
        
    def create_router_chain(self, templates_prompts: list[Dict[str, str]], llm: Optional[ChatGroq] = None):
        MULTI_PROMPT_ROUTER_TEMPLATE = """Given a raw text input to a \
            language model select the model prompt best suited for the input. \
            You will be given the names of the available prompts and a \
            description of what the prompt is best suited for. \
            You may also revise the original input if you think that revising\
            it will ultimately lead to a better response from the language model.

            << FORMATTING >>
            Return a markdown code snippet with a JSON object formatted to look like:
            ```json
            {{{{
                "destination": string \ name of the prompt to use or "DEFAULT"
                "next_inputs": string \ a potentially modified version of the original input
            }}}}
            ```

            REMEMBER: "destination" MUST be one of the candidate prompt \
            names specified below OR it can be "DEFAULT" if the input is not\
            well suited for any of the candidate prompts.
            REMEMBER: "next_inputs" can just be the original input \
            if you don't think any modifications are needed.

            << CANDIDATE PROMPTS >>
            {destinations}

            << INPUT >>
            {{input}}

            << OUTPUT (remember to include the ```json)>>"""
        destination_chains = {}
        for template in templates_prompts:
            destination_chains[template['name']] = LLMChain(llm=llm or self.client, memory=self.memory, prompt=ChatPromptTemplate.from_template(template= template['prompt_template']))
        destinations = [f"{template['name']}: {template['description']}" for template in templates_prompts]
        destinations_str = "\n".join(destinations)
        router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations_str)
        router_prompt = PromptTemplate(
            template=router_template,
            input_variables=["input"],
            output_parser=RouterOutputParser(),
        )
        default_prompt = ChatPromptTemplate.from_template("{input}")
        default_chain = LLMChain(llm=llm or self.client, memory=self.memory, prompt=default_prompt)
        router_chain = LLMRouterChain.from_llm(llm or self.client, router_prompt)
        chain = MultiPromptChain(router_chain=router_chain, 
                         destination_chains=destination_chains, 
                         default_chain=default_chain, verbose=True
                        )
        return chain



class ConversationLLM(LLM, Chains):
    def __init__(self, type:str='groq', conversational_memory_length: int = 10, api_key: str = os.getenv('GROQ_API_KEY'), model: str = os.getenv('GROQ_MODEL')):
        LLM.__init__(self, type=type, model=model, api_key=api_key)
        Chains.__init__(self, client=self.client)
        self.memory: ConversationBufferWindowMemory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)
        self.conversation: Optional[LLMChain] = None
    
    def create(self, prompt: str = None, llm = None, memory = None, verbose: bool = True):
        self.conversation = LLMChain(
            llm=llm or self.client,
            memory=memory or self.memory,
            prompt=self.create_template(prompt) if prompt else None,
            verbose=verbose
        )
        return self.conversation

    def create_template(self, base_prompt: str) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
                    SystemMessage(
                        content=base_prompt
                    ),  # This is the persistent system prompt that is always included at the start of the chat.

                    MessagesPlaceholder(
                        variable_name="chat_history"
                    ),  # This placeholder will be replaced by the actual chat history during the conversation. It helps in maintaining context.

                    HumanMessagePromptTemplate.from_template(
                        "{human_input}"
                    ),  # This template is where the user's current input will be injected into the prompt.
                ])


    def chat(self, user_input: str) -> str:
        if self.conversation is None:
            raise ValueError("Conversation not initialized. Call create_conversation() first.")
        return self.conversation.predict(human_input =user_input)

    # def get_conditional_template(self, input: str, categories: list[Dict[str, str]]) -> ChatPromptTemplate:
    #     MULTI_PROMPT_ROUTER_TEMPLATE = """Given a raw text input to a \
    #         language model select the model prompt best suited for the input. \
    #         You will be given the names of the available prompts and a \
    #         description of what the prompt is best suited for. \
    #         You may also revise the original input if you think that revising\
    #         it will ultimately lead to a better response from the language model.

    #         << FORMATTING >>
    #         Return a markdown code snippet with a JSON object formatted to look like:
    #         ```json
    #         {{{{
    #             "destination": string \ name of the prompt to use or "DEFAULT"
    #             "next_inputs": string \ a potentially modified version of the original input
    #         }}}}
    #         ```

    #         REMEMBER: "destination" MUST be one of the candidate prompt \
    #         names specified below OR it can be "DEFAULT" if the input is not\
    #         well suited for any of the candidate prompts.
    #         REMEMBER: "next_inputs" can just be the original input \
    #         if you don't think any modifications are needed.

    #         << CANDIDATE PROMPTS >>
    #         {destinations}

    #         << INPUT >>
    #         {input}

    #         << OUTPUT (remember to include the ```json)>>""".format(destinations = "\n".join([f"{template['name']}: {template['description']}" for template in categories]), input = input)
        
    #     router_prompt = PromptTemplate(
    #         template=MULTI_PROMPT_ROUTER_TEMPLATE,
    #         input_variables=["input"],
    #     )

    #     response = LLMChain(llm=self.client, prompt=router_prompt).predict(input = input)

    #     json_str = response.split('```json')[1].split('```')[0].strip()
    #     return json.loads(json_str)

    # def chat_docs(self, doc: str, query: str) -> str:
    #     loader = CSVLoader(file_path=doc)
    #     # Basic index creator
    #     # index = VectorstoreIndexCreator(
    #     #     vectorstore_cls=DocArrayInMemorySearch
    #     # ).from_loaders([loader])
    #     # return index.query(query, llm=self.client)

    #     # In chunck
    #     docs = loader.load()
    #     embeddings = OpenAIEmbeddings()
    #     vectorstore = DocArrayInMemorySearch.from_documents(docs, embeddings)
    #     retriever = vectorstore.as_retriever()
    #     qa_stuff = RetrievalQA.from_chain_type(
    #         llm=self.client, 
    #         chain_type="stuff", 
    #         # chain_type="map_reduce",
    #         # chain_type="refine",
    #         # chain_type="map_rerank",
    #         retriever=retriever, 
    #         verbose=True,
    #         memory=self.memory
    #     )
    #     return qa_stuff
    
    # # @staticmethod
    # # def create_agent_tools(self, func: function ):
    # #     @tool
    # #     def func_tool():
    # #        func() 
    # #     return func_tool
    
    # # def create_agent(self, tools: list[function], func: function, clear:bool = False):
    # #     self.agent_tools = [tools ] if clear else self.agent_tools.append(tools)
    # #     tools_loaded = load_tools(self.agent_tools, llm=self.client)
    # #     agent = initialize_agent(
    # #         tools_loaded + [func], 
    # #         llm=self.client, 
    # #         agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    # #         handle_parsing_errors=True,
    # #         verbose = True)
    # #     return agent


    