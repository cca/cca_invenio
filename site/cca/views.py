"""Additional views."""

from flask import Blueprint

from .vocablist.vocablist import VocabListView


# Registration
def create_blueprint(app):
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "cca",
        __name__,
        template_folder="./templates",
    )

    # ! This doesn't seem to work anymore?
    blueprint.add_url_rule(
        "/vocablist",
        view_func=VocabListView.as_view("vocablist"),
    )

    # Add URL rules
    return blueprint
