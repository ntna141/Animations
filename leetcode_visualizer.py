from typing import List, Dict, Any, Optional, Tuple
import json
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from simple_visualizer import SimpleVisualizer, VisualizerConfig
from frame import Frame, DataStructure
from data_structures import Node, TreeNode
from data_structure_examples import get_data_structure_examples, get_available_data_structures

load_dotenv()
chat_model = ChatAnthropic(
    api_key=os.getenv('ANTHROPIC_API_KEY'),
    model_name="claude-3-5-sonnet-20240620",
    max_tokens=8192
)

def analyze_solution(solution_code: str) -> Tuple[List[str], Any, str]:
    system_message = SystemMessage(content="""You are a helpful coding assistant that analyzes algorithms.
When generating visualizations:
- Use arrows=[(i,j)] for curved arrows between different elements
- Use self_arrows=[i] for straight vertical arrows pointing to the same element
- Use labels={i: ["label"]} for labels that appear below cells
- Use pointers={i: ["ptr"]} for pointers that appear above cells with vertical arrows""")
    
    prompt = PromptTemplate.from_template("""Analyze this LeetCode solution and determine:
1. What data structures that is used in the solution? List all data structures used from the list of available data structures: {available_data_structures}.
2. What would be a good example input to demonstrate this algorithm? For arrays, provide just the numbers in brackets. For linked lists, use the Node(value)->Node(value) format.
3. A brief description of what the solution does.
                                          
Format your response exactly like this:
DATA_STRUCTURES: [array, linked_list, dict] (list all used)
INITIAL_DATA: [1, 2, 3, 4] or Node(1)->Node(2)->Node(3)
DESCRIPTION: Brief description

Here's the solution:

{solution_code}""")

    message = chat_model.invoke([
        system_message,
        HumanMessage(content=prompt.format(
            solution_code=solution_code,
            available_data_structures=get_available_data_structures()
        ))
    ])
    
    response = message.content
    
    data_structures = []
    initial_data = None
    description = None
    print(response)
    for line in response.split('\n'):
        if line.startswith('DATA_STRUCTURES:'):
            try:
                # Convert bare words to proper Python string literals
                data_str = line.split(':')[1].strip()
                if data_str.startswith('[') and data_str.endswith(']'):
                    data_str = data_str[1:-1]  # Remove brackets
                # Split by comma and clean up each item
                items = [item.strip() for item in data_str.split(',')]
                # Convert to proper Python list of strings
                data_structures = items
                print(f"Successfully parsed data structures: {data_structures}")
            except Exception as e:
                print(f"Error parsing data structures: {e}")
                print(f"Raw data structures string: '{line}'")
                # More reasonable default that includes dict if we see 'dict' in the string
                if 'dict' in line.lower() or 'hashmap' in line.lower():
                    data_structures = ['array', 'dict']
                else:
                    data_structures = ['array']
        elif line.startswith('INITIAL_DATA:'):
            raw_data = line.split(':')[1].strip()
            if 'Node' in raw_data:
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
            else:
                try:
                    initial_data = eval(raw_data)
                except:
                    initial_data = []
        elif line.startswith('DESCRIPTION:'):
            description = line.split(':')[1].strip()
    
    return data_structures, initial_data, description

def generate_walkthrough_script(solution_code: str, description: str) -> str:
    system_message = SystemMessage(content="""You are a patient and thorough coding tutor who explains algorithms through visual steps.
Create a step-by-step walkthrough that shows exactly how the algorithm works with a specific example, similar to watching an animation.
Focus on showing the state of the data structure at each step and explaining what's happening, not on explaining the code itself.

For trees, always use array representation where:
- Each node's value is at index i
- Left child is at index 2i + 1
- Right child is at index 2i + 2
- Use None for missing nodes
Example: [1, 2, 3, 4, None, 6, None] represents:
    1
   / \
  2   3
 /     \
4       6""")
    
    prompt = PromptTemplate.from_template("""Create a step-by-step visual walkthrough of this algorithm:

Description: {description}
Code:
{solution_code}

Your walkthrough should:
1. Use a specific, simple example that clearly demonstrates the algorithm
2. Show the exact state of the data structure at each step
3. Use visual markers like underlines (_) for anchors and arrows (↑) for pointers
4. Explain what's happening in plain English at each step
5. Focus on the algorithm's behavior, not the code implementation

Format your response like this example:

Let me show you how we solve the threeSum problem using the array [-4, -1, -1, 0, 1, 2].

STEP 0 - THE SETUP
First, think of this like a game where you're trying to balance a scale to zero. We'll pick one number as our anchor, then try to find two other numbers that balance it out.

We sort our numbers first: [-4, -1, -1, 0, 1, 2]

STEP 1 - FIRST ANCHOR (-4)
Let's pick -4 as our anchor. We'll underline it and use two pointers (L and R) to find numbers that sum with it to zero:

[-4, -1, -1,  0,  1,  2]
 _    ↑               ↑
 i    L               R

Think: "We need two numbers that add up to +4 to balance out our -4"

[Continue with similar detailed visual steps...]

Remember to:
1. Show the exact state of the data structure at each step
2. Use visual markers consistently
3. Explain the reasoning behind each move
4. Keep the focus on what's happening visually""")

    message = chat_model.invoke([
        system_message,
        HumanMessage(content=prompt.format(
            description=description,
            solution_code=solution_code
        ))
    ])
    
    return message.content

