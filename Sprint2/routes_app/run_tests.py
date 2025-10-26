#!/usr/bin/env python3
"""
Script para ejecutar las pruebas del proyecto routes_app

Este script proporciona diferentes opciones para ejecutar las pruebas:
- Pruebas unitarias únicamente
- Pruebas de integración únicamente
- Todas las pruebas
- Con cobertura de código
"""

import sys
import subprocess
import argparse


def run_command(command):
    """Ejecuta un comando y retorna el código de salida"""
    print(f"Ejecutando: {' '.join(command)}")
    result = subprocess.run(command, capture_output=False)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Ejecutar pruebas para routes_app")
    parser.add_argument(
        "--unit", action="store_true", help="Ejecutar solo pruebas unitarias"
    )
    parser.add_argument(
        "--api", action="store_true", help="Ejecutar solo pruebas de API/integración"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Ejecutar con reporte de cobertura"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Salida verbosa")
    parser.add_argument(
        "--file", "-f", help="Ejecutar un archivo específico de pruebas"
    )

    args = parser.parse_args()

    # Comando base de pytest
    cmd = ["python", "-m", "pytest"]

    # Agregar verbosidad si se solicita
    if args.verbose:
        cmd.append("-v")

    # Agregar cobertura si se solicita
    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=term-missing", "--cov-report=html"])

    # Determinar qué pruebas ejecutar
    if args.file:
        cmd.append(args.file)
    elif args.unit:
        cmd.extend(["-m", "unit"])
    elif args.api:
        cmd.extend(["-m", "api"])
    else:
        # Ejecutar todas las pruebas por defecto
        cmd.append("test/")

    # Ejecutar el comando
    return run_command(cmd)


if __name__ == "__main__":
    sys.exit(main())
