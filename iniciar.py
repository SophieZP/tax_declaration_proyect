#!/usr/bin/env python3
"""
Script para iniciar la aplicación del Chat Formulario 210
"""

import subprocess
import sys
import os

def main():
    print("🤖 Chat Formulario 210 - Iniciando aplicación...")
    print("📄 PDF: Formulario_210_2025.pdf (251 fragmentos)")
    print("🧠 IA: Google Gemini AI")
    print("🔗 URL: http://127.0.0.1:5000")
    print("\n" + "="*50)
    
    try:
        # Verificar que existe el archivo
        if not os.path.exists("app.py"):
            print("❌ Error: No se encuentra app.py")
            return
            
        print("✅ Iniciando servidor Flask...")
        print("🌐 Abre tu navegador en: http://127.0.0.1:5000")
        print("❌ Para cerrar: Ctrl+C")
        print("\n" + "="*50)
        
        # Ejecutar la aplicación
        subprocess.run([sys.executable, "app.py"])
        
    except KeyboardInterrupt:
        print("\n🛑 Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()