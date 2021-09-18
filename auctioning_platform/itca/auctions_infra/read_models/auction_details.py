from sqlalchemy import BigInteger, Column, String, Table

from itca.db import JSONB, metadata

auction_read_model = Table(
    "auction_read_model",
    metadata,
    Column("id", BigInteger()),
    Column("current_price", JSONB()),
    Column("starting_price", JSONB()),
    Column("title", String()),
    Column("description", String()),
)
