from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime, date
from app.utils.cnpj import validate_cnpj_digits

# ========== COMPANY ==========

class CompanyBase(BaseModel):
    nome: str
    plano: str = "free"
    razao_social: Optional[str] = None
    cnpj: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    responsavel: Optional[str] = None
    cep: Optional[str] = None
    endereco: Optional[str] = None
    numero: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    logotipo: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class ManagedCompanyCreate(BaseModel):
    razao_social: str = Field(..., min_length=1, max_length=255)
    nome: str = Field(..., min_length=1, max_length=255)
    cnpj: str = Field(..., min_length=1, max_length=30)
    telefone: str = Field(..., min_length=1, max_length=30)
    email: EmailStr
    responsavel: str = Field(..., min_length=1, max_length=255)
    cep: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = Field(None, max_length=255)
    numero: Optional[str] = Field(None, max_length=30)
    bairro: Optional[str] = Field(None, max_length=120)
    cidade: Optional[str] = Field(None, max_length=120)
    estado: Optional[str] = Field(None, max_length=2)
    logotipo: Optional[str] = Field(None, max_length=500)
    plano: str = Field("free", max_length=50)
    admin_email: EmailStr
    admin_senha: str = Field(..., min_length=6, max_length=72)
    whatsapp_phone_number_id: Optional[str] = Field(None, min_length=5, max_length=80)
    whatsapp_business_account_id: Optional[str] = Field(None, min_length=5, max_length=80)

    @field_validator("cnpj")
    @classmethod
    def normalize_cnpj(cls, value: str) -> str:
        return validate_cnpj_digits(value)

class CompanyResponse(CompanyBase):
    id: int
    ativo: bool
    read_only: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== USER ==========

class UserBase(BaseModel):
    email: EmailStr
    role: str = "admin"

class UserCreate(UserBase):
    senha: str = Field(..., min_length=6, max_length=72)

class ManagedUserCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=160)
    email: EmailStr
    senha: str = Field(..., min_length=6, max_length=72)
    role: str = Field("observador", pattern="^(admin|operador_captura|observador)$")
    company_id: Optional[int] = None
    exigir_troca_senha: bool = True

class ManagedUserUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=160)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(admin|operador_captura|observador)$")
    ativo: Optional[bool] = None
    senha: Optional[str] = Field(None, min_length=6, max_length=72)
    exigir_troca_senha: Optional[bool] = None
    motivo: str = Field(..., min_length=3, max_length=500)

class ManagedCompanyUpdate(BaseModel):
    ativo: Optional[bool] = None
    read_only: Optional[bool] = None
    razao_social: Optional[str] = Field(None, min_length=1, max_length=255)
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    cnpj: Optional[str] = Field(None, min_length=1, max_length=30)
    telefone: Optional[str] = Field(None, min_length=1, max_length=30)
    email: Optional[EmailStr] = None
    responsavel: Optional[str] = Field(None, min_length=1, max_length=255)
    cep: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = Field(None, max_length=255)
    numero: Optional[str] = Field(None, max_length=30)
    bairro: Optional[str] = Field(None, max_length=120)
    cidade: Optional[str] = Field(None, max_length=120)
    estado: Optional[str] = Field(None, max_length=2)
    logotipo: Optional[str] = Field(None, max_length=500)
    plano: Optional[str] = Field(None, max_length=50)
    whatsapp_phone_number_id: Optional[str] = Field(None, min_length=5, max_length=80)
    whatsapp_business_account_id: Optional[str] = Field(None, min_length=5, max_length=80)

    @field_validator("cnpj")
    @classmethod
    def normalize_cnpj(cls, value: Optional[str]) -> Optional[str]:
        return validate_cnpj_digits(value) if value is not None else value

class UserLogin(BaseModel):
    email: EmailStr
    senha: str

class PasswordChange(BaseModel):
    senha_atual: str = Field(..., min_length=6, max_length=72)
    nova_senha: str = Field(..., min_length=8, max_length=72)

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
    motivo: str = Field(..., min_length=1, max_length=500)
    valor_compra: Optional[float] = Field(None, ge=0)

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
    nome: Optional[str] = Field(None, max_length=120)
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    acumulavel: bool = True
    prioridade: int = Field(0, ge=0, le=999)
    limite_por_cliente: Optional[int] = Field(None, ge=1)
    limite_total: Optional[int] = Field(None, ge=1)
    valor_minimo_compra: Optional[float] = Field(None, ge=0)
    recompensa_tipo: str = Field("pontos", pattern="^(pontos|produto|desconto_valor|desconto_percentual|multiplicador|cupom)$")
    recompensa_valor: Optional[float] = Field(None, ge=0)
    condicao_campo: Optional[str] = None
    condicao_operador: Optional[str] = None
    condicao_valor: Optional[float] = None
    produtos_elegiveis: Optional[list[int]] = None
    categorias_elegiveis: Optional[list[int]] = None
    motivo_alteracao: str = Field(..., min_length=3, max_length=500)

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
    nome: Optional[str] = Field(None, max_length=120)
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    acumulavel: Optional[bool] = None
    prioridade: Optional[int] = Field(None, ge=0, le=999)
    limite_por_cliente: Optional[int] = Field(None, ge=1)
    limite_total: Optional[int] = Field(None, ge=1)
    valor_minimo_compra: Optional[float] = Field(None, ge=0)
    recompensa_tipo: Optional[str] = Field(None, pattern="^(pontos|produto|desconto_valor|desconto_percentual|multiplicador|cupom)$")
    recompensa_valor: Optional[float] = Field(None, ge=0)
    condicao_campo: Optional[str] = None
    condicao_operador: Optional[str] = None
    condicao_valor: Optional[float] = None
    produtos_elegiveis: Optional[list[int]] = None
    categorias_elegiveis: Optional[list[int]] = None
    motivo_alteracao: str = Field(..., min_length=3, max_length=500)

class PromotionConfigResponse(PromotionConfigBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PromotionSimulation(BaseModel):
    compras: int = Field(0, ge=0)
    valor_compra: float = Field(0, ge=0)

# ========== WHATSAPP / N8N ==========

class WhatsAppQueueGenerate(BaseModel):
    tipo: str = Field(..., min_length=1, max_length=50)
    mensagem_template: str = Field(..., min_length=1)
    customer_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    max_attempts: int = Field(3, ge=1, le=10)

class WhatsAppMessageStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(enviado|entregue|lido|erro|cancelado)$")
    provider_message_id: Optional[str] = None
    erro: Optional[str] = None

class N8nWhatsAppConsume(BaseModel):
    limit: int = Field(20, ge=1, le=100)
