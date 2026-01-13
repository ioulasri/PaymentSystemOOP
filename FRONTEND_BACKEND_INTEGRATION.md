# 🚀 Frontend & Backend Integration Guide

## 📋 Technology Stack

### **Frontend**
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand + React Query
- **Forms**: React Hook Form + Zod

### **Backend API**
- **Framework**: FastAPI
- **Database**: PostgreSQL (existing)
- **Models**: Keep existing OOP models (no ORM, raw SQL with psycopg)
- **Authentication**: JWT tokens

---

## 🏗️ Project Structure

```
PaymentSystemOOP/
├── backend/                    # Rename/organize existing src/
│   ├── api/                   # NEW: FastAPI routes
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── dependencies.py   # Auth, DB deps
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py       # Login, register, JWT
│   │       ├── users.py      # User management
│   │       ├── orders.py     # Order endpoints
│   │       ├── items.py      # Product catalog
│   │       └── payments.py   # Payment processing
│   ├── schemas/              # NEW: Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── order.py
│   │   ├── item.py
│   │   └── payment.py
│   └── src/                  # EXISTING: Your models
│       ├── models/           # Customer, Order, Item, etc.
│       ├── services/         # PaymentProcessor, Factory
│       ├── repositories/     # DB operations
│       └── utils/
│
├── frontend/                  # NEW: Next.js application
│   ├── public/
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   ├── dashboard/
│   │   │   ├── orders/
│   │   │   ├── checkout/
│   │   │   └── admin/
│   │   ├── components/
│   │   │   ├── ui/           # shadcn components
│   │   │   ├── layout/
│   │   │   ├── forms/
│   │   │   └── payment/
│   │   ├── lib/
│   │   │   ├── api.ts        # Axios config
│   │   │   ├── auth.ts
│   │   │   └── utils.ts
│   │   ├── hooks/
│   │   ├── store/            # Zustand stores
│   │   ├── types/            # TypeScript types
│   │   └── styles/
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   └── tailwind.config.ts
│
├── database/
├── tests/
└── README.md
```

---

## 🔧 Backend Setup - FastAPI Integration

### **1. Install FastAPI Dependencies**

```bash
# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install fastapi uvicorn[standard] pydantic "python-jose[cryptography]" "passlib[bcrypt]" python-multipart "pydantic[email]"
```

**Or update requirements.txt:**
```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic[email]>=2.5.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
```

Then install:
```bash
pip install -r requirements.txt
```

### **2. Create FastAPI Application**

**`backend/api/main.py`**

```python
"""
FastAPI application entry point.
Integrates with existing Payment System OOP models.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api.routes import auth, users, orders, items, payments
from src.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Starting Payment System API")
    yield
    logger.info("Shutting down Payment System API")


app = FastAPI(
    title="Payment System API",
    version="1.0.0",
    description="RESTful API for OOP Payment System",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",
        "https://yourdomain.com"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])


@app.get("/")
async def root():
    """API health check."""
    return {
        "message": "Payment System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
```

### **3. Pydantic Schemas (API Request/Response)**

> **Important**: Pydantic schemas are for **API validation only**. They convert between JSON and your existing OOP models.

**`backend/schemas/user.py`**

