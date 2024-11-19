
import requests
from bs4 import BeautifulSoup
from helpers.LLM import ConversationLLM 

class Scrapper:
    def __init__(self, url: str, groq_instance: ConversationLLM):
        self.url = url
        self.groq_instance = groq_instance

    def scrape(self):
        response = requests.get(self.url)
        response.raise_for_status
        return response.content

    def parse(self, content: str):
        soup = BeautifulSoup(content, 'html.parser')
        return ' '.join(soup.stripped_strings)

    def compress(self, content: str):
        return ' '.join(content.split())

    def truncate(self, content: str):
        return content[:1000] + '...' if len(content) > 1000 else content
        
    def analyze(self, content: str):
        prompt = """
        Analyze the following HTML content with exceptional precision and depth:
        {content}
        """
        response = self.groq_instance.chat(prompt.format(content=content))
        return response
    
    def extract(self, content: str):
        prompt = """
        Extract the following structured data from the HTML content:

        {content}
        1. JSON representation: Extract key information and structure it in JSON format.
        2. Table extraction: Identify and extract any tables, presenting them in JSON format.
        3. List compilation: Extract and present lists from the content in JSON format.
        4. Key-value pair extraction: Identify and extract key-value pairs, presenting them in JSON format.
        5. Numerical data analysis: Extract and present numerical data in JSON format.
        6. Entity recognition: Identify and categorize named entities, presenting them in JSON format.
        7. Sentiment analysis: Assess overall tone and sentiment, presenting results in JSON format.
        8. Language detection: Identify the primary language and any secondary languages, presenting in JSON format.
        9. Structured data markup: Extract any structured data present on the page, presenting in JSON format.
        10. API endpoints: Document any API endpoints referenced, presenting in JSON format.

        Ensure the extracted data is well-structured and properly formatted in JSON.
        {content}
        Provide the data in JSON format.
        """
        response = self.groq_instance.chat(prompt.format(content=content))
        return response
