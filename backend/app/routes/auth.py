from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models import Company, User
from app.schemas.schemas import BootstrapMasterRequest, UserCreate, UserLogin, RegisterRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Registra nova empresa com admin"""
    
    try:
        result = AuthService.register(db, data.company_name, data.email, data.senha)
        return {
            "success": True,
            "message": "Empresa registrada com sucesso",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login")
def login(
    body: UserLogin,
    db: Session = Depends(get_db)
):
    """Autentica usuário"""
    
    result = AuthService.login(db, body.email, body.senha)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    return {
        "success": True,
        "data": result
    }


@router.post("/bootstrap-master")
def bootstrap_master(
    body: BootstrapMasterRequest,
    db: Session = Depends(get_db)
):
    """Cria ou atualiza o usuario Master usando a SECRET_KEY do ambiente."""

    if body.secret_key != settings.secret_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chave de bootstrap invalida"
        )

    if settings.master_email and body.email.lower() != settings.master_email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email diferente do MASTER_EMAIL configurado"
        )

    company = db.query(Company).filter(Company.nome == "Master").first()
    if not company:
        company = Company(nome="Master", plano="enterprise", ativo=True)
        db.add(company)
        db.flush()

    user = db.query(User).filter(User.email == body.email).first()
    senha_hash = AuthService.hash_password(body.senha)
    if not user:
        user = User(
            email=body.email,
            senha_hash=senha_hash,
            company_id=company.id,
            role="master",
            ativo=True,
        )
        db.add(user)
    else:
        user.senha_hash = senha_hash
        user.company_id = company.id
        user.role = "master"
        user.ativo = True

    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "message": "Master criado ou atualizado com sucesso",
        "data": {
            "email": user.email,
            "role": user.role
        }
    }