```python
"""
Pydantic schemas for User API endpoints.
These schemas validate API requests/responses and convert to/from existing models.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Import your existing models
from src.models.customer import Customer
from src.models.admin import Admin


class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration (API input)."""
    password: str = Field(..., min_length=8, max_length=100)
    role: Optional[str] = "customer"  # customer or admin


class UserLogin(BaseModel):
    """Schema for user login (API input)."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response (API output - public data only)."""
    id: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

    @staticmethod
    def from_customer(customer: Customer) -> "UserResponse":
        """Convert Customer model to API response."""
        return UserResponse(
            id=customer._user_id,
            username=customer._name,
            email=customer.email,
            role="customer",
            is_active=True,
            created_at=datetime.utcnow()  # TODO: Get from DB
        )

    @staticmethod
    def from_admin(admin: Admin) -> "UserResponse":
        """Convert Admin model to API response."""
        return UserResponse(
            id=admin._user_id,
            username=admin._name,
            email=admin.email,
            role="admin",
            is_active=True,
            created_at=datetime.utcnow()  # TODO: Get from DB
        )


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

**`backend/schemas/order.py`**

```python
"""
Pydantic schemas for Order API endpoints.
Converts between API JSON and your existing Order/Item models.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# Import your existing models
from src.models.order import Order
from src.models.item import Item


class ItemInOrder(BaseModel):
    """Item within an order (API representation)."""
    item_id: str
    name: str
    price: Decimal
    quantity: int = 1

    @staticmethod
    def from_item(item: Item, quantity: int = 1) -> "ItemInOrder":
        """Convert Item model to API response."""
        return ItemInOrder(
            item_id=item.item_id,
            name=item.name,
            price=Decimal(str(item.price)),
            quantity=quantity
        )


class OrderCreate(BaseModel):
    """Schema for creating an order (API input)."""
    items: List[ItemInOrder] = Field(..., min_items=1)


class OrderUpdate(BaseModel):
    """Schema for updating order status (API input)."""
    status: str = Field(..., pattern="^(pending|processing|completed|cancelled)$")


class OrderResponse(BaseModel):
    """Schema for order response (API output)."""
    order_id: str
    customer_id: str
    customer_name: str
    customer_email: str
    items: List[ItemInOrder]
    total_amount: Decimal
    status: str
    created_at: datetime
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None

    class Config:
        from_attributes = True

    @staticmethod
    def from_order(order: Order) -> "OrderResponse":
        """Convert Order model to API response."""
        return OrderResponse(
            order_id=order.order_id,
            customer_id=order.customer._user_id,
            customer_name=order.customer._name,
            customer_email=order.customer.email,
            items=[ItemInOrder.from_item(item) for item in order.items],
            total_amount=Decimal(str(order.total_amount)),
            status=order.status,
            created_at=order.created_at,
            payment_method=order.payment_method,
            transaction_id=order.transaction_id
        )
```

**`backend/schemas/payment.py`**

```python
"""
Pydantic schemas for Payment API endpoints.
Validates API input and converts to PaymentFactory parameters.
Uses your existing PaymentFactory, PaymentProcessor, and payment method classes.
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Union
from decimal import Decimal

# Your existing payment classes are used by the routes
# from src.payment.methods.credit_card import CreditCardPayment
# from src.payment.methods.paypal import PayPalPayment
# from src.payment.methods.crypto import CryptoPayment
# from src.services.payment_factory import PaymentFactory


class CreditCardPaymentInput(BaseModel):
    """Credit card payment details (API input)."""
    payment_type: Literal["credit_card"] = "credit_card"
    cardholder: str = Field(..., min_length=3)
    cardnumber: str = Field(..., pattern=r"^\d{13,19}$")
    expirationdate: str = Field(..., pattern=r"^\d{2}-\d{2}$")  # MM-YY
    cvv: str = Field(..., pattern=r"^\d{3,4}$")


class PayPalPaymentInput(BaseModel):
    """PayPal payment details (API input)."""
    payment_type: Literal["paypal"] = "paypal"
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str = Field(..., min_length=6)


class CryptoPaymentInput(BaseModel):
    """Cryptocurrency payment details (API input)."""
    payment_type: Literal["crypto"] = "crypto"
    wallet_address: str = Field(..., min_length=26, max_length=62)
    crypto_type: Literal["BTC", "ETH", "USDT"] = "BTC"


class PaymentRequest(BaseModel):
    """Payment processing request (API input)."""
    order_id: str
    payment_details: Union[CreditCardPaymentInput, PayPalPaymentInput, CryptoPaymentInput] = Field(..., discriminator='payment_type')


class PaymentResponse(BaseModel):
    """Payment processing response (API output)."""
    success: bool
    transaction_id: str
    amount: Decimal
    payment_method: str
    card_number: Optional[str] = None
    status: str
    message: str

    @staticmethod
    def from_receipt(receipt: dict) -> "PaymentResponse":
        """
        Convert receipt from PaymentProcessor.process_payment() to API response.
        
        Your existing PaymentProcessor returns a dict with:
        - TransactionID
        - Amount
        - PaymentMethod
        - CardNumber (optional)
        - Transaction status
        """
        return PaymentResponse(
            success=receipt.get("Transaction status") == "completed",
            transaction_id=receipt.get("TransactionID", ""),
            amount=Decimal(str(receipt.get("Amount", 0))),
            payment_method=receipt.get("PaymentMethod", ""),
            card_number=receipt.get("CardNumber"),
            status=receipt.get("Transaction status", "failed"),
            message="Payment processed successfully" if receipt.get("Transaction status") == "completed" else "Payment failed"
        )
```

**`backend/schemas/item.py`**

```python
"""
Pydantic schemas for Item API endpoints.
Converts between API JSON and your existing Item model.
"""

from pydantic import BaseModel, Field
from decimal import Decimal

# Import your existing model
from src.models.item import Item


class ItemCreate(BaseModel):
    """Schema for creating an item (API input)."""
    name: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    description: str = ""


class ItemUpdate(BaseModel):
    """Schema for updating an item (API input)."""
    name: str | None = None
    price: Decimal | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    description: str | None = None


class ItemResponse(BaseModel):
    """Schema for item response (API output)."""
    item_id: str
    name: str
    price: Decimal
    stock: int
    description: str

    class Config:
        from_attributes = True

    @staticmethod
    def from_item(item: Item) -> "ItemResponse":
        """Convert Item model to API response."""
        return ItemResponse(
            item_id=item.item_id,
            name=item.name,
            price=Decimal(str(item.price)),
            stock=item.stock,
            description=getattr(item, 'description', '')  # If description exists
        )

    def to_item(self) -> Item:
        """Convert API input to Item model."""
        item = Item(self.name)
        item.price = float(self.price)
        item.stock = self.stock
        if hasattr(item, 'description'):
            item.description = self.description
        return item
```

### **4. FastAPI Routes (Using Your Models)**

> **Key Point**: Routes use Pydantic schemas for API validation, then work with your existing OOP models.

**`backend/api/routes/auth.py`**

```python
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

from backend.schemas.user import UserCreate, UserLogin, UserResponse, Token
from src.models.customer import Customer  # YOUR existing model
from src.models.admin import Admin  # YOUR existing model
# from src.repositories.base_repository import UserRepository  # TODO: Implement

router = APIRouter()

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
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user using YOUR existing models
        if user_data.role == "admin":
            user = Admin(user_data.username, user_data.email)  # YOUR Admin model
        else:
            user = Customer(user_data.username, user_data.email)  # YOUR Customer model
        
        # TODO: Save to database with UserRepository
        # user_repo = UserRepository()
        # user_repo.create(user, hashed_password)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.email, "role": user_data.role},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Convert YOUR model to API response using schema helper
        if user_data.role == "admin":
            user_response = UserResponse.from_admin(user)
        else:
            user_response = UserResponse.from_customer(user)
        
        return Token(access_token=access_token, user=user_response)
        
    except Exception as e:
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
```

**`backend/api/routes/orders.py`**

```python
"""
Order management routes.
Uses your existing Order and Item models.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from backend.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from backend.api.routes.auth import get_current_user
from src.models.customer import Customer  # YOUR existing model
from src.models.order import Order  # YOUR existing model
from src.models.item import Item  # YOUR existing model

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new order.
    
    - Requires authentication
    - Creates order with items
    - Returns order details
    """
    try:
        # Create customer using YOUR existing Customer model
        customer = Customer(current_user["email"], current_user["email"])
        
        # Create order using YOUR existing Order model
        order = Order(customer=customer)
        
        # Add items to order using YOUR existing Item model
        for item_data in order_data.items:
            item = Item(item_data.name)
            item.price = float(item_data.price)
            item.stock = item_data.quantity
            # YOUR Order model's add_item method
            order.add_item(item, quantity=item_data.quantity)
        
        # TODO: Save to database
        # order_repo = OrderRepository()
        # order_repo.save(order)
        
        # Convert YOUR Order model to API response using schema helper
        return OrderResponse.from_order(order)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order creation failed: {str(e)}"
        )


@router.get("/", response_model=List[OrderResponse])
async def get_orders(current_user: dict = Depends(get_current_user)):
    """
    Get all orders for current user.
    
    - Returns user's order history
    """
    # TODO: Fetch from database filtered by user
    return []


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get order by ID."""
    # TODO: Fetch from database and verify ownership
    raise HTTPException(status_code=404, detail="Order not found")


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    update_data: OrderUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update order status (admin only)."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # TODO: Update in database
    raise HTTPException(status_code=404, detail="Order not found")
```

**`backend/api/routes/payments.py`**

```python
"""
Payment processing routes.
Uses your existing PaymentFactory, PaymentProcessor, and payment method classes.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.schemas.payment import PaymentRequest, PaymentResponse
from backend.api.routes.auth import get_current_user
from src.services.payment_factory import PaymentFactory  # YOUR existing factory
from src.services.payment_processor import PaymentProcessor  # YOUR existing processor
from src.models.customer import Customer  # YOUR existing model

