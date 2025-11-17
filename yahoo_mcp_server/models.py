"""
SQLAlchemy Models for Yahoo MCP Server
Maps to existing SQLite database from Phase 1
"""
from sqlalchemy import Column, String, Integer, Float, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import json

Base = declarative_base()


class Tenant(Base):
    __tablename__ = 'tenants'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    adapter_type = Column(String, nullable=False)
    adapter_config = Column(Text, nullable=False)  # JSON
    is_active = Column(Integer, default=1)
    created_at = Column(String)
    updated_at = Column(String)
    
    def adapter_config_dict(self):
        return json.loads(self.adapter_config)


class Principal(Base):
    __tablename__ = 'principals'
    
    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    principal_id = Column(String, nullable=False)
    auth_token = Column(String, nullable=False)
    access_level = Column(String, default='standard')
    principal_metadata = Column('metadata', Text)  # JSON - map to 'metadata' column in DB
    is_active = Column(Integer, default=1)
    created_at = Column(String)
    
    def metadata_dict(self):
        return json.loads(self.principal_metadata) if self.principal_metadata else {}


class MatchedAudience(Base):
    __tablename__ = 'matched_audiences'
    
    id = Column(String, primary_key=True)
    segment_id = Column(String, nullable=False, unique=True)
    segment_name = Column(String, nullable=False)
    tenant_id = Column(String, nullable=False)
    principal_id = Column(String, nullable=False)
    overlap_count = Column(Integer, nullable=False)
    total_nike_segment = Column(Integer)
    total_yahoo_segment = Column(Integer)
    match_rate = Column(Float)
    demographics = Column(Text, nullable=False)  # JSON
    engagement_score = Column(Float)
    quality_score = Column(Float)
    privacy_params = Column(Text)  # JSON
    created_at = Column(String)
    expires_at = Column(String)
    
    def demographics_dict(self):
        return json.loads(self.demographics)
    
    def privacy_params_dict(self):
        return json.loads(self.privacy_params) if self.privacy_params else {}


class Product(Base):
    __tablename__ = 'products'
    
    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    product_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    product_type = Column(String)
    properties = Column(Text, nullable=False)  # JSON
    formats = Column(Text, nullable=False)  # JSON
    targeting = Column(Text)  # JSON
    matched_audience_ids = Column(Text)  # JSON
    pricing = Column(Text, nullable=False)  # JSON
    minimum_budget = Column(Float)
    estimated_reach = Column(Integer)
    matched_reach = Column(Integer)
    estimated_impressions = Column(Integer)
    available_from = Column(String)
    available_to = Column(String)
    is_active = Column(Integer, default=1)
    principal_access = Column(Text)  # JSON
    created_at = Column(String)
    updated_at = Column(String)
    
    def properties_list(self):
        return json.loads(self.properties)
    
    def formats_list(self):
        return json.loads(self.formats)
    
    def targeting_dict(self):
        return json.loads(self.targeting) if self.targeting else {}
    
    def matched_audience_ids_list(self):
        return json.loads(self.matched_audience_ids) if self.matched_audience_ids else []
    
    def pricing_dict(self):
        return json.loads(self.pricing)
    
    def principal_access_dict(self):
        return json.loads(self.principal_access) if self.principal_access else {}


class MediaBuy(Base):
    __tablename__ = 'media_buys'
    
    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    media_buy_id = Column(String, nullable=False)
    principal_id = Column(String, nullable=False)
    product_ids = Column(Text, nullable=False)  # JSON
    total_budget = Column(Float, nullable=False)
    currency = Column(String, default='USD')
    flight_start_date = Column(String, nullable=False)
    flight_end_date = Column(String, nullable=False)
    targeting = Column(Text)  # JSON
    matched_audience_id = Column(String)
    assigned_creatives = Column(Text)  # JSON
    status = Column(String, default='pending')
    workflow_state = Column(Text)  # JSON
    impressions_delivered = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    external_campaign_id = Column(String)
    created_at = Column(String)
    updated_at = Column(String)
    
    def product_ids_list(self):
        return json.loads(self.product_ids)
    
    def targeting_dict(self):
        return json.loads(self.targeting) if self.targeting else {}
    
    def assigned_creatives_list(self):
        return json.loads(self.assigned_creatives) if self.assigned_creatives else []
    
    def workflow_state_dict(self):
        return json.loads(self.workflow_state) if self.workflow_state else {}


class Creative(Base):
    __tablename__ = 'creatives'
    
    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    creative_id = Column(String, nullable=False)
    principal_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    format = Column(String, nullable=False)
    file_url = Column(Text, nullable=False)
    preview_url = Column(Text)
    dimensions = Column(Text)  # JSON
    file_size_bytes = Column(Integer)
    duration_seconds = Column(Integer)
    approval_status = Column(String, default='approved')
    approval_notes = Column(Text)
    reviewed_by = Column(String)
    reviewed_at = Column(String)
    created_at = Column(String)
    updated_at = Column(String)
    
    def dimensions_dict(self):
        return json.loads(self.dimensions) if self.dimensions else {}


class DeliveryMetric(Base):
    __tablename__ = 'delivery_metrics'
    
    id = Column(String, primary_key=True)
    media_buy_id = Column(String, nullable=False)
    date = Column(String, nullable=False)
    hour = Column(Integer)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    product_id = Column(String)
    creative_id = Column(String)
    geo = Column(String)
    device_type = Column(String)
    created_at = Column(String)


class AuditLog(Base):
    __tablename__ = 'audit_log'
    
    id = Column(String, primary_key=True)
    principal_id = Column(String)
    tenant_id = Column(String)
    operation = Column(String, nullable=False)
    tool_name = Column(String)
    request_params = Column(Text)  # JSON
    response_data = Column(Text)  # JSON
    status = Column(String)
    ip_address = Column(String)
    user_agent = Column(Text)
    timestamp = Column(String)
    
    def request_params_dict(self):
        return json.loads(self.request_params) if self.request_params else {}
    
    def response_data_dict(self):
        return json.loads(self.response_data) if self.response_data else {}


# Database utilities
def get_engine(database_path: str):
    """Create SQLAlchemy engine"""
    return create_engine(f'sqlite:///{database_path}')


def get_session(database_path: str):
    """Create database session"""
    engine = get_engine(database_path)
    Session = sessionmaker(bind=engine)
    return Session()

