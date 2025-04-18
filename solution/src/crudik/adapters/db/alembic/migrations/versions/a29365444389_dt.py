"""['dt']

Revision ID: a29365444389
Revises: c7c730a97a19
Create Date: 2025-02-19 20:40:27.082298

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a29365444389'
down_revision = 'c7c730a97a19'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('campaign', sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.add_column('click', sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.add_column('impression', sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('impression', 'created_at')
    op.drop_column('click', 'created_at')
    op.drop_column('campaign', 'created_at')
    # ### end Alembic commands ###