router = APIRouter()


@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    payment_data: PaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Process a payment for an order.
    
    - Validates payment details
    - Uses existing PaymentFactory and PaymentProcessor
    - Returns transaction receipt
    """
    try:
        # TODO: Fetch order from database
        # order_repo = OrderRepository()
        # order = order_repo.get(payment_data.order_id)
        
        # Create customer using YOUR existing Customer model
        customer = Customer(current_user["email"], current_user["email"])
        
        # Create payment method using YOUR existing PaymentFactory
        payment_details = payment_data.payment_details
        
        if payment_details.payment_type == "credit_card":
            payment_method = PaymentFactory.create(
                "credit_card",
                cardholder=payment_details.cardholder,
                cardnumber=payment_details.cardnumber,
                expirationdate=payment_details.expirationdate,
                cvv=payment_details.cvv,
                balance=10000.00  # TODO: Get from database
            )
        elif payment_details.payment_type == "paypal":
            payment_method = PaymentFactory.create(
                "paypal",
                email=payment_details.email,
                password=payment_details.password,
                balance=10000.00  # TODO: Get from database
            )
        elif payment_details.payment_type == "crypto":
            payment_method = PaymentFactory.create(
                "crypto",
                wallet_address=payment_details.wallet_address,
                crypto_type=payment_details.crypto_type,
                balance=10.0  # TODO: Get from database
            )
        else:
            raise ValueError("Invalid payment type")
        
        # Process with YOUR existing PaymentProcessor
        # receipt = PaymentProcessor.process_payment(customer, order, payment_method)
        # return PaymentResponse.from_receipt(receipt)
        
        # For now, mock response until order is fetched from DB
        mock_receipt = {
            "TransactionID": "TXN-MOCK-12345",
            "Amount": 100.00,
            "PaymentMethod": payment_details.payment_type,
            "CardNumber": getattr(payment_details, 'cardnumber', None),
            "Transaction status": "completed"
        }
        return PaymentResponse.from_receipt(mock_receipt)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment processing failed: {str(e)}"
        )
```

### **5. Run FastAPI Server**

We've created a convenient startup script that handles all the path setup:

**`run_backend.py`** (already created in project root)

```python
#!/usr/bin/env python3
"""
Startup script for FastAPI backend.
Sets up Python path before starting uvicorn.
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path so both 'api' and 'src' modules are found
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set PYTHONPATH environment variable for subprocesses
os.environ['PYTHONPATH'] = str(backend_dir)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        reload_dirs=[str(backend_dir)]
    )
```

**Run the server:**

```bash
# Make sure you're in the project root and venv is activated
source venv/bin/activate

# Run the backend
python run_backend.py
```

**Access the API:**
- **Swagger UI (Interactive API Docs)**: http://localhost:8000/docs
- **ReDoc (Alternative Docs)**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health

---

## 🎨 Frontend Setup - Next.js

### **1. Create Next.js Project**

```bash
# From project root
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir

# Options:
# ✔ Would you like to use TypeScript? Yes
# ✔ Would you like to use ESLint? Yes
# ✔ Would you like to use Tailwind CSS? Yes
# ✔ Would you like to use `src/` directory? Yes
# ✔ Would you like to use App Router? Yes
# ✔ Would you like to customize the default import alias? No

cd frontend
```

### **2. Install Dependencies**

```bash
npm install axios
npm install zustand
npm install @tanstack/react-query
npm install react-hook-form
npm install zod
npm install react-hot-toast
npm install lucide-react  # Icons

# shadcn/ui (optional but recommended)
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input card form
```

### **3. Configure Environment Variables**

**`frontend/.env.local`**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME=Payment System
```

### **4. API Client Setup**

**`frontend/src/lib/api.ts`**

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired, redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### **5. TypeScript Types**

**`frontend/src/types/index.ts`**

