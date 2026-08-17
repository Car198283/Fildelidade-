from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.schemas import PasswordChange, UserCreate, UserLogin, RegisterRequest
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_user

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


@router.post("/change-password")
def change_password(
    body: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not AuthService.verify_password(body.senha_atual, current_user.senha_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    if body.senha_atual == body.nova_senha:
        raise HTTPException(status_code=400, detail="A nova senha deve ser diferente da atual")
    current_user.senha_hash = AuthService.hash_password(body.nova_senha)
    current_user.exigir_troca_senha = False
    db.commit()
    return {"success": True, "message": "Senha alterada com sucesso"}
