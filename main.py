#!/usr/bin/env python
import sys
import warnings

from dotenv import load_dotenv
from datetime import datetime
import os
from two_agent.crew import TwoAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

inputs = {'problem_statement': 'A 2D plate occupies 1 m-by-1 m domain. It is made of copper and has a circular hole of radius 0.2 m in the middle. It has zero displacement on the left edge and 0.02 m displacement along x direction on the right edge. The top and bottom edges are free to move. Please use FENICS to solve the displacement, store the result in a PNG file and figure out the total force on the right edge.'}

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

# def execute_result():
#     code_editor(input_file_path='./fenics_solution_complete10.md', output_file_path='results/final_solution1.py')

#     host_results_dir = Path("results")
#     host_results_path = host_results_dir.resolve()

#     script_filename = "final_solution.py"
#     host_script_path = host_results_path / script_filename

#     container_work_dir = Path("/app")
#     script_in_container = container_work_dir / script_filename

#     command = [
#         'docker', 'run', '--rm',
#         '-v', f'{host_results_path}:{container_work_dir}:rw',
#         '--workdir', str(container_work_dir),
#         'my-fenics-image:latest',
#         'python3', str(script_in_container)
#     ]

#     try:
#         result = subprocess.run(command, check=True, capture_output=True, text=True)
#         print(result.stdout)
#     except subprocess.CalledProcessError as e:
#         print(f"Failed to run code in the container ❌:\n{e.stderr}")


def run():
    """
    Run the crew.
    """
    # inputs = {'problem_statement': 'A 2D plate occupies a 1 meter by 1 meter domain. It is modeled as a compressible Neo-Hookean hyperelastic material with Young’s modulus of 1 GPa and Poisson’s ratio of 0.3. The left edge of the plate has zero displacement in both directions and the right edge has a prescribed displacement of 0.5 meters in the x-direction. The top and bottom edges are free to move. Solve for the displacement field considering finite deformation and nonlinear behavior and save the displacement result into a PNG file.'}
    
    try:
        # TwoAgent().crew().kickoff(inputs=inputs)
        crew_instance = TwoAgent().crew()              # آبجکت crew ساخته میشه
        crew_instance.reset_memories(command_type='short')  # ریست کردن حافظه بلندمدت
        crew_instance.kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
        


def train():
    """
    Train the crew for a given number of iterations.
    """
    #inputs = {
    #   "topic": "AI LLMs",
    #    'current_year': str(datetime.now().year)
    #}
    try:
        TwoAgent().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        TwoAgent().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    #inputs = {
    #    "topic": "AI LLMs",
    #    "current_year": str(datetime.now().year)
    #}
    
    try:
        TwoAgent().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
