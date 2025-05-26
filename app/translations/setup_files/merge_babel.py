"""
Description: Allows to work with translations in one json file
"""

from app import create_app
from app.translations.setup_files.utils import export_strings
from app.translations.setup_files.utils import import_strings

app = create_app()

with app.app_context():
    import_strings(target="tt")
    print("Setup executed succesfully!")
