from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Product
from app.schemas.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductImportService
from app.utils.dependencies import get_current_user, get_effective_company_id, get_writable_company_id, require_admin_or_master
import pandas as pd
import io

router = APIRouter(prefix="/produtos", tags=["Products"])

@router.post("/importar-excel")
async def importar_produtos(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_writable_company_id)
):
    """Importa produtos de arquivo Excel"""
    
    try:
        # Lê arquivo
        contents = await file.read()
        
        # Parse com suporte ao modelo simples e ao layout por categorias
        df = ProductImportService.normalizar_excel(contents)
        
        # Valida
        is_valid, erros = ProductImportService.validar_dados(df)
        
        if not is_valid:
            return {
                "success": False,
                "message": "Arquivo com erros",
                "erros": erros
            }
        
        # Importa
        result = ProductImportService.importar_produtos(
            db=db,
            company_id=company_id,
            df=df
        )
        
        return {
            "success": True,
            "message": "Produtos importados",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )

@router.get("/template-excel")
def baixar_template_excel():
    """Baixa modelo de importação"""
    
    template = ProductImportService.gerar_template_excel()
    
    return StreamingResponse(
        io.BytesIO(template),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=produto_template.xlsx"}
    )

@router.get("/exportar-excel")
def exportar_produtos_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Exporta todos os produtos para Excel"""
    
    try:
        excel_data = ProductImportService.exportar_produtos(
            db=db,
            company_id=current_user.company_id
        )
        
        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=produtos_export.xlsx"}
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao exportar: {str(e)}"
        )

@router.get("/")
def listar_produtos(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: str = Query(None),
    categoria_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """Lista produtos com filtros"""
    
    query = db.query(Product).filter(Product.company_id == company_id)
    
    if search:
        query = query.filter(Product.nome.ilike(f"%{search}%"))
    
    if categoria_id:
        query = query.filter(Product.categoria_id == categoria_id)
    
    total = query.count()
    
    produtos = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "success": True,
        "total": total,
        "page": page,
        "limit": limit,
        "data": [
            {
                "id": p.id,
                "nome": p.nome,
                "preco": p.preco,
                "categoria_id": p.categoria_id,
                "categoria": p.category.nome if p.category else None
            }
            for p in produtos
        ]
    }

@router.post("/")
def criar_produto(
    body: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_writable_company_id)
):
    """Cria novo produto"""
    
    produto = Product(
        nome=body.nome,
        preco=body.preco,
        categoria_id=body.categoria_id,
        company_id=company_id
    )
    db.add(produto)
    db.commit()
    db.refresh(produto)
    
    return {
        "success": True,
        "data": {
            "id": produto.id,
            "nome": produto.nome,
            "preco": produto.preco,
            "categoria_id": produto.categoria_id
        }
    }

@router.get("/{produto_id}")
def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """Obtém detalhes do produto"""
    
    produto = db.query(Product).filter(
        Product.id == produto_id,
        Product.company_id == company_id
    ).first()
    
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    return {
        "success": True,
        "data": {
            "id": produto.id,
            "nome": produto.nome,
            "preco": produto.preco,
            "categoria_id": produto.categoria_id,
            "categoria": produto.category.nome if produto.category else None
        }
    }

@router.put("/{produto_id}")
def atualizar_produto(
    produto_id: int,
    body: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_writable_company_id)
):
    """Atualiza produto"""
    
    produto = db.query(Product).filter(
        Product.id == produto_id,
        Product.company_id == company_id
    ).first()
    
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    if body.nome:
        produto.nome = body.nome
    if body.preco:
        produto.preco = body.preco
    if body.categoria_id:
        produto.categoria_id = body.categoria_id
    
    db.commit()
    db.refresh(produto)
    
    return {
        "success": True,
        "data": {
            "id": produto.id,
            "nome": produto.nome,
            "preco": produto.preco
        }
    }

@router.delete("/{produto_id}")
def deletar_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_writable_company_id)
):
    """Deleta produto"""
    
    produto = db.query(Product).filter(
        Product.id == produto_id,
        Product.company_id == company_id
    ).first()
    
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    db.delete(produto)
    db.commit()
    
    return {"success": True, "message": "Produto deletado"}
