"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision}
Create Date: ${create_date}

"""

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

from alembic import context


def upgrade():
    schema_upgrades()
    if context.get_x_argument(as_dictionary=True).get('data', None):
        data_upgrades()

def downgrade():
    if context.get_x_argument(as_dictionary=True).get('data', None):
        data_downgrades()
    schema_downgrades()

def schema_upgrades():
    """schema upgrade migrations go here."""
    ${upgrades if upgrades else "pass"}

def schema_downgrades():
    """schema downgrade migrations go here."""
    ${downgrades if downgrades else "pass"}

def data_upgrades():
    """Add any optional data upgrade migrations here!"""
    pass

def data_downgrades():
    """Add any optional data downgrade migrations here!"""
    pass
