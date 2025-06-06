import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
import yaml

def load_yaml(file_path):
    here = os.path.dirname(__file__)
    abs_path = os.path.join(here, file_path)
    with open(abs_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def make_agents():
    agents_config = load_yaml("config/agents.yaml")

    news_reporter = Agent(
        role=agents_config["news_reporter"]["role"],
        goal=agents_config["news_reporter"]["goal"],
        backstory=agents_config["news_reporter"]["backstory"],
        tools=[SerperDevTool()],
        llm=agents_config["news_reporter"]["llm"],
        verbose=True
    )

    news_copywriter = Agent(
        role=agents_config["news_copywriter"]["role"],
        goal=agents_config["news_copywriter"]["goal"],
        backstory=agents_config["news_copywriter"]["backstory"],
        llm=agents_config["news_copywriter"]["llm"],
        verbose=True
    )

    designer_agent = Agent(
        role=agents_config["designer_agent"]["role"],
        goal=agents_config["designer_agent"]["goal"],
        backstory=agents_config["designer_agent"]["backstory"],
        llm=agents_config["designer_agent"]["llm"],
        verbose=True
    )

    return news_reporter, news_copywriter, designer_agent

def make_tasks(news_reporter, news_copywriter, designer_agent, field, websites, style_examples_text):
    tasks_config = load_yaml("config/tasks.yaml")

    fetch_news_desc = tasks_config["fetch_news"]["description"].format(
        field=field, websites=", ".join(websites)
    )
    rewrite_article_desc = tasks_config["rewrite_article"]["description"].format(
        style_examples=style_examples_text
    )
    gen_img_prompt_desc = tasks_config["generate_image_prompt"]["description"]

    fetch_news = Task(
        description=fetch_news_desc,
        expected_output=tasks_config["fetch_news"]["expected_output"],
        agent=news_reporter
    )
    rewrite_article = Task(
        description=rewrite_article_desc,
        expected_output=tasks_config["rewrite_article"]["expected_output"],
        agent=news_copywriter,
        context=[fetch_news]
    )
    generate_image_prompt = Task(
        description=gen_img_prompt_desc,
        expected_output=tasks_config["generate_image_prompt"]["expected_output"],
        agent=designer_agent,
        context=[rewrite_article]
    )
    return fetch_news, rewrite_article, generate_image_prompt

def build_crew(field, websites, style_examples_text):
    news_reporter, news_copywriter, designer_agent = make_agents()
    fetch_news, rewrite_article, generate_image_prompt = make_tasks(
        news_reporter, news_copywriter, designer_agent, field, websites, style_examples_text
    )

    crew = Crew(
        agents=[news_reporter, news_copywriter, designer_agent],
        tasks=[fetch_news, rewrite_article, generate_image_prompt],
        process=Process.sequential,
        verbose=True
    )
    return crew
