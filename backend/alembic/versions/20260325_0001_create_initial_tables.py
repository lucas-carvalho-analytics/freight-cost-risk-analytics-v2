"""create initial tables

Revision ID: 20260325_0001
Revises:
Create Date: 2026-03-25 15:10:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260325_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "shipments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("data_embarque", sa.Date(), nullable=False),
        sa.Column("origem", sa.String(length=120), nullable=False),
        sa.Column("destino", sa.String(length=120), nullable=False),
        sa.Column("valor_carga", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("tipo_veiculo", sa.String(length=80), nullable=False),
        sa.Column("transportadora", sa.String(length=120), nullable=False),
        sa.Column("taxa_ad_valorem_pct", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("frete_peso", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("ocorrencia", sa.Text(), nullable=True),
        sa.Column("tem_ocorrencia", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("ad_valorem", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_shipments_data_embarque"), "shipments", ["data_embarque"], unique=False)
    op.create_index(op.f("ix_shipments_destino"), "shipments", ["destino"], unique=False)
    op.create_index(op.f("ix_shipments_origem"), "shipments", ["origem"], unique=False)
    op.create_index(op.f("ix_shipments_transportadora"), "shipments", ["transportadora"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("endpoint", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_user_id"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_shipments_transportadora"), table_name="shipments")
    op.drop_index(op.f("ix_shipments_origem"), table_name="shipments")
    op.drop_index(op.f("ix_shipments_destino"), table_name="shipments")
    op.drop_index(op.f("ix_shipments_data_embarque"), table_name="shipments")
    op.drop_table("shipments")
