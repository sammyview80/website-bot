from flask import Blueprint, request, jsonify, session
from models import UserModal
from helpers.LLM import ConversationLLM 
from helpers.prompts import PromptManager
from helpers.Scrapy import Scrapper
from routes.llm.assistant.index import assistantBlueprint
import requests


llm = Blueprint('llm', __name__)

llm.register_blueprint(assistantBlueprint, url_prefix='/assistant')

prompt_manager = PromptManager()
prompt_manager.load_prompt('base_prompt', 'prompts/base_prompts.txt')
prompt_manager.load_prompt('base_chatbot_prompt', 'prompts/base_chatbot_prompts.txt')
prompt_manager.load_prompt('base_seo_prompt', 'prompts/base_seo_prompts.txt')
prompt_manager.load_prompt('base_content_prompt', 'prompts/base_content_prompts.txt')
base_prompt = prompt_manager.get_prompt('base_prompt')
base_chatbot_prompt = prompt_manager.get_prompt('base_chatbot_prompt')
base_seo_prompt = prompt_manager.get_prompt('base_seo_prompt')
base_content_prompt = prompt_manager.get_prompt('base_content_prompt')

llmInstance = ConversationLLM()
llmInstance.create(base_prompt)

@llm.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data['url']
    # Check user authentication
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    user = UserModal.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    
    print('hiee \n\n\n')
    try:
        scrapper = Scrapper(url, llmInstance)
        content = scrapper.scrape()
        content = scrapper.parse(content)
        content = scrapper.compress(content)
        content = scrapper.truncate(content)
        content = scrapper.analyze(content)
        json = scrapper.extract(content)
        return jsonify({'json': json, "descripton": content}), 200
    except requests.RequestException as e:
        return jsonify({'message': f'Error fetching URL: {str(e)}'}), 400
    except Exception as e:
        print(e, 'error')
        return jsonify({'message': f'Error processing HTML: {str(e)}'}), 500

@llm.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data['message']
    chains = llmInstance.create_sequential_chain()
    prompt = """
    Analyze the user's input to determine the desired output format.
    If the user requests a specific format (e.g., JSON, Excel), format the response accordingly.
    If no specific format is mentioned, provide a normal view.

    Your task is to analyze the following user input and provide a short response:

    {message}

    If you detect a request for JSON format in the user's input, wrap your response in a JSON structure like this:
    {{"json": "<json_content_here>"}}

    For other formats (e.g., Excel), indicate the format in your response, but provide the content in a text-based representation.

    If no specific format is requested, provide a comprehensive analysis in a normal, readable format.
    Analyze the user's input to determine if they're asking for a specific piece of information or a summary/opinion.
    If they're asking for specific information, provide only that information without additional explanation.
    If they're asking for a summary or your view, provide a concise explanation.
    If they're asking for a specific format, provide the response in the requested format.
    
    Response should be simple and to the point at most it should be a simple text or a json
    
"""
    response = llmInstance.chat(prompt.format(message=message))
    return jsonify({'response': response}), 200



@llm.route('/create_api', methods=['POST'])
def create_api():
    data = request.json
    url = data['url']
    pattern = data['pattern']
    
    # Define the pattern prompt
    pattern_prompt = """
    Given the following content, extract the services and format them as a JSON object:
    {content}

    The response should be in the format:
    {{"json": {pattern}}}
    """

    try:
        scrapper = Scrapper(url, llmInstance)
        print(scrapper,' scrapper')
        content = scrapper.scrape()
        print(content, 'contern')
        
        content = scrapper.parse(content)
        content = scrapper.compress(content)
        content = scrapper.truncate(content)
        
        # Use the pattern prompt to generate the response
        response = llmInstance.chat(pattern_prompt.format(content=content, pattern=pattern))

        return jsonify({'response': response}), 200
    except requests.RequestException as e:
        return jsonify({'message': f'Error fetching URL: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'message': f'Error processing HTML: {str(e)}'}), 500

