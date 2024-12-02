from typing import Dict, Any
import os
from pathlib import Path

import py_eureka_client.eureka_client as eureka_client
from dotenv import load_dotenv
from flask import Flask

from app.logger_setup import logger
from app.routes import register_routes

# Constantes
EUREKA_DEFAULT_PORT = 8761
INSTANCE_DEFAULT_PORT = 5000
DEFAULT_CERT_DATE = '2019-01-01'

def load_config() -> Dict[str, Any]:
    """Carga y valida la configuración desde variables de entorno."""
    load_dotenv()
    
    config = {
        'production': os.getenv('PRODUCTION', 'FALSE').upper() == 'TRUE',
        'eureka_port': int(os.getenv('EUREKA_PORT', EUREKA_DEFAULT_PORT)),
        'instance_port': int(os.getenv('INSTANCE_PORT', INSTANCE_DEFAULT_PORT)),
        'cert_date': os.getenv('CERT_DATE', DEFAULT_CERT_DATE),
        'cert_path': os.getenv('CERT'),
        'privatekey_path': os.getenv('PRIVATEKEY')
    }
    
    # Logging de configuración
    for key, value in config.items():
        logger.info(f'{key}={value}/{os.getenv(key.upper())}')
    
    return config

def read_file_content(file_path: str, file_type: str) -> str:
    """Lee el contenido de un archivo de forma segura."""
    try:
        content = Path(file_path).read_text()
        logger.info(f'Contenido del archivo {file_type}:\n{content}')
        return content
    except Exception as e:
        logger.error(f'Error al leer el archivo {file_type}: {e}')
        raise RuntimeError(f'Error al leer el archivo {file_type}') from e

def create_app() -> Flask:
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    config = load_config()
    
    # Leer archivos de certificados
    read_file_content(config['cert_path'], 'CERT')
    read_file_content(config['privatekey_path'], 'PRIVATEKEY')
    
    # Configurar Eureka
    eureka_client.init(
        eureka_server=f'http://eureka-service:{config["eureka_port"]}',
        app_name='pyafipws-service',
        instance_port=config['instance_port']
    )
    
    # Registrar blueprint
    afipws_blueprint = register_routes(config)
    app.register_blueprint(afipws_blueprint)
    
    return app

# Creación de la aplicación
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)