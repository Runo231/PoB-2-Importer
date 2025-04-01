import base64
import zlib

def decode_pob(code):
    # Si el código tiene prefijo "PoB", lo eliminamos.
    #if code.startswith("PoB"):
    #    code = code[3:]
    
    # Reemplazar caracteres URL-safe a estándar
    code = code.replace('-', '+').replace('_', '/')
    
    # Añadir padding si es necesario
    padding = len(code) % 4
    if padding:
        code += '=' * (4 - padding)
    
    # Decodificar la cadena base64 a datos binarios
    compressed_data = base64.b64decode(code)
    
    # Descomprimir los datos usando zlib
    try:
        decompressed_data = zlib.decompress(compressed_data)
    except zlib.error as e:
        raise Exception("Error al descomprimir los datos: " + str(e))
    
    # Convertir los datos descomprimidos a cadena (asumiendo UTF-8)
    return decompressed_data.decode('utf-8')

if __name__ == '__main__':
    pob_code = input("Introduce el código PoB: ").strip()
    try:
        decoded_json = decode_pob(pob_code)
        print("JSON decodificado:")
        print(decoded_json)
    except Exception as e:
        print("Error:", e)
