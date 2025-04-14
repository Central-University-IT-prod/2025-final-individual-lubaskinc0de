from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, Table, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as SA_UUID

from crudik.domain.entity.advertiser import Advertiser
from crudik.domain.entity.campaign import Campaign, TargetGender
from crudik.domain.entity.click import Click
from crudik.domain.entity.client import Client, Gender
from crudik.domain.entity.impression import Impression
from crudik.domain.entity.relevance import Relevance

from .registry import mapper_registry

metadata = mapper_registry.metadata

client_table = Table(
    "client",
    metadata,
    Column("client_id", SA_UUID(as_uuid=True), primary_key=True),
    Column("login", Text, nullable=False),
    Column("age", Integer, nullable=False),
    Column("location", Text, nullable=False),
    Column("gender", Enum(Gender), nullable=False),
)

advertiser_table = Table(
    "advertiser",
    metadata,
    Column("advertiser_id", SA_UUID(as_uuid=True), primary_key=True),
    Column("name", Text, nullable=False),
)

relevance_table = Table(
    "relevance",
    metadata,
    Column(
        "client_id",
        SA_UUID(as_uuid=True),
        ForeignKey("client.client_id"),
        primary_key=True,
    ),
    Column(
        "advertiser_id",
        SA_UUID(as_uuid=True),
        ForeignKey("advertiser.advertiser_id"),
        primary_key=True,
    ),
    Column("score", Integer, nullable=False),
)

campaign_table = Table(
    "campaign",
    metadata,
    Column("campaign_id", SA_UUID(as_uuid=True), primary_key=True),
    Column(
        "advertiser_id",
        SA_UUID(as_uuid=True),
        ForeignKey("advertiser.advertiser_id"),
        nullable=False,
        index=True,
    ),
    Column("impressions_limit", Integer, nullable=False),
    Column("clicks_limit", Integer, nullable=False),
    Column("cost_per_impression", Numeric(10, 2), nullable=False),
    Column("cost_per_click", Numeric(10, 2), nullable=False),
    Column("ad_title", Text, nullable=False),
    Column("ad_text", Text, nullable=False),
    Column("start_date", Integer, nullable=False),
    Column("end_date", Integer, nullable=False),
    Column("age_from", Integer, nullable=True, index=True),
    Column("age_to", Integer, nullable=True, index=True),
    Column("location", Text, nullable=True, index=True),
    Column("gender", Enum(TargetGender), nullable=True, index=True),
    Column("image_path", Text, nullable=True),
    Column("is_deleted", Boolean, nullable=False, index=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

click_table = Table(
    "click",
    metadata,
    Column("click_id", SA_UUID(as_uuid=True), primary_key=True),
    Column(
        "ad_id",
        SA_UUID(as_uuid=True),
        ForeignKey("campaign.campaign_id"),
        nullable=False,
        index=True,
    ),
    Column(
        "client_id",
        SA_UUID(as_uuid=True),
        ForeignKey("client.client_id"),
        nullable=False,
        index=True,
    ),
    Column("cost_per_click", Numeric(10, 2), nullable=False, index=True),
    Column("day", Integer, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint("client_id", "ad_id"),
)

impression_table = Table(
    "impression",
    metadata,
    Column("impression_id", SA_UUID(as_uuid=True), primary_key=True),
    Column(
        "ad_id",
        SA_UUID(as_uuid=True),
        ForeignKey("campaign.campaign_id"),
        nullable=False,
        index=True,
    ),
    Column(
        "client_id",
        SA_UUID(as_uuid=True),
        ForeignKey("client.client_id"),
        nullable=False,
        index=True,
    ),
    Column("cost_per_impression", Numeric(10, 2), nullable=False, index=True),
    Column("day", Integer, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint("client_id", "ad_id"),
)

mapper_registry.map_imperatively(Client, client_table)
mapper_registry.map_imperatively(Advertiser, advertiser_table)
mapper_registry.map_imperatively(Relevance, relevance_table)
mapper_registry.map_imperatively(Campaign, campaign_table)
mapper_registry.map_imperatively(Click, click_table)
mapper_registry.map_imperatively(Impression, impression_table)
