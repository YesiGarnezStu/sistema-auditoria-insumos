import os
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from app.schemas.network_audit import NetworkScanRequest, NetworkScanResponse
from app.mcp_server import scan_network, generate_network_audit_report

router = APIRouter(
    prefix="/audit",
    tags=["Auditoría de Redes (Nmap & IA)"]
)

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "reports")

@router.post("/scan", response_model=NetworkScanResponse, status_code=status.HTTP_200_OK)
def run_network_audit(request: NetworkScanRequest):
    """
    Ejecuta un escaneo real de red utilizando python-nmap e interpreta
    la superficie de ataque generando un informe de seguridad.
    """
    scan_res = scan_network(
        target=request.target,
        ports=request.ports,
        scan_type=request.scan_type
    )

    if scan_res.get("status") != "success":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=scan_res.get("message", "Error al ejecutar el escaneo.")
        )

    report_file = None
    risk_level = None

    if request.generate_report:
        report_res = generate_network_audit_report(
            scan_results=scan_res,
            report_title=f"Auditoría API - {request.target}"
        )
        if report_res.get("status") == "success":
            report_file = report_res.get("filename")
            risk_level = report_res.get("risk_level")

    return NetworkScanResponse(
        status="success",
        target=scan_res.get("target"),
        hosts_up=scan_res.get("hosts_up", 0),
        total_open_ports=scan_res.get("total_open_ports", 0),
        elapsed_seconds=scan_res.get("elapsed_seconds", 0.0),
        security_findings=scan_res.get("security_findings", []),
        report_file=report_file,
        risk_level=risk_level
    )

@router.get("/reports", response_model=List[str])
def list_audit_reports():
    """Lista todos los reportes de auditoría generados en formato Markdown."""
    if not os.path.exists(REPORTS_DIR):
        return []
    return [f for f in os.listdir(REPORTS_DIR) if f.endswith(".md")]

@router.get("/reports/{filename}")
def get_audit_report_content(filename: str):
    """Obtiene el contenido completo de un reporte de auditoría en texto Markdown."""
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(REPORTS_DIR, safe_filename)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reporte '{filename}' no encontrado."
        )
    with open(file_path, "r", encoding="utf-8") as f:
        return {"filename": safe_filename, "content": f.read()}
