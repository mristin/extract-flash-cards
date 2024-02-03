"""Convert a CSV file to an anki deck."""

import argparse
import csv
import pathlib
import shutil
import sys
import uuid

import anki.collection
import anki.exporting
import anki.notes
import gtts


def main(prog: str) -> int:
    """
    Execute the main routine.

    :param prog: name of the program to be displayed in the help
    :return: exit code
    """
    parser = argparse.ArgumentParser(prog=prog, description=__doc__)
    parser.add_argument(
        "--csv_path",
        help=("Path to the CSV file with the generated cards."),
        required=True,
    )
    parser.add_argument(
        "--anki_path", help="Path to the file with the Anki deck", required=True
    )
    parser.add_argument("--deck_name", help="Name of the Anki deck", required=True)
    parser.add_argument(
        "--synthesize_audio",
        help=(
            "Specify the language to synthesize source with Google Text-to-speech. "
            "If not specified, the audio is not synthesized"
        ),
    )

    args = parser.parse_args()

    csv_path = pathlib.Path(args.csv_path)
    anki_path = pathlib.Path(args.anki_path)
    deck_name = str(args.deck_name)
    synthesize_audio = (
        str(args.synthesize_audio) if args.synthesize_audio is not None else None
    )

    if not csv_path.exists():
        print(f"--csv_path does not exist: {csv_path}", file=sys.stderr)
        return 1

    if not csv_path.is_file():
        print(f"--csv_path is not a file: {csv_path}", file=sys.stderr)
        return 1

    with csv_path.open("rt", encoding="utf-8") as fid:
        reader = csv.reader(fid)
        for i, row in enumerate(reader):
            if i == 0:
                continue

            if len(row) != 4:
                print(
                    f"Ignoring an invalid row {i+1} in "
                    f"--csv_path {csv_path}: {row}",
                    file=sys.stderr,
                )
                continue

    anki_path.parent.mkdir(exist_ok=True, parents=True)

    uid4 = uuid.uuid4()
    tmp_dir = anki_path.parent / f"{anki_path.name}.{uid4}"
    tmp_dir.mkdir()

    try:
        collection = anki.collection.Collection(str(tmp_dir / "collection.anki2"))

        collection.decks.add_normal_deck_with_name(deck_name)
        deck_id = collection.decks.id_for_name(deck_name)
        assert deck_id is not None

        model = collection.models.new(f"{deck_name} model")
        model["did"] = deck_id

        collection.models.add_field(model, collection.models.new_field("source"))

        if synthesize_audio is not None:
            collection.models.add_field(model, collection.models.new_field("tts"))

        collection.models.add_field(model, collection.models.new_field("target"))
        collection.models.add_field(
            model, collection.models.new_field("example_source")
        )
        collection.models.add_field(
            model, collection.models.new_field("example_target")
        )

        tmpl = collection.models.new_template("main-template")
        if synthesize_audio is not None:
            tmpl["qfmt"] = "{{source}}\n\n{{tts}}"
        else:
            tmpl["qfmt"] = "{{source}}"

        tmpl["afmt"] = (
            "{{FrontSide}}\n\n"
            "<hr>\n\n"
            "<div>{{target}}</div>"
            "<div>{{example_source}}</div>"
            "<div>{{example_target}}</div>"
        )
        collection.models.addTemplate(model, tmpl)

        collection.models.update(model)
        collection.models.set_current(model)
        collection.models.save(model)

        with csv_path.open("rt", encoding="utf-8") as fid:
            reader = csv.reader(fid)
            for i, row in enumerate(reader):
                if i == 0:
                    continue

                if len(row) != 4:
                    continue

                source, target, example_source, example_target = row

                note = anki.notes.Note(collection, model)
                note["source"] = source
                note["target"] = target
                note["example_source"] = example_source
                note["example_target"] = example_target
                note.guid = f"card{i}"

                if synthesize_audio is not None:
                    tts = gtts.gTTS(text=source, lang=synthesize_audio)

                    mp3_pth = tmp_dir / f"{uid4}-{i}.mp3"
                    tts.save(str(mp3_pth))
                    collection.media.add_file(str(mp3_pth))
                    note["tts"] = f"[sound:{mp3_pth.name}]"

                collection.addNote(note)

        export = anki.exporting.AnkiPackageExporter(collection)
        export.exportInto(str(anki_path))
    finally:
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)

    return 0


def entry_point() -> int:
    """Provide an entry point for a console script."""
    return main(prog="csv-to-anki")


if __name__ == "__main__":
    sys.exit(main(prog="csv-to-anki"))
