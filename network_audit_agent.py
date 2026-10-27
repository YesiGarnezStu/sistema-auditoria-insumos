"""
Agente de Inteligencia Artificial para Auditoría de Red y Ciberseguridad.
Conectado mediante FastMCP y python-nmap para escanear redes de laboratorio,
interpretar resultados reales y redactar reportes de seguridad.
"""
import os
import sys
import re
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

# Asegurar path del proyecto y codificación UTF-8 en Windows
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

# Importar las herramientas expuestas por FastMCP
from app.mcp_server import scan_network, generate_network_audit_report

class NetworkAuditAgent:
    """
    Agente de IA especializado en auditoría y reconocimiento de redes.
    Interpreta instrucciones en lenguaje natural, ejecuta escaneos con Nmap
    a través de FastMCP, analiza la superficie de ataque y genera reportes.
    """

    def __init__(self, name: str = "NetAudit-Agent"):
        self.name = name

    def parse_natural_language_query(self, query: str) -> Dict[str, Any]:
        """
        Interpreta la intención del usuario a partir de texto en lenguaje natural.
        Extrae el host objetivo, lista de puertos y tipo de escaneo.
        """
        query_clean = query.strip()
        params = {
            "target": "127.0.0.1",
            "ports": "21,22,23,25,53,80,110,135,139,443,445,1433,3306,3389,5432,8000,8080,9000",
            "scan_type": "ports",
            "explanation": ""
        }

        # 1. Extracción de IP o Hostname
        ip_match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b", query_clean)
        if ip_match:
            params["target"] = ip_match.group(0)
        elif "localhost" in query_clean.lower():
            params["target"] = "127.0.0.1"

        # 2. Extracción de Puertos específicos (ej. "puertos 80, 443, 8000" o "puerto 3306")
        ports_match = re.search(r"(?:puertos?|ports?)\s*([0-9,\s\-]+)", query_clean, re.IGNORECASE)
        if ports_match:
            raw_ports = ports_match.group(1).replace(" ", "")
            # Limpiar comas duplicadas o finales
            clean_ports = ",".join([p for p in raw_ports.split(",") if p])
            if clean_ports:
                params["ports"] = clean_ports

        # 3. Detección de tipo de escaneo
        q_lower = query_clean.lower()
        if "rápido" in q_lower or "rapido" in q_lower or "quick" in q_lower or "top" in q_lower:
            params["scan_type"] = "quick"
        elif "versión" in q_lower or "version" in q_lower or "servicio" in q_lower:
            params["scan_type"] = "service_version"
        elif "ping" in q_lower or "descubrimiento" in q_lower or "discovery" in q_lower:
            params["scan_type"] = "ping_scan"

        params["explanation"] = (
            f"Instrucción interpretada: Escanear objetivo '{params['target']}' "
            f"con modo '{params['scan_type']}' "
            f"{'en puertos ' + params['ports'] if params['scan_type'] != 'quick' else '(top ports)'}."
        )
        return params

    def analyze_results_with_ai(self, scan_data: Dict[str, Any]) -> str:
        """
        Analizador de seguridad heurístico e inteligente.
        Examina el estado de los puertos y servicios descubiertos por Nmap
        y genera un diagnóstico técnico sobre el nivel de exposición.
        """
        if scan_data.get("status") != "success":
            return f"❌ No se pudo completar el análisis debido a un error: {scan_data.get('message')}"

        target = scan_data.get("target")
        hosts = scan_data.get("hosts", [])
        total_open = scan_data.get("total_open_ports", 0)
        findings = scan_data.get("security_findings", [])

        analysis_lines = [
            f"🤖 [{self.name}]: He finalizado el análisis del escaneo sobre `{target}`.",
            f"📊 Hosts detectados: {len(hosts)} | Puertos abiertos totales: {total_open}",
            ""
        ]

        if total_open == 0:
            analysis_lines.append("🛡️ **Diagnóstico:** El host no tiene puertos abiertos en el rango evaluado (o está protegido por filtrado de firewall).")
            analysis_lines.append("✅ **Riesgo:** MÍNIMO.")
            return "\n".join(analysis_lines)

        analysis_lines.append("🔍 **Evaluación de Servicios Expuestos:**")
        for h in hosts:
            for p in h.get("tcp_ports", []):
                if p["state"] == "open":
                    svc_desc = f"Puerto {p['port']}/TCP ({p['service']})"
                    if p.get("product"):
                        svc_desc += f" -> Software: {p['product']} {p.get('version', '')}"
                    analysis_lines.append(f"  • {svc_desc}")

        analysis_lines.append("")
        if findings:
            analysis_lines.append(f"⚠️ **Riesgos y Vulnerabilidades Potenciales ({len(findings)} detectados):**")
            for f in findings:
                analysis_lines.append(f"  • [{f['severity']}] Puerto {f['port']} ({f['service']}): {f['description']}")
        else:
            analysis_lines.append("✅ No se detectaron puertos críticos de alto riesgo comúnmente explotados.")

        return "\n".join(analysis_lines)

    def run_audit(self, target: str = "127.0.0.1", ports: Optional[str] = None, scan_type: str = "ports", custom_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Flujo de ejecución completo:
        1. Invoca la tool FastMCP scan_network.
        2. Analiza los resultados mediante el motor de IA.
        3. Invoca la tool FastMCP generate_network_audit_report.
        4. Retorna el resultado consolidado.
        """
        print(f"\n" + "="*70)
        print(f"🚀 [{self.name}] INICIANDO AUDITORÍA DE RED")
        print(f"🎯 Objetivo: {target}")
        print(f"🔌 Modo: {scan_type} | Puertos: {ports or 'Por defecto'}")
        print("="*70 + "\n")

        # Paso 1: Escaneo real con la tool FastMCP
        print(f"📡 [Paso 1] Ejecutando herramienta FastMCP 'scan_network'...")
        scan_results = scan_network(
            target=target,
            ports=ports,
            scan_type=scan_type
        )

        if scan_results.get("status") != "success":
            print(f"❌ Error durante el escaneo: {scan_results.get('message')}")
            return scan_results

        print(f"✅ Escaneo completado en {scan_results.get('elapsed_seconds')}s.")
        print(f"   Comando Nmap real: {scan_results.get('command')}")
        print(f"   Puertos abiertos detectados: {scan_results.get('total_open_ports')}")

        # Paso 2: Análisis inteligente de la superficie de ataque
        print(f"\n🧠 [Paso 2] Agente analizando postura de seguridad...")
        ai_summary = self.analyze_results_with_ai(scan_results)
        print(ai_summary)

        # Paso 3: Generación del Reporte formal de Auditoría
        print(f"\n📝 [Paso 3] Ejecutando herramienta FastMCP 'generate_network_audit_report'...")
        report_title = custom_title or f"Reporte de Auditoría de Red - {target}"
        report_output = generate_network_audit_report(
            scan_results=scan_results,
            report_title=report_title
        )

        if report_output.get("status") == "success":
            print(f"✅ Reporte generado y guardado en:")
            print(f"   📄 Archivo: {report_output.get('report_file')}")
            print(f"   🛡️ Nivel de Riesgo Global: {report_output.get('risk_level')}")
        else:
            print(f"⚠️ Aviso al generar reporte: {report_output.get('message')}")

        print("\n" + "="*70)
        print(f"🏁 AUDITORÍA COMPLETADA EXITOSAMENTE")
        print("="*70 + "\n")

        return {
            "status": "success",
            "scan_data": scan_results,
            "ai_analysis": ai_summary,
            "report_data": report_output
        }

    def process_instruction(self, instruction: str) -> Dict[str, Any]:
        """
        Punto de entrada para recibir instrucciones en lenguaje natural.
        """
        print(f"💬 Instrucción recibida: \"{instruction}\"")
        parsed = self.parse_natural_language_query(instruction)
        print(f"💡 {parsed['explanation']}")
        return self.run_audit(
            target=parsed["target"],
            ports=parsed["ports"],
            scan_type=parsed["scan_type"],
            custom_title=f"Auditoría Solicitada: {instruction[:50]}"
        )

def main():
    parser = argparse.ArgumentParser(description="Agente de IA para Auditoría de Red con FastMCP y python-nmap")
    parser.add_argument("--target", default="127.0.0.1", help="IP o hostname a auditar (ej. 127.0.0.1, 192.168.0.1)")
    parser.add_argument("--ports", default="21,22,23,25,53,80,110,135,139,443,445,1433,3306,3389,5432,8000,8080,9000", help="Puertos a escanear")
    parser.add_argument("--type", default="ports", choices=["quick", "ports", "service_version", "ping_scan"], help="Tipo de escaneo")
    parser.add_argument("--query", help="Instrucción en lenguaje natural (ej. 'Escanear localhost en puertos 80 y 443')")
    parser.add_argument("--interactive", action="store_true", help="Modo interactivo en consola")
    args = parser.parse_args()

    agent = NetworkAuditAgent()

    if args.interactive:
        print("\n=== AGENTE DE AUDITORÍA DE RED (MODO INTERACTIVO) ===")
        print("Escribe tus instrucciones en lenguaje natural (ej. 'Escanear localhost', 'Auditar 192.168.0.1 en puertos 80,443').")
        print("Escribe 'salir' o 'exit' para terminar.\n")
        while True:
            try:
                user_input = input("NetAudit> ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("salir", "exit", "quit", "q"):
                    print("👋 Cerrando sesión del agente.")
                    break
                agent.process_instruction(user_input)
            except KeyboardInterrupt:
                print("\n👋 Sesión interrumpida por el usuario.")
                break
            except Exception as e:
                print(f"❌ Error durante el procesamiento: {e}\n")
    elif args.query:
        agent.process_instruction(args.query)
    else:
        agent.run_audit(target=args.target, ports=args.ports, scan_type=args.type)

if __name__ == "__main__":
    main()
