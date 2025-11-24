from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Table, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    USER = "user"
    TRAINER = "trainer"
    ADMIN = "admin"

class MembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class TrainingType(str, enum.Enum):
    INDIVIDUAL = "individual"
    GROUP = "group"

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    client_profile = relationship("Client", back_populates="user", uselist=False)
    trainer_profile = relationship("Trainer", back_populates="user", uselist=False)
    memberships = relationship("Membership", back_populates="user")
    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("Review", back_populates="user")

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    preferences = Column(JSON, default=dict)
    join_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="client_profile")
    memberships = relationship("Membership", back_populates="client")
    bookings = relationship("Booking", back_populates="client")
    reviews = relationship("Review", back_populates="client")

class Trainer(Base):
    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    specialization = Column(String, nullable=False)
    experience = Column(Integer, default=0)
    bio = Column(Text, nullable=True)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    photo_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trainer_profile")
    trainings = relationship("Training", back_populates="trainer")
    reviews = relationship("Review", back_populates="trainer")

class MembershipType(Base):
    __tablename__ = "membership_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    duration_days = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    features = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    membership_type_id = Column(Integer, ForeignKey("membership_types.id"))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(Enum(MembershipStatus), default=MembershipStatus.ACTIVE)
    custom_options = Column(JSON, default=dict)
    pause_history = Column(JSON, default=list)
    current_pause = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="memberships")
    client = relationship("Client", back_populates="memberships")
    membership_type = relationship("MembershipType")

class Training(Base):
    __tablename__ = "trainings"

    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(TrainingType), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    max_participants = Column(Integer, default=1)
    current_participants = Column(Integer, default=0)
    status = Column(String, default="available")
    price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    trainer = relationship("Trainer", back_populates="trainings")
    bookings = relationship("Booking", back_populates="training")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    training_id = Column(Integer, ForeignKey("trainings.id"))
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    client = relationship("Client", back_populates="bookings")
    training = relationship("Training", back_populates="bookings")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    client = relationship("Client", back_populates="reviews")
    trainer = relationship("Trainer", back_populates="reviews")