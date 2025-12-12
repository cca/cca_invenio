import click

from cca.scripts.add_editor import add_editor
from cca.scripts.add_users import add_users
from cca.scripts.clean import clean
from cca.scripts.courses_index import courses_index
from cca.scripts.groups_sync import groups_sync
from cca.scripts.set_owner import set_owner


@click.group()
@click.help_option("-h", "--help")
def cca():
    """CCA's custom CLI commands."""


cca.add_command(add_editor)
cca.add_command(add_users)
cca.add_command(clean)
cca.add_command(courses_index)
cca.add_command(groups_sync)
cca.add_command(set_owner)