```typescript
// Match backend Pydantic schemas

export interface User {
  id: string;
  username: string;
  email: string;
  role: 'customer' | 'admin';
  is_active: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Item {
  item_id: string;
  name: string;
  price: number;
  stock: number;
  description?: string;
}

export interface ItemInOrder {
  item_id: string;
  name: string;
  price: number;
  quantity: number;
}

export interface Order {
  order_id: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
  items: ItemInOrder[];
  total_amount: number;
  status: 'pending' | 'processing' | 'completed' | 'cancelled';
  created_at: string;
  payment_method?: string;
  transaction_id?: string;
}

export interface PaymentMethod {
  payment_type: 'credit_card' | 'paypal' | 'crypto';
}

export interface CreditCardPayment extends PaymentMethod {
  payment_type: 'credit_card';
  cardholder: string;
  cardnumber: string;
  expirationdate: string;
  cvv: string;
}

export interface PayPalPayment extends PaymentMethod {
  payment_type: 'paypal';
  email: string;
  password: string;
}

export interface CryptoPayment extends PaymentMethod {
  payment_type: 'crypto';
  wallet_address: string;
  crypto_type: 'BTC' | 'ETH' | 'USDT';
}

export interface PaymentRequest {
  order_id: string;
  payment_details: CreditCardPayment | PayPalPayment | CryptoPayment;
}

export interface PaymentResponse {
  success: boolean;
  transaction_id: string;
  amount: number;
  payment_method: string;
  card_number?: string;
  status: string;
  message: string;
}
```

### **6. API Services**

**`frontend/src/lib/services/auth.ts`**

```typescript
import api from '../api';
import { Token } from '@/types';

export const authService = {
  async login(email: string, password: string): Promise<Token> {
    const response = await api.post<Token>('/auth/login', { email, password });
    localStorage.setItem('access_token', response.data.access_token);
    return response.data;
  },

  async register(username: string, email: string, password: string): Promise<Token> {
    const response = await api.post<Token>('/auth/register', {
      username,
      email,
      password,
      role: 'customer',
    });
    localStorage.setItem('access_token', response.data.access_token);
    return response.data;
  },

  logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  },
};
```

**`frontend/src/lib/services/orders.ts`**

```typescript
import api from '../api';
import { Order } from '@/types';

export const orderService = {
  async getOrders(): Promise<Order[]> {
    const response = await api.get<Order[]>('/orders');
    return response.data;
  },

  async getOrder(orderId: string): Promise<Order> {
    const response = await api.get<Order>(`/orders/${orderId}`);
    return response.data;
  },

  async createOrder(items: Array<{ item_id: string; name: string; price: number; quantity: number }>): Promise<Order> {
    const response = await api.post<Order>('/orders', { items });
    return response.data;
  },
};
```

**`frontend/src/lib/services/payments.ts`**

```typescript
import api from '../api';
import { PaymentRequest, PaymentResponse } from '@/types';

export const paymentService = {
  async processPayment(paymentData: PaymentRequest): Promise<PaymentResponse> {
    const response = await api.post<PaymentResponse>('/payments/process', paymentData);
    return response.data;
  },
};
```

### **7. Example Page - Login**

**`frontend/src/app/(auth)/login/page.tsx`**

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/services/auth';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await authService.login(email, password);
      toast.success(`Welcome back, ${result.user.username}!`);
      router.push('/dashboard');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-3xl font-bold text-center">Login</h2>
        <form onSubmit={handleSubmit} className="space-y-6">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 border rounded"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border rounded"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            {loading ? 'Loading...' : 'Login'}
          </button>
        </form>
      </div>
   ✅ Current Setup Status

**Completed:**
- ✅ FastAPI backend structure created
- ✅ Pydantic schemas for API validation
- ✅ JWT authentication routes (auth endpoints)
- ✅ Order management routes
- ✅ Payment processing routes
- ✅ Integration with existing OOP models
- ✅ Run script for easy backend startup
- ✅ CORS configuration for frontend
- ✅ API documentation (Swagger/ReDoc)

**Project Structure:**
```
PaymentSystemOOP/
├── backend/
│   ├── api/
│   │   ├── main.py           ✅ FastAPI app
│   │   └── routes/
│   │       ├── auth.py       ✅ JWT auth endpoints
│   │       ├── orders.py     ✅ Order CRUD
│   │       ├── payments.py   ✅ Payment processing
│   │       ├── users.py      ✅ User management
│   │       └── items.py      ✅ Product catalog
│   ├── schemas/              ✅ Pydantic validation
│   │   ├── user.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   └── item.py
│   └── src/                  ✅ Your existing OOP models
│       ├── models/
│       ├── services/
│       ├── payment/
│       └── utils/
├── run_backend.py            ✅ Backend startup script
├── venv/                     ✅ Virtual environment
└── frontend/                 🔲 To be created
```

---

## 🚀 Next Steps

### **Backend (Immediate)**
1. **Database Integration**: Connect routes to PostgreSQL
   - Implement UserRepository for user CRUD
   - Implement OrderRepository for order persistence
   - Add database session management

