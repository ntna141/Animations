from typing import List, Dict, Any, Optional, Tuple
import json
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from visualize_solution import SolutionVisualizer, get_available_commands, format_command_template
from linked_list_visualizer import Node

load_dotenv()
chat_model = ChatAnthropic(
    api_key=os.getenv('ANTHROPIC_API_KEY'),
    model_name="claude-3-5-sonnet-20240620",
    max_tokens=8192
)

def analyze_solution(solution_code: str) -> Tuple[str, Any, str]:
    system_message = SystemMessage(content="You are a helpful coding assistant that analyzes algorithms.")
    
    prompt = PromptTemplate.from_template("""Analyze this LeetCode solution and determine:
1. What data structure it primarily operates on (array or linked list)?
2. What would be a good example input to demonstrate this algorithm? For arrays, provide just the numbers in brackets. For linked lists, use the Node(value)->Node(value) format.
3. A brief description of what the solution does.

Format your response exactly like this:
DATA_STRUCTURE: array or linked_list
INITIAL_DATA: [1, 2, 3, 4] or Node(1)->Node(2)->Node(3)
DESCRIPTION: Brief description

Here's the solution:

{solution_code}""")

    message = chat_model.invoke([
        system_message,
        HumanMessage(content=prompt.format(solution_code=solution_code))
    ])
    
    response = message.content
    
    data_structure = None
    initial_data = None
    description = None
    
    for line in response.split('\n'):
        if line.startswith('DATA_STRUCTURE:'):
            data_structure = line.split(':')[1].strip()
        elif line.startswith('INITIAL_DATA:'):
            raw_data = line.split(':')[1].strip()
            if data_structure == "array":
                try:
                    initial_data = eval(raw_data)
                except:
                    initial_data = []
            elif data_structure == "linked_list":
                try:
                    values = [int(x.split('(')[1].split(')')[0]) 
                             for x in raw_data.split('->')]
                    if values:
                        head = Node(values[0])
                        current = head
                        for val in values[1:]:
                            current.next = Node(val)
                            current = current.next
                        initial_data = head
                except:
                    initial_data = Node(0)
        elif line.startswith('DESCRIPTION:'):
            description = line.split(':')[1].strip()
    
    return data_structure, initial_data, description

def generate_walkthrough(solution_code: str, description: str) -> str:
    system_message = SystemMessage(content="You are a helpful coding assistant that explains algorithms clearly.")
    
    prompt = PromptTemplate.from_template("""Here's a LeetCode solution that {description}:

{solution_code}

Please provide a step-by-step walkthrough of the intuition and approach for a VERY WEAK leetcode student.
Break it down into clear, logical steps that we can visualize.
Focus on the key operations and comparisons that happen in the code, explain what happens in complicated operations with examples.
Feel free to switch between examples to go deeper into the code.
Make sure to explain what happens at each step in a way that can be visualized.""")

    message = chat_model.invoke([
        system_message,
        HumanMessage(content=prompt.format(solution_code=solution_code, description=description))
    ])
    
    return message.content

def generate_visualization_commands(walkthrough: str, data_structure_type: str, solution_code: str) -> List[Dict[str, Any]]:
    commands = get_available_commands(data_structure_type)
    template = format_command_template(data_structure_type)
    
    system_message = SystemMessage(content="You are a helpful coding assistant that generates precise visualization commands.")
    
    prompt = PromptTemplate.from_template("""Based on this algorithm walkthrough:

{walkthrough}

And this solution code:
{solution_code}

Generate concise JSON visualization commands to explain this algorithm step by step.
Use these available actions: {actions}

Each command should be a concise JSON object with these fields:
- step: number (required) - The step number in sequence
- target: string (required) - The name of the data structure to modify (e.g. "main_array")
- state: object (required) - The complete target state to animate to:
  - elements: array - The values in the data structure
  - highlighted: array - Indices of highlighted elements
  - arrows: array - Pairs of [from_idx, to_idx] for arrows between elements
- duration: string (optional) - Animation duration (default "2s")
- line: number (optional) - Code line to highlight
- text: string (optional) - Transcript text to display

Example commands:
[
    {{
        "step": 1,
        "target": "main_array",
        "state": {{
            "elements": [1, 2, 3, 4],
            "highlighted": [0],
            "arrows": []
        }},
        "line": 3,
        "text": "Starting with first element"
    }},
    {{
        "step": 2,
        "target": "main_array",
        "state": {{
            "elements": [2, 1, 3, 4],
            "highlighted": [0, 1],
            "arrows": [[0, 1]]
        }},
        "duration": "1.5s",
        "line": 4,
        "text": "Swap adjacent elements"
    }}
]

Requirements:
1. Keep explanations brief and focused
2. Use simple timings (1-2s)
3. Each step must have an increasing step number
4. The main array/list is already created as "main_array"
5. Only create new structures for separate examples
6. Return ONLY the JSON array of commands, nothing else

Return ONLY the JSON array of commands, nothing else.""")

    message = chat_model.invoke([
        system_message,
        HumanMessage(content=prompt.format(
            walkthrough=walkthrough,
            solution_code=solution_code,
            actions=', '.join(commands['actions']),
            template=template
        ))
    ])
    
    try:
        response = message.content
        print(response)
        
        start_idx = response.find('[')
        end_idx = response.rfind(']')
        
        if start_idx == -1 or end_idx == -1:
            print("Could not find JSON array in response")
            return []
            
        json_str = response[start_idx:end_idx + 1]
        
        try:
            commands = json.loads(json_str)
            return commands
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON array: {e}")
            print("Attempting to fix truncated JSON...")
            
            commands = []
            depth = 0
            last_complete_idx = start_idx
            
            for i, char in enumerate(json_str):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        last_complete_idx = i + 1
            
            if last_complete_idx > start_idx:
                try:
                    fixed_json = json_str[:last_complete_idx] + "]"
                    commands = json.loads(fixed_json)
                    print(f"Successfully parsed {len(commands)} complete commands")
                    return commands
                except json.JSONDecodeError:
                    print("Failed to parse even with truncation fix")
            
            return []
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def process_leetcode_solution(solution_code: str, output_file: str = "animation.mp4") -> None:
    data_structure_type, initial_data, description = analyze_solution(solution_code)
    
    walkthrough = generate_walkthrough(solution_code, description)
    
    commands = generate_visualization_commands(walkthrough, data_structure_type, solution_code)
    
    visualizer = SolutionVisualizer()
    visualizer.set_solution_code(solution_code)
    visualizer.create_visualization(initial_data, data_structure_type, commands, output_file)
    visualizer.cleanup() 