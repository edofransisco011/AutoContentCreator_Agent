import os
import yaml
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

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
        tools=[SerperDevTool(), ScrapeWebsiteTool()],
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

def make_tasks(news_reporter, news_copywriter, designer_agent, field, website, style_examples_text):
    tasks_config = load_yaml("config/tasks.yaml")

    find_urls_desc = tasks_config["find_article_urls"]["description"].format(
        field=field, website=website
    )
    find_article_urls = Task(
        description=find_urls_desc,
        expected_output=tasks_config["find_article_urls"]["expected_output"],
        agent=news_reporter
    )

    scrape_article_content = Task(
        description=tasks_config["scrape_article_content"]["description"],
        expected_output=tasks_config["scrape_article_content"]["expected_output"],
        agent=news_reporter,
        context=[find_article_urls]
    )

    rewrite_article_desc = tasks_config["rewrite_article"]["description"].replace(
        "{style_examples}", style_examples_text
    )
    rewrite_article = Task(
        description=rewrite_article_desc,
        expected_output=tasks_config["rewrite_article"]["expected_output"],
        agent=news_copywriter,
        context=[scrape_article_content]
    )

    generate_image_prompt = Task(
        description=tasks_config["generate_image_prompt"]["description"],
        expected_output=tasks_config["generate_image_prompt"]["expected_output"],
        agent=designer_agent,
        context=[rewrite_article]
        # REMOVED output_json=True from here
    )

    return [find_article_urls, scrape_article_content, rewrite_article, generate_image_prompt]


def build_crew(field, website, style_examples_text):
    news_reporter, news_copywriter, designer_agent = make_agents()
    tasks = make_tasks(
        news_reporter, news_copywriter, designer_agent, field, website, style_examples_text
    )

    crew = Crew(
        agents=[news_reporter, news_copywriter, designer_agent],
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )
    return crew