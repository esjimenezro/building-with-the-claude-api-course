from anthropic.types import Message, ToolParam
from datetime import datetime, timedelta
import json
from src.utils import get_client, get_model, chat, add_assistant_message, text_from_message, add_user_message, chat_stream
from src.text_editor_tool import TextEditorTool


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
text_editor_tool = TextEditorTool()


client = get_client()
model = get_model()


def get_current_datetime(date_format: str = DATETIME_FORMAT) -> str:
    """
    Returns the current date and time formatted according to the provided date_format string.
    The date_format parameter should be a valid format string compatible with Python's strftime function.
    If no date_format is provided, it defaults to "%Y-%m-%d %H:%M:%S". The function raises a ValueError if the date_format is empty.

    Args:
        date_format (str): A format string for the output date and time. Defaults to "%Y-%m-%d %H:%M:%S".
    Returns:
        str: The current date and time formatted according to the provided date_format.
    """

    if not date_format:
        raise ValueError("date_format cannot be empty")

    return datetime.now().strftime(date_format)


def add_duration_to_datetime(
    datetime_str: str,
    duration: int = 0,
    unit: str = "days",
    input_format: str = DATE_FORMAT
) -> str:
    """
    Adds a specified duration to a datetime string and returns the resulting datetime in a detailed format.
    This tool converts an input datetime string to a Python datetime object, adds the specified duration in
    the requested unit, and returns a formatted string of the resulting datetime.
    It handles various time units including seconds, minutes, hours, days, weeks, months, and years,
    with special handling for month and year calculations to account for varying month lengths and leap years.
    The output is always returned in a detailed format that includes the day of the week, month name, day, year,
    and time with AM/PM indicator (e.g., 'Thursday, April 03, 2025 10:30:00 AM').

    Args:
        datetime_str (str): The input datetime string to which the duration will be added.
        duration (int): The amount of time to add to the datetime.
        unit (str): The unit of time for the duration.
        input_format (str): The format string for parsing the input datetime_str, using Python's strptime format codes.

    Returns:
        str: The resulting datetime after adding the duration, formatted in a detailed string format.
    """

    date = datetime.strptime(datetime_str, input_format)

    if unit == "seconds":
        new_date = date + timedelta(seconds=duration)
    elif unit == "minutes":
        new_date = date + timedelta(minutes=duration)
    elif unit == "hours":
        new_date = date + timedelta(hours=duration)
    elif unit == "days":
        new_date = date + timedelta(days=duration)
    elif unit == "weeks":
        new_date = date + timedelta(weeks=duration)
    elif unit == "months":
        month = date.month + duration
        year = date.year + month // 12
        month = month % 12
        if month == 0:
            month = 12
            year -= 1
        day = min(
            date.day,
            [
                31,
                29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ][month - 1],
        )
        new_date = date.replace(year=year, month=month, day=day)
    elif unit == "years":
        new_date = date.replace(year=date.year + duration)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")

    return new_date.strftime("%A, %B %d, %Y %I:%M:%S %p")


def set_reminder(content: str, timestamp: str) -> None:
    """
    Creates a timed reminder that will notify the user at the specified time with the provided content.

    Args:
        content (str): The message text that will be displayed in the reminder notification.
        timestamp (str): The exact date and time when the reminder should be triggered.
    """

    print(f"----\nSetting the following reminder for {timestamp}:\n{content}\n----")


get_current_datetime_schema = ToolParam({
    "name": "get_current_datetime",
    "description": "Returns the current date and time formatted according to a specified format string. Use this tool when the user asks about the current date, time, or both. Do not use this tool if the user is asking about a historical or future date — it only returns the current moment. The format string follows Python's strftime directives (e.g., '%Y-%m-%d' for ISO date, '%H:%M:%S' for time, '%Y-%m-%d %H:%M:%S' for full datetime). An empty format string will raise an error and must be avoided.",
    "input_schema": {
        "type": "object",
        "properties": {
            "date_format": {
                "type": "string",
                "description": "A Python strftime-compatible format string that controls the structure of the returned datetime string. For example, '%Y-%m-%d' returns '2025-04-01', '%H:%M:%S' returns '14:30:00', and '%Y-%m-%d %H:%M:%S' returns '2025-04-01 14:30:00'. Must not be an empty string. Defaults to the system DATETIME_FORMAT constant if omitted.",
                "default": DATETIME_FORMAT
            }
        },
        "required": []
    },
    "input_examples": [
        {"date_format": "%Y-%m-%d"},
        {"date_format": "%H:%M:%S"},
        {"date_format": "%Y-%m-%d %H:%M:%S"},
        {"date_format": "%A, %B %d %Y"}
    ]
})


