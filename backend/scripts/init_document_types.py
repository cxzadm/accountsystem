#!/usr/bin/env python3
"""
Script para inicializar los tipos de documentos contables ecuatorianos
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.models.user import User
from app.models.company import Company
from app.models.document_type import DocumentType

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
        # Comprobantes de Egreso
        "CE": {
            "bank_movement": "D",
            "customer_movement": "D",
            "is_electronic": False,
        },
        # Comprobantes de Ingreso
        "CI": {
            "bank_movement": "C",
            "customer_movement": "C",
            "is_electronic": False,
        },
        # Facturas de Venta
        "21": {
            "customer_movement": "C",
            "is_electronic": False,
        },
        # Facturas de Venta Electrónica
        "31": {
            "customer_movement": "C",
            "is_electronic": True,
        },
        # Facturas de Compra
        "01": {
            "supplier_movement": "D",
            "is_electronic": False,
        },
        # Facturas de Compra con Retención Cero
        "10": {
            "supplier_movement": "D",
            "is_electronic": False,
        },
        # Notas de Crédito
        "NC": {
            "customer_movement": "D",
            "is_electronic": False,
        },
        # Notas de Crédito Electrónica
        "16": {
            "customer_movement": "D",
            "is_electronic": True,
        },
        # Notas de Débito
        "ND": {
            "customer_movement": "C",
            "is_electronic": False,
        },
        # Comprobante de Diario
        "CD": {
            "is_electronic": False,
        },
        # Retenciones
        "RI": {
            "customer_movement": "D",
            "is_electronic": False,
        },
        "RF": {
            "supplier_movement": "D",
            "is_electronic": False,
        },
        "RC": {
            "customer_movement": "D",
            "is_electronic": False,
        },
        "RA": {
            "customer_movement": "D",
            "is_electronic": False,
        },
        "RE": {
            "is_electronic": True,
        },
        # Movimientos de Bodega
        "02": {
            "product_movement": "I",
            "is_electronic": False,
        },
        "03": {
            "product_movement": "E",
            "is_electronic": False,
        },
        "22": {
            "product_movement": "E",
            "is_electronic": False,
        },
        "23": {
            "product_movement": "I",
            "is_electronic": False,
        },
        "28": {
            "product_movement": "E",
            "is_electronic": False,
        },
        # Roles de Pago
        "RP": {
            "is_electronic": False,
        },
        "R3": {
            "is_electronic": False,
        },
        "R4": {
            "is_electronic": False,
        },
        "RU": {
            "is_electronic": False,
        },
        "RV": {
            "is_electronic": False,
        },
    }
    
    return configs.get(code, {
        "is_electronic": False,
    })

async def init_document_types():
    """Inicializar tipos de documentos contables"""
    
    # Conectar a MongoDB
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    
    # Inicializar Beanie
    await init_beanie(
        database=database,
        document_models=[
            User,
            Company,
            DocumentType
        ]
    )
    
    print("✅ Base de datos conectada")
    
    # Obtener todas las empresas
    companies = await Company.find_all().to_list()
    
    if not companies:
        print("❌ No se encontraron empresas. Ejecuta primero init_db.py")
        return
    
    print(f"📋 Encontradas {len(companies)} empresas")
    
    # Procesar cada empresa
    for company in companies:
        print(f"\n🏢 Procesando empresa: {company.name}")
        
        # Eliminar tipos de documentos existentes para esta empresa
        await DocumentType.find(DocumentType.company_id == str(company.id)).delete()
        print("🗑️  Tipos de documentos existentes eliminados")
        
        # Crear tipos de documentos
        created_count = 0
        for doc_data in ECUADORIAN_DOCUMENT_TYPES:
            config = get_document_configuration(doc_data["code"])
            
            document_type = DocumentType(
                code=doc_data["code"],
                name=doc_data["name"],
                establishment_point="001-001",  # Punto de emisión por defecto
                bank_movement=config.get("bank_movement"),
                customer_movement=config.get("customer_movement"),
                supplier_movement=config.get("supplier_movement"),
                product_movement=config.get("product_movement"),
                is_electronic=config.get("is_electronic", False),
                next_sequence=0,
                padding=6,  # Formato: CE-000001
                company_id=str(company.id),
                is_active=True,
                created_by=str(company.created_by) if company.created_by else None
            )
            
            await document_type.insert()
            created_count += 1
        
        print(f"✅ {created_count} tipos de documentos creados para {company.name}")
    
    print(f"\n🎉 Inicialización de tipos de documentos completada!")
    print(f"📊 Total de tipos de documentos: {len(ECUADORIAN_DOCUMENT_TYPES)}")
    print(f"🏢 Empresas procesadas: {len(companies)}")

if __name__ == "__main__":
    asyncio.run(init_document_types())


