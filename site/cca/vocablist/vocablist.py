from flask import render_template
from flask.views import MethodView
from invenio_vocabularies.records.models import VocabularyScheme, VocabularyType


class VocabListView(MethodView):
    """Vocablist view."""

    def __init__(self):
        self.template = "cca/vocablist.html"

    def get(self):
        """Renders the template."""
        vocabs = VocabularyType.query.all()
        vocabs = vocabs + VocabularyScheme.query.all()
        return render_template(self.template, vocabs=vocabs)
