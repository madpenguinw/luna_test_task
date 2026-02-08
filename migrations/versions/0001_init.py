"""init

Revision ID: 0001
Revises:
Create Date: 2026-02-07 14:39:17.075989

"""

from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "buildings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("address", sa.String(500), nullable=False),
        sa.Column(
            "location",
            geoalchemy2.types.Geography(
                geometry_type="POINT",
                srid=4326,
                spatial_index=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_buildings_location",
        "buildings",
        ["location"],
        postgresql_using="gist",
    )

    op.create_table(
        "activities",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "parent_id",
            sa.Uuid(),
            sa.ForeignKey("activities.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("level", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("level >= 1 AND level <= 3", name="ck_activity_level"),
    )
    op.create_index(op.f("ix_activities_name"), "activities", ["name"])
    op.create_index(op.f("ix_activities_parent_id"), "activities", ["parent_id"])

    op.create_table(
        "organizations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("phone_numbers", sa.ARRAY(sa.String(50)), nullable=False),
        sa.Column(
            "building_id",
            sa.Uuid(),
            sa.ForeignKey("buildings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(op.f("ix_organizations_name"), "organizations", ["name"])
    op.create_index(
        op.f("ix_organizations_building_id"), "organizations", ["building_id"]
    )

    op.create_table(
        "organization_activity",
        sa.Column(
            "organization_id",
            sa.Uuid(),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "activity_id",
            sa.Uuid(),
            sa.ForeignKey("activities.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("organization_activity")
    op.drop_index(op.f("ix_organizations_name"), table_name="organizations")
    op.drop_index(op.f("ix_organizations_building_id"), table_name="organizations")
    op.drop_table("organizations")
    op.drop_index(op.f("ix_activities_parent_id"), table_name="activities")
    op.drop_index(op.f("ix_activities_name"), table_name="activities")
    op.drop_table("activities")
    op.drop_index("ix_buildings_location", table_name="buildings")
    op.drop_table("buildings")
    op.execute("DROP EXTENSION IF EXISTS postgis")
