import json
import os
from io import StringIO
from babel.messages.pofile import read_po, write_po
from babel.messages.catalog import Catalog
from ...extensions import babel
from pathlib import Path


def export_strings(source="en", target=None):
    """Export translation strings to JSON format."""
    # Get the absolute path to translations directory
    translations_dir = Path(__file__).parent.parent

    source_str = StringIO(
        open(
            translations_dir / source / "LC_MESSAGES/messages.po",
            "r",
            encoding="utf-8",
        ).read()
    )
    source_catalog = read_po(source_str)
    for_tron = {
        message.id: {source: message.string} for message in source_catalog if message.id
    }

    if not target:
        for locale in babel.list_translations():
            locale = locale.language
            if locale != source:
                target_str = StringIO(
                    open(
                        translations_dir / locale / "LC_MESSAGES/messages.po",
                        "r",
                        encoding="utf-8",
                    ).read()
                )
                target_catalog = read_po(target_str)

                for message in target_catalog:
                    if message.id and message.id in for_tron.keys():
                        for_tron[message.id][locale] = message.string
    else:
        target_str = StringIO(
            open(
                translations_dir / target / "LC_MESSAGES/messages.po",
                "r",
                encoding="utf-8",
            ).read()
        )
        target_catalog = read_po(target_str)

        for message in target_catalog:
            if message.id and message.id in for_tron.keys():
                for_tron[message.id][target] = message.string

    # Save JSON in translations directory
    output_path = translations_dir / "setup_files" / "strings.json"
    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(for_tron, outfile, ensure_ascii=False, indent=2)


def import_strings(filename=None, source="en", target=None):
    """Import translation strings from JSON format."""
    translations_dir = Path(__file__).parent.parent

    if filename:
        from_tron = json.loads(open(filename, "r", encoding="utf-8").read())
    else:
        from_tron = json.loads(
            open(
                translations_dir / "setup_files" / "strings.json", "r", encoding="utf-8"
            ).read()
        )

    template_path = translations_dir / "setup_files" / "messages.pot"
    template_str = StringIO(open(template_path, "r", encoding="utf-8").read())
    template = read_po(template_str)

    if not target:
        for locale in babel.list_translations():
            locale = locale.language
            new_catalog = Catalog()
            for id in from_tron:
                if locale in from_tron[id].keys():
                    new_catalog.add(id, from_tron[id][locale])
            new_catalog.update(template)
            write_po(
                open(
                    translations_dir / locale / "LC_MESSAGES/messages.po",
                    "wb",
                ),
                new_catalog,
            )
    else:
        new_catalog = Catalog()
        for id in from_tron:
            if target in from_tron[id].keys():
                new_catalog.add(id, from_tron[id][target])
        new_catalog.update(template)
        write_po(
            open(
                translations_dir / target / "LC_MESSAGES/messages.po", "wb"
            ),
            new_catalog,
        )


if __name__ == "__main__":
    export_strings()
