"""hashed_password and salt update for Users model

Revision ID: be7cef1b49e9
Revises: 4cc2763a54c5
Create Date: 2025-01-25 20:24:37.368958

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be7cef1b49e9'
down_revision: Union[str, None] = '4cc2763a54c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=False))
    op.add_column('users', sa.Column('salt', sa.String(), nullable=False))
    op.drop_column('users', 'password_hash')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password_hash', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('users', 'salt')
    op.drop_column('users', 'hashed_password')
    # ### end Alembic commands ###
