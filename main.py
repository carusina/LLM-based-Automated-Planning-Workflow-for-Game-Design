"""
Main entry point for the Game Design Document (GDD) generation workflow.
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
from models.local_image_generator import GeminiImageGenerator
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

app = typer.Typer(
    help="Game Design Automation CLI: A tool for generating game design documents, storylines, and concept art using AI.",
    add_completion=False,
    rich_markup_mode="markdown"
)

def get_llm_service() -> LLMService:
    """Initializes and returns the LLMService, handling potential errors."""
    try:
        return LLMService()
    except (ValueError, ImportError) as e:
        typer.secho(f"Error initializing LLM Service: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def gdd(
    idea: str = typer.Option(..., "--idea", help="Core one-sentence idea of the game."),
    genre: str = typer.Option(..., "--genre", help="Game's genre (e.g., 'Epic Fantasy Action RPG')."),
    target: str = typer.Option(..., "--target", help="Target audience for the game."),
    concept: str = typer.Option(..., "--concept", help="Core gameplay concepts and systems."),
    art_style: str = typer.Option("Default", "--art-style", help="Art style for concept art (e.g., 'Ghibli-inspired', 'Cyberpunk')."),
    output_dir: str = typer.Option("output", "-o", "--output-dir", help="Directory to save all generated files."),
    generate_images: bool = typer.Option(False, "--generate-images", help="Flag to generate all images after GDD creation."),
    num_chapters: int = typer.Option(5, "--chapters", "-c", help="Number of storyline chapters for image generation."),
    skip_concepts: bool = typer.Option(False, "--skip-concepts", help="Skip individual concept art generation.")
):
    """
    Generates a Game Design Document (GDD) and optionally creates a full asset pipeline including concept art.
    """
    typer.secho("--- GDD Generation Pipeline ---", fg=typer.colors.CYAN, bold=True)

    # --- Part 1: GDD Generation ---
    typer.echo("\n[Step 1/3] Initializing services...")
    llm_service = get_llm_service()
    gdd_generator = GameDesignGenerator(llm_service)

    typer.echo("Prompt parameters are ready for GDD generation.")

    typer.echo("\n[Step 2/3] Generating GDD... This may take a while.")
    markdown_content = gdd_generator.generate_gdd(
        idea=idea,
        genre=genre,
        target=target,
        concept=concept
    )
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"GDD_{art_style.replace(' ', '_')}_{timestamp}"
    gdd_filename = Path(output_dir) / f"{base_filename}.md"
    
    with open(gdd_filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    typer.secho(f"Successfully generated GDD: {gdd_filename}", fg=typer.colors.GREEN)

    typer.echo("\n[Step 3/3] Extracting metadata from GDD...")
    kg_service = KnowledgeGraphService(llm_service)
    metadata = kg_service.extract_metadata_from_gdd(markdown_content)
    meta_filename = Path(output_dir) / f"{base_filename}_meta.json"
    
    with open(meta_filename, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    typer.secho(f"Successfully extracted and saved metadata: {meta_filename}", fg=typer.colors.GREEN)

    if not generate_images:
        typer.secho("\n--- GDD Generation Finished ---", fg=typer.colors.CYAN, bold=True)
        return

    # --- Part 2: Image Generation Pipeline ---
    typer.secho("\n--- Starting Full Image Generation Pipeline ---", fg=typer.colors.MAGENTA, bold=True)
    
    typer.echo(f"\n[Step 4/7] Generating a {num_chapters}-chapter storyline...")
    storyline_generator = StorylineGenerator(llm_service)
    scenes = storyline_generator.generate(metadata, num_chapters)
    storyline_filename = Path(output_dir) / f"{base_filename}_storyline.json"
    with open(storyline_filename, "w", encoding="utf-8") as f:
        json.dump(scenes, f, ensure_ascii=False, indent=2)
    typer.secho(f"Successfully generated and saved storyline: {storyline_filename}", fg=typer.colors.GREEN)

    typer.echo("\n[Step 5/7] Initializing Art Director and establishing visual identity...")
    image_generator = GeminiImageGenerator(llm_service)
    image_generator.establish_visual_identity(gdd_text=markdown_content, metadata=metadata)
    typer.echo("Visual identity has been established.")

    image_output_dir = Path(output_dir) / timestamp
    if not skip_concepts:
        typer.echo("\n[Step 6/7] Generating individual concept arts...")
        concept_art_dir = image_output_dir / "concepts"
        concept_images = image_generator.generate_images(metadata=metadata, output_dir=str(concept_art_dir))
        if concept_images:
            typer.secho(f"Successfully generated {len(concept_images)} concept art images in {concept_art_dir}", fg=typer.colors.GREEN)
    else:
        typer.echo("\n[Step 6/7] Skipping individual concept art generation.")

    typer.echo("\n[Step 7/7] Generating cinematic scene images...")
    try:
        from models.cinematic_generator import CinematicGenerator
        cinematic_gen = CinematicGenerator(llm_service, image_generator)
        scene_image_dir = image_output_dir / "scenes"
        scene_image_files = cinematic_gen.generate_scenes(storyline_data=scenes, output_dir=str(scene_image_dir))
        if scene_image_files:
            typer.secho(f"\nSuccessfully generated {len(scene_image_files)} cinematic scene images.", fg=typer.colors.GREEN)
    except ImportError as e:
        typer.secho(f"\nCould not import CinematicGenerator. Skipping. Error: {e}", fg=typer.colors.YELLOW)
    except Exception as e:
        typer.secho(f"\nAn error occurred during cinematic scene generation: {e}", fg=typer.colors.RED)
    
    typer.secho("\n--- Full Project Generation Pipeline Finished! ---", fg=typer.colors.CYAN, bold=True)

@app.command()
def storyline():
    """
    (Placeholder) Generates or modifies a storyline based on an existing GDD.
    """
    typer.echo("Storyline generation command is not yet implemented.")

@app.command()
def web():
    """
    (Placeholder) Launches the web interface for interacting with the project.
    """
    typer.echo("Web interface command is not yet implemented.")

if __name__ == "__main__":
    app()