from sqlalchemy.orm import Mapped, mapped_column
from gym_saas.app.extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(db.String(50), primary_key=True)

    gym_id: Mapped[str] = mapped_column(db.String(50),
                                        db.ForeignKey("gyms.id"),
                                        nullable=False,
                                        index=True)

    name: Mapped[str] = mapped_column(db.String(200),
                                      nullable=False,
                                      index=True)

    email: Mapped[str] = mapped_column(
        db.String(100), nullable=False, unique=True, index=True)

    phone_number: Mapped[str] = mapped_column(db.String(20),
                                              nullable=False,
                                              unique=True,
                                              index=True)

    role: Mapped[str] = mapped_column(db.Enum(
                                    "owner",
                                    "staff",
                                    name="user_roles"),
                                    nullable=False,
                                    index=True,
                                    default="staff")

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "gym_id": self.gym_id,
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }
