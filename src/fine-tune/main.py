import os
import openai
from dotenv import load_dotenv

from typing import List, Dict 
# from utils.typeCheck import BaseTypeCheck 

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")
__dir = os.path.join(os.getcwd(), "src","fine-tune","dataset.jsonl")

# uploaded_file = openai.File.create(
#     file=open(__dir, "rb"),
#     purpose='fine-tune'
# )
# file_id = uploaded_file.id

# # Start a fine-tuning job
# finetuning_job = openai.FineTuningJob.create(
#     training_file=file_id,
#     model="gpt-3.5-turbo"
# )
# print("Fine-tuning job ID:", finetuning_job.id)

# Retrieve the status of a fine-tuning job
# jobstatus = openai.FineTuningJob.retrieve('ftjob-1pFt3g9xkOovGuQfCVmM5TRW')
# print("Job Status:", jobstatus.status)

# # If the job succeeds, deploy the model for completions
# if jobstatus.status == "succeeded":
#     fine_tuned_model = jobstatus.fine_tuned_model
#     response = openai.ChatCompletion.create(
#         model=fine_tuned_model,
# messages=[
#     {"role": "system", "content": "You are a webscraper"},
#     {"role": "user", "content": "who are you?"}
#   ]
#     )
#     print("Response:", response.choices[0].message)

import openai
from openai import OpenAI as OAIAPI  # Importing OpenAI class with alias OAIAPI

class OpenAI: 
    def __init__(self, api_key:str = os.environ.get("OPENAI_API_KEY")):
        key = api_key 
        if not key: raise ValueError("No API key provided")
        key = api_key or os.environ.get("OPENAI_API_KEY")
        
        # Initialize OAIAPI object with proper type hinting
        self.openai: OAIAPI = OAIAPI(api_key=key)

    def chat(self, model:str, messages:str):
        print(model, messages)
        response = self.openai.chat.completions.create(
            model=model,
            messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text":messages
        }
      ]
    }
  ]
        )
        print(response.choices[0].message.content)
        return response
# ai = OpenAI()
# ai.chat(model='ft:gpt-3.5-turbo-0125:personal::AT5xuOD7', messages= "What services does TechCrunch offer?")


class FineTume(OpenAI):
    def __init__(self, api_key:str = os.environ.get("OPENAI_API_KEY")):
        super().__init__(api_key)

    def create_file_openai(self,__dir:str, purpose:str='fine-tune'):
        self.uploaded_file = self.openai.files.create(
        file=open(__dir, "rb"),
        purpose=purpose
        )

        return self.uploaded_file 
    
    def create_filetune(self, _id:str=None, model:str= 'gpt-3.5-turbo'):
        # if _id is not None and not self.uploaded_file.id: raise ValueError("No file uploaded to OpenAI")
        self.finetuning_job = self.openai.fine_tuning.jobs.create(
            training_file= _id ,
            model=model
        )
        print("Fine-tuning job ID:", self.finetuning_job.id)
        print(self.finetuning_job)
        return self.finetuning_job 

ft = FineTume()
# reponse = ft.create_file_openai( os.path.join(os.getcwd(), "src","fine-tune","preprocessed.jsonl"))
# print(reponse)
# ft.create_filetune(_id='file-eU9zMilHbMc7zdMoILvw7hbt')

    # def chat(self, model:str, messages:List[Dict[str, str]]):
    #     if not BaseTypeCheck.is_list(message): 
    #         raise TypeError("Messages must be a list of dictionaries with 'role' and 'content' keys")

    #     for message in messages:
    #         if not isinstance(message, dict) or 'role' not in message or 'content' not in message:
    #             raise TypeError("Each message must be a dictionary with 'role' and 'content' keys")
    #         if message['role'] not in ['system', 'user', 'assistant']:
    #             raise ValueError("Role must be either 'system', 'user', or 'assistant'")

    #     response = self.openai.ChatCompletion.create(
    #         model=model or self.finetuning_job.fine_tune_model,
    #         messages=messages
    #     )

    #     if isinstance(response.choices, list) and len(response.choices) > 0:
    #         return response.choices[0].message
    #     else:
    #         raise ValueError("Response does not contain valid choices")