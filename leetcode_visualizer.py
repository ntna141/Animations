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

command_format = '''
{
    "step": number (required) - The step number in sequence
    "target": "main_array" (required) - MUST ALWAYS be "main_array"
    "state": {
        "elements": array (required) - MUST contain the COMPLETE array state
        "highlighted": array - Indices to highlight
        "arrows": array - Pairs of [from_idx, to_idx] for arrows
    },
    "duration": string (optional) - Animation duration (default "3s")
    "line": number (optional) - Code line to highlight
    "text": {
        "content": string (required) - A detailed explanation in complete sentences
        "pre_duration": string (optional) - Time to show text before animation (default "1s")
        "post_duration": string (optional) - Time to show text after animation (default "2s")
    }
}'''

example_commands = '''[
    {
        "step": 1,
        "target": "main_array",
        "state": {
            "elements": [1, 2, 3, 4],
            "highlighted": [0],
            "arrows": []
        },
        "text": {
            "content": "Let's start by looking at our initial array. We have four numbers in ascending order, which will help us understand how the algorithm works with sorted data.",
            "pre_duration": "1s",
            "post_duration": "2s"
        }
    },
    {
        "step": 2,
        "target": "main_array",
        "state": {
            "elements": [2, 1, 3, 4],
            "highlighted": [0, 1],
            "arrows": []
        },
        "text": {
            "content": "When we compare the first two elements, we notice that 2 is greater than 1. This means we need to swap them to maintain our sorting criteria. Understanding these basic comparison and swap operations is crucial for following the algorithm's logic.",
            "pre_duration": "1s",
            "post_duration": "2s"
        }
    }
]'''

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

def generate_walkthrough_script(solution_code: str, description: str) -> str:
    system_message = SystemMessage(content="""You are a patient and thorough coding tutor who explains algorithms step by step.
Your goal is to help students understand not just what the code does, but why each step is necessary.""")
    
    prompt = PromptTemplate.from_template("""Given this solution code and description:

Description: {description}
Code:
{solution_code}

Create a detailed walkthrough that explains how the code works. For each step:
1. Explain what the code is doing in plain English, using complete sentences
2. Explain WHY this step is necessary for solving the problem
3. Connect each step to the bigger picture of the algorithm
4. Use student-friendly language, avoiding jargon when possible
5. If there are edge cases or special conditions, explain why we need to handle them

Focus on helping students build a mental model of how the algorithm works.
Each explanation should be 2-3 sentences long, detailed enough for a beginner to understand.

Return the walkthrough as a series of steps, where each step includes:
1. The current state of the data structure
2. A thorough explanation of what's happening
3. Any elements that should be highlighted
4. Any arrows or connections to show
6. Have time long enough for the user to read and understand the text
                                          
Format each step as a visualization command following this structure:
{command_format}""")

    message = chat_model.invoke([
        system_message,
        HumanMessage(content=prompt.format(
            description=description,
            solution_code=solution_code,
            command_format=command_format
        ))
    ])
    
    return message.content

def generate_visualization_commands_from_script(walkthrough_script: str, data_structure_type: str, solution_code: str) -> List[Dict[str, Any]]:
    commands = get_available_commands(data_structure_type)
    template = format_command_template(data_structure_type)
    
    system_message = SystemMessage(content="You are a helpful coding assistant that converts walkthrough scripts into precise visualization commands.")
    
    prompt = PromptTemplate.from_template("""Here's a walkthrough script explaining an algorithm:

{walkthrough_script}

Convert this script into visualization commands that show each step.
Each command MUST be a state-based command (not action-based) with these fields:

{command_format}

Example of proper state-based commands:
{example_commands}

Requirements:
1. EVERY command MUST:
   - Use "main_array" as target
   - Include complete array state in elements
   - Use state-based format (not action-based)
2. NO action-based commands (new_diagram, highlight, swap, etc.)
3. Keep array state consistent between steps
4. Use step numbers in sequence
5. Keep explanations brief and focused
6. Have time long enough for the user to read and understand the text

Return ONLY the JSON array of commands, nothing else.""")

    message = chat_model.invoke([
        system_message,
        HumanMessage(content=prompt.format(
            walkthrough_script=walkthrough_script,
            command_format=command_format,
            example_commands=example_commands
        ))
    ])
    
    try:
        response = message.content
        print("\nRaw Commands Generated:")
        print(response)
        
        start_idx = response.find('[')
        end_idx = response.rfind(']')
        
        if start_idx == -1 or end_idx == -1:
            print("Could not find JSON array in response")
            return []
            
        json_str = response[start_idx:end_idx + 1]
        
        try:
            commands = json.loads(json_str)
            valid_commands = []
            for cmd in commands:
                if cmd.get("target") != "main_array":
                    print(f"Skipping command with invalid target: {cmd.get('target')}")
                    continue
                if not cmd.get("state", {}).get("elements"):
                    print(f"Skipping command without elements state: {cmd}")
                    continue
                valid_commands.append(cmd)
            print(f"\nProcessed {len(valid_commands)} valid commands")
            return valid_commands
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON array: {e}")
            return []
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def generate_intuition_commands(solution_code: str) -> List[Dict[str, Any]]:
    system_message = SystemMessage(content="""You are an expert algorithm teacher who creates clear, visual explanations.
Your goal is to help students understand the core concepts before diving into code.""")
    
    prompt = PromptTemplate.from_template("""Given this solution code:

{solution_code}

Create a step-by-step intuitive explanation of how the algorithm works. Each step should be 4-5 seconds long.

Focus on:
1. Start with a simple example that shows the problem
2. Break down the core pattern/idea of the algorithm
3. Show how the pattern solves the problem
4. Demonstrate with 2-3 different examples
5. Point out any tricks or optimizations

For each step:
1. Use clear, complete sentences a beginner can understand
2. Explain WHY each part is important
3. Build up the concept gradually
4. Use arrows to show relationships
5. Highlight relevant elements

Each step should follow this exact format:
{command_format}

Make sure to:
1. Include at least 6-8 steps for proper explanation
2. Set duration to "4s" or "5s" for each step
3. Set pre_duration to "1s" and post_duration to "2s"
4. Use highlighting and arrows to draw attention
5. Keep array state consistent between steps
6. Have time long enough for the user to read and understand the text

Example step:
{example_commands}""")

    message = chat_model.invoke([
        system_message,
        HumanMessage(content=prompt.format(
            solution_code=solution_code,
            command_format=command_format,
            example_commands=example_commands[0:200]
        ))
    ])
    
    try:
        response = message.content
        start_idx = response.find('[')
        end_idx = response.rfind(']')
        
        if start_idx == -1 or end_idx == -1:
            print("Could not find JSON array in response")
            return []
            
        json_str = response[start_idx:end_idx + 1]
        commands = json.loads(json_str)
        
        # Ensure minimum duration for each command
        valid_commands = []
        for cmd in commands:
            if cmd.get("target") != "main_array":
                print(f"Skipping command with invalid target: {cmd.get('target')}")
                continue
            if not cmd.get("state", {}).get("elements"):
                print(f"Skipping command without elements state: {cmd}")
                continue
                
            # Ensure proper text format and duration
            if isinstance(cmd.get("text"), str):
                cmd["text"] = {
                    "content": cmd["text"],
                    "pre_duration": "1s",
                    "post_duration": "2s"
                }
            cmd["duration"] = "4s"  # Ensure minimum duration
            valid_commands.append(cmd)
        
        if len(valid_commands) < 4:
            print("Warning: Generated too few steps for intuition video")
            
        return valid_commands
    except Exception as e:
        print(f"Error generating intuition commands: {e}")
        return []

def process_leetcode_solution(solution_code: str, output_file: str = "animation.mp4") -> None:
    print("\n=== Step 1: Analyzing Solution ===")
    data_structure_type, initial_data, description = analyze_solution(solution_code)
    print(f"Data Structure: {data_structure_type}")
    print(f"Initial Data: {initial_data}")
    print(f"Description: {description}")
    
    print("\n=== Step 2: Generating Intuition Video ===")
    raw_intuition_commands = generate_intuition_commands(solution_code)
    
    # Process intuition commands to ensure text is string
    intuition_commands = []
    for cmd in raw_intuition_commands:
        text_data = cmd.get("text", {})
        if isinstance(text_data, dict):
            cmd["text"] = text_data.get("content", "")
        elif isinstance(text_data, str):
            cmd["text"] = text_data
        else:
            cmd["text"] = str(text_data)
        intuition_commands.append(cmd)
    
    print(f"Generated {len(intuition_commands)} intuition commands")
    
    intuition_visualizer = SolutionVisualizer()
    intuition_visualizer.create_visualization(initial_data, data_structure_type, intuition_commands, "intuition.mp4")
    intuition_visualizer.cleanup()
    
    print("\n=== Step 3: Generating Code Walkthrough Script ===")
    walkthrough_script = generate_walkthrough_script(solution_code, description)
    print("Walkthrough Script:")
    print(walkthrough_script)
    
    print("\n=== Step 4: Converting Script to Visualization Commands ===")
    raw_commands = generate_visualization_commands_from_script(walkthrough_script, data_structure_type, solution_code)
    print(f"Generated {len(raw_commands)} raw commands")
    
    print("\n=== Step 5: Processing Commands ===")
    commands = []
    for cmd in raw_commands:
        if cmd.get("target") != "main_array":
            print(f"Skipping command with invalid target: {cmd.get('target')}")
            continue
            
        # Convert from action-based format to state-based format
        if "action" in cmd:
            state = {
                "elements": cmd.get("state", {}).get("elements", []),
                "highlighted": cmd.get("state", {}).get("highlighted", []),
                "arrows": cmd.get("state", {}).get("arrows", [])
            }
            
            # Extract text content
            text_data = cmd.get("text", {})
            if isinstance(text_data, dict):
                text_content = text_data.get("content", "")
            elif isinstance(text_data, str):
                text_content = text_data
            else:
                text_content = str(text_data)
            
            command = {
                "step": cmd["step"],
                "target": "main_array",
                "state": state,
                "duration": cmd.get("properties", {}).get("duration", "3s"),
                "line": cmd.get("code_lines", {}).get("line") if "code_lines" in cmd else None,
                "text": text_content
            }
            commands.append(command)
        else:
            # Extract text content for non-action commands
            text_data = cmd.get("text", {})
            if isinstance(text_data, dict):
                cmd["text"] = text_data.get("content", "")
            elif isinstance(text_data, str):
                cmd["text"] = text_data
            else:
                cmd["text"] = str(text_data)
            commands.append(cmd)
    
    print(f"Processed {len(commands)} valid commands")
    
    print("\n=== Step 6: Creating Code Walkthrough Video ===")
    code_visualizer = SolutionVisualizer()
    code_visualizer.set_solution_code(solution_code)
    code_visualizer.create_visualization(initial_data, data_structure_type, commands, output_file)
    code_visualizer.cleanup()
    print(f"Visualization saved to {output_file}") 