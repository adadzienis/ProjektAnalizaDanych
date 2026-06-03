"""
Konwersja notebooka Jupyter do pliku HTML przy użyciu nbconvert.

Domyślne działanie:
- wejście: projekt.ipynb
- wyjście: output/projekt.html
- notebook nie jest wykonywany ponownie, konwertowane są zapisane komórki i wyniki.

Przykłady użycia:
    python convert_to_html.py
    python convert_to_html.py --input projekt.ipynb --output-dir output
    python convert_to_html.py --execute
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Konwertuje notebook Jupyter do pliku HTML przy użyciu nbconvert."
    )

    parser.add_argument(
        "--input",
        default="projekt.ipynb",
        help="Ścieżka do notebooka wejściowego. Domyślnie: projekt.ipynb.",
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Katalog, w którym zostanie zapisany plik HTML. Domyślnie: output.",
    )

    parser.add_argument(
        "--output-name",
        default=None,
        help=(
            "Nazwa pliku wynikowego bez rozszerzenia .html. "
            "Domyślnie używana jest nazwa notebooka."
        ),
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Wykonuje notebook przed konwersją. "
            "Domyślnie notebook nie jest wykonywany ponownie."
        ),
    )

    parser.add_argument(
        "--no-embed-images",
        action="store_true",
        help=(
            "Nie osadza obrazów w pliku HTML. "
            "Domyślnie obrazy są osadzane w HTML."
        ),
    )

    return parser.parse_args()


def build_nbconvert_command(
    notebook_path: Path,
    output_dir: Path,
    output_name: str,
    execute: bool,
    embed_images: bool,
) -> list[str]:
    command = [
        "jupyter",
        "nbconvert",
        "--to",
        "html",
    ]

    if embed_images:
        command.append("--embed-images")

    if execute:
        command.append("--execute")

    command.extend(
        [
            str(notebook_path),
            "--output",
            output_name,
            "--output-dir",
            str(output_dir),
        ]
    )

    return command


def convert_notebook_to_html(
    notebook_path: Path,
    output_dir: Path,
    output_name: str | None = None,
    execute: bool = False,
    embed_images: bool = True,
) -> Path:
    if not notebook_path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku notebooka: {notebook_path}")

    if notebook_path.suffix.lower() != ".ipynb":
        raise ValueError("Plik wejściowy musi mieć rozszerzenie .ipynb.")

    output_dir.mkdir(parents=True, exist_ok=True)

    html_name = output_name or notebook_path.stem
    command = build_nbconvert_command(
        notebook_path=notebook_path,
        output_dir=output_dir,
        output_name=html_name,
        execute=execute,
        embed_images=embed_images,
    )

    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as error:
        raise RuntimeError(
            "Nie znaleziono polecenia 'jupyter'. "
            "Sprawdź, czy w środowisku zainstalowano jupyter i nbconvert."
        ) from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            "Konwersja notebooka do HTML nie powiodła się. "
            "Sprawdź komunikaty błędów powyżej."
        ) from error

    return output_dir / f"{html_name}.html"


def main() -> int:
    args = parse_arguments()

    notebook_path = Path(args.input)
    output_dir = Path(args.output_dir)
    embed_images = not args.no_embed_images

    try:
        html_path = convert_notebook_to_html(
            notebook_path=notebook_path,
            output_dir=output_dir,
            output_name=args.output_name,
            execute=args.execute,
            embed_images=embed_images,
        )
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        print(f"Błąd: {error}", file=sys.stderr)
        return 1

    print(f"Utworzono plik HTML: {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
