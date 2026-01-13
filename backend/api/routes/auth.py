"""
Authentication routes (Login, Register, JWT).
Uses your existing Customer and Admin models.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

from schemas.user import UserCreate, UserLogin, UserResponse, Token
from src.models.customer import Customer  # YOUR existing model
from src.models.admin import Admin  # YOUR existing model
from src.utils.logger import get_logger
# from src.repositories.base_repository import UserRepository  # TODO: Implement

router = APIRouter()
logger = get_logger("auth_routes")

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"  # Use env variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user.
    
    - Creates a new customer or admin account
    - Returns JWT token for immediate login
    """
    try:
        logger.info(f"Registration attempt for email: {user_data.email}, role: {user_data.role}")
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        logger.info(f"Password hashed successfully")
        
        # Create user using YOUR existing models
        if user_data.role == "admin":
            user = Admin(user_data.username, user_data.email)  # YOUR Admin model
        else:
            user = Customer(user_data.username, user_data.email)  # YOUR Customer model
        
        logger.info(f"User object created: {user._user_id}")
        
        # TODO: Save to database with UserRepository
        # user_repo = UserRepository()
        # user_repo.create(user, hashed_password)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.email, "role": user_data.role},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(f"Access token created")
        
        # Convert YOUR model to API response using schema helper
        if user_data.role == "admin":
            user_response = UserResponse.from_admin(user)
        else:
            user_response = UserResponse.from_customer(user)
        
        logger.info(f"User response created, returning token")
        
        return Token(access_token=access_token, user=user_response)
        
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """
    Login user and return JWT token.
    
    - Validates credentials
    - Returns access token
    """
    # TODO: Fetch user from database
    # user_repo = UserRepository()
    # user = user_repo.get_by_email(user_data.email)
    
    # For now, mock authentication
    # if not user or not verify_password(user_data.password, user.hashed_password):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect email or password",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    
    # Create mock user for demo
    user = Customer("Demo User", user_data.email)
    
    access_token = create_access_token(
        data={"sub": user.email, "role": "customer"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    user_response = UserResponse.from_customer(user)
    
    return Token(access_token=access_token, user=user_response)


@router.post("/token", response_model=Token)
async def token_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token endpoint."""
    # Reuse login logic
    user_data = UserLogin(email=form_data.username, password=form_data.password)
    return await login(user_data)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    Use this in protected routes.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None:
            raise credentials_exception
        return {"email": email, "role": role}
    except JWTError:
        raise credentials_exception