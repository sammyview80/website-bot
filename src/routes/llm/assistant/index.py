import re
import json
from flask import Blueprint, request, jsonify, session
from helpers.prompts import PromptManager
from helpers.LLM import ConversationLLM, LLM

assistantBlueprint = Blueprint('assistant', __name__)

prompt_manager = PromptManager()
prompt_manager.load_prompt('base_prompt', 'prompts/base_assistant_prompts.txt')
basePrompt = prompt_manager.get_prompt('base_prompt')

assistantLLM = ConversationLLM()
assistantLLM.create(basePrompt)

def create_json_from_response(response_text):
    """Create a JSON object from the given text."""
    try:
        # Attempting to convert the response into a JSON object directly
        return json.loads(response_text)
    except json.JSONDecodeError:
        # In case conversion fails, we'll build a simple JSON object containing the original response
        return {'message': response_text}

@assistantBlueprint.route('/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data['prompt']
    response = assistantLLM.chat(prompt)
    # llm= LLM('groq')
    # prompt = """
    #         Given an unformatted multi-line JSON string, please clean up the formatting to produce a single-line JSON string without any unnecessary whitespace. Ensure that the resulting JSON adheres strictly to standards and is easy to read. Below is an example of how an unformatted JSON looks; transform it accordingly:

    #         Example Input:
    #         ```json
    #         {
    #           "command": "osascript -e 'tell application "System Events" to set brightness of keyboard to 100'"
    #         }
    #         ```

    #         Your task is to take similar inputs and return them in a properly formatted single-line JSON string. Do not modify the structure or content of the JSON, simply correct its formatting.

    #         Here is the input: {input}
    #         """
        
    
    return jsonify({'json': response, "description": response}), 200

def clean_command(json_command):
    # Parse the JSON string to extract the command
    command_dict = json.loads(json_command)
    raw_command = command_dict.get('script', '')
    print(raw_command)
    return raw_command

    # Clean up escape characters: remove unnecessary backslashes
    clean_command = raw_command.replace('\\"', '"').replace('\\\\', '\\')

    return clean_command