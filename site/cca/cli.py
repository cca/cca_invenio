import click

from cca.scripts.courses_index import courses_index
from cca.scripts.groups_sync import groups_sync


@click.group()
@click.help_option("-h", "--help")
def cca():
    """CCA's custom CLI commands."""


cca.add_command(courses_index)
cca.add_command(groups_sync)
