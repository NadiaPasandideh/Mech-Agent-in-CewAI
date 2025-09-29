from crewai import Agent, Crew, Process, Task
from crewai.memory.short_term.short_term_memory import ShortTermMemory
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from two_agent.tools.docker_executer import DockerExecutorTool


# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

short_term_memory = ShortTermMemory()

code_interpreter = DockerExecutorTool(docker_image_name='my-fenics-image:latest')

@CrewBase
class TwoAgent():
    """TwoAgent crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def assistant_engineer(self) -> Agent:
        # Loads config from config/agents.yaml
        # tool = CodeInterpreterTool()
        return Agent(
            config=self.agents_config['assistant_engineer'], # type: ignore[index]
            # tools=[tool],
            verbose=True,
            allow_delegation=False,
            memory=False
        )

        

    @agent
    def user_proxy(self) -> Agent:
        
        return Agent(
            config=self.agents_config['user_proxy'], # type: ignore[index]
            tools=[code_interpreter],
            verbose=True,
            allow_delegation=False,
            memory=False,
            # allow_code_execution=True
        )
    
    @agent
    def conversation_observer(self) -> Agent:
        return Agent(
            config=self.agents_config['conversation_observer'],  # type: ignore[index]
            verbose=True,
            memory=True,
            allow_delegation=False,
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def receive_problem_task(self) -> Task:
        return Task(
            config=self.tasks_config['receive_problem_task'],
            agent=self.user_proxy()
        )

    @task
    def generate_initial_fenics_code_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_initial_fenics_code_task'],
            agent=self.assistant_engineer(),
            context=[self.receive_problem_task()]
        )

    @task
    def execute_and_validate_fenics_task(self) -> Task:
        return Task(
            config=self.tasks_config['execute_and_validate_fenics_task'],
            agent=self.user_proxy(),
            context=[self.generate_initial_fenics_code_task()]
        )

    @task
    def debug_and_fix_fenics_code_task(self) -> Task:
        return Task(
            config=self.tasks_config['debug_and_fix_fenics_code_task'],
            agent=self.assistant_engineer(),
            context=[self.execute_and_validate_fenics_task()]
        )
        
    @task
    def finalize_fenics_solution_task(self) -> Task:
        return Task(
            config=self.tasks_config['finalize_fenics_solution_task'],
            agent=self.assistant_engineer(),
            context=[self.debug_and_fix_fenics_code_task()]
        )
    
    @task
    def conversation_task(self) -> Task:
        return Task(       
            config=self.tasks_config['conversation_task'],
            agent=self.conversation_observer(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
            short_term_memory=short_term_memory,
            cache=False
        )
