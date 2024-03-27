import re
from CodeAnalyzer.CodeAnalyzer import CodeAnalyzer
import subprocess
import argparse

def needs_comment(file_content):
    for i, line in enumerate(file_content):
        match = re.match(r'\s*(def|class)\s+(\w+)', line)
        if match:
            if i == 0 or not file_content[i - 1].strip().startswith("#"):
                return True
    return False

def get_staged_python_files():
    result = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True)
    modified_files = result.stdout.split('\n')
    return [file for file in modified_files if file.endswith('.py')]

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

    This function reads the source code from the specified file, inserts comments above functions
    or classes that are keys in the comments_map, and writes the modified source code back to the file.

    Args:
        file_path (str): The path to the Python file into which to insert comments.
        comments_map (dict): A dictionary mapping function or class names to their descriptive comments.

    Note:
        If a function or class already has a comment directly above it, no new comment is added.
    """
    with open(file_path, 'r') as file:
        content = file.readlines()
    
    new_content = []

    for i, line in enumerate(content):
        # Check if the line is a function or class definition
        match = re.match(r'\s*(def|class)\s+(\w+)', line)
        if match:
            # Check if there's a comment directly above this line
            if i > 0 and content[i - 1].strip().startswith("#"):
                new_content.append(line)
            else:
                # If there's no comment, check if the function/class is in the comments_map
                name = match.group(2)
                if name in comments_map:
                    comment_line = f"# {comments_map[name]}\n"
                    new_content.append(comment_line)
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
