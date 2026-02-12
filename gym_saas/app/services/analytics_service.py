class AnalyticsService
  @staticmethod
  def get_membership_stats(gym_id):
     gym_id_valid, gym_id_err = validate_id(gym_id)
     if not gym_id_valid:
        return None, gym_id_err
        # 🔹 Total Members
     total_members = Member.query.filter_by(gym_id=gym_id).count()

     # 🔹 Active Memberships
     active_memberships = Membership.query.filter_by
     (gym_id=gym_id, is_active=True).count()
     # 🔹 Revenue
     total_revenue = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter_by(gym_id=gym_id).scalar()
     # 🔹 Pending Payments
     pending_payments = db.session.query(func.coalesce(func.sum(Membership.plan.price), 0)).filter
     (Membership.gym_id == gym_id, Membership.is_active.is_(True)).scalar()
     total_paid = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).join(Membership).filter
     (Membership.gym_id == gym_id, Membership.is_active.is_(True)).scalar()
     pending_amount = pending_payments - total_paid
     # return {
     #    "total_members": total_members,
     #    "active_memberships": active_memberships,
     #    "total_revenue": total_revenue,
     #    "pending_amount": pending_amount
     # }
     # 🔹 Membership Status Distribution
     status_distribution = db.session.query(
        Membership.status,
        func.count(Membership.id)
     ).filter_by(gym_id=gym_id).group_by(Membership.status).all()
     status_distribution = {status: count for status, count in status_distribution}
     # 🔹 Revenue by Plan
     revenue_by_plan = db.session.query
     (Plan.name, func.coalesce(func.sum(Payment.amount), 0)).join(Membership).join(Plan).filter
     (Membership.gym_id == gym_id).group_by(Plan.name).all()
     revenue_by_plan = {plan: amount for plan, amount in revenue_by_plan}
     # 🔹 Membership Duration Distribution
     duration_distribution = db.session.query
     (Plan.duration_months, func.count(Membership.id)).join(Membership).filter
     (Membership.gym_id == gym_id).group_by(Plan.duration_months).all()
     duration_distribution = {duration: count for duration, count in duration_distribution}
     return

   @staticmethod
   def get_membership_stats(gym_id):
     gym_id_valid, gym_id_err = validate_id(gym_id)
     if not gym_id_valid:
        return None, gym_id_err
       