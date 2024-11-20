import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, session
from helpers.prompts import PromptManager
from helpers.LLM import ConversationLLM, LLM

load_dotenv()

assistantBlueprint = Blueprint('assistant', __name__)

prompt_manager = PromptManager()
prompt_manager.load_prompt('base_prompt', 'prompts/base_assistant_prompts.txt')
basePrompt = prompt_manager.get_prompt('base_prompt')

assistantLLM = ConversationLLM(type='openai', model=os.environ.get('MAC_OPENAI_MODEL'),api_key=os.environ.get('OPENAI_API_KEY'))
assistantLLM.create(basePrompt)

@assistantBlueprint.route('/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data['prompt']
    response = assistantLLM.chat(prompt)
    
    return jsonify({"script": response}), 200
