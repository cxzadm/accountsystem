// MongoDB initialization script for Docker
db = db.getSiblingDB('sistema_contable_ec');

// Create collections with validation
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['username', 'email', 'password_hash', 'role'],
      properties: {
        username: { bsonType: 'string' },
        email: { bsonType: 'string' },
        password_hash: { bsonType: 'string' },
        role: { 
          bsonType: 'string',
          enum: ['admin', 'contador', 'auditor', 'interno']
        }
      }
    }
  }
});

db.createCollection('companies', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['name', 'ruc', 'legal_name'],
      properties: {
        name: { bsonType: 'string' },
        ruc: { bsonType: 'string' },
        legal_name: { bsonType: 'string' }
      }
    }
  }
});

db.createCollection('accounts', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['code', 'name', 'account_type', 'company_id'],
      properties: {
        code: { bsonType: 'string' },
        name: { bsonType: 'string' },
        account_type: {
          bsonType: 'string',
          enum: ['activo', 'pasivo', 'patrimonio', 'ingresos', 'gastos', 'costos']
        },
        company_id: { bsonType: 'string' }
      }
    }
  }
});

db.createCollection('journal_entries', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['entry_number', 'date', 'description', 'company_id'],
      properties: {
        entry_number: { bsonType: 'string' },
        date: { bsonType: 'date' },
        description: { bsonType: 'string' },
        company_id: { bsonType: 'string' }
      }
    }
  }
});

db.createCollection('audit_logs', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'action', 'module', 'description'],
      properties: {
        user_id: { bsonType: 'string' },
        action: {
          bsonType: 'string',
          enum: ['create', 'read', 'update', 'delete', 'login', 'logout', 'approve', 'reject', 'export', 'import']
        },
        module: {
          bsonType: 'string',
          enum: ['auth', 'users', 'companies', 'accounts', 'journal', 'reports', 'sri', 'assets', 'payables', 'receivables']
        },
        description: { bsonType: 'string' }
      }
    }
  }
});

// Create indexes for better performance
db.users.createIndex({ username: 1 }, { unique: true });
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ role: 1 });
db.users.createIndex({ status: 1 });

db.companies.createIndex({ ruc: 1 }, { unique: true });
db.companies.createIndex({ name: 1 });
db.companies.createIndex({ status: 1 });

db.accounts.createIndex({ code: 1, company_id: 1 }, { unique: true });
db.accounts.createIndex({ company_id: 1 });
db.accounts.createIndex({ account_type: 1 });
db.accounts.createIndex({ is_active: 1 });

db.journal_entries.createIndex({ entry_number: 1 }, { unique: true });
db.journal_entries.createIndex({ company_id: 1 });
db.journal_entries.createIndex({ date: 1 });
db.journal_entries.createIndex({ status: 1 });
db.journal_entries.createIndex({ entry_type: 1 });

db.audit_logs.createIndex({ user_id: 1 });
db.audit_logs.createIndex({ action: 1 });
db.audit_logs.createIndex({ module: 1 });
db.audit_logs.createIndex({ timestamp: 1 });
db.audit_logs.createIndex({ company_id: 1 });

print('Database initialized successfully!');










