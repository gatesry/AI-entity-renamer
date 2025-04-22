"""Constants for the Entity Renamer integration."""
import json
import os

DOMAIN = "entity_renamer"

# Get version from manifest.json
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "manifest.json")
with open(MANIFEST_PATH) as manifest_file:
    manifest = json.load(manifest_file)
    VERSION = manifest["version"]
