import re
from CodeAnalyzer.CodeAnalyzer import CodeAnalyzer
import argparse

def needs_comment(file_content):
    for i, line in enumerate(file_content):
        match = re.match(r'\s*(def|class)\s+(\w+)', line)
        if match:
            if i == 0 or not file_content[i - 1].strip().startswith("#"):
                return True
    return False

def get_source_code(file_path: str):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error retrieving source code from {file_path}: {e}")
        return ""

def insert_comments(file_path: str, comments_map: dict):
    """
    Inserts comments into a Python file based on the provided comments map.

    This function reads the source code from the specified file, inserts comments in docstring format
    just below the function or class definitions that are keys in the comments_map, and writes the 
    modified source code back to the file.

    Args:
        file_path (str): The path to the Python file into which to insert comments.
        comments_map (dict): A dictionary mapping function or class names to their descriptive comments.
    """
    with open(file_path, 'r') as file:
        content = file.readlines()
    
    new_content = []
    skip_next_line = False

    for i, line in enumerate(content):
        if skip_next_line:
            skip_next_line = False
            continue
        match = re.match(r'\s*(def|class)\s+(\w+)', line)
        if match:
            name = match.group(2)
            if name in comments_map:
                comment = comments_map[name].replace('\n', '\n    ')
                comment_line = f'    """\n    {comment}\n    """\n'
                new_content.append(line)
                new_content.append(comment_line)
                skip_next_line = True if '{' in line else False
            else:
                new_content.append(line)
        else:
            new_content.append(line)

    with open(file_path, 'w') as file:
        file.writelines(new_content)

def parse_arguments():
    parser = argparse.ArgumentParser(description="LLM code understanding.")
    parser.add_argument('--model', type=str, default='codellama', help='Model to use for code analysis.')
    parser.add_argument('filenames', nargs='*', help='Python filenames to analyze.')

    return parser.parse_args()

def main():
    args = parse_arguments()
    code_analyzer = CodeAnalyzer(args.model)

    for file_path in args.filenames:
        with open(file_path, 'r') as file:
            file_content = file.readlines()

        if needs_comment(file_content):
            source_code = "".join(file_content)
            llm_output = code_analyzer.analyze_code(source_code)
            comments_pairs = code_analyzer.organize_output(llm_output)
            insert_comments(file_path, comments_pairs)

if __name__ == "__main__":
    main()
