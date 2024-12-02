import pyqrcode
import png
from pyqrcode import QRCode
import os
import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def generate_table_qr_codes(num_tables):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        static_dir = os.path.join(current_dir, 'static')
        qr_codes_dir = os.path.join(static_dir, 'qr_codes')
        
        os.makedirs(qr_codes_dir, exist_ok=True)

        local_ip = get_local_ip()
        base_url = f"http://{local_ip}:5000"

        for table in range(1, num_tables + 1):
            try:
                url = f"{base_url}/?table={table}"
                print(f"Generating QR code for URL: {url}")
                
                qr = pyqrcode.create(url)
                
                png_path = os.path.join(qr_codes_dir, f"table_{table}.png")
                qr.png(png_path, scale=8)
                
                if os.path.exists(png_path):
                    print(f"Successfully generated QR code for table {table}")
                    
            except Exception as e:
                print(f"Error generating QR code for table {table}: {str(e)}")

    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    print("Starting QR code generation...")
    generate_table_qr_codes(10)
    print("Process completed")