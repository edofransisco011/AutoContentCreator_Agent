import json
import random
import os
import argparse
from auto_content_creator.crew import build_crew

def get_style_examples(style_json_path, n=2):
    with open(style_json_path, "r", encoding="utf-8") as f:
        style_examples = json.load(f)
    if len(style_examples) < n:
        n = len(style_examples)
    selected = random.sample(style_examples, n)
    examples_text = "\n\n".join(
        [f"Title: {ex['title']}\nCaption: {ex['caption']}" for ex in selected]
    )
    return examples_text

def save_output(result_json_string, website, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        final_data = json.loads(result_json_string)
    except (json.JSONDecodeError, TypeError):
        print(f"Could not parse JSON from result for {website}. Raw result: {result_json_string}")
        final_data = {}

    hook_title = final_data.get("hook_title", "No Title")
    caption = final_data.get("caption", "No Caption")
    image_prompt = final_data.get("image_prompt", "No Image Prompt")

    safe_website_name = website.replace('https://', '').replace('www.', '').replace('/', '_').split('.')[0]
    output_file = os.path.join(output_dir, f"{safe_website_name}_news_post.md")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# {hook_title}\n\n")
        f.write(f"{caption}\n\n")
        f.write(f"**Image Prompt:**\n{image_prompt}\n")
    
    print(f"✅ Output for {website} saved to {output_file}")


def run():
    parser = argparse.ArgumentParser(description="Run the Auto Content Creator crew.")
    parser.add_argument('--field', type=str, default="artificial intelligence", help='The field or topic for news gathering.')
    parser.add_argument('--websites', nargs='+', default=["https://www.artificialintelligence-news.com/", "https://techcrunch.com/category/artificial-intelligence/"], help='A list of websites to search for news.')
    args = parser.parse_args()

    here = os.path.dirname(__file__)
    style_examples_path = os.path.join(here, "data", "style_bank.json")
    examples_text = get_style_examples(style_examples_path, n=2)
    output_dir = os.path.join(here, "..", "..", "output")

    for website in args.websites:
        print(f"🚀 Starting crew for website: {website}")
        
        crew = build_crew(field=args.field, website=website, style_examples_text=examples_text)
        
        print("Running the Crew...")
        result = crew.kickoff()

        print("\n==== RAW CrewAI output ====\n")
        print(result)
        print("\n==========================\n")

        save_output(result, website, output_dir)

if __name__ == "__main__":
    run()