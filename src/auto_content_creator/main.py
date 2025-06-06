import json
import random
import os
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

def parse_final_output(result):
    # If it's a string, try to parse as JSON
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except Exception:
            pass

    # If result is a dict and has only "Final Answer" or similar
    if isinstance(result, dict):
        # Check for a "Final Answer" key
        if "Final Answer" in result:
            result = result["Final Answer"]
        else:
            # Might be a dict of UUIDs, so flatten to list of values
            all_values = []
            for v in result.values():
                if isinstance(v, list):
                    all_values.extend(v)
                else:
                    all_values.append(v)
            result = all_values

    # If it's a list, return as-is
    if isinstance(result, list):
        return result
    # If it's a single dict, wrap in list
    elif isinstance(result, dict):
        return [result]
    # If it's just a string or other type, wrap in list for downstream code
    else:
        return [result]

def save_outputs(parsed_results, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for idx, item in enumerate(parsed_results):
        # Use site name if present, or index as fallback
        site = item.get("website", f"site_{idx+1}") if isinstance(item, dict) else f"site_{idx+1}"
        output_file = os.path.join(output_dir, f"{str(site).replace('.', '_')}_news_post.md")
        with open(output_file, "w", encoding="utf-8") as f:
            if isinstance(item, dict):
                if "hook_title" in item:
                    f.write(f"# {item['hook_title']}\n\n")
                if "caption" in item:
                    f.write(item['caption'] + "\n\n")
                if "image_prompt" in item:
                    f.write(f"**Image Prompt:**\n{item['image_prompt']}\n")
                # Add more fields as needed
            else:
                # Just write the string
                f.write(str(item))
        print(f"Output saved to {output_file}")

def run():
    here = os.path.dirname(__file__)
    style_examples_path = os.path.join(here, "data", "style_bank.json")
    examples_text = get_style_examples(style_examples_path, n=2)

    field = "artificial intelligence"
    websites = [
        "https://www.artificialintelligence-news.com/",
        "https://techcrunch.com/category/artificial-intelligence/"
    ]

    crew = build_crew(field=field, websites=websites, style_examples_text=examples_text)
    print("Running the Crew...")
    result = crew.kickoff(inputs={})

    print("\n==== RAW CrewAI output ====\n")
    print(result)
    print("\n==========================\n")

    # Parse the output flexibly
    parsed_results = parse_final_output(result)

    print("Parsed output for Markdown export:")
    print(parsed_results)

    output_dir = os.path.join(here, "output")
    save_outputs(parsed_results, output_dir)

if __name__ == "__main__":
    run()
