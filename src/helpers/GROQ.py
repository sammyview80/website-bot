from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.chains import LLMChain, SequentialChain
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from typing import Dict, Optional
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain,RouterOutputParser
from langchain.prompts import PromptTemplate
import pandas as pd
import os
import json

class GROQ:
    def __init__(self, api_key: str = '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'):
        self.client: Groq = Groq(
            api_key=api_key
        )

    def chat(self, prompt: str, model: str, response_format: Optional[Dict]) -> str:
        completion = self.client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], response_format=response_format)

        return completion.choices[0].message.content
    
    
    def get_summarization(self, user_question: str, df: pd.DataFrame, model: str) -> str:
        """
        This function generates a summarization prompt based on the user's question and the resulting data. 
        It then sends this summarization prompt to the Groq API and retrieves the AI's response.

        Parameters:
        client (Groqcloud): The Groq API client.
        user_question (str): The user's question.
        model (str): The AI model to use for the response.


        Returns:
        str: The content of the AI's response to the summarization prompt.
        """
        prompt = '''
          {user_question}
      '''.format(user_question = user_question)
        # Response format is set to 'None'
        return self.chat(prompt,model,None)


class ConversationGROQ:
    def __init__(self, conversational_memory_length: int = 10, api_key: str = os.getenv('GROQ_API_KEY'), model: str = os.getenv('GROQ_MODEL')):
        self.client: ChatGroq = ChatGroq(
            groq_api_key=api_key,
            model=model
        )
        self.memory: ConversationBufferWindowMemory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)
        self.conversation: Optional[LLMChain] = None
    
    def sequential_chain(self, llm: ChatGroq, prompt_sequences: list[Dict[str, str]], input_variable: list[str], output_variable: list[str]):
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

    def get_conditional_template(self, input: str, categories: list[Dict[str, str]]) -> ChatPromptTemplate:
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
            {input}

            << OUTPUT (remember to include the ```json)>>""".format(destinations = "\n".join([f"{template['name']}: {template['description']}" for template in categories]), input = input)
        
        router_prompt = PromptTemplate(
            template=MULTI_PROMPT_ROUTER_TEMPLATE,
            input_variables=["input"],
        )

        response = LLMChain(llm=self.client, prompt=router_prompt).predict(input = input)

        json_str = response.split('```json')[1].split('```')[0].strip()
        return json.loads(json_str)

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

    def create_conversation(self, prompt: str = None, llm = None, memory = None, verbose: bool = True):
        self.conversation = LLMChain(
            llm=llm or self.client,
            memory=memory or self.memory,
            prompt=self.create_template(prompt) if prompt else None,
            verbose=verbose
        )
        return self.conversation

    def chat(self, user_input: str) -> str:
        if self.conversation is None:
            raise ValueError("Conversation not initialized. Call create_conversation() first.")
        return self.conversation.predict(human_input =user_input)
