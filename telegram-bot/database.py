"""Database models and operations for the licensing system."""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class License(Base):
    """License key model."""
    __tablename__ = 'licenses'

    id = Column(Integer, primary_key=True)
    license_key = Column(String(64), unique=True, nullable=False)
    key_hash = Column(String(64), nullable=False)  # Hashed version for verification
    status = Column(String(20), default='inactive')  # inactive, active, expired, revoked
    created_at = Column(DateTime, default=datetime.utcnow)
    activated_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(100), nullable=True)
    device_fingerprint = Column(String(128), nullable=True)
    plan_type = Column(String(20), default='standard')  # standard, premium, lifetime
    max_channels = Column(Integer, default=5)
    auto_post_enabled = Column(Boolean, default=True)
    used_activation_count = Column(Integer, default=0)
    max_activations = Column(Integer, default=1)  # How many times key can be used


class User(Base):
    """User model for tracking registered users."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    license_key = Column(String(64), nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_premium = Column(Boolean, default=False)


class Payment(Base):
    """Payment records."""
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='USD')
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(128), unique=True, nullable=True)
    status = Column(String(20), default='pending')  # pending, completed, failed, refunded
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    notes = Column(String(500), nullable=True)


class UserLog(Base):
    """User activity logs for tracking interactions and future subscriptions."""
    __tablename__ = 'user_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    action = Column(String(50), nullable=False)  # purchase_intent, payment_method_selected, support_contacted, etc.
    plan_type = Column(String(20), nullable=True)  # standard, premium, lifetime
    payment_method = Column(String(50), nullable=True)  # btc, eth, usdt, paypal
    details = Column(String(500), nullable=True)  # Additional JSON or text data
    created_at = Column(DateTime, default=datetime.utcnow)


class PaymentCredential(Base):
    """User saved payment credentials/preferences for future subscriptions."""
    __tablename__ = 'payment_credentials'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)

    # Payment method type
    payment_method = Column(String(50), nullable=False)  # btc, eth, usdt, paypal, card

    # Crypto wallet addresses (user's wallet for refunds/payment tracking)
    btc_address = Column(String(128), nullable=True)
    eth_address = Column(String(128), nullable=True)
    usdt_address = Column(String(128), nullable=True)

    # Traditional payment
    paypal_email = Column(String(128), nullable=True)
    card_last_four = Column(String(4), nullable=True)  # Only last 4 digits for security

    # Payment preferences
    preferred_method = Column(String(50), nullable=True)  # User's preferred payment method
    is_default = Column(Boolean, default=False)  # Is this the default payment method

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(String(500), nullable=True)  # Additional info like "business account"


class PaymentProof(Base):
    """Payment proof submissions from users."""
    __tablename__ = 'payment_proofs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)

    # Payment details
    plan_type = Column(String(20), nullable=True)  # standard, premium, lifetime
    payment_method = Column(String(50), nullable=False)  # btc, eth, usdt, paypal
    amount_sent = Column(String(50), nullable=True)  # Amount user claims to have sent
    to_address = Column(String(128), nullable=False)  # Address sent to (e.g., ETH address)
    transaction_id = Column(String(256), nullable=True)  # TXID or transaction hash
    from_address = Column(String(128), nullable=True)  # User's sending address (optional)

    # Proof details
    screenshot_path = Column(String(500), nullable=True)  # Path to saved screenshot file_id
    message_text = Column(String(1000), nullable=True)  # Additional message from user

    # Status
    status = Column(String(20), default='pending')  # pending, verified, rejected
    verified_by = Column(Integer, nullable=True)  # Admin ID who verified
    verified_at = Column(DateTime, nullable=True)
    notes = Column(String(500), nullable=True)  # Admin notes

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Database:
    """Database manager."""

    def __init__(self, db_path='bot_database.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    # License operations
    def generate_license_key(self, plan_type='standard', duration_days=30, max_activations=1):
        """Generate a new license key."""
        # Generate random key
        key = secrets.token_urlsafe(32)[:32].upper()
        # Format: XXXX-XXXX-XXXX-XXXX
        formatted_key = '-'.join([key[i:i+4] for i in range(0, 16, 4)])

        # Hash for storage
        key_hash = hashlib.sha256(formatted_key.encode()).hexdigest()

        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(days=duration_days) if duration_days else None

        # Set max channels based on plan
        max_channels = {
            'standard': 5,
            'premium': 15,
            'lifetime': 50
        }.get(plan_type, 5)

        license = License(
            license_key=formatted_key,
            key_hash=key_hash,
            plan_type=plan_type,
            expires_at=expires_at,
            max_channels=max_channels,
            max_activations=max_activations
        )

        self.session.add(license)
        self.session.commit()

        return formatted_key

    def verify_license_key(self, key):
        """Verify if a license key is valid."""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        license = self.session.query(License).filter_by(key_hash=key_hash).first()

        if not license:
            return None, "Invalid license key."

        if license.status == 'revoked':
            return None, "This license has been revoked."

        if license.status == 'expired':
            return None, "This license has expired."

        if license.expires_at and license.expires_at < datetime.utcnow():
            license.status = 'expired'
            self.session.commit()
            return None, "This license has expired."

        if license.used_activation_count >= license.max_activations:
            return None, "This license has reached maximum activations."

        return license, "Valid license."

    def activate_license(self, key, user_id, username, device_fingerprint=None):
        """Activate a license for a user."""
        license, message = self.verify_license_key(key)

        if not license:
            return False, message

        if license.status == 'active' and license.user_id != user_id:
            return False, "This license is already activated on another account."

        license.status = 'active'
        license.user_id = user_id
        license.username = username
        license.activated_at = datetime.utcnow()
        license.used_activation_count += 1
        if device_fingerprint:
            license.device_fingerprint = device_fingerprint

        self.session.commit()
        return True, "License activated successfully!"

    def get_user_license(self, user_id):
        """Get active license for a user."""
        return self.session.query(License).filter_by(
            user_id=user_id,
            status='active'
        ).first()

    def revoke_license(self, key):
        """Revoke a license key."""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        license = self.session.query(License).filter_by(key_hash=key_hash).first()

        if license:
            license.status = 'revoked'
            self.session.commit()
            return True
        return False

    def get_all_licenses(self, status=None):
        """Get all licenses, optionally filtered by status."""
        query = self.session.query(License)
        if status:
            query = query.filter_by(status=status)
        return query.all()

    def get_license_by_key(self, key):
        """Get license by key (exact match)."""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.session.query(License).filter_by(key_hash=key_hash).first()

    # User operations
    def get_or_create_user(self, telegram_id, username=None, first_name=None):
        """Get existing user or create new one."""
        user = self.session.query(User).filter_by(telegram_id=telegram_id).first()

        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name
            )
            self.session.add(user)
            self.session.commit()
        else:
            user.last_active = datetime.utcnow()
            if username:
                user.username = username
            if first_name:
                user.first_name = first_name
            self.session.commit()

        return user

    def has_active_license(self, user_id):
        """Check if user has an active license."""
        license = self.get_user_license(user_id)
        if not license:
            return False

        if license.expires_at and license.expires_at < datetime.utcnow():
            license.status = 'expired'
            self.session.commit()
            return False

        return True

    def get_license_info(self, user_id):
        """Get detailed license info for a user."""
        license = self.get_user_license(user_id)
        if not license:
            return None

        days_left = None
        if license.expires_at:
            days_left = (license.expires_at - datetime.utcnow()).days

        return {
            'key': license.license_key[:12] + '****',  # Masked
            'plan': license.plan_type,
            'status': license.status,
            'activated_at': license.activated_at,
            'expires_at': license.expires_at,
            'days_left': days_left,
            'max_channels': license.max_channels,
            'auto_post': license.auto_post_enabled
        }

    # Payment operations
    def create_payment_record(self, user_id, amount, currency='USD', payment_method=None, notes=None):
        """Create a payment record."""
        payment = Payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            notes=notes
        )
        self.session.add(payment)
        self.session.commit()
        return payment.id

    def verify_payment(self, payment_id, transaction_id):
        """Mark payment as verified."""
        payment = self.session.query(Payment).filter_by(id=payment_id).first()
        if payment:
            payment.status = 'completed'
            payment.transaction_id = transaction_id
            payment.verified_at = datetime.utcnow()
            self.session.commit()
            return True
        return False

    # User logging operations
    def log_user_action(self, user_id, username=None, first_name=None, action=None, plan_type=None, payment_method=None, details=None):
        """Log a user action for tracking and future subscriptions."""
        log_entry = UserLog(
            user_id=user_id,
            username=username,
            first_name=first_name,
            action=action,
            plan_type=plan_type,
            payment_method=payment_method,
            details=details
        )
        self.session.add(log_entry)
        self.session.commit()
        return log_entry.id

    def get_user_logs(self, user_id, action=None, limit=100):
        """Get user activity logs, optionally filtered by action."""
        query = self.session.query(UserLog).filter_by(user_id=user_id)
        if action:
            query = query.filter_by(action=action)
        return query.order_by(UserLog.created_at.desc()).limit(limit).all()

    def get_users_with_purchase_intent(self, days=30):
        """Get users who showed purchase intent but haven't bought yet."""
        since = datetime.utcnow() - timedelta(days=days)
        # Get users with purchase_intent logs but no active license
        subquery = self.session.query(UserLog.user_id).filter(
            UserLog.action == 'purchase_intent',
            UserLog.created_at >= since
        ).subquery()

        users_with_license = self.session.query(License.user_id).filter(
            License.status == 'active'
        ).subquery()

        potential_customers = self.session.query(UserLog).filter(
            UserLog.user_id.in_(subquery),
            ~UserLog.user_id.in_(users_with_license)
        ).order_by(UserLog.created_at.desc()).all()

        return potential_customers

    def get_user_payment_preferences(self, user_id):
        """Get user's preferred payment methods from logs."""
        logs = self.session.query(UserLog).filter(
            UserLog.user_id == user_id,
            UserLog.payment_method.isnot(None)
        ).order_by(UserLog.created_at.desc()).all()

        return [log.payment_method for log in logs if log.payment_method]

    # Payment credentials operations
    def save_payment_credential(self, user_id, payment_method, **kwargs):
        """Save or update user payment credential.

        Args:
            user_id: Telegram user ID
            payment_method: 'btc', 'eth', 'usdt', 'paypal', 'card'
            **kwargs: btc_address, eth_address, usdt_address, paypal_email, card_last_four, notes
        """
        # Check if credential already exists for this user and method
        credential = self.session.query(PaymentCredential).filter_by(
            user_id=user_id,
            payment_method=payment_method
        ).first()

        if credential:
            # Update existing
            if 'btc_address' in kwargs and kwargs['btc_address']:
                credential.btc_address = kwargs['btc_address']
            if 'eth_address' in kwargs and kwargs['eth_address']:
                credential.eth_address = kwargs['eth_address']
            if 'usdt_address' in kwargs and kwargs['usdt_address']:
                credential.usdt_address = kwargs['usdt_address']
            if 'paypal_email' in kwargs and kwargs['paypal_email']:
                credential.paypal_email = kwargs['paypal_email']
            if 'card_last_four' in kwargs and kwargs['card_last_four']:
                credential.card_last_four = kwargs['card_last_four']
            if 'notes' in kwargs:
                credential.notes = kwargs['notes']
            if 'is_default' in kwargs:
                credential.is_default = kwargs['is_default']
            credential.updated_at = datetime.utcnow()
        else:
            # Create new
            credential = PaymentCredential(
                user_id=user_id,
                username=kwargs.get('username'),
                first_name=kwargs.get('first_name'),
                payment_method=payment_method,
                btc_address=kwargs.get('btc_address'),
                eth_address=kwargs.get('eth_address'),
                usdt_address=kwargs.get('usdt_address'),
                paypal_email=kwargs.get('paypal_email'),
                card_last_four=kwargs.get('card_last_four'),
                preferred_method=payment_method,
                is_default=kwargs.get('is_default', False),
                notes=kwargs.get('notes')
            )
            self.session.add(credential)

        self.session.commit()
        return credential.id

    def get_user_payment_credentials(self, user_id):
        """Get all saved payment credentials for a user."""
        return self.session.query(PaymentCredential).filter_by(user_id=user_id).all()

    def get_default_payment_method(self, user_id):
        """Get user's default payment method."""
        credential = self.session.query(PaymentCredential).filter_by(
            user_id=user_id,
            is_default=True
        ).first()

        if not credential:
            # Return first saved method if no default
            credential = self.session.query(PaymentCredential).filter_by(
                user_id=user_id
            ).first()

        return credential

    def get_payment_credential_by_method(self, user_id, payment_method):
        """Get specific payment credential by method."""
        return self.session.query(PaymentCredential).filter_by(
            user_id=user_id,
            payment_method=payment_method
        ).first()

    def delete_payment_credential(self, credential_id):
        """Delete a payment credential."""
        credential = self.session.query(PaymentCredential).filter_by(id=credential_id).first()
        if credential:
            self.session.delete(credential)
            self.session.commit()
            return True
        return False

    def set_default_payment_method(self, user_id, payment_method):
        """Set a payment method as default for user."""
        # Clear existing default
        self.session.query(PaymentCredential).filter_by(
            user_id=user_id,
            is_default=True
        ).update({'is_default': False})

        # Set new default
        credential = self.session.query(PaymentCredential).filter_by(
            user_id=user_id,
            payment_method=payment_method
        ).first()

        if credential:
            credential.is_default = True
            credential.preferred_method = payment_method
            self.session.commit()
            return True
        return False

    # Payment proof operations
    def save_payment_proof(self, user_id, username, first_name, payment_method, to_address,
                           plan_type=None, amount_sent=None, transaction_id=None,
                           from_address=None, screenshot_path=None, message_text=None):
        """Save a payment proof submission.

        Args:
            user_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            payment_method: 'btc', 'eth', 'usdt', 'paypal'
            to_address: The address payment was sent to
            plan_type: Optional plan they purchased
            amount_sent: Optional amount claimed
            transaction_id: TXID or transaction hash
            from_address: User's sending wallet address
            screenshot_path: Telegram file_id of screenshot
            message_text: Additional message from user
        """
        proof = PaymentProof(
            user_id=user_id,
            username=username,
            first_name=first_name,
            payment_method=payment_method,
            to_address=to_address,
            plan_type=plan_type,
            amount_sent=amount_sent,
            transaction_id=transaction_id,
            from_address=from_address,
            screenshot_path=screenshot_path,
            message_text=message_text,
            status='pending'
        )
        self.session.add(proof)
        self.session.commit()
        return proof.id

    def get_payment_proof(self, proof_id):
        """Get a payment proof by ID."""
        return self.session.query(PaymentProof).filter_by(id=proof_id).first()

    def get_user_payment_proofs(self, user_id, status=None):
        """Get all payment proofs for a user, optionally filtered by status."""
        query = self.session.query(PaymentProof).filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(PaymentProof.created_at.desc()).all()

    def get_pending_payment_proofs(self):
        """Get all pending payment proofs for admin review."""
        return self.session.query(PaymentProof).filter_by(status='pending').order_by(
            PaymentProof.created_at.desc()
        ).all()

    def verify_payment_proof(self, proof_id, admin_id, notes=None):
        """Mark a payment proof as verified."""
        proof = self.session.query(PaymentProof).filter_by(id=proof_id).first()
        if proof:
            proof.status = 'verified'
            proof.verified_by = admin_id
            proof.verified_at = datetime.utcnow()
            if notes:
                proof.notes = notes
            self.session.commit()
            return True
        return False

    def reject_payment_proof(self, proof_id, admin_id, notes=None):
        """Reject a payment proof."""
        proof = self.session.query(PaymentProof).filter_by(id=proof_id).first()
        if proof:
            proof.status = 'rejected'
            proof.verified_by = admin_id
            proof.verified_at = datetime.utcnow()
            if notes:
                proof.notes = notes
            self.session.commit()
            return True
        return False

    def get_payment_stats(self, days=30):
        """Get payment proof statistics."""
        since = datetime.utcnow() - timedelta(days=days)

        total = self.session.query(PaymentProof).filter(PaymentProof.created_at >= since).count()
        pending = self.session.query(PaymentProof).filter(
            PaymentProof.created_at >= since,
            PaymentProof.status == 'pending'
        ).count()
        verified = self.session.query(PaymentProof).filter(
            PaymentProof.created_at >= since,
            PaymentProof.status == 'verified'
        ).count()
        rejected = self.session.query(PaymentProof).filter(
            PaymentProof.created_at >= since,
            PaymentProof.status == 'rejected'
        ).count()

        return {
            'total': total,
            'pending': pending,
            'verified': verified,
            'rejected': rejected
        }

    def close(self):
        """Close database connection."""
        self.session.close()
