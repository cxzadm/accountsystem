const fs = require('fs');
const path = require('path');

// Leer la configuración centralizada
const configPath = path.join(__dirname, '..', 'config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// Usar configuración de producción para Docker
const prodConfig = config.production;

// Generar docker-compose.yml
const dockerComposeContent = `version: '3.8'

services:
  mongodb:
    image: mongo:5.0
    container_name: sistema-contable-mongodb
    restart: unless-stopped
    ports:
      - "${prodConfig.database.port}:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password123
      MONGO_INITDB_DATABASE: sistema_contable_ec
    volumes:
      - mongodb_data:/data/db
      - ./backend/scripts/mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
    networks:
      - sistema-contable-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: sistema-contable-backend
    restart: unless-stopped
    ports:
      - "${prodConfig.backend.port}:${prodConfig.backend.port}"
    environment:
      - MONGODB_URL=mongodb://admin:password123@mongodb:27017/sistema_contable_ec?authSource=admin
      - SECRET_KEY=tu-clave-secreta-super-segura-para-produccion
      - DEBUG=false
      - ENVIRONMENT=production
    depends_on:
      - mongodb
    networks:
      - sistema-contable-network
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host ${prodConfig.backend.host} --port ${prodConfig.backend.port}

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: sistema-contable-frontend
    restart: unless-stopped
    ports:
      - "${prodConfig.frontend.port}:80"
    depends_on:
      - backend
    networks:
      - sistema-contable-network

volumes:
  mongodb_data:

networks:
  sistema-contable-network:
    driver: bridge
`;

// Escribir el archivo docker-compose.yml
const dockerComposePath = path.join(__dirname, '..', 'docker-compose.yml');
fs.writeFileSync(dockerComposePath, dockerComposeContent);

console.log('✅ docker-compose.yml generado exitosamente con la configuración centralizada');
console.log(`📊 Configuración aplicada:`);
console.log(`   - Backend: puerto ${prodConfig.backend.port}`);
console.log(`   - Frontend: puerto ${prodConfig.frontend.port}`);
console.log(`   - Database: puerto ${prodConfig.database.port}`);
