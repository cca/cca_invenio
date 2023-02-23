"""Additional views."""

from flask import Blueprint

from .vocablist.vocablist import VocabListView

#
# Registration
#
def create_blueprint(app):
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "vault",
        __name__,
        template_folder="./templates",
    )

    blueprint.add_url_rule(
        "/vocablist",
        view_func=VocabListView.as_view("vocablist"),
    )

    # Add URL rules
    return blueprint
