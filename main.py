"""
Main entry point for the Game Design Document (GDD) generation workflow.
"""
import json
import os
from datetime import datetime

import typer
from dotenv import load_dotenv
from google import genai

from models.game_design_generator import GameDesignGenerator
from models.knowledge_graph_service import KnowledgeGraphService
from models.llm_service import LLMService
from models.storyline_generator import StorylineGenerator
from models.graph_rag import GraphRAG
from models.local_image_generator import GeminiImageGenerator
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

app = typer.Typer(
    help="Game Design Automation CLI: A tool for generating game design documents, storylines, and concept art using AI.",
    add_completion=False,
    rich_markup_mode="markdown"
)


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

    # Configure API and create a single client instance
    try:
        # The new google-genai library takes the API key directly in the Client constructor.
        api_key = os.environ["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
    except KeyError:
        typer.secho("Error: GEMINI_API_KEY not found in .env file.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Inject the client into the services
    llm_service = LLMService(client=client)
    gdd_generator = GameDesignGenerator(llm_service)

    typer.echo("Prompt parameters are ready for GDD generation.")

    typer.echo("\n[Step 2/3] Generating GDD... This may take a while.")
    markdown_content = gdd_generator.generate_gdd(
        idea=idea,
        genre=genre,
        target=target,
        concept=concept
    )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create a timestamped directory for all outputs
    output_dir = Path(output_dir) / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    base_filename = f"GDD_{art_style.replace(' ', '_')}_{timestamp}"
    gdd_filename = output_dir / f"{base_filename}.md"
    
    with open(gdd_filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    typer.secho(f"Successfully generated GDD: {gdd_filename}", fg=typer.colors.GREEN)

    typer.echo("\n[Step 3/3] Extracting metadata from GDD...")
    kg_service = KnowledgeGraphService(llm_service)
    metadata = kg_service.extract_metadata_from_gdd(markdown_content)
    meta_filename = output_dir / f"{base_filename}_meta.json"
    
    with open(meta_filename, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    typer.secho(f"Successfully extracted and saved metadata: {meta_filename}", fg=typer.colors.GREEN)

    typer.echo("\n[Step 4/8] Creating knowledge graph from metadata...")
    try:
        kg_service.create_graph_from_metadata(metadata)
        typer.secho("Successfully created knowledge graph.", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Error creating knowledge graph: {e}", fg=typer.colors.RED)


    if not generate_images:
        typer.secho("\n--- GDD Generation Finished ---", fg=typer.colors.CYAN, bold=True)
        return

    # --- Part 2: Image Generation Pipeline ---
    typer.secho("\n--- Starting Full Image Generation Pipeline ---", fg=typer.colors.MAGENTA, bold=True)
    
    typer.echo(f"\n[Step 5/8] Generating a {num_chapters}-chapter storyline...")
    storyline_generator = StorylineGenerator(llm_service)
    scenes = storyline_generator.generate(metadata, num_chapters)
    storyline_filename = output_dir / f"{base_filename}_storyline.json"
    with open(storyline_filename, "w", encoding="utf-8") as f:
        json.dump(scenes, f, ensure_ascii=False, indent=2)
    typer.secho(f"Successfully generated and saved storyline: {storyline_filename}", fg=typer.colors.GREEN)

    typer.echo("\n[Step 6/8] Initializing Art Director and establishing visual identity...")
    image_generator = GeminiImageGenerator(client=client, llm_service=llm_service)
    image_generator.establish_visual_identity(gdd_text=markdown_content, metadata=metadata)
    typer.echo("Visual identity has been established.")

    image_output_dir = output_dir
    if not skip_concepts:
        typer.echo("\n[Step 7/8] Generating individual concept arts...")
        concept_art_dir = image_output_dir / "concepts"
        concept_images = image_generator.generate_images(metadata=metadata, output_dir=str(concept_art_dir))
        if concept_images:
            typer.secho(f"Successfully generated {len(concept_images)} concept art images in {concept_art_dir}", fg=typer.colors.GREEN)
    else:
        typer.echo("\n[Step 7/8] Skipping individual concept art generation.")

    typer.echo("\n[Step 8/8] Generating cinematic scene images...")
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
def update_gdd(
    gdd_path: str = typer.Option(..., "--gdd-path", help="Path to the original GDD markdown file."),
    update_request: str = typer.Option(..., "--update-request", help="A prompt describing the changes you want to make."),
    output_path: str = typer.Option(..., "--output-path", help="Path to save the updated GDD file."),
):
    """
    Updates an existing Game Design Document using GraphRAG to ensure consistency.
    """
    typer.secho("--- GDD Update Pipeline (with GraphRAG) ---", fg=typer.colors.CYAN, bold=True)

    # --- Part 1: Initialization ---
    typer.echo("\n[Step 1/4] Initializing services...")
    try:
        api_key = os.environ["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
    except KeyError:
        typer.secho("Error: GEMINI_API_KEY not found in .env file.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    llm_service = LLMService(client=client)
    kg_service = KnowledgeGraphService(llm_service)
    graph_rag = GraphRAG(kg_service, llm_service)

    # --- Part 2: Read Original GDD ---
    typer.echo(f"\n[Step 2/4] Reading original GDD from: {gdd_path}")
    try:
        with open(gdd_path, "r", encoding="utf-8") as f:
            original_content = f.read()
    except FileNotFoundError:
        typer.secho(f"Error: GDD file not found at {gdd_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # --- Part 3: Update GDD with GraphRAG ---
    typer.echo("\n[Step 3/4] Updating GDD using GraphRAG... This may take a while.")
    updated_content = graph_rag.update_from_document(
        original_content=original_content,
        update_request=update_request,
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    typer.secho(f"Successfully generated updated GDD: {output_path}", fg=typer.colors.GREEN)

    # --- Part 4: Update Knowledge Graph ---
    typer.echo("\n[Step 4/4] Updating knowledge graph from the new GDD...")
    try:
        graph_rag.update_graph_from_document(updated_content)
        typer.secho("Successfully updated knowledge graph.", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Error updating knowledge graph: {e}", fg=typer.colors.RED)

    typer.secho("\n--- GDD Update Finished! ---", fg=typer.colors.CYAN, bold=True)


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

@app.command()
def resume_video(
    timestamp: str = typer.Option(..., "--timestamp", "-t", help="Timestamp of the project to resume video generation."),
    output_dir: str = typer.Option("output", "-o", "--output-dir", help="Directory where the project is saved."),
):
    """
    Resumes video generation for a project that was previously interrupted.
    """
    typer.secho(f"--- Resuming Video Generation for project {timestamp} ---", fg=typer.colors.CYAN, bold=True)

    project_dir = Path(output_dir) / timestamp
    if not project_dir.exists():
        typer.secho(f"Error: Project directory not found at {project_dir}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Find the GDD, metadata, and storyline files
    try:
        gdd_file = list(project_dir.glob("GDD_*.md"))[0]
        meta_file = list(project_dir.glob("*_meta.json"))[0]
        storyline_file = list(project_dir.glob("*_storyline.json"))[0]
    except IndexError:
        typer.secho(f"Error: Could not find all required files (GDD, meta, storyline) in {project_dir}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # --- Initialize services ---
    typer.echo("\n[Step 1/3] Initializing services...")
    try:
        api_key = os.environ["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
    except KeyError:
        typer.secho("Error: GEMINI_API_KEY not found in .env file.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    llm_service = LLMService(client=client)
    image_generator = GeminiImageGenerator(client=client, llm_service=llm_service)

    # --- Load existing data ---
    typer.echo("\n[Step 2/3] Loading existing project data...")
    with open(gdd_file, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    with open(meta_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    with open(storyline_file, "r", encoding="utf-8") as f:
        scenes = json.load(f)

    image_generator.establish_visual_identity(gdd_text=markdown_content, metadata=metadata)
    typer.echo("Visual identity has been re-established.")

    # --- Resume cinematic scene generation ---
    typer.echo("\n[Step 3/3] Resuming cinematic scene generation...")
    try:
        from models.cinematic_generator import CinematicGenerator
        cinematic_gen = CinematicGenerator(llm_service, image_generator)
        scene_image_dir = project_dir / "scenes"
        scene_image_files = cinematic_gen.resume_generation(storyline_data=scenes, output_dir=str(scene_image_dir))
        if scene_image_files:
            typer.secho(f"\nSuccessfully generated {len(scene_image_files)} new cinematic scene images.", fg=typer.colors.GREEN)
    except ImportError as e:
        typer.secho(f"\nCould not import CinematicGenerator. Skipping. Error: {e}", fg=typer.colors.YELLOW)
    except Exception as e:
        typer.secho(f"\nAn error occurred during cinematic scene generation: {e}", fg=typer.colors.RED)

    typer.secho("\n--- Video Generation Finished! ---", fg=typer.colors.CYAN, bold=True)


if __name__ == "__main__":
    app()