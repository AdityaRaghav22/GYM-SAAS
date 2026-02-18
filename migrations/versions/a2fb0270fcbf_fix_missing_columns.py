from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "NEW_ID"
down_revision = "e7f9afec78b2"
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    columns = [c["name"] for c in inspector.get_columns("gyms")]

    if "reset_token" not in columns:
        op.add_column(
            "gyms",
            sa.Column("reset_token", sa.String(length=255), nullable=True),
        )

    if "reset_token_expiry" not in columns:
        op.add_column(
            "gyms",
            sa.Column("reset_token_expiry", sa.DateTime(), nullable=True),
        )

def downgrade():
    pass