add_duration_to_datetime_schema = ToolParam({
    "name": "add_duration_to_datetime",
    "description": "Adds a specified duration to a datetime string and returns the resulting datetime in a detailed format. This tool converts an input datetime string to a Python datetime object, adds the specified duration in the requested unit, and returns a formatted string of the resulting datetime. It handles various time units including seconds, minutes, hours, days, weeks, months, and years, with special handling for month and year calculations to account for varying month lengths and leap years. The output is always returned in a detailed format that includes the day of the week, month name, day, year, and time with AM/PM indicator (e.g., 'Thursday, April 03, 2025 10:30:00 AM').",
    "input_schema": {
        "type": "object",
        "properties": {
            "datetime_str": {
                "type": "string",
                "description": "The input datetime string to which the duration will be added. This should be formatted according to the input_format parameter.",
            },
            "duration": {
                "type": "number",
                "description": "The amount of time to add to the datetime. Can be positive (for future dates) or negative (for past dates). Defaults to 0.",
            },
            "unit": {
                "type": "string",
                "description": "The unit of time for the duration. Must be one of: 'seconds', 'minutes', 'hours', 'days', 'weeks', 'months', or 'years'. Defaults to 'days'.",
            },
            "input_format": {
                "type": "string",
                "description": "The format string for parsing the input datetime_str, using Python's strptime format codes. For example, '%Y-%m-%d' for ISO format dates like '2025-04-03'. Defaults to '%Y-%m-%d'.",
            },
        },
        "required": ["datetime_str"],
    },
})


set_reminder_schema = ToolParam({
    "name": "set_reminder",
    "description": "Creates a timed reminder that will notify the user at the specified time with the provided content. This tool schedules a notification to be delivered to the user at the exact timestamp provided. It should be used when a user wants to be reminded about something specific at a future point in time. The reminder system will store the content and timestamp, then trigger a notification through the user's preferred notification channels (mobile alerts, email, etc.) when the specified time arrives. Reminders are persisted even if the application is closed or the device is restarted. Users can rely on this function for important time-sensitive notifications such as meetings, tasks, medication schedules, or any other time-bound activities.",
    "input_schema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "The message text that will be displayed in the reminder notification. This should contain the specific information the user wants to be reminded about, such as 'Take medication', 'Join video call with team', or 'Pay utility bills'.",
            },
            "timestamp": {
                "type": "string",
                "description": "The exact date and time when the reminder should be triggered, formatted as an ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SS) or a Unix timestamp. The system handles all timezone processing internally, ensuring reminders are triggered at the correct time regardless of where the user is located. Users can simply specify the desired time without worrying about timezone configurations.",
            },
        },
        "required": ["content", "timestamp"],
    },
})


batch_tool_schema = ToolParam({
    "name": "batch_tool",
    "description": "Invoke multiple other tool calls simultaneously",
    "input_schema": {
        "type": "object",
        "properties": {
            "invocations": {
                "type": "array",
                "description": "The tool calls to invoke",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the tool to invoke",
                        },
                        "arguments": {
                            "type": "string",
                            "description": "The arguments to the tool, encoded as a JSON string",
                        },
                    },
                    "required": ["name", "arguments"],
                },
            }
        },
        "required": ["invocations"],
    },
})


def run_tool(tool_name: str, tool_input: dict):
    """
    Executes a tool based on its name and input parameters.

    Args:
        tool_name (str): The name of the tool to execute.
        tool_input (dict): A dictionary containing the input parameters for the tool.

    Returns:
        The output of the executed tool, which can be of any type depending on the tool's functionality.
    """

    if tool_name == "get_current_datetime":
        return get_current_datetime(**tool_input)
    elif tool_name == "add_duration_to_datetime":
        return add_duration_to_datetime(**tool_input)
    elif tool_name == "set_reminder":
        return set_reminder(**tool_input)
    elif tool_name == "save_article":
        return save_article(**tool_input)
    elif tool_name == "str_replace_based_edit_tool":
        command = tool_input["command"]
        if command == "view":
            return text_editor_tool.view(
                tool_input["path"], tool_input.get("view_range")
            )
        elif command == "str_replace":
            return text_editor_tool.str_replace(
                tool_input["path"], tool_input["old_str"], tool_input["new_str"]
            )
        elif command == "create":
            return text_editor_tool.create(tool_input["path"], tool_input["file_text"])
        elif command == "insert":
            return text_editor_tool.insert(
                tool_input["path"],
                tool_input["insert_line"],
                tool_input["new_str"],
            )
        elif command == "undo_edit":
            return text_editor_tool.undo_edit(tool_input["path"])
        else:
            raise Exception(f"Unknown text editor command: {command}")
    else:
        raise ValueError(f"Tool '{tool_name}' is not defined.")


