import subprocess
import os
from pathlib import Path
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class DockerExecutorInput(BaseModel):
    """Input schema for the Docker Code Executor Tool."""
    python_code: str = Field(..., description="A string containing the Python code to be executed.")

class DockerExecutorTool(BaseTool):
    name: str = "Docker Code Executor"
    description: str = (
        "Executes Python code in a pre-configured FEniCS Docker image and saves any "
        "generated files (e.g., plots, data) into a 'results' folder in the project directory."
    )
    args_schema: Type[BaseModel] = DockerExecutorInput
    docker_image_name: str = ""

    def __init__(self, docker_image_name: str, **kwargs):
        super().__init__(**kwargs)
        self.docker_image_name = docker_image_name
        print(f"--- [DEBUG] Tool Initialized. Docker Image: {self.docker_image_name} ---")

    def _run(self, python_code: str) -> str:
        print("\n--- [DEBUG] _run method started ---")
        if not self.docker_image_name:
            return "Error: Docker image name is not configured for the tool."

        # Define and create the 'results' directory on the host
        host_results_dir = Path("results")
        host_results_path = host_results_dir.resolve()

        print(f"--- [DEBUG] Absolute path for 'results' folder: {host_results_path} ---")

        try:
            host_results_dir.mkdir(exist_ok=True)
            print(f"--- [DEBUG] 'results' directory ensured to exist. ---")
        except Exception as e:
            print(f"--- [DEBUG] FAILED to create 'results' directory. Error: {e} ---")
            return f"Error: Could not create the results directory at {host_results_path}. Check permissions."

        # Define the script path inside the host's results directory
        script_filename = "_temp_script.py"
        host_script_path = host_results_path / script_filename

        # Write the Python code to the temporary script file
        with open(host_script_path, "w", encoding="utf-8") as f:
            f.write(python_code)

        print(f"--- [DEBUG] Temporary script created at: {host_script_path} ---")

        # Define the working directory inside the container
        container_work_dir = Path("/app")
        script_in_container = container_work_dir / script_filename

        command = [
            'docker', 'run', '--rm',
            '-v', f'{host_results_path}:{container_work_dir}:rw',
            '-w', str(container_work_dir),
            self.docker_image_name,
            'python3', str(script_in_container)
        ]

        # --- CRITICAL DEBUG STEP: PRINT THE EXACT COMMAND ---
        command_str = " ".join(map(str, command))
        print(f"\n--- [DEBUG] EXECUTING DOCKER COMMAND: ---\n{command_str}\n--------------------------------------\n")

        try:
            process = subprocess.run(
                command, capture_output=True, text=True, check=False
            )
            console_output = process.stdout + process.stderr
        finally:
            # Clean up the temporary script file after execution
            if os.path.exists(host_script_path):
                os.remove(host_script_path)
            print(f"--- [DEBUG] Temporary script cleaned up. ---")

        print(f"--- [DEBUG] Docker execution finished. Exit Code: {process.returncode} ---")
        print(f"--- [DEBUG] Console Output from Docker:\n{console_output.strip()}\n---")

        # After execution, list all files created in the results directory
        created_files = [str(f.name) for f in host_results_path.glob('*')]
        print(f"--- [DEBUG] Files found in '{host_results_path}': {created_files} ---")
        

        if process.returncode == 0:
            if created_files:
                files_list_str = "\n".join(created_files)
                return (f"Execution Successful.\n"
                        f"Console Output:\n---\n{console_output.strip()}\n---\n"
                        f"Output files created in the '{host_results_dir}' folder:\n{files_list_str}")
            else:
                return f"Execution Successful:\n---\n{console_output.strip()}"
        else:
            return f"Execution Failed (Exit Code {process.returncode}):\n---\n{console_output.strip()}"