from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Company, User
from app.services.auth_service import AuthService

security = HTTPBearer()

ROLE_MASTER = "master"
ROLE_ADMIN = "admin"
ROLE_CAPTURE_OPERATOR = "operador_captura"
ROLE_OBSERVER = "observador"
ALL_ROLES = {ROLE_MASTER, ROLE_ADMIN, ROLE_CAPTURE_OPERATOR, ROLE_OBSERVER}


def normalize_role(role: str) -> str:
    return (role or "").strip().lower()


def is_master(user: User) -> bool:
    return normalize_role(user.role) == ROLE_MASTER


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Extrai usuario do JWT token."""
    token_data = AuthService.verify_token(credentials.credentials)

    if token_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    user = db.query(User).filter(User.id == token_data["user_id"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario nao encontrado")

    if not user.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inativo")

    company = db.query(Company).filter(Company.id == user.company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Empresa nao encontrada")

    if not company.ativo and not is_master(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Empresa bloqueada")

    return user


def require_roles(*roles: str):
    allowed = {normalize_role(role) for role in roles}

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if normalize_role(current_user.role) not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado para este perfil"
            )
        return current_user

    return dependency


require_master = require_roles(ROLE_MASTER)
require_admin_or_master = require_roles(ROLE_ADMIN, ROLE_MASTER)
require_capture_operator = require_roles(ROLE_CAPTURE_OPERATOR, ROLE_ADMIN, ROLE_MASTER)
require_read_access = require_roles(ROLE_OBSERVER, ROLE_CAPTURE_OPERATOR, ROLE_ADMIN, ROLE_MASTER)
require_points_write_access = require_roles(ROLE_CAPTURE_OPERATOR, ROLE_ADMIN, ROLE_MASTER)
require_operator_or_above = require_read_access


def get_effective_company_id(
    x_company_id: int | None = Header(default=None, alias="X-Company-Id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> int:
    """Empresa de trabalho. Master pode escolher via X-Company-Id."""
    if is_master(current_user):
        company_id = x_company_id or current_user.company_id
        company = db.query(Company).filter(Company.id == company_id, Company.ativo == True).first()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa nao encontrada")
        return company_id

    return current_user.company_id


def get_writable_company_id(
    company_id: int = Depends(get_effective_company_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> int:
    """Empresa de escrita. Conta em somente leitura pode consultar, mas nao alterar dados."""
    if is_master(current_user):
        return company_id

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company or not company.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Empresa bloqueada")
    if company.read_only:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conta em somente leitura")
    return company_id
