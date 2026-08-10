from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date

# ========== COMPANY ==========

class CompanyBase(BaseModel):
    nome: str
    plano: str = "free"

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: int
    ativo: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== USER ==========

class UserBase(BaseModel):
    email: EmailStr
    role: str = "admin"

class UserCreate(UserBase):
    senha: str = Field(..., min_length=6, max_length=72)

class UserLogin(BaseModel):
    email: EmailStr
    senha: str

class RegisterRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    senha: str = Field(..., min_length=6, max_length=72)

class UserResponse(UserBase):
    id: int
    company_id: int
    ativo: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== CUSTOMER ==========

class CustomerBase(BaseModel):
    nome: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    data_nascimento: Optional[date] = None  # NOVO: para aniversariantes

class CustomerCreate(CustomerBase):
    pass

class PublicCustomerRegistration(CustomerBase):
    token: str = Field(..., min_length=1)
class CustomerUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    data_nascimento: Optional[date] = None
    # Campos de premiação
    valor_gasto_atual: Optional[float] = None
    quantidade_produtos_comprados: Optional[int] = None
    meta_premiacao_valor: Optional[float] = None
    meta_premiacao_quantidade: Optional[int] = None

class CustomerResponse(CustomerBase):
    id: int
    pontos: float
    company_id: int
    ativo: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== POINTS TRANSACTION ==========

class PointsTransactionBase(BaseModel):
    pontos: float = Field(..., gt=0)
    tipo: str  # entrada ou saida
    descricao: Optional[str] = None
    product_id: Optional[int] = None

class PointsTransactionCreate(BaseModel):
    pontos: float = Field(..., gt=0)
    tipo: str  # entrada ou saida
    descricao: Optional[str] = None
    product_id: Optional[int] = None

class PointsTransactionResponse(BaseModel):
    id: int
    customer_id: int
    pontos: float
    tipo: str
    descricao: Optional[str]
    product_id: Optional[int] = None
    product_nome: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== CATEGORY ==========

class CategoryBase(BaseModel):
    nome: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== PRODUCT ==========

class ProductBase(BaseModel):
    nome: str
    preco: float = Field(..., gt=0)
    categoria_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    nome: Optional[str] = None
    preco: Optional[float] = None
    categoria_id: Optional[int] = None

class ProductResponse(ProductBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== PAGINATION ==========

class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: list

# ========== PROMOTION CONFIG ==========

class PromotionConfigBase(BaseModel):
    tipo: str  # "quantidade", "valor", "percentual", "personalizada"
    quantidade_produtos: Optional[int] = None
    pontos_por_quantidade: Optional[float] = None
    valor_gasto: Optional[float] = None
    pontos_por_valor: Optional[float] = None
    percentual: Optional[float] = None
    descricao: Optional[str] = None
    ativo: bool = True

class PromotionConfigCreate(PromotionConfigBase):
    pass

class PromotionConfigUpdate(BaseModel):
    tipo: Optional[str] = None
    quantidade_produtos: Optional[int] = None
    pontos_por_quantidade: Optional[float] = None
    valor_gasto: Optional[float] = None
    pontos_por_valor: Optional[float] = None
    percentual: Optional[float] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None

class PromotionConfigResponse(PromotionConfigBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== WHATSAPP / N8N ==========

class WhatsAppQueueGenerate(BaseModel):
    tipo: str = Field(..., min_length=1, max_length=50)
    mensagem_template: str = Field(..., min_length=1)
    customer_id: Optional[int] = None

class WhatsAppMessageStatusUpdate(BaseModel):
    status: str = Field(..., min_length=1, max_length=30)
    provider_message_id: Optional[str] = None
    erro: Optional[str] = None