def run_tools(message: Message) -> list[dict]:
    """
    Identifies tool use blocks in the assistant's message, executes the corresponding tools with the provided input, and returns a list of tool result blocks to be included in the conversation.
    This function processes the content of a Message object to find any blocks that represent tool use. For each tool use block, it extracts the tool name and input parameters, executes the appropriate tool function, and captures the output. The results are formatted into a list of tool result blocks, which include the type, tool use ID, content (either the tool output or an error message), and an is_error flag indicating whether the execution was successful or if an error occurred.

    Args:
        message (Message): The Message object from the assistant that may contain tool use blocks.

    Returns:
        list: A list of dictionaries representing the results of the executed tools, formatted as tool result blocks to be included in the conversation.
    """

    tool_requests = [block for block in message.content if block.type == "tool_use"]
    tool_result_blocks = []

    for tool_request in tool_requests:
        try:
            tool_output = run_tool(tool_request.name, tool_request.input)
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": json.dumps(tool_output),
                "is_error": False,
            }
        except Exception as e:
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": f"Error: {e}",
                "is_error": True,
            }

        tool_result_blocks.append(tool_result_block)

    return tool_result_blocks


def save_article(**kwargs):
    return "Article saved!"


'''
def run_conversation(messages: list[Message | str]) -> list[Message | str]:
    """
    Runs a conversation loop that continues until the assistant's response does not include a tool use block.
    In each iteration, it sends the current list of messages to the API, processes the assistant's response for
    any tool use blocks, executes the corresponding tools, and appends both the assistant's message and any tool
    results back into the conversation.

    Args:
        messages (list): The initial list of messages to start the conversation.

    Returns:
        list: The final list of messages after the conversation loop has completed, including all assistant responses and tool results.
    """
    while True:
        response = chat(
            messages=messages,
            client=client,
            model=model,
            tools=[
                get_current_datetime_schema,
                add_duration_to_datetime_schema,
                set_reminder_schema,
            ]
        )

        add_assistant_message(messages, response)
        print(text_from_message(response))

        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

    return messages


def run_conversation(
    messages: list,
    tools: list = [],
    tool_choice: dict | None = None,
    fine_grained: bool = False
) -> list:
    """
    Runs a conversation loop with the given messages and tools. It continues until
    the assistant's response does not indicate a tool use. If tool_choice is
    provided, it will break after the first response regardless of tool use.

    Args:
        messages (list): The initial list of messages to start the conversation.
        tools (list): A list of tools to include in the API calls.
        tool_choice (dict, optional): A dictionary specifying a tool choice to force in the API calls.
        fine_grained (bool): Whether to use fine-grained tool streaming, which provides more detailed information about tool calls in the stream.

    Returns:
        list: The final list of messages after the conversation loop completes.
    """

    while True:
        with chat_stream(
            messages=messages,
            client=client,
            model=model,
            tools=tools,
            betas=["fine-grained-tool-streaming-2025-05-14"] if fine_grained else [],
            tool_choice=tool_choice,
        ) as stream:
            for chunk in stream:
                if chunk.type == "text":
                    print(chunk.text, end="")

                if chunk.type == "content_block_start":
                    if chunk.content_block.type == "tool_use":
                        print(f'\n>>> Tool Call: "{chunk.content_block.name}"')

                if chunk.type == "input_json" and chunk.partial_json:
                    print(chunk.partial_json, end="")

                if chunk.type == "content_block_stop":
                    print("\n")

            response = stream.get_final_message()

        add_assistant_message(messages, response)

        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

        if tool_choice:
            break

    return messages
'''


def get_text_edit_schema(model):
    return {
        "type": "text_editor_20250728",
        "name": "str_replace_based_edit_tool",
    }


def run_conversation(messages):
    while True:
        response = chat(
            messages=messages,
            client=client,
            model=model,
            tools=[get_text_edit_schema(model)],
        )

        add_assistant_message(messages, response)
        print(text_from_message(response))

        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

    return messages
