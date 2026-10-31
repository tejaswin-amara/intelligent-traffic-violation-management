"""Initial schema

Revision ID: 1a2b3c4d5e6f
Revises:
Create Date: 2023-10-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1a2b3c4d5e6f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Read and execute the original schema.sql
    with open('../intelligent-traffic-violation-management/database/schema.sql', 'r') as f:
        sql = f.read()
    op.execute(sql)


def downgrade() -> None:
    # Basic teardown
    op.execute("""
        DROP TABLE IF EXISTS audit_events CASCADE;
        DROP TABLE IF EXISTS notifications CASCADE;
        DROP TABLE IF EXISTS appeals CASCADE;
        DROP TABLE IF EXISTS payment_webhook_events CASCADE;
        DROP TABLE IF EXISTS payment_ledger_entries CASCADE;
        DROP TABLE IF EXISTS payments CASCADE;
        DROP TABLE IF EXISTS notices CASCADE;
        DROP TABLE IF EXISTS fine_assessments CASCADE;
        DROP TABLE IF EXISTS review_decisions CASCADE;
        DROP TABLE IF EXISTS detection_runs CASCADE;
        DROP TABLE IF EXISTS evidence_assets CASCADE;
        DROP TABLE IF EXISTS violations CASCADE;
        DROP TABLE IF EXISTS fine_schedules CASCADE;
        DROP TABLE IF EXISTS offences CASCADE;
        DROP TABLE IF EXISTS vehicle_ownership_history CASCADE;
        DROP TABLE IF EXISTS drivers CASCADE;
        DROP TABLE IF EXISTS persons CASCADE;
        DROP TABLE IF EXISTS vehicles CASCADE;
        DROP TABLE IF EXISTS jurisdictions CASCADE;
        DROP TABLE IF EXISTS memberships CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
        DROP TABLE IF EXISTS organisations CASCADE;
    """)
