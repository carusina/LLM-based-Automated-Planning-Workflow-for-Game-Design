"""
Main entry point for the Game Design Document (GDD) generation workflow.

This script provides a command-line interface (CLI) to run the various modules
of the project, such as generating a GDD, extracting metadata, and creating
a storyline.
"""
import json
import os
from datetime import datetime

import typer
from dotenv import load_dotenv

from models.game_design_generator import GameDesignGenerator
from models.knowledge_graph_service import KnowledgeGraphService
from models.llm_service import LLMService
from models.storyline_generator import StorylineGenerator

# Load environment variables from .env file
load_dotenv()

app = typer.Typer()


def get_llm_service() -> LLMService:
    """Initializes and returns the LLMService using the factory pattern."""
    # The LLMService constructor now intelligently selects the provider
    # based on environment variables like DEFAULT_LLM_PROVIDER and the corresponding API key.
    # Ensure .env file has DEFAULT_LLM_PROVIDER="gemini" and GEMINI_API_KEY="your_key".
    try:
        return LLMService()
    except (ValueError, ImportError) as e:
        print(f"Error initializing LLM Service: {e}")
        raise typer.Exit(code=1)


@app.command()
def gdd(idea: str, output_dir: str = "output"):
    """
    Generates a Game Design Document (GDD) from a user's idea.
    """
    print(f"Received idea: {idea}")
    print("Initializing services...")
    llm_service = get_llm_service()
    gdd_generator = GameDesignGenerator(llm_service)

    print("Generating GDD... This may take a while.")
    markdown_content = gdd_generator.generate(idea)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save the GDD markdown file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    gdd_filename = os.path.join(output_dir, f"GDD_{timestamp}.md")
    with open(gdd_filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Successfully generated GDD: {gdd_filename}")

    # Extract metadata and save as JSON
    print("Extracting metadata from GDD...")
    kg_service = KnowledgeGraphService(llm_service)
    metadata = kg_service.extract_metadata_from_gdd(markdown_content)

    meta_filename = os.path.join(output_dir, f"GDD_{timestamp}_meta.json")
    with open(meta_filename, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Successfully extracted and saved metadata: {meta_filename}")


@app.command()
def storyline(
    gdd_file: str = typer.Argument(..., help="Path to the GDD.md file."),
    num_chapters: int = typer.Option(5, "--chapters", "-c", help="Number of chapters to generate.")
):
    """
    Generates a cinematic storyline from a GDD file.
    """
    print(f"Loading GDD file: {gdd_file}")
    if not os.path.exists(gdd_file):
        print(f"Error: File not found at {gdd_file}")
        raise typer.Exit(code=1)

    with open(gdd_file, "r", encoding="utf-8") as f:
        gdd_content = f.read()

    print("Initializing services...")
    llm_service = get_llm_service()
    kg_service = KnowledgeGraphService(llm_service)
    storyline_generator = StorylineGenerator(llm_service)

    # 1. Extract metadata from the GDD content
    print("Extracting metadata from GDD...")
    metadata = kg_service.extract_metadata_from_gdd(gdd_content)
    if not metadata:
        print("Error: Could not extract metadata from the GDD. Cannot generate storyline.")
        raise typer.Exit(code=1)
    
    print("Successfully extracted metadata.")

    # 2. Generate the storyline using the new generator
    print(f"Generating a {num_chapters}-chapter storyline... This may take some time.")
    scenes = storyline_generator.generate(metadata, num_chapters)

    if not scenes:
        print("Error: Storyline generation failed. No scenes were created.")
        raise typer.Exit(code=1)

    # 3. Save the structured storyline to a JSON file
    output_dir = os.path.dirname(gdd_file)
    base_filename = os.path.splitext(os.path.basename(gdd_file))[0]
    storyline_filename = os.path.join(output_dir, f"{base_filename}_storyline.json")

    with open(storyline_filename, "w", encoding="utf-8") as f:
        json.dump(scenes, f, ensure_ascii=False, indent=2)

    print("\n" + "-" * 50)
    print(f"Successfully generated cinematic storyline!")
    print(f"Output saved to: {storyline_filename}")
    print("-" * 50)


if __name__ == "__main__":
    app()