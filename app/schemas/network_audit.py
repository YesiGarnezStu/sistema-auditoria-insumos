from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class NetworkScanRequest(BaseModel):
    target: str = Field("127.0.0.1", description="IP, hostname o rango CIDR a escanear")
    ports: Optional[str] = Field("21,22,23,25,53,80,110,135,139,443,445,1433,3306,3389,5432,8000,8080,9000", description="Puertos separados por comas o rango")
    scan_type: str = Field("ports", description="Tipo de escaneo: 'quick', 'ports', 'service_version', 'ping_scan'")
    generate_report: bool = Field(True, description="Si es True, genera el reporte Markdown automáticamente")

class NetworkScanResponse(BaseModel):
    status: str
    target: str
    hosts_up: int
    total_open_ports: int
    elapsed_seconds: float
    security_findings: List[Dict[str, Any]]
    report_file: Optional[str] = None
    risk_level: Optional[str] = None
