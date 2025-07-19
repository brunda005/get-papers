from get_papers.fetch import fetch_papers
from get_papers.filter import filter_non_academic_authors
from get_papers.formatter import save_to_csv  # You'll create this next
import typer

app = typer.Typer()

@app.command()
def main(
    query: str,
    file: str = typer.Option(None, "--file", "-f", help="Output CSV filename"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging")
):
    typer.echo(f"Running query: {query}")
    papers = fetch_papers(query, debug=debug)
    filtered = filter_non_academic_authors(papers)
    
    if file:
        save_to_csv(filtered, file)
        typer.echo(f"Saved to {file}")
    else:
        for paper in filtered:
            typer.echo(paper)

if __name__ == "__main__":
    app()