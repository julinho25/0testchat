"""initial schema"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_table(
        "depots",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("address", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_table(
        "vehicles",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("plate", sa.String(), nullable=False),
        sa.Column("vehicle_type", sa.String(), nullable=False),
        sa.Column("capacity_kg", sa.Float()),
        sa.Column("capacity_m3", sa.Float()),
        sa.Column("height_m", sa.Float()),
        sa.Column("width_m", sa.Float()),
        sa.Column("length_m", sa.Float()),
        sa.Column("tare_kg", sa.Float()),
        sa.Column("max_stops", sa.Integer()),
        sa.Column("start_depot_id", pg.UUID(as_uuid=True)),
        sa.Column("end_depot_id", pg.UUID(as_uuid=True)),
        sa.Column("shift_start", sa.Time()),
        sa.Column("shift_end", sa.Time()),
        sa.Column("tags", pg.ARRAY(sa.String())),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("km_per_liter", sa.Float()),
        sa.Column("fixed_cost_period", sa.String()),
        sa.Column("fixed_cost_value", sa.Float()),
        sa.Column("cost_per_km", sa.Float()),
        sa.Column("cost_per_hour", sa.Float()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_table(
        "clients",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("cpf_cnpj", sa.String()),
        sa.Column("phone", sa.String()),
        sa.Column("email", sa.String()),
        sa.Column("commercial_terms", pg.JSONB()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_table(
        "client_addresses",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("label", sa.String()),
        sa.Column("street", sa.String()),
        sa.Column("number", sa.String()),
        sa.Column("district", sa.String()),
        sa.Column("city", sa.String()),
        sa.Column("state", sa.String()),
        sa.Column("zip", sa.String()),
        sa.Column("lat", sa.Float()),
        sa.Column("lng", sa.Float()),
        sa.Column("geocode_source", sa.String()),
        sa.Column("restrictions", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_table(
        "route_jobs",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("depot_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("shift", sa.String(), nullable=False),
        sa.Column("route_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("config", pg.JSONB()),
        sa.Column("started_at", sa.DateTime()),
        sa.Column("finished_at", sa.DateTime()),
        sa.Column("created_by", pg.UUID(as_uuid=True)),
        sa.Column("error_message", sa.Text()),
    )
    op.create_table(
        "deliveries",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", sa.String(), nullable=False),
        sa.Column("client_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("address_id", pg.UUID(as_uuid=True)),
        sa.Column("lat", sa.Float()),
        sa.Column("lng", sa.Float()),
        sa.Column("weight_kg", sa.Float()),
        sa.Column("volume_m3", sa.Float()),
        sa.Column("time_window_start", sa.Time()),
        sa.Column("time_window_end", sa.Time()),
        sa.Column("revenue_expected", sa.Numeric(12, 2)),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("routed_job_id", pg.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_table(
        "routes",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("route_job_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("vehicle_id", pg.UUID(as_uuid=True)),
        sa.Column("total_km", sa.Float()),
        sa.Column("total_time_min", sa.Float()),
        sa.Column("cost_fuel", sa.Float()),
        sa.Column("cost_km", sa.Float()),
        sa.Column("cost_hour", sa.Float()),
        sa.Column("cost_fixed", sa.Float()),
        sa.Column("cost_total", sa.Float()),
        sa.Column("baseline_cost_total", sa.Float()),
        sa.Column("savings_value", sa.Float()),
        sa.Column("polyline_geojson", pg.JSONB()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_table(
        "route_stops",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("route_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("stop_sequence", sa.Integer(), nullable=False),
        sa.Column("delivery_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("eta", sa.DateTime()),
        sa.Column("service_time_min", sa.Integer(), server_default="5"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_table(
        "invoices",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("month_ref", sa.String(), nullable=False),
        sa.Column("amount_expected", sa.Numeric(12, 2)),
        sa.Column("status", sa.String()),
        sa.Column("due_date", sa.Date()),
    )
    op.create_table(
        "payments",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("invoice_id", pg.UUID(as_uuid=True)),
        sa.Column("delivery_id", pg.UUID(as_uuid=True)),
        sa.Column("paid_at", sa.DateTime()),
        sa.Column("amount", sa.Numeric(12, 2)),
        sa.Column("method", sa.String()),
        sa.Column("notes", sa.Text()),
    )
    op.create_table(
        "audit_log",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True)),
        sa.Column("entity", sa.String()),
        sa.Column("entity_id", pg.UUID(as_uuid=True)),
        sa.Column("action", sa.String()),
        sa.Column("before", pg.JSONB()),
        sa.Column("after", pg.JSONB()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("ip", sa.String()),
        sa.Column("user_agent", sa.String()),
    )

    op.create_index("idx_deliveries_status_created", "deliveries", ["status", "created_at"])
    op.create_index("idx_deliveries_order", "deliveries", ["order_id"])
    op.create_index("idx_vehicle_plate", "vehicles", ["plate"])
    op.create_index("idx_routes_job", "routes", ["route_job_id"])
    op.create_index("idx_audit_entity", "audit_log", ["entity", "created_at"])
    op.create_index("idx_payments_paid", "payments", ["paid_at"])


def downgrade():
    op.drop_index("idx_payments_paid", table_name="payments")
    op.drop_index("idx_audit_entity", table_name="audit_log")
    op.drop_index("idx_routes_job", table_name="routes")
    op.drop_index("idx_vehicle_plate", table_name="vehicles")
    op.drop_index("idx_deliveries_order", table_name="deliveries")
    op.drop_index("idx_deliveries_status_created", table_name="deliveries")
    op.drop_table("audit_log")
    op.drop_table("payments")
    op.drop_table("invoices")
    op.drop_table("route_stops")
    op.drop_table("routes")
    op.drop_table("deliveries")
    op.drop_table("route_jobs")
    op.drop_table("client_addresses")
    op.drop_table("clients")
    op.drop_table("vehicles")
    op.drop_table("depots")
    op.drop_table("users")
