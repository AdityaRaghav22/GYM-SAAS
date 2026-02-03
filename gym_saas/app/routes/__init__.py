from flask import Blueprint
from . import gym_auth, member, plans, membership, payment, dashboard, public

api_v1 = Blueprint("api_v1", __name__, url_prefix="")

api_v1.register_blueprint(gym_auth.gym_auth_bp, url_prefix="/gym")
api_v1.register_blueprint(member.member_bp, url_prefix="/member")
api_v1.register_blueprint(plans.plan_bp, url_prefix="/plan")
api_v1.register_blueprint(membership.membership_bp, url_prefix="/membership")
api_v1.register_blueprint(payment.payment_bp, url_prefix="/payment")
api_v1.register_blueprint(dashboard.dashboard_bp, url_prefix="/dashboard")
api_v1.register_blueprint(public.public_bp, url_prefix= "/")
