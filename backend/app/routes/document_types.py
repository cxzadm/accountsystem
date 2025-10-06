from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List, Optional
from datetime import datetime

from app.models.document_type import (
    DocumentType,
    DocumentTypeCreate,
    DocumentTypeUpdate,
    DocumentTypeResponse,
)
from app.models.journal import JournalEntry
from app.models.user import User
from app.models.document_reservation import DocumentNumberReservation, ReservationStatus
from app.auth.dependencies import require_permission, log_audit, AuditAction, AuditModule


router = APIRouter(prefix="/document-types", tags=["Document Types"])


def to_response(doc: DocumentType) -> DocumentTypeResponse:
    return DocumentTypeResponse(
        id=str(doc.id),
        code=doc.code,
        name=doc.name,
        control_number=doc.control_number,
        establishment_point=doc.establishment_point,
        receipt_type=doc.receipt_type,
        bank_movement=doc.bank_movement,
        customer_movement=doc.customer_movement,
        supplier_movement=doc.supplier_movement,
        product_movement=doc.product_movement,
        is_electronic=doc.is_electronic,
        responsible_code=doc.responsible_code,
        responsible_name=doc.responsible_name,
        next_sequence=doc.next_sequence,
        padding=doc.padding,
        company_id=doc.company_id,
        is_active=doc.is_active,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.get("/", response_model=List[DocumentTypeResponse])
async def list_document_types(
    company_id: str = Query(...),
    current_user: User = Depends(require_permission("companies:update"))
):
    items = await DocumentType.find(DocumentType.company_id == company_id).to_list()

    # Sincronizar next_sequence con el máximo número existente de asientos por código
    for doc in items:
        try:
            # Buscar el último asiento con prefijo CODE- y misma empresa
            last_list = await JournalEntry.find({
                "company_id": company_id,
                "entry_number": {"$regex": f"^{doc.code}-"}
            }).sort("-entry_number").limit(1).to_list()
            if last_list:
                last_number_str = last_list[0].entry_number.split("-")[-1]
                last_numeric = int(last_number_str)
                if doc.next_sequence < last_numeric:
                    doc.next_sequence = last_numeric
                    await doc.save()
        except Exception:
            # No interrumpir listado por errores de parseo/consulta
            pass

    return [to_response(i) for i in items]


@router.post("/", response_model=DocumentTypeResponse)
async def create_document_type(
    data: DocumentTypeCreate,
    request: Request,
    company_id: str = Query(...),
    current_user: User = Depends(require_permission("companies:update"))
):
    # Unicidad por code+company
    exists = await DocumentType.find_one(
        DocumentType.company_id == company_id,
        DocumentType.code == data.code
    )
    if exists:
        raise HTTPException(status_code=400, detail="Código ya existe para la empresa")

    doc = DocumentType(
        code=data.code,
        name=data.name,
        establishment_point=data.establishment_point,
        receipt_type=data.receipt_type,
        bank_movement=data.bank_movement,
        customer_movement=data.customer_movement,
        supplier_movement=data.supplier_movement,
        product_movement=data.product_movement,
        is_electronic=data.is_electronic,
        responsible_code=data.responsible_code,
        responsible_name=data.responsible_name,
        padding=data.padding,
        company_id=company_id,
        created_by=str(current_user.id)
    )
    await doc.insert()
    await log_audit(
        user=current_user,
        action=AuditAction.CREATE,
        module=AuditModule.ADMIN,
        description=f"Tipo de documento creado: {doc.code} - {doc.name}",
        resource_id=str(doc.id),
        resource_type="document_type",
        new_values=doc.dict(),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    return to_response(doc)


@router.put("/{doc_id}", response_model=DocumentTypeResponse)
async def update_document_type(
    doc_id: str,
    data: DocumentTypeUpdate,
    request: Request,
    current_user: User = Depends(require_permission("companies:update"))
):
    from bson import ObjectId
    try:
        doc = await DocumentType.find_one(DocumentType.id == ObjectId(doc_id))
    except Exception:
        doc = None
    if not doc:
        raise HTTPException(status_code=404, detail="Tipo de documento no encontrado")
    old_values = doc.dict()
    for k, v in data.dict(exclude_unset=True).items():
        setattr(doc, k, v)
    doc.updated_at = datetime.now()
    await doc.save()
    await log_audit(
        user=current_user,
        action=AuditAction.UPDATE,
        module=AuditModule.ADMIN,
        description=f"Tipo de documento actualizado: {doc.code}",
        resource_id=str(doc.id),
        resource_type="document_type",
        old_values=old_values,
        new_values=doc.dict(),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    return to_response(doc)


@router.post("/{doc_id}/next-number")
async def get_next_document_number_post(
    doc_id: str,
    request: Request,
    current_user: User = Depends(require_permission("journal:create"))
):
    """Incrementa de forma atómica y devuelve el próximo número formateado"""
    # Usar motor para incremento atómico
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo import ReturnDocument
    from bson import ObjectId
    from app.config import settings

    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    col = db.document_types

    try:
        oid = ObjectId(doc_id)
    except Exception:
        client.close()
        raise HTTPException(status_code=400, detail="ID de documento inválido")

    # Obtener el doc para calcular relleno de huecos
    doc_row = await col.find_one({"_id": oid})
    if not doc_row:
        client.close()
        raise HTTPException(status_code=404, detail="Tipo de documento no encontrado")

    code = doc_row.get("code")
    padding = int(doc_row.get("padding", 5))
    company_id = str(doc_row.get("company_id"))

    # Buscar huecos según asientos existentes usando consulta directa
    journal_col = db.journal_entries
    existing = await journal_col.find({
        "company_id": company_id,
        "entry_number": {"$regex": f"^{code}-"}
    }, {"entry_number": 1}).to_list(length=None)
    used = set()
    for e in existing:
        try:
            used.add(int(e["entry_number"].split("-")[-1]))
        except Exception:
            continue
    seq = 1
    while seq in used:
        seq += 1

    # Actualizar next_sequence al nuevo seq
    result = await col.find_one_and_update(
        {"_id": oid},
        {"$set": {"next_sequence": seq, "updated_at": datetime.now()}},
        return_document=ReturnDocument.AFTER
    )
    if not result:
        client.close()
        raise HTTPException(status_code=404, detail="Tipo de documento no encontrado")

    code = result.get("code")
    padding = int(result.get("padding", 5))
    seq = int(result.get("next_sequence", 1))
    formatted = f"{code}-{str(seq).zfill(padding)}"

    # Guardar control_number
    await col.update_one({"_id": result["_id"]}, {"$set": {"control_number": formatted}})
    
    # Registrar reserva solo si no existe ya
    try:
        existing_reservation = await DocumentNumberReservation.find_one({
            "company_id": str(result.get("company_id")),
            "document_type_id": str(result.get("_id")),
            "number": formatted,
            "status": ReservationStatus.RESERVED
        })

        if not existing_reservation:
            await DocumentNumberReservation(
                company_id=str(result.get("company_id")),
                document_type_id=str(result.get("_id")),
                document_code=code,
                sequence=seq,
                number=formatted,
                status=ReservationStatus.RESERVED,
                reserved_by=str(current_user.id)
            ).insert()

    except Exception:
        pass

    client.close()
    return {"number": formatted, "sequence": seq}


@router.get("/{doc_id}/next-number")
async def get_next_document_number_get(
    doc_id: str,
    request: Request,
    current_user: User = Depends(require_permission("journal:create"))
):
    # Reutilizar la lógica del POST para compatibilidad
    return await get_next_document_number_post(doc_id, request, current_user)


@router.get("/{doc_id}/peek-next")
async def peek_next_document_number(
    doc_id: str,
    current_user: User = Depends(require_permission("journal:create"))
):
    """Obtiene el siguiente número sugerido sin reservar ni modificar BD"""
    from motor.motor_asyncio import AsyncIOMotorClient
    from bson import ObjectId
    from app.config import settings

    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    col = db.document_types

    try:
        oid = ObjectId(doc_id)
    except Exception:
        client.close()
        raise HTTPException(status_code=400, detail="ID de documento inválido")

    row = await col.find_one({"_id": oid})
    if not row:
        client.close()
        raise HTTPException(status_code=404, detail="Tipo de documento no encontrado")

    code = row.get("code")
    padding = int(row.get("padding", 5))
    company_id = str(row.get("company_id"))

    # Use direct MongoDB query for better performance
    journal_col = db.journal_entries
    existing = await journal_col.find({
        "company_id": company_id,
        "entry_number": {"$regex": f"^{code}-"}
    }, {"entry_number": 1}).to_list(length=None)
    
    used = set()
    for e in existing:
        try:
            used.add(int(e["entry_number"].split("-")[-1]))
        except Exception:
            continue
    seq = 1
    while seq in used:
        seq += 1
    formatted = f"{code}-{str(seq).zfill(padding)}"
    client.close()
    return {"number": formatted, "sequence": seq}


@router.post("/reset-numbers")
async def reset_all_document_numbers(
    company_id: str = Query(...),
    current_user: User = Depends(require_permission("companies:update"))
):
    """Reinicia todos los next_sequence y control_number de los tipos de documentos de la empresa.
    Si no existen tipos de documentos, los crea automáticamente."""
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.config import settings
    
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    col = db.document_types
    
    # Verificar si existen tipos de documentos para esta empresa
    existing_count = await col.count_documents({"company_id": company_id})
    
    if existing_count == 0:
        # Si no existen tipos de documentos, crearlos automáticamente
        from app.models.company import Company
        from app.models.document_type import DocumentType
        
        # Obtener la empresa
        from bson import ObjectId
        try:
            company = await Company.find_one(Company.id == ObjectId(company_id))
        except Exception:
            company = None
        if not company:
            client.close()
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
        
        # Documentos contables ecuatorianos
        ECUADORIAN_DOCUMENT_TYPES = [
            {"code": "CC", "name": "CANCELACIÓN DE CLIENTES"},
            {"code": "CP", "name": "CANCELACIÓN DE PROVEEDORES"},
            {"code": "CR", "name": "COMPROBANTE DE RETENCIÓN"},
            {"code": "AJ", "name": "AJUSTE CLIENTES"},
            {"code": "BI", "name": "BALANCE INICIAL"},
            {"code": "PR", "name": "CHEQUE PROTESTADO"},
            {"code": "CO", "name": "COMPROBANTE DE COBRO"},
            {"code": "CD", "name": "COMPROBANTE DE DIARIO"},
            {"code": "CE", "name": "COMPROBANTE DE EGRESO"},
            {"code": "CI", "name": "COMPROBANTE DE INGRESO"},
            {"code": "RI", "name": "COMPROBANTE DE RETENCIÓN DEL IVA"},
            {"code": "RF", "name": "COMPROBANTE DE RETENCIÓN EN LA FUENTE"},
            {"code": "CT", "name": "COMPROBANTE DE TRANSFERENCIA"},
            {"code": "IB", "name": "INGRESO BANCARIO"},
            {"code": "IC", "name": "INGRESO CAJA"},
            {"code": "20", "name": "DOC. EMITIDOS POR INT. DEL ESTADO"},
            {"code": "01", "name": "FACTURA DE COMPRA"},
            {"code": "10", "name": "FACTURA DE COMPRA CON RETENCIÓN CERO"},
            {"code": "21", "name": "FACTURA DE VENTA"},
            {"code": "31", "name": "FACTURA DE VENTA ELECTRÓNICA"},
            {"code": "IN", "name": "INTERESES FINANCIEROS"},
            {"code": "ZG", "name": "CHEQUE GIRADO NO COBRADO"},
            {"code": "NC", "name": "NOTA DE CRÉDITO"},
            {"code": "ND", "name": "NOTA DE DÉBITO"},
            {"code": "03", "name": "TRANSFERENCIA DE BODEGA"},
            {"code": "FH", "name": "FACTURA DE HOSPEDAJE"},
            {"code": "25", "name": "AJUSTE DE EGRESO"},
            {"code": "05", "name": "AJUSTE DE INGRESO"},
            {"code": "22", "name": "EGRESO DE BODEGA"},
            {"code": "28", "name": "EGRESO DE BODEGA - PRODUCCIÓN"},
            {"code": "29", "name": "FACTURA DE EXPORTACIÓN"},
            {"code": "02", "name": "INGRESO DE BODEGA"},
            {"code": "09", "name": "LIQUIDACIÓN DE IMPORTACIÓN"},
            {"code": "26", "name": "NOTA DE CRÉDITO PROVEEDOR"},
            {"code": "27", "name": "NOTA DE ENTREGA A CLIENTE"},
            {"code": "07", "name": "NOTA DE ENTREGA DE PROVEEDOR"},
            {"code": "NP", "name": "NOTA DE PEDIDO"},
            {"code": "PF", "name": "PROFORMA - COTIZACIÓN"},
            {"code": "24", "name": "SALDO INICIAL EGRESO"},
            {"code": "04", "name": "SALDO INICIAL INGRESO"},
            {"code": "23", "name": "TRANSFERENCIA A BODEGA"},
            {"code": "11", "name": "LIQUIDACIÓN ELECTRÓNICA DE COMPRAS"},
            {"code": "06", "name": "NOTA DE CRÉDITO CLIENTE"},
            {"code": "16", "name": "NOTA DE CRÉDITO ELECTRÓNICA"},
            {"code": "08", "name": "ORDEN DE PRODUCCIÓN"},
            {"code": "RC", "name": "RETENCIÓN DE CLIENTES"},
            {"code": "RA", "name": "RETENCIÓN DE TARJETA DE CRÉDITO"},
            {"code": "RE", "name": "RETENCIÓN ELECTRÓNICA"},
            {"code": "R4", "name": "ROL DE DÉCIMO CUARTO"},
            {"code": "R3", "name": "ROL DE DÉCIMO TERCERO"},
            {"code": "RP", "name": "ROL DE PAGOS"},
            {"code": "RU", "name": "ROL DE UTILIDADES"},
            {"code": "RV", "name": "ROL DE VACACIONES"},
            {"code": "SF", "name": "SALDO A FAVOR CLIENTE"},
        ]
        
        def get_document_configuration(code: str) -> dict:
            """Obtener configuración específica para cada tipo de documento"""
            configs = {
                "CE": {"bank_movement": "D", "customer_movement": "D", "is_electronic": False},
                "CI": {"bank_movement": "C", "customer_movement": "C", "is_electronic": False},
                "21": {"customer_movement": "C", "is_electronic": False},
                "31": {"customer_movement": "C", "is_electronic": True},
                "01": {"supplier_movement": "D", "is_electronic": False},
                "10": {"supplier_movement": "D", "is_electronic": False},
                "NC": {"customer_movement": "D", "is_electronic": False},
                "16": {"customer_movement": "D", "is_electronic": True},
                "ND": {"customer_movement": "C", "is_electronic": False},
                "CD": {"is_electronic": False},
                "RI": {"customer_movement": "D", "is_electronic": False},
                "RF": {"supplier_movement": "D", "is_electronic": False},
                "RC": {"customer_movement": "D", "is_electronic": False},
                "RA": {"customer_movement": "D", "is_electronic": False},
                "RE": {"is_electronic": True},
                "02": {"product_movement": "I", "is_electronic": False},
                "03": {"product_movement": "E", "is_electronic": False},
                "22": {"product_movement": "E", "is_electronic": False},
                "23": {"product_movement": "I", "is_electronic": False},
                "28": {"product_movement": "E", "is_electronic": False},
                "RP": {"is_electronic": False},
                "R3": {"is_electronic": False},
                "R4": {"is_electronic": False},
                "RU": {"is_electronic": False},
                "RV": {"is_electronic": False},
            }
            return configs.get(code, {"is_electronic": False})
        
        # Crear tipos de documentos
        created_count = 0
        for doc_data in ECUADORIAN_DOCUMENT_TYPES:
            config = get_document_configuration(doc_data["code"])
            
            document_type = DocumentType(
                code=doc_data["code"],
                name=doc_data["name"],
                establishment_point="001-001",
                bank_movement=config.get("bank_movement"),
                customer_movement=config.get("customer_movement"),
                supplier_movement=config.get("supplier_movement"),
                product_movement=config.get("product_movement"),
                is_electronic=config.get("is_electronic", False),
                next_sequence=0,
                padding=6,
                company_id=company_id,
                is_active=True,
                created_by=str(current_user.id)
            )
            
            await document_type.insert()
            created_count += 1
        
        client.close()
        return {"message": f"Se crearon {created_count} tipos de documentos y se reiniciaron los números"}
    
    else:
        # Si existen tipos de documentos, solo reiniciar números
        result = await col.update_many(
            {"company_id": company_id},
            {
                "$set": {
                    "next_sequence": 0,
                    "control_number": None,
                    "updated_at": datetime.now()
                }
            }
    )
    
    client.close()
    return {"message": f"Reiniciados {result.modified_count} tipos de documentos"}


