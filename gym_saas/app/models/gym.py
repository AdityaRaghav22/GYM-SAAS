from sqlalchemy.orm import Mapped, mapped_column
from gym_saas.app.extensions import db
from datetime import datetime


class Gym(db.Model):
    __tablename__ = "gyms"

    id: Mapped[str] = mapped_column(db.String(50), primary_key=True)

    name: Mapped[str] = mapped_column(db.String(100), nullable=False)

    phone_number: Mapped[str] = mapped_column(db.String(20),
                                              unique=True,
                                              nullable=False)

    email: Mapped[str] = mapped_column(db.String(100),
                                       unique=True,
                                       nullable=False)

    password_hash: Mapped[str] = mapped_column(nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    users = db.relationship("User", backref="gym")

    members = db.relationship("Member", backref="gym", cascade="all, delete-orphan")
    membership = db.relationship("Membership", backref="gym", cascade="all, delete-orphan")
    plans = db.relationship("Plan", backref="gym", cascade="all, delete-orphan")
    payments = db.relationship("Payment", backref="gym", cascade="all, delete-orphan")
    
    @property
    def currently_active(self) -> bool:
        return self.is_active

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone_number": self.phone_number,
            "email": self.email,
            "created_at":
            self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active
        }
