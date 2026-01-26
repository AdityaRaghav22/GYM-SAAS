from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db
from datetime import datetime


class Member(db.Model):
    __tablename__ = "members"        

    id: Mapped[str] = mapped_column(db.String(50), primary_key=True)

    gym_id: Mapped[str] = mapped_column(db.String(50),
                                        db.ForeignKey("gyms.id"),
                                        nullable=False,
                                        index=True)

    name: Mapped[str] = mapped_column(db.String(200),
                                        nullable=False,
                                        index=True)

    phone_number: Mapped[str] = mapped_column(db.String(20),
                                        nullable=False,
                                        index=True)

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    join_date: Mapped[datetime] = mapped_column(DateTime,
                                        default=datetime.utcnow,
                                        index=True)

    __table_args__ = (db.UniqueConstraint("gym_id",
                                        "phone_number",
                                        name="uq_member_phone_per_gym"), )

    memberships = db.relationship("Membership",
                                        backref="member",
                                        cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "gym_id": self.gym_id,
            "name": self.name,
            "phone_number": self.phone_number,
            "join_date": self.join_date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }
