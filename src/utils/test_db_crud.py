# Test script for DB connection and CRUD operations on User model
from src.models.sqlalchemy_models import User, UserRole
from src.utils.db_session import SessionLocal


def test_user_crud() -> None:
    """Test CRUD operations for the User model using SQLAlchemy ORM."""
    session = SessionLocal()
    try:
        # Create
        user = User(
            username="testuser",
            email="testuser@example.com",
            hashed_password="hashedpassword123",
            role=UserRole.CUSTOMER,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"Created User: {user.id}, {user.username}, {user.email}")

        # Read
        fetched = session.query(User).filter_by(username="testuser").first()
        print(f"Fetched User: {fetched.id}, {fetched.username}, {fetched.email}")

        # Update
        fetched.email = "updateduser@example.com"
        session.commit()
        print(f"Updated User Email: {fetched.email}")

        # Delete
        session.delete(fetched)
        session.commit()
        print("User deleted.")
    finally:
        session.close()


if __name__ == "__main__":
    test_user_crud()
