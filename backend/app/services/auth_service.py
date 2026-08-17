import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config import settings
from app.models import User, Company
from app.schemas.schemas import UserCreate

logger = logging.getLogger("uvicorn.error")

# Contexto para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Serviço de Autenticação"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash da senha"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se senha está correta"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Cria JWT token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verifica e decodifica JWT token"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id_str = payload.get("sub")
            if user_id_str is None:
                return None
            return {"user_id": int(user_id_str), "company_id": payload.get("company_id")}
        except JWTError as e:
            print(f"[DEBUG] verify_token: JWTError: {e}")
            return None
        except Exception as e:
            print(f"[DEBUG] verify_token: Exceção geral: {e}")
            return None
    
    @staticmethod
    def register(db: Session, company_name: str, email: str, password: str) -> dict:
        """Registra nova empresa + admin"""
        
        # Verifica se email já existe
        # tenant-scope: global - email e unico em todo o sistema.
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("Email já registrado")
        
        # Cria empresa
        company = Company(nome=company_name, plano="free", ativo=True)
        db.add(company)
        db.flush()
        
        # Cria usuario admin
        hashed_password = AuthService.hash_password(password)
        user = User(
            email=email,
            senha_hash=hashed_password,
            company_id=company.id,
            role="admin",
            ativo=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "user_id": user.id,
            "company_id": company.id,
            "email": user.email,
            "role": user.role,
            "company_read_only": company.read_only
        }
    
    @staticmethod
    def create_customer_registration_token(company_id: int) -> str:
        """Cria convite temporário para o cadastro público de clientes."""
        return AuthService.create_access_token(
            data={"purpose": "customer_registration", "company_id": company_id},
            expires_delta=timedelta(days=30)
        )

    @staticmethod
    def verify_customer_registration_token(token: str) -> Optional[int]:
        """Retorna a empresa do convite, se ele ainda for válido."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            if payload.get("purpose") != "customer_registration":
                return None
            company_id = payload.get("company_id")
            return int(company_id) if company_id is not None else None
        except (JWTError, TypeError, ValueError):
            return None
    @staticmethod
    def login(db: Session, email: str, password: str) -> Optional[dict]:
        """Autentica usuário"""

        configured_master_match = bool(
            settings.master_email
            and email.strip().casefold() == settings.master_email.strip().casefold()
        )
        # tenant-scope: global - login precisa localizar a empresa pelo email unico.
        user = db.query(User).filter(User.email == email, User.ativo == True).first()
        if not user:
            logger.warning(
                "[AUTH_DIAGNOSTIC] login_negado etapa=usuario_ativo_nao_encontrado "
                "master_email_corresponde=%s email_tem_espaco_borda=%s",
                configured_master_match,
                email != email.strip(),
            )
            return None
        
        # Verifica se empresa está ativa
        company = db.query(Company).filter(Company.id == user.company_id).first()
        if not company or not company.ativo:
            logger.warning(
                "[AUTH_DIAGNOSTIC] login_negado etapa=empresa_inativa_ou_ausente "
                "user_id=%s company_id=%s master_email_corresponde=%s",
                user.id,
                user.company_id,
                configured_master_match,
            )
            return None
        
        password_matches = AuthService.verify_password(password, user.senha_hash)
        if not password_matches:
            logger.warning(
                "[AUTH_DIAGNOSTIC] login_negado etapa=senha_nao_corresponde "
                "user_id=%s company_id=%s role=%s master_email_corresponde=%s",
                user.id,
                user.company_id,
                user.role,
                configured_master_match,
            )
            return None

        logger.info(
            "[AUTH_DIAGNOSTIC] login_aprovado user_id=%s company_id=%s role=%s "
            "master_email_corresponde=%s",
            user.id,
            user.company_id,
            user.role,
            configured_master_match,
        )

        user.ultimo_acesso = datetime.utcnow()
        db.commit()
        
        # Cria token
        token = AuthService.create_access_token(
            data={"sub": str(user.id), "company_id": user.company_id}
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "company_id": user.company_id,
            "email": user.email,
            "nome": user.nome,
            "role": user.role,
            "exigir_troca_senha": user.exigir_troca_senha,
            "company_read_only": company.read_only
        }
