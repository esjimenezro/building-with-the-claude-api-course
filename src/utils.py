import os
from anthropic import Anthropic
from anthropic.types import Message
from anthropic.types.beta import BetaMessage
from dotenv import load_dotenv

load_dotenv()

MAX_TOKENS = 4000


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


def add_user_message(messages: list, message: Message | list | str) -> None:
    """
    Adds a user message to the list of messages.

    Args:
        messages (list): The list of messages.
        message (Message | list | str): The user message object or its content.
    """
    if isinstance(message, list):
        user_message = {
            "role": "user",
            "content": message
        }
    elif isinstance(message, Message):
        user_message = {
            "role": "user",
            "content": message.content,
        }
    else:
        user_message = {
            "role": "user",
            "content": [{"type": "text", "text": message}]
        }

    messages.append(user_message)


def add_assistant_message(messages: list, message: Message | list | str) -> None:
    """
    Adds an assistant message to the list of messages.

    Args:
        messages (list): The list of messages.
        message (Message | list | str): The assistant message object or its content.
    """

    if isinstance(message, list):
        assistant_message = {
            "role": "assistant",
            "content": message,
        }
    elif isinstance(message, (Message, BetaMessage)):
        content_list = []
        for block in message.content:
            if block.type == "text":
                content_list.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                content_list.append(
                    {
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    }
                )
        assistant_message = {
            "role": "assistant",
            "content": content_list,
        }
    else:
        # String messages need to be wrapped in a list with text block
        assistant_message = {
            "role": "assistant",
            "content": [{"type": "text", "text": message}],
        }

    messages.append(assistant_message)


def chat(
    messages: list,
    client: Anthropic,
    model: str,
    system_prompt: str | None = None,
    temperature: float = 1.0,
    stop_sequences: list | None = None,
    tools: list | None = None,
    thinking: bool = False,
    thinking_budget: int = 1024,
) -> Message:
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
        tools (list, optional): A list of tools to include in the API call.
        thinking (bool, optional): Whether to enable thinking mode.
        thinking_budget (int, optional): The budget for thinking mode.
    """

    params = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "messages": messages,
        "temperature": temperature,
    }

    if stop_sequences:
        params["stop_sequences"] = stop_sequences

    if tools:
        # Always cache tools
        tools_clone = tools.copy()
        last_tool = tools_clone[-1].copy()
        last_tool["cache_control"] = {"type": "ephemeral"}
        tools_clone[-1] = last_tool
        params["tools"] = tools_clone

    if system_prompt:
        # Always cache system prompts
        params["system"] = [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    if thinking:
        params["thinking"] = {
            "type": "enabled",
            "budget_tokens": thinking_budget,
        }

    message = client.messages.create(**params)

    return message


def text_from_message(message: Message) -> str:
    """
    Extracts and concatenates the text content from a Message object.

    Args:
        message (Message): The Message object from which to extract text.
    Returns:
        str: A single string containing the concatenated text from all text
            blocks in the message content.
    """

    return "\n".join([
        block.text
        for block in message.content
        if block.type == "text"
    ])


def chat_stream(
    messages: list,
    client: Anthropic,
    model: str,
    system_prompt: str | None = None,
    temperature: float = 1.0,
    stop_sequences: list | None = None,
    tools: list | None = None,
    tool_choice: dict | None = None,
    betas=[],
):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if tool_choice:
        params["tool_choice"] = tool_choice

    if tools:
        params["tools"] = tools

    if system_prompt:
        params["system"] = system_prompt

    if betas:
        params["betas"] = betas

    return client.beta.messages.stream(**params)
