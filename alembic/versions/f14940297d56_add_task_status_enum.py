"""add task status enum

Revision ID: f14940297d56
Revises: 21f7db92e6e2
Create Date: 2026-03-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f14940297d56"
down_revision: Union[str, None] = "21f7db92e6e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


task_status_enum = sa.Enum(
    "todo",
    "in_progress",
    "done",
    name="task_status",
)


def upgrade() -> None:
    task_status_enum.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        "tasks",
        "status",
        existing_type=sa.String(length=50),
        type_=task_status_enum,
        existing_nullable=False,
        postgresql_using="status::task_status",
    )


def downgrade() -> None:
    op.alter_column(
        "tasks",
        "status",
        existing_type=task_status_enum,
        type_=sa.String(length=50),
        existing_nullable=False,
        postgresql_using="status::text",
    )

    task_status_enum.drop(op.get_bind(), checkfirst=True)