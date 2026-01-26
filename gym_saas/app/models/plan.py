from sqlalchemy.orm import Mapped, mapped_column
from app.extensions import db
from sqlalchemy import Numeric
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .membership import Membership


class Plan(db.Model):
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(db.String(50), primary_key=True)

    gym_id: Mapped[str] = mapped_column(db.String(50),
                                        db.ForeignKey("gyms.id"),
                                        nullable=False,
                                        index=True)

    name: Mapped[str] = mapped_column(db.String(200),
                                      nullable=False,
                                      index=True)

    duration_months: Mapped[int] = mapped_column(db.Integer, nullable=False)

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    description: Mapped[str | None] = mapped_column(db.String(2000))

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("gym_id",
                                          "name",
                                          name="uq_plan_name_per_gym"), )

    memberships: Mapped[list["Membership"]] = relationship(
        "Membership", back_populates="plan")

    def to_dict(self):
        return {
            "id": self.id,
            "gym_id": self.gym_id,
            "name": self.name,
            "duration_months": self.duration_months,
            "price": self.price,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }
