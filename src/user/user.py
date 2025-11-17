"""User base module.

This module defines the abstract `User` base class used by the
application. Concrete user types (for example, `Customer` or `Admin`)
should extend `User` and implement the abstract methods.

Notes
-----
This file intentionally only documents the current, minimal shape of the
base class. It does not change behaviour. If you'd like, I can also
initialize attributes and fix method signatures so the base class is
directly instantiable and correct for subclasses.
"""

from abc import ABC, abstractmethod
from datetime import date


class User(ABC):
    """Abstract base class for all users.

    The class currently declares the common attributes used across user
    implementations and defines the abstract methods that concrete
    subclasses must implement.

    Attributes
    ----------
    _user_id : str
        Identifier for the user. Subclasses are expected to assign a
        concrete value.
    _name : str
        Human-readable name of the user.
    _email : str
        Contact email address.
    _created_at : datetime.date
        Date when the user was created.
    _role : str
        Role name (for example, "customer" or "admin").
    _is_active : bool
        Whether the user account is active.

    Implementation notes
    --------------------
    The current `__init__` only defines the attribute annotations to make
    the intended shape explicit. Concrete subclasses should assign
    appropriate values to these attributes (or you can ask me to change
    the base class to accept parameters and initialize them).
    """

    def __init__(self):
        """Set up attribute annotations for the user instance.

        The base initializer does not populate the attributes with values;
        it is intentionally minimal so subclasses can choose how to
        obtain and assign values (for example, from a database record or
        constructor parameters).
        """
        super().__init__()
        self._user_id: str
        self._name: str 
        self._email: str
        self._created_at: date = date.today()
        self._role: str 
        self._is_active: bool


    @abstractmethod
    def get_user_info() -> dict:
        """Return a mapping containing user information.

        Implementations should return a JSON-serializable dictionary with
        the essential user fields (for example: ``{'id': ..., 'name': ...}``).

        Note: this is intended to be an instance method implemented by
        subclasses; when implementing, include the usual `self` parameter
        (the base signature in this file is kept minimal to avoid
        changing behaviour unexpectedly).
        """
        pass

    @abstractmethod
    def deactivate() -> None:
        """Deactivate the user account.

        Concrete subclasses should implement logic that marks the user as
        inactive (for example, toggling ``_is_active`` and persisting the
        change where appropriate).

        As with ``get_user_info``, this is intended to be an instance
        method; include ``self`` when implementing the method in
        subclasses.
        """
        pass
