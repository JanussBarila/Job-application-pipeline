"""Copy the existing vacancy CSV into this separate application project.

Place this script in Desktop/Python Job Applications, alongside the existing
Desktop/Python Biznesa datu analze project. Only the CSV is read from that project.
Uses Python's standard library; no packages or network access are needed.
"""

import csv
import io
import os
import sys
import tempfile
from pathlib import Path


def main():
    project = Path(__file__).resolve().parent
    source = project.parent / "Python Biznesa datu analze" / "vacancies_live.csv"
    destination = project / "data" / "vacancies_live.csv"

    try:
        # Read once, so the copied bytes and the displayed count agree.
        content = source.read_bytes()
        text = content.decode("utf-8-sig")
        first_line = text.splitlines()[0] if text.splitlines() else ""
        if not first_line.strip():
            raise ValueError("CSV fails ir tukšs vai tam nav kolonnu nosaukumu.")
        dialect = csv.Sniffer().sniff(first_line, delimiters=";,\t")
        reader = csv.reader(io.StringIO(text, newline=""), dialect, strict=True)
        columns = next(reader)
        if any(not name.strip() for name in columns):
            raise ValueError("CSV failā ir kolonna bez nosaukuma.")
        count = 0
        for row in reader:
            if not row or not any(value.strip() for value in row):
                continue
            if len(row) != len(columns):
                raise ValueError(
                    f"CSV rindā pie {reader.line_num}. līnijas nesakrīt kolonnu skaits."
                )
            count += 1
    except FileNotFoundError:
        print(f"Nav atrasts fails:\n{source}")
        print("Pārbaudi, vai abas projekta mapes ir blakus uz darbvirsmas.")
        print("Šim skriptam jāatrodas mapē Python Job Applications.")
        return 1
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"Neizdevās nolasīt vakanču failu: {error}")
        return 1

    temporary = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Replace only this project's copy, after the new copy is fully written.
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=destination.parent, prefix=".vacancies_", delete=False
        ) as output:
            temporary = Path(output.name)
            output.write(content)
        os.replace(temporary, destination)
    except OSError as error:
        print(f"Neizdevās saglabāt kopiju: {error}")
        print("Ja kopija ir atvērta Excel, aizver to un palaid skriptu vēlreiz.")
        return 1
    finally:
        if temporary is not None and temporary.exists():
            try:
                temporary.unlink()
            except OSError:
                pass

    print("GATAVS — vakanču fails ir nokopēts.")
    print(f"Avots: {source}")
    print(f"Kopija: {destination}")
    print(f"Vakanču skaits: {count}")
    print("Kolonnas: " + ", ".join(columns))
    print("Katrs skripta starts paņem faila tajā brīdī saglabāto versiju.")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
