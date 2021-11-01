"""add order_items table

Revision ID: 2df077842216
Revises: 2d9b85621f11
Create Date: 2021-10-31 16:23:52.201888

"""

# revision identifiers, used by Alembic.
revision = '2df077842216'
down_revision = '2d9b85621f11'

import sqlalchemy as sa
from alembic import context
from alembic import op


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
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order_items',
                    sa.Column('id', sa.INTEGER(), sa.Identity(always=True, cache=5),
                              nullable=False),
                    sa.Column('order_id', sa.INTEGER(), nullable=False),
                    sa.Column('product_id', sa.Integer(), nullable=True),
                    sa.Column('quantity', sa.SMALLINT(), server_default=sa.text('1'),
                              nullable=False),
                    sa.ForeignKeyConstraint(['order_id'], ['orders.id'],
                                            name='FK__order_items__order_item_order',
                                            onupdate='CASCADE', ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['product_id'], ['products.id'],
                                            name='FK__order_items__order_item_product',
                                            onupdate='CASCADE', ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('order_id')
                    )
    # ### end Alembic commands ###


def schema_downgrades():
    """schema downgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order_items')
    # ### end Alembic commands ###


def data_upgrades():
    """Add any optional data upgrade migrations here!"""
    pass


def data_downgrades():
    """Add any optional data downgrade migrations here!"""
    pass
