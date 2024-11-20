import os
import openai
from dotenv import load_dotenv
from openai import OpenAI as OAIAPI  # Importing OpenAI class with alias OAIAPI

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

class OpenAI: 
    def __init__(self, api_key:str = os.environ.get("OPENAI_API_KEY")):
        key = api_key 
        if not key: raise ValueError("No API key provided")
        key = api_key or os.environ.get("OPENAI_API_KEY")
        
        self.openai: OAIAPI = OAIAPI(api_key=key)

    def create(self, model:str, messages:str):
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
        return response.choices[0].message.content


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
        self.finetuning_job = self.openai.fine_tuning.jobs.create(
            training_file= _id ,
            model=model
        )
        print("Fine-tuning job ID:", self.finetuning_job.id)
        return self.finetuning_job