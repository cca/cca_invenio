"""JS/CSS Webpack bundles for CCA."""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={"cca-test": "./js/cca/test.js"},
        ),
    },
)
