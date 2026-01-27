from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from gym_saas.app.extensions import db
from datetime import datetime
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .plan import Plan


class Membership(db.Model):
    __tablename__ = "memberships"

    id: Mapped[str] = mapped_column(db.String(50), primary_key=True)

    member_id: Mapped[str] = mapped_column(db.String(50),
                                           db.ForeignKey("members.id"),
                                           nullable=False,
                                           index=True)

    gym_id: Mapped[str] = mapped_column(db.String(50),
                                        db.ForeignKey("gyms.id"),
                                        nullable=False,
                                        index=True)

    plan_id: Mapped[str] = mapped_column(db.String(50),
                                         db.ForeignKey("plans.id"),
                                         nullable=False,
                                         index=True)

    start_date: Mapped[datetime] = mapped_column(DateTime,
                                                 default=datetime.utcnow)
    end_date: Mapped[datetime] = mapped_column(DateTime,
                                               nullable=False,
                                               index=True)

    status: Mapped[str] = mapped_column(db.Enum("active",
                                                "expired",
                                                "cancelled",
                                                name="membership_status"),
                                        nullable=False,
                                        default="active",
                                        index=True)

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=datetime.utcnow,
                                                 index=True)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="memberships")

    payments = relationship("Payment",
                            backref="membership",
                            cascade="all, delete-orphan")

    @property
    def currently_active(self):
        return (self.is_active and self.status == "active"
                and self.end_date >= datetime.utcnow())

    def to_dict(self):
        return {
            "id": self.id,
            "member_id": self.member_id,
            "plan_id": self.plan_id,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "status": self.status,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }
