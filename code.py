import base64
import zlib
import xml.etree.ElementTree as ET
import os

def encode_pob(xml_str):
    # Convertir el XML a bytes usando UTF-8
    xml_bytes = xml_str.encode('utf-8')
    
    # Comprimir los datos con zlib
    compressed_data = zlib.compress(xml_bytes)
    
    # Codificar en base64
    b64_str = base64.b64encode(compressed_data).decode('ascii')
    
    # Reemplazar caracteres para hacerlo URL-safe y eliminar padding
    url_safe = b64_str.replace('+', '-').replace('/', '_').rstrip('=')
    
    return url_safe

def read_xml_file(file_path):
    try:
        # Verificar si el archivo existe
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo {file_path} no existe")
        
        # Leer el archivo XML como texto
        with open(file_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()
        
        # Opcional: verificar que sea un XML válido
        ET.fromstring(xml_content)
        
        return xml_content
    except ET.ParseError:
        raise ValueError("El archivo no contiene XML válido")

if __name__ == '__main__':
    try:
        # Ruta del archivo XML (en la misma carpeta que el script)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        xml_file = os.path.join(script_dir, "character.xml")
        
        # Leer el archivo XML
        xml_content = read_xml_file(xml_file)
        
        # Codificar el contenido XML
        encoded_code = encode_pob(xml_content)
        
        print("Código PoB generado:")
        print(encoded_code)
    except Exception as e:
        print("Error:", e)