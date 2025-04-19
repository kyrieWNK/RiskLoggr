import os

def parse_input(input_data: str, is_file: bool = False) -> str:
    """
    Parses input data, handling freeform text or file paths.

    Args:
        input_data: The input string, either freeform text or a file path.
        is_file: Boolean indicating if input_data is a file path.

    Returns:
        The parsed text content.
    """
    if is_file:
        if not os.path.exists(input_data):
            return f"Error: File not found at {input_data}"
        try:
            with open(input_data, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Error reading file {input_data}: {e}"
    else:
        return input_data