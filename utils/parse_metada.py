def parse_metadata(metadata_input):
    """
    Parses a metadata input string of the format 'key1=value1, key2=value2, ...' into a dictionary.

    Parameters:
    - metadata_input (str): The input string containing metadata.

    Returns:
    - dict: A dictionary with keys and values parsed from the input string.
    """
    metadata_dict = {}
    if metadata_input:
        items = metadata_input.split(',')
        for item in items:
            if '=' in item:
                key, value = item.split('=', 1)
                metadata_dict[key.strip()] = value.strip()
            else:
                # Optionally handle invalid entries
                pass  # You can log a warning or raise an exception if needed
    return metadata_dict
