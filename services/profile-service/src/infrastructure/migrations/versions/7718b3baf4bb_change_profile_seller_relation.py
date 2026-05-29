"""change profile - seller relation

Revision ID: 7718b3baf4bb
Revises: 07b0c398af30
Create Date: 2026-05-29 03:50:17.225856

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7718b3baf4bb"
down_revision: Union[str, Sequence[str], None] = "07b0c398af30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_foreign_key(
        "fk_seller_accounts_user_id",
        "seller_accounts",
        "profiles",
        ["user_id"],
        ["user_id"],
        source_schema="profile",
        referent_schema="profile",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_seller_accounts_user_id",
        "seller_accounts",
        schema="profile",
        type_="foreignkey",
    )
