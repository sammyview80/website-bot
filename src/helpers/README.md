# GROQ and ConversationGROQ Classes

This module provides two main classes for interacting with the Groq API: `GROQ` and `ConversationGROQ`. These classes offer various functionalities for chat completions, summarization, and creating conversation chains.

## GROQ Class

The `GROQ` class provides basic functionality for interacting with the Groq API.

### Methods

#### `__init__(self, api_key: str = '<your groq api key here'')`

Initializes the GROQ class with the provided API key.

#### `chat(self, prompt: str, model: str, response_format: Optional[Dict]) -> str`

Sends a chat completion request to the Groq API.

- `prompt`: The input prompt for the chat completion.
- `model`: The AI model to use.
- `response_format`: Optional response format configuration.

Returns the content of the AI's response.

#### `get_summarization(self, user_question: str, df: pd.DataFrame, model: str) -> str`

Generates a summarization based on the user's question and the provided data.

- `user_question`: The user's question.
- `df`: A pandas DataFrame containing the data (currently unused in the method).
- `model`: The AI model to use for the response.

Returns the content of the AI's response to the summarization prompt.

## ConversationGROQ Class

The `ConversationGROQ` class provides more advanced functionality for creating conversation chains and managing chat history.

### Methods

#### `__init__(self, conversational_memory_length: int = 10, api_key: str = os.getenv('GROQ_API_KEY'), model: str = os.getenv('GROQ_MODEL'))`

Initializes the ConversationGROQ class with the specified parameters.

#### `sequential_chain(self, llm: ChatGroq, prompt_sequences: list[Dict[str, str]], input_variable: list[str], output_variable: list[str])`

Creates a sequential chain of LLM chains based on the provided prompt sequences, input variables, and output variables.

#### `create_router_chain(self, templates_prompts: list[Dict[str, str]], llm: Optional[ChatGroq] = None)`

Creates a router chain for selecting the best-suited prompt based on the input.

#### `get_conditional_template(self, input: str, categories: list[Dict[str, str]]) -> ChatPromptTemplate`

Selects the best-suited prompt template based on the input and provided categories.

#### `create_template(self, base_prompt: str) -> ChatPromptTemplate`

Creates a chat prompt template with the given base prompt.

#### `create_conversation(self, prompt: str = None, llm = None, memory = None, verbose: bool = True)`

Initializes a conversation chain with the specified parameters.

#### `chat(self, user_input: str) -> str`

Sends a user input to the conversation chain and returns the AI's response.

## Usage

To use these classes, you need to have the Groq API key and the required dependencies installed. Make sure to set up the necessary environment variables or provide the API key directly when initializing the classes.

Example usage:
