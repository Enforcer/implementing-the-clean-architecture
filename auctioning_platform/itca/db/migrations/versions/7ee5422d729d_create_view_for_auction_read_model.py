"""Create view for auction read model

Revision ID: 7ee5422d729d
Revises: 873d26933b37
Create Date: 2021-09-18 21:49:49.017835

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "7ee5422d729d"
down_revision = "873d26933b37"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    CREATE VIEW auction_read_model AS
    SELECT
        auctions.id,
        auctions.current_price,
        auctions.starting_price,
        auctions_descriptors.title,
        auctions_descriptors.description
    FROM auctions
    JOIN auctions_descriptors
        ON auctions.id = auctions_descriptors.id
    """
    )


def downgrade():
    op.execute("DROP VIEW auction_read_model")
