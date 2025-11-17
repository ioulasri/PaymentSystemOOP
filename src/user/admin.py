"""Administration user model.

This module provides the ``Admin`` concrete user type which extends the
abstract :class:`~src.user.user.User` base class. The implementation is
kept lightweight for tests and local development: it stores permissions,
a review queue and an audit log in memory. Administrative methods such
as approving, rejecting and flagging transactions operate on these
structures and emit simple audit records.

In production you would replace these in-memory stores with persistent
backing stores and tie actions to real transaction services.
"""

from typing import Any, Dict, List, Optional

from .user import User


class Admin(User):
    """Administrator user with elevated privileges.

    Attributes
    ----------
    _user_id : str
        Unique identifier for the admin user.
    _name : str
        Administrator's name.
    _email : str
        Contact email for notifications.
    _permissions : List[str]
        Permission strings describing allowed actions (for example
        ``"approve_transactions"``).
    _review_queue : List[Dict[str, Any]]
        Items pending manual review, typically transaction records.
    _audit_log : List[Dict[str, Any]]
        Historical records of administrative actions; used for
        reporting and auditing.
    """

    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        permissions: Optional[List[str]] = None,
    ):
        super().__init__()
        self._user_id = user_id
        self._name = name
        self._email = email
        self._permissions: List[str] = permissions or []
        self._review_queue: List[Dict[str, Any]] = []
        self._audit_log: List[Dict[str, Any]] = []
        # mark active by default
        self._is_active: bool = True

    def get_user_info(self) -> Dict[str, Any]:
        """Return a serializable mapping with basic admin information."""
        return {
            "id": self._user_id,
            "name": self._name,
            "email": self._email,
            "role": getattr(self, "_role", "admin"),
            "is_active": bool(getattr(self, "_is_active", True)),
            "permissions": list(self._permissions),
        }

    def deactivate(self) -> None:
        """Mark the admin user as inactive."""
        self._is_active = False

    def review_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Return a copy of a transaction in the review queue (or None)."""
        for txn in self._review_queue:
            if txn.get("id") == transaction_id:
                return dict(txn)
        return None

    def approve_transaction(self, transaction_id: str) -> bool:
        """Approve a queued transaction, record it in the audit log, return True on success."""

        for idx, txn in enumerate(self._review_queue):
            if txn.get("id") == transaction_id:
                record = dict(txn)
                record.update({"action": "approved", "handled_by": self._user_id})
                self._audit_log.append(record)
                del self._review_queue[idx]
                return True
        return False

    def reject_transaction(self, transaction_id: str) -> bool:
        """Reject a queued transaction, record it in the audit log, return True on success."""
        for idx, txn in enumerate(self._review_queue):
            if txn.get("id") == transaction_id:
                record = dict(txn)
                record.update({"action": "rejected", "handled_by": self._user_id})
                self._audit_log.append(record)
                del self._review_queue[idx]
                return True
        return False

    def flag_transaction(self, transaction_id: str, reason: str) -> None:
        """Mark a transaction as flagged for review; record reason in audit log."""
        # try to find in review queue first, otherwise create a flagged record
        for txn in self._review_queue:
            if txn.get("id") == transaction_id:
                flagged = dict(txn)
                flagged.update(
                    {
                        "flagged": True,
                        "flag_reason": reason,
                        "flagged_by": self._user_id,
                    }
                )
                self._audit_log.append(flagged)
                return

        self._audit_log.append(
            {
                "id": transaction_id,
                "flagged": True,
                "flag_reason": reason,
                "flagged_by": self._user_id,
            }
        )

    def generate_report(self, filter_params: Dict[str, Any]) -> Dict[str, Any]:
        """Return a simple report filtered from the audit log.

        Supported filter keys: any key present in audit records; records must
        match all provided key/value pairs to be included.
        """
        def matches(rec: Dict[str, Any]) -> bool:
            for k, v in filter_params.items():
                if rec.get(k) != v:
                    return False
            return True

        matched = [dict(r) for r in self._audit_log if matches(r)]
        return {"count": len(matched), "results": matched}

    def view_all_transactions(self) -> List[Dict[str, Any]]:
        """Return a shallow copy of the audit log (transactions visible to admin)."""
        return list(self._audit_log)

    def view_flagged_transactions(self) -> List[Dict[str, Any]]:
        """Return transactions that have been flagged for review."""
        return [dict(r) for r in self._audit_log if r.get("flagged")]

    def has_permission(self, permission: str) -> bool:
        """Return True if the admin has the given permission."""
        return permission in self._permissions