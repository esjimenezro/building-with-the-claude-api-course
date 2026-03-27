import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MAX_TOKENS = 1000


def get_client() -> Anthropic:
    """
    Returns an initialized Anthropic client.
    This function reads the API key from the environment variables and
    initializes the Anthropic client.
    If the API key is not found, it raises a ValueError.

    Returns:
        Anthropic: An instance of the Anthropic client initialized with the
            API key.
    Raises:
        ValueError: If the API key is not found in the environment variables.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY no encontrada. "
            "Asegúrate de tener un archivo .env con tu API key."
        )

    return Anthropic(api_key=api_key)


def get_model(
    default_model: str = "claude-sonnet-4-0",
    use_default: bool = False
) -> str:
    """
    Returns the model configured in the environment variables.
    If not found, returns the default model (claude-sonnet-4-0).
    If use_default is True, it will return the default model
    regardless of the environment variable.

    Args:
        default_model (str): The default model to use if not found in the
            environment variables.
        use_default (bool): If True, it will return the default model
            regardless of the environment variable.

    Returns:
        str: The name of the model to use for API calls.
    """
    if use_default:
        return default_model
    return os.getenv("ANTHROPIC_MODEL", default_model)


def add_user_message(messages: list, content: str) -> None:
    """
    Adds a user message to the list of messages.

    Args:
        messages (list): The list of messages.
        content (str): The content of the user message.
    """

    user_message = {"role": "user", "content": content}

    messages.append(user_message)


def add_assistant_message(messages: list, content: str) -> None:
    """
    Adds an assistant message to the list of messages.

    Args:
        messages (list): The list of messages.
        content (str): The content of the assistant message.
    """

    assistant_message = {"role": "assistant", "content": content}

    messages.append(assistant_message)


def chat(
    messages: list,
    client: Anthropic,
    model: str,
    system_prompt: str | None = None,
    temperature: float = 1.0,
    stop_sequences: list | None = None,
) -> str:
    """
    Passes the list of messages to the API and returns the assistant's
    response content.

    Args:
        messages (list): The list of messages to send to the API.
        client (Anthropic): The initialized Anthropic client.
        model (str): The name of the model to use for API calls.
        system_prompt (str, optional): The system prompt to include in the
            API call.
        temperature (float): The temperature for the API call.
        stop_sequences (list, optional): A list of sequences to stop the
            API call.
    """

    params = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "messages": messages,
        "temperature": temperature,
    }

    if system_prompt:
        params["system"] = system_prompt

    if stop_sequences:
        params["stop_sequences"] = stop_sequences

    message = client.messages.create(**params)

    return message.content[0].text