def safe_eval_frames(frames_str: str) -> List[Frame]:
    """Safely evaluate frames string into Frame objects"""
    
    frames_str = frames_str.strip()
    
    if 'Frame(' not in frames_str[:10]:  
        start_idx = frames_str.find('[')
        if start_idx == -1:
            return []
        frames_str = frames_str[start_idx:]
    
    try:
        globals_dict = {
            'Frame': Frame,
            'DataStructure': DataStructure,
            'TreeNode': TreeNode,
            'True': True,
            'False': False,
            'None': None
        }
        
        local_dict = {}
        exec(f"frames = {frames_str}", globals_dict, local_dict)
        
        return local_dict['frames']
    except Exception as e:
        print(f"Error evaluating frames: {e}")
        return []

def generate_intuition_frames(solution_code: str, description: str) -> List[Frame]:
    system_message = SystemMessage(content="""You are an expert algorithm teacher who creates clear, visual explanations.
For merge sort specifically, use multiple arrays to show the division and merging process clearly.
Your goal is to help students understand the core concepts before diving into code.

When using variables in the visualization:
1. Only track variables that help explain the core concept
2. Prefer visual elements (arrows, highlights, labels) over variables
3. Use variables for:
   - Result collections that show what we're building
   - Algorithm-specific data structures (queue in BFS, stack in DFS)
   - Important values that can't be shown visually
4. Don't track variables that are already shown with visual elements
5. Keep it minimal - only show what's needed to understand the concept""")
    
    prompt = PromptTemplate.from_template("""Create an intuitive explanation of this algorithm:

Solution:
{solution_code}

Description:
{description}

Each frame should be created using this format:

Frame(
    structures={{
        'main': DataStructure(
            type="array",  
            elements=[1, 2, 3],  
            highlighted=[0, 1],  
            arrows=[(0, 2)],     
            self_arrows=[1],     
            labels={{0: ["i"]}},   
            pointers={{1: ["L"]}}  
        )
    }},
    variables={{'res': []}},  # Only use variables when they add value:
                            # - For result collections
                            # - For algorithm-specific data structures
                            # - Don't duplicate visual information
    duration="3s",       
    line=5,             
    text="First, think of this like a game where you're trying to balance a scale to zero. We'll pick one number as our anchor, then try to find two other numbers that balance it out."   
)

Focus on:
1. Start with a simple example that clearly shows the pattern
2. Break down the core idea step by step
3. Show how the pattern solves the problem, you can use the before frame as a reference to show how the data structure changes
4. Point out key insights and tricks
5. Use visual elements (highlights, arrows, labels) effectively
6. Do not skip any steps, explain the reasoning behind each move

Requirements:
1. Include 6-8 frames for a proper explanation
2. Set appropriate durations (longer for complex ideas)
3. Use clear, complete sentences a beginner can understand
4. Build concepts gradually
5. Use arrows to show relationships
6. Use labels and pointers to identify important elements
7. Keep text concise but informative
8. Use the before frame as a reference to show how the data structure changes if needed
9. Only use variables when they enhance understanding:
   - Prefer visual elements over variables
   - Only track essential algorithm state
   - Don't duplicate information shown visually

Return ONLY the Python list of Frame objects, nothing else.""")

    message = chat_model.invoke([
        system_message,
        HumanMessage(content=prompt.format(
            solution_code=solution_code,
            description=description
        ))
    ])
    
    try:
        response = message.content
        print("\nRaw Intuition Frames Generated:")
        print(response)
        
        
        frames_str = response[response.find('['):response.rfind(']')+1]
        
        frames_str = frames_str.replace('\n', ' ').strip()
        namespace = {
            'Frame': Frame,
            'DataStructure': DataStructure,
            'True': True,
            'False': False,
            'None': None,
            'List': List
        }
        frames = eval(frames_str, namespace)
        print(f"\nProcessed {len(frames)} frames")
        return frames
    except Exception as e:
        print(f"Error generating frames: {e}")
        return []

def generate_visualization_frames(walkthrough_script: str, data_structures: List[str], solution_code: str) -> List[Frame]:
    system_message = SystemMessage(content="""You are a helpful coding assistant that converts walkthrough scripts into precise visualization frames.
For merge sort specifically, use multiple arrays to show the division and merging process clearly.
When using variables:
1. Only track variables that are essential to understanding the algorithm (e.g., result arrays, queue in BFS, pointers in two-pointer)
2. Don't track variables that are obvious from the visualization (e.g., if a pointer is shown with an arrow, don't duplicate it as a variable)
3. Prefer using visual elements (arrows, highlights, labels) over variables when possible
4. Use variables for:
   - Collecting results (e.g., res = [])
   - Data structures needed by the algorithm (e.g., queue = [] in BFS)
   - Important counters or values not easily shown in the visualization
5. Don't track temporary loop variables or indices that aren't crucial to understanding

For trees, always use array representation where:
- Each node's value is at index i
- Left child is at index 2i + 1
- Right child is at index 2i + 2
- Use None for missing nodes
Example: [1, 2, 3, 4, None, 6, None] represents:
    1
   / \
  2   3
 /     \
4       6""")
    
    # Get example frames for all data structures used
    examples = get_data_structure_examples(data_structures)
    examples_str = str(examples).replace('\n', ' ')
    
    prompt = PromptTemplate.from_template("""Here's a walkthrough script explaining an algorithm:

{walkthrough_script}

Convert this script into visualization frames that show each step.
For example, with merge sort, you should:
1. Show the division process by creating separate arrays for each subarray
2. Name the arrays meaningfully (e.g., 'left', 'right', 'left1', 'left2', etc.)
3. Show the merging process by displaying both input arrays and the merged result

Here are example frames showing how to use each data structure:

{examples}

The algorithm uses these data structures: {data_structures}

Requirements:
1. Show the COMPLETE process of the algorithm using multiple data structures if needed
2. Keep data structure state consistent between frames
3. Do not use step numbers in sequence
4. Explanations should be simple and easy to understand, good enough for a beginner who barely understand Data Structures and faithful to the script
5. Have time long enough for the user to read and understand the text
6. Be faithful to the script, use the same example, same dialoge and steps, same highlights and arrows if available
7. Use line numbers from the solution code when relevant
8. If it is a complicated process for a beginneer, use the before frame as a reference to show how the data structure changes
9. Only use variables when they add value to understanding:
   - Use them for result collections, algorithm-specific data structures (queue, stack)
   - Don't duplicate information already shown by visual elements
   - Don't track obvious or temporary variables

Return ONLY the Python list of Frame objects, nothing else.""")

    message = chat_model.invoke([
        system_message,
        HumanMessage(content=prompt.format(
            walkthrough_script=walkthrough_script,
            data_structures=data_structures,
            examples=examples_str
        ))
    ])
    
    try:
        response = message.content
        print("\nRaw Frames Generated:")
        print(response)
        
        frames = safe_eval_frames(response)
        print(f"\nProcessed {len(frames)} frames")
        return frames
    except Exception as e:
        print(f"Error generating frames: {e}")
        return []

def process_leetcode_solution(solution_code: str, output_file: str = "animation.mp4") -> None:
    print("\n=== Step 1: Analyzing Solution ===")
    data_structures, initial_data, description = analyze_solution(solution_code)
    print(f"Data Structures: {data_structures}")
    print(f"Initial Data: {initial_data}")
    print(f"Description: {description}")
    
    # print("\n=== Step 2: Generating Intuition Frames ===")
    # intuition_frames = generate_intuition_frames(solution_code, description)
    # print(f"Generated {len(intuition_frames)} intuition frames")
    
    # print("\n=== Step 3: Creating Intuition Video ===")
    config = VisualizerConfig()
    # visualizer = SimpleVisualizer(config)
    # visualizer.visualize_frames(intuition_frames, "intuition.mp4")
    
    print("\n=== Step 4: Generating Walkthrough Script ===")
    walkthrough_script = generate_walkthrough_script(solution_code, description)
    print("Walkthrough Script:")
    print(walkthrough_script)
    
    print("\n=== Step 5: Converting Script to Frames ===")
    walkthrough_frames = generate_visualization_frames(walkthrough_script, data_structures, solution_code)
    print(f"Generated {len(walkthrough_frames)} walkthrough frames")
    
    print("\n=== Step 6: Creating Walkthrough Video ===")
    visualizer = SimpleVisualizer(config)
    visualizer.visualize_frames(walkthrough_frames, output_file)
    print(f"Visualization saved to {output_file}") 