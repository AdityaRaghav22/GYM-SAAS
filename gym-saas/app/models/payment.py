from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db
from datetime import datetime
from sqlalchemy import DateTime, Numeric
from decimal import Decimal

class Payment(db.Model):
  __tablename__ = "payments"

  id: Mapped[str] = mapped_column(db.String(50),primary_key=True)

  gym_id: Mapped[str] = mapped_column(db.String(50),
                            db.ForeignKey("gyms.id"),
                            nullable=False,
                            index= True)
  
  membership_id: Mapped[str] = mapped_column(db.String(50),
                            db.ForeignKey("memberships.id"),
                            nullable=False,
                            index= True)

  amount: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=False)

  payment_method: Mapped[str] = mapped_column(db.Enum("cash", "upi", name="payment_methods"),
                             nullable=False)

  status: Mapped[str] = mapped_column(db.Enum("PENDING", "PAID", "FAILED",
                     name="payment_status"),
                     nullable=False,
                     default="PENDING",
                     index= True)

  paid_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index= True)

  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index= True)

  def to_dict(self):
    return {
        "id": self.id,
        "gym_id": self.gym_id,
        "membership_id": self.membership_id,
        "amount": str(self.amount),
        "payment_method": self.payment_method,
        "status": self.status,
        "paid_at": self.paid_at.isoformat(),
        "created_at": self.created_at.isoformat()
    }
