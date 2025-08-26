"""
Database models and management for the Outlook Automation Tool
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any

Base = declarative_base()

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    display_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    time_zone = Column(String(50), default="UTC")
    preferences_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    templates = relationship("Template", back_populates="owner")
    signatures = relationship("Signature", back_populates="owner")
    messages = relationship("Message", back_populates="user")
    rules = relationship("Rule", back_populates="owner")
    integrations = relationship("Integration", back_populates="user")

class Template(Base):
    """Email template model"""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    schema_json = Column(JSON, nullable=False)
    version = Column(Integer, default=1)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="templates")

class Signature(Base):
    """Email signature model"""
    __tablename__ = "signatures"
    
    id = Column(Integer, primary_key=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    html = Column(Text, nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="signatures")

class Message(Base):
    """Email message tracking model"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    graph_message_id = Column(String(255), unique=True)
    internet_message_id = Column(String(255))
    conversation_id = Column(String(255))
    subject = Column(String(500))
    sent_at = Column(DateTime)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="messages")
    recipients = relationship("Recipient", back_populates="message")

class Recipient(Base):
    """Email recipient tracking model"""
    __tablename__ = "recipients"
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    email = Column(String(255), nullable=False)
    name = Column(String(255))
    status = Column(String(50), default="Pending")  # Pending, Replied, Bounced
    last_change = Column(DateTime, default=func.now())
    
    # Relationships
    message = relationship("Message", back_populates="recipients")

class Rule(Base):
    """Automation rule model"""
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(100), nullable=False)  # attachment, filing, reminder
    criteria_json = Column(JSON, nullable=False)
    actions_json = Column(JSON, nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="rules")

class Job(Base):
    """Background job model"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True)
    type = Column(String(100), nullable=False)
    schedule = Column(String(255))
    status = Column(String(50), default="pending")
    last_run = Column(DateTime)
    result_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())

class Integration(Base):
    """External integration model"""
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # Zoom, Teams, etc.
    tokens_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="integrations")

class DatabaseManager:
    """Database management class"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def initialize(self):
        """Initialize database tables"""
        Base.metadata.create_all(bind=self.engine)
        
        # Create default data if needed
        with self.get_session() as session:
            if not session.query(User).first():
                self._create_default_data(session)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def _create_default_data(self, session: Session):
        """Create default templates and signatures"""
        # Create default user
        default_user = User(
            display_name="Default User",
            email="user@example.com",
            preferences_json={"theme": "light"}
        )
        session.add(default_user)
        session.flush()
        
        # Create default templates
        default_templates = [
            {
                "name": "Zoom Meeting Invite",
                "category": "Meetings",
                "schema_json": {
                    "subject": "Zoom Meeting with <RecipientName> — <ShortTopic>",
                    "body": "Hi <RecipientName>\n\nPlease join the Zoom call at <ZoomLink> on <LocalDateTime>.\n\n<UserMessage>\n\nRegards,\n<Signature>",
                    "placeholders": {
                        "ShortTopic": {"type": "string", "required": False},
                        "LocalDateTime": {"type": "datetime", "required": False},
                        "ZoomLink": {"type": "url", "required": True},
                        "UserMessage": {"type": "multiline", "required": False},
                        "Signature": {"type": "signature", "required": False}
                    },
                    "defaults": {"ShortTopic": "Catch-up"},
                    "useSignature": True
                }
            },
            {
                "name": "Follow-up Reminder",
                "category": "Follow-ups",
                "schema_json": {
                    "subject": "Following up on our previous conversation",
                    "body": "Hi <RecipientName>\n\nI wanted to follow up regarding <UserMessage>. Please let me know your thoughts.\n\nBest Regards,\n<Signature>",
                    "placeholders": {
                        "UserMessage": {"type": "multiline", "required": True},
                        "Signature": {"type": "signature", "required": False}
                    },
                    "useSignature": True
                }
            },
            {
                "name": "Thank You Note",
                "category": "General",
                "schema_json": {
                    "subject": "Thank you for your time",
                    "body": "Hi <RecipientName>\n\nThank you for <UserMessage>. It was a pleasure working with you.\n\nWarm Regards,\n<Signature>",
                    "placeholders": {
                        "UserMessage": {"type": "string", "required": True},
                        "Signature": {"type": "signature", "required": False}
                    },
                    "useSignature": True
                }
            }
        ]
        
        for template_data in default_templates:
            template = Template(
                owner_user_id=default_user.id,
                name=template_data["name"],
                category=template_data["category"],
                schema_json=template_data["schema_json"],
                is_default=True
            )
            session.add(template)
        
        # Create default signature
        default_signature = Signature(
            owner_user_id=default_user.id,
            name="Default Signature",
            html="<p>Best regards,<br>Your Name<br>Your Title<br>Your Company</p>",
            is_default=True
        )
        session.add(default_signature)
        
        session.commit()