2. **Authentication Enhancement**:
   - Store hashed passwords in database
   - Implement refresh tokens
   - Add role-based access control

3. **API Testing**:
   - Test all endpoints via Swagger UI
   - Add pytest tests for API routes
   - Integration tests with database

### **Frontend (Next Phase)**
1. **Initialize Next.js Project**:
   ```bash
## 🛠️ Quick Start Guide

### **Backend Only (Current)**

```bash
# 1. Navigate to project
cd PaymentSystemOOP

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies (if not done)
pip install fastapi uvicorn[standard] pydantic[email] python-jose[cryptography] passlib[bcrypt] python-multipart

# 4. Run backend
python run_backend.py
```

**Test the API:**
- Open http://localhost:8000/docs in your browser
- Try the `/` endpoint to see API info
- Test `/health` endpoint
- Explore authentication endpoints under `/api/auth`

### **Full Stack (After Frontend Setup)**

**Terminal 1 - Backend:**
```bash
cd PaymentSystemOOP
source venv/bin/activate
python run_backend.py
```

**Terminal 2 - Frontend:**
```bash
cd PaymentSystemOOP/frontend
npm run dev
```

---

## 📝 Important Notes

### **Module Import Structure**
The backend runs from the `backend/` directory, so imports use:
- `from src.models.customer import Customer` (your existing models)
- `from api.routes.auth import router` (FastAPI routes)
- `from schemas.user import UserCreate` (Pydantic schemas)

This structure allows your existing `src/` code to work without modifications while adding FastAPI on top.

### **Troubleshooting**

**Issue: `ModuleNotFoundError: No module named 'jose'`**
```bash
pip install python-jose[cryptography]
```

**Issue: `email-validator is not installed`**
```bash
pip install pydantic[email]
```

**Issue: `ModuleNotFoundError: No module named 'src'`**
- Make sure you're running `python run_backend.py` from project root
- The script automatically sets up the correct Python path

**Issue: Port 8000 already in use**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or change the port in run_backend.py
```

---

**Created**: January 12, 2026  
**Last Updated**: January 12, 2026  
**Stack**: Next.js 14 + TypeScript + FastAPI + PostgreSQL  
**Status**: ✅ Backend API Running | 🔲 Frontend Pending

2. **Install Frontend Dependencies**:
   ```bash
   cd frontend
   npm install axios zustand @tanstack/react-query react-hook-form zod react-hot-toast
   ```

3. **Build Core Pages**:
   - Login/Register pages
   - Dashboard
   - Checkout flow
   - Order history
   - Admin panel

### **DevOps**
1. Docker containerization (backend + frontend)
2. Update CI/CD for FastAPI + Next.js
3. Environment variable management
4. Production deployment setup

Access at: `http://localhost:3000`

---

## 🔄 Integration Flow

```
Frontend (Next.js)          Backend (FastAPI)           Models (Existing)
     |                            |                            |
     |--- POST /api/auth/login--->|                            |
     |                            |--- Verify credentials ---->|
     |                            |    (Customer/Admin model)  |
     |<--- JWT Token -------------|                            |
     |                            |                            |
     |--- POST /api/orders ------>|                            |
     |                            |--- Create Order ---------->|
     |                            |    (Order model)           |
     |<--- Order Response --------|                            |
     |                            |                            |
     |--- POST /api/payments ---->|                            |
     |                            |--- PaymentFactory -------->|
     |                            |    PaymentProcessor ------>|
     |                            |    (CreditCard/PayPal)     |
     |<--- Payment Receipt -------|                            |
```

---

## 🚀 Next Steps

1. **Backend**: Create database repositories (`UserRepository`, `OrderRepository`)
2. **Backend**: Implement JWT authentication fully
3. **Backend**: Connect FastAPI routes to PostgreSQL
4. **Frontend**: Build remaining pages (checkout, orders, admin)
5. **Frontend**: Add form validation with Zod
6. **Frontend**: Implement state management with Zustand
7. **Testing**: API integration tests
8. **Deployment**: Docker containerization
9. **CI/CD**: Update GitHub Actions for Next.js build

---

## 📝 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **shadcn/ui**: https://ui.shadcn.com/
- **React Query**: https://tanstack.com/query/latest

---

**Created**: January 12, 2026  
**Stack**: Next.js 14 + TypeScript + FastAPI + PostgreSQL
