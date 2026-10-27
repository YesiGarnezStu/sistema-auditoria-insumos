import uuid
import os
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP
from app.database import SessionLocal
from app.crud import tickets as crud_tickets
from app.crud import foods as crud_foods
from app.crud import food_images as crud_food_images
from app.schemas.purchase_tickets import PurchaseTicketCreate, PurchaseTicketUpdateOCR
from app.schemas.foods import FoodCreate
from app.schemas.food_images import FoodImageCreate

# Inicializamos el servidor FastMCP con su nombre identificador
mcp = FastMCP("SmartFridge-Agent-Server")

@mcp.tool()
def update_ticket_ocr(
    ticket_id: str,
    raw_text_ocr: str,
    store_name: Optional[str] = None,
    purchase_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Herramienta para que el Agente de IA guarde el texto OCR extraído y los metadatos
    de la tienda en el ticket de compra existente (tabla purchase_tickets), marcándolo como procesado por IA.
    
    Args:
        ticket_id: UUID del ticket creado previamente al subir la imagen.
        raw_text_ocr: Texto completo sin procesar extraído por OCR.
        store_name: Nombre identificado del supermercado (ej: 'Walmart', 'Costco').
        purchase_date: Fecha de compra identificada en formato 'YYYY-MM-DD'.
    """
    db = SessionLocal()
    try:
        parsed_date = None
        if purchase_date:
            try:
                parsed_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
            except ValueError:
                parsed_date = date.today()

        ocr_data = PurchaseTicketUpdateOCR(
            store_name=store_name,
            purchase_date=parsed_date,
            raw_text_ocr=raw_text_ocr,
            processed_by_ai=True,
        )

        ticket = crud_tickets.update_ticket_ocr(db=db, ticket_id=ticket_id, ocr_data=ocr_data)
        if not ticket:
            return {"status": "error", "message": f"Ticket con ID {ticket_id} no fue encontrado"}

        return {
            "status": "success",
            "message": f"Ticket {ticket.id} actualizado exitosamente",
            "ticket_id": str(ticket.id),
            "store_name": ticket.store_name,
            "purchase_date": str(ticket.purchase_date) if ticket.purchase_date else None,
            "processed_by_ai": ticket.processed_by_ai,
        }
    finally:
        db.close()

@mcp.tool()
def create_purchase_ticket(
    user_id: str,
    ticket_image_url: str,
    refrigerator_id: Optional[str] = None,
    store_name: Optional[str] = None,
    purchase_date: Optional[str] = None,
    raw_text_ocr: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Herramienta para crear directamente un registro maestro en 'purchase_tickets'
    si el ticket no fue precargado vía API REST.

    Args:
        user_id: UUID del usuario dueño.
        ticket_image_url: URL de la imagen en MinIO.
        refrigerator_id: UUID del refrigerador vinculado (opcional).
        store_name: Nombre de la tienda.
        purchase_date: Fecha de compra en formato 'YYYY-MM-DD'.
        raw_text_ocr: Texto OCR en crudo.
    """
    db = SessionLocal()
    try:
        parsed_date = None
        if purchase_date:
            try:
                parsed_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
            except ValueError:
                parsed_date = date.today()

        ticket_create = PurchaseTicketCreate(
            user_id=uuid.UUID(user_id),
            refrigerator_id=uuid.UUID(refrigerator_id) if refrigerator_id else None,
            store_name=store_name,
            purchase_date=parsed_date,
            ticket_image_url=ticket_image_url,
            raw_text_ocr=raw_text_ocr,
            processed_by_ai=True,
        )

        ticket = crud_tickets.create_ticket(db=db, ticket=ticket_create)
        return {
            "status": "success",
            "ticket_id": str(ticket.id),
            "store_name": ticket.store_name,
            "ticket_image_url": ticket.ticket_image_url,
        }
    finally:
        db.close()

@mcp.tool()
def add_food_to_refrigerator(
    refrigerator_id: str,
    name: str,
    category: Optional[str] = None,
    quantity: Optional[float] = 1.0,
    unit: Optional[str] = "pz",
    purchase_date: Optional[str] = None,
    expiration_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Herramienta para que el Agente de IA inserte un alimento detectado en la tabla 'foods'
    asociándolo al refrigerador correspondiente.
    
    Args:
        refrigerator_id: UUID del refrigerador donde se almacenará el producto.
        name: Nombre del producto (ej: 'Leche entera 1L', 'Manzanas Rojas').
        category: Categoría sugerida (ej: 'Lácteos', 'Frutas', 'Verduras', 'Carnes').
        quantity: Cantidad numérica detectada (ej: 1, 2.5).
        unit: Unidad de medida ('pz', 'kg', 'lt', 'paquete').
        purchase_date: Fecha de compra ('YYYY-MM-DD').
        expiration_date: Fecha de caducidad calculada o detectada ('YYYY-MM-DD').
    """
    db = SessionLocal()
    try:
        p_date = None
        if purchase_date:
            try:
                p_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
            except ValueError:
                p_date = date.today()

        exp_date = None
        if expiration_date:
            try:
                exp_date = datetime.strptime(expiration_date, "%Y-%m-%d").date()
            except ValueError:
                exp_date = None

        food_create = FoodCreate(
            refrigerator_id=uuid.UUID(refrigerator_id),
            name=name,
            category=category,
            quantity=quantity,
            unit=unit,
            purchase_date=p_date,
            expiration_date=exp_date,
            status="fresh",
        )

        food = crud_foods.create_food(db=db, food=food_create)
        return {
            "status": "success",
            "food_id": str(food.id),
            "name": food.name,
            "category": food.category,
            "quantity": float(food.quantity) if food.quantity is not None else 1.0,
            "unit": food.unit,
            "expiration_date": str(food.expiration_date) if food.expiration_date else None,
        }
    finally:
        db.close()

@mcp.tool()
def record_food_image_analysis(
    ticket_id: str,
    image_url: str,
    ocr_extracted_text: str,
    ai_analysis: str,
    food_id: Optional[str] = None,
    image_type: str = "ticket",
) -> Dict[str, Any]:
    """
    Herramienta para poblar la tabla 'food_images', vinculando la imagen del ticket
    con el análisis global de IA y el texto OCR extraído.
    
    Args:
        ticket_id: UUID del ticket de compra.
        image_url: URL de la imagen en MinIO.
        ocr_extracted_text: Texto OCR extraído.
        ai_analysis: Resumen o análisis del LLM (JSON o texto).
        food_id: UUID de un alimento en particular (opcional).
        image_type: Tipo de imagen ('ticket', 'food_item', 'receipt_crop').
    """
    db = SessionLocal()
    try:
        food_image_data = FoodImageCreate(
            ticket_id=uuid.UUID(ticket_id) if ticket_id else None,
            food_id=uuid.UUID(food_id) if food_id else None,
            image_url=image_url,
            image_type=image_type,
            ocr_extracted_text=ocr_extracted_text,
            ai_analysis=ai_analysis,
        )

        created_img = crud_food_images.create_food_image(db=db, food_image=food_image_data)
        return {
            "status": "success",
            "food_image_id": str(created_img.id),
            "ticket_id": str(created_img.ticket_id) if created_img.ticket_id else None,
            "image_url": created_img.image_url,
        }
    finally:
        db.close()

# Instancia perezosa (lazy) de EasyOCR para no ralentizar el inicio del servidor
_easyocr_reader = None

def get_easyocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        # Idiomas español e inglés, gpu=False por defecto para máxima portabilidad
        _easyocr_reader = easyocr.Reader(['es', 'en'], gpu=False)
    return _easyocr_reader

@mcp.tool()
def extract_text_with_easyocr(image_path: str) -> Dict[str, Any]:
    """
    Herramienta local de OCR usando la librería EasyOCR.
    Extrae texto de tickets o recibos de forma local y eficiente,
    evitando enviar imágenes completas al LLM y ahorrando tokens de visión.
    
    Args:
        image_path: Ruta local al archivo de imagen en el disco.
    """
    if not os.path.exists(image_path):
        return {
            "status": "error",
            "message": f"El archivo de imagen no existe en la ruta: {image_path}"
        }

    try:
        reader = get_easyocr_reader()
        detected_lines = reader.readtext(image_path, detail=0)
        raw_text = "\n".join(detected_lines)
        return {
            "status": "success",
            "lines_count": len(detected_lines),
            "raw_text_ocr": raw_text,
            "detected_lines": detected_lines,
            "engine": "easyocr_local",
        }
    except ImportError:
        return {
            "status": "warning",
            "message": "Librería EasyOCR no disponible aún en el entorno.",
            "raw_text_ocr": (
                "SUPERMERCADO CENTRAL\n"
                "1x LECHE DESLACTOSADA 1L $31.00\n"
                "2x YOGURT NATURAL 150G $38.00\n"
                "1x MANZANAS 1KG $45.00\n"
                "TOTAL: $114.00"
            ),
            "engine": "simulated_fallback"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al procesar la imagen con EasyOCR: {str(e)}"
        }

# ==============================================================================
# HERRAMIENTAS DE AUDITORÍA DE RED CON PYTHON-NMAP
# ==============================================================================

def _ensure_nmap_in_path():
    """Asegura que el binario de nmap esté presente en la variable de entorno PATH."""
    candidate_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nmap", "nmap-7.92"),
        r"C:\Program Files\Nmap",
        r"C:\Program Files (x86)\Nmap",
    ]
    current_path = os.environ.get("PATH", "")
    for cp in candidate_paths:
        if os.path.exists(os.path.join(cp, "nmap.exe")) and cp.lower() not in current_path.lower():
            os.environ["PATH"] = cp + os.pathsep + current_path
            current_path = os.environ["PATH"]
            break

def _validate_scan_target(target: str) -> bool:
    """Valida que el objetivo sea un hostname, IP o rango CIDR seguro sin caracteres maliciosos."""
    import re
    if not target or not isinstance(target, str):
        return False
    # Rechazar caracteres de inyección de shell o comandos
    if re.search(r"[;&|`$<>\r\n\"\']", target):
        return False
    # Permitir IPs, rangos CIDR, localhost y dominios alfanuméricos válidos
    pattern = r"^[a-zA-Z0-9\.\-\_\/]+$"
    return bool(re.match(pattern, target.strip()))

@mcp.tool()
def scan_network(
    target: str = "127.0.0.1",
    ports: Optional[str] = "21,22,23,25,53,80,110,135,139,443,445,1433,3306,3389,5432,8000,8080,9000",
    scan_type: str = "ports",
    custom_args: Optional[str] = None
) -> Dict[str, Any]:
    """
    Herramienta de auditoría de red que ejecuta escaneos reales utilizando python-nmap.
    Permite detectar hosts activos, puertos abiertos, servicios en ejecución y versiones.
    
    Args:
        target: IP objetivo, rango CIDR o nombre de host (ej. '127.0.0.1', 'localhost', '192.168.0.0/24').
        ports: Lista o rango de puertos separados por coma o guion (ej. '80,443,8000', '1-1024').
        scan_type: Tipo de escaneo ('quick', 'ports', 'service_version', 'ping_scan').
        custom_args: Argumentos adicionales seguros de Nmap (ej. '-sT -Pn -T4').
    """
    _ensure_nmap_in_path()
    
    clean_target = target.strip()
    if not _validate_scan_target(clean_target):
        return {
            "status": "error",
            "message": f"Objetivo inválido o sospechoso: '{target}'. Utilice una IP, hostname o CIDR válido sin caracteres especiales."
        }

    try:
        import nmap
    except ImportError:
        return {
            "status": "error",
            "message": "La librería 'python-nmap' no está instalada. Ejecute 'pip install python-nmap'."
        }

    # Configuración de argumentos seguros adaptados a Windows (usando TCP connect -sT por defecto para no requerir privilegios de kernel)
    base_args = "-sT -Pn -T4"
    if scan_type == "quick":
        nmap_args = f"-F {base_args}"
        target_ports = None
    elif scan_type == "service_version":
        nmap_args = f"-sV --version-light {base_args}"
        target_ports = ports
    elif scan_type == "ping_scan":
        nmap_args = "-sn -PE -T4"
        target_ports = None
    else:  # scan_type == 'ports'
        nmap_args = base_args
        target_ports = ports

    if custom_args and _validate_scan_target(custom_args):
        nmap_args = f"{nmap_args} {custom_args}"

    try:
        scanner = nmap.PortScanner()
        start_time = datetime.now()
        scan_raw = scanner.scan(hosts=clean_target, ports=target_ports, arguments=nmap_args)
        elapsed = (datetime.now() - start_time).total_seconds()

        hosts_results = []
        total_open_ports = 0

        for host_ip in scanner.all_hosts():
            host_data = scanner[host_ip]
            host_state = host_data.state()
            hostnames = [h.get("name", "") for h in host_data.hostnames() if h.get("name")]

            tcp_ports_list = []
            if "tcp" in host_data:
                for port_num, pinfo in host_data["tcp"].items():
                    p_state = pinfo.get("state", "unknown")
                    if p_state == "open":
                        total_open_ports += 1
                    tcp_ports_list.append({
                        "port": port_num,
                        "protocol": "tcp",
                        "state": p_state,
                        "service": pinfo.get("name", "unknown"),
                        "product": pinfo.get("product", ""),
                        "version": pinfo.get("version", ""),
                        "extrainfo": pinfo.get("extrainfo", ""),
                        "cpe": pinfo.get("cpe", "")
                    })

            udp_ports_list = []
            if "udp" in host_data:
                for port_num, pinfo in host_data["udp"].items():
                    p_state = pinfo.get("state", "unknown")
                    if p_state == "open":
                        total_open_ports += 1
                    udp_ports_list.append({
                        "port": port_num,
                        "protocol": "udp",
                        "state": p_state,
                        "service": pinfo.get("name", "unknown"),
                        "product": pinfo.get("product", ""),
                        "version": pinfo.get("version", ""),
                    })

            hosts_results.append({
                "ip": host_ip,
                "hostnames": hostnames,
                "state": host_state,
                "tcp_ports": tcp_ports_list,
                "udp_ports": udp_ports_list,
                "open_ports_count": len([p for p in tcp_ports_list if p["state"] == "open"])
            })

        # Evaluación de riesgos
        findings = []
        for h in hosts_results:
            for p in h["tcp_ports"]:
                port_num = p["port"]
                if p["state"] == "open":
                    if port_num in (135, 139, 445):
                        findings.append({
                            "severity": "ALTO",
                            "port": port_num,
                            "service": p["service"],
                            "description": f"Servicio SMB/RPC expuesto en el puerto {port_num}. Puede permitir enumeración de red o ataques de movimientos laterales si no está segmentado."
                        })
                    elif port_num in (3306, 5432, 1433, 27017):
                        findings.append({
                            "severity": "MEDIO",
                            "port": port_num,
                            "service": p["service"],
                            "description": f"Puerto de base de datos ({p['service']}) abierto. Verificar que requiera contraseñas robustas y no esté expuesto a redes públicas."
                        })
                    elif port_num in (21, 23):
                        findings.append({
                            "severity": "ALTO",
                            "port": port_num,
                            "service": p["service"],
                            "description": f"Protocolo sin cifrar ({p['service']}) en el puerto {port_num}. Transmite credenciales en texto plano; migrar a SSH/SFTP."
                        })
                    elif port_num in (80, 8080, 8000, 9000):
                        findings.append({
                            "severity": "BAJO",
                            "port": port_num,
                            "service": p["service"],
                            "description": f"Servidor web / API HTTP detectado en el puerto {port_num} ({p.get('product', '')}). Comprobar cabeceras de seguridad y autenticación."
                        })

        return {
            "status": "success",
            "target": clean_target,
            "command": scan_raw.get("nmap", {}).get("command_line", f"nmap {nmap_args} {clean_target}"),
            "nmap_version": scanner.nmap_version(),
            "elapsed_seconds": round(elapsed, 2),
            "hosts_up": len([h for h in hosts_results if h["state"] == "up"]),
            "total_open_ports": total_open_ports,
            "hosts": hosts_results,
            "security_findings": findings
        }

    except nmap.PortScannerError as pse:
        return {
            "status": "error",
            "message": f"Error de Nmap al ejecutar el escaneo: {str(pse)}. Verifique la disponibilidad de nmap en el sistema."
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Fallo inesperado durante el escaneo de red: {str(exc)}"
        }

@mcp.tool()
def generate_network_audit_report(
    scan_results: Dict[str, Any],
    report_title: str = "Auditoría de Seguridad y Escaneo de Red con Nmap"
) -> Dict[str, Any]:
    """
    Genera un informe técnico y ejecutivo en formato Markdown a partir de los resultados
    de un escaneo de red de Nmap, y lo guarda en disco en la carpeta de reportes.
    
    Args:
        scan_results: Diccionario con la salida estructurada de la herramienta 'scan_network'.
        report_title: Título personalizado para el encabezado del reporte.
    """
    if not isinstance(scan_results, dict) or scan_results.get("status") != "success":
        return {
            "status": "error",
            "message": "Los datos de escaneo suministrados no son válidos o reportan un estado de error."
        }

    target = scan_results.get("target", "N/A")
    command = scan_results.get("command", "N/A")
    elapsed = scan_results.get("elapsed_seconds", 0)
    hosts_up = scan_results.get("hosts_up", 0)
    total_open = scan_results.get("total_open_ports", 0)
    findings = scan_results.get("security_findings", [])
    hosts = scan_results.get("hosts", [])

    # Calcular nivel de riesgo global
    severities = [f.get("severity", "BAJO") for f in findings]
    if "ALTO" in severities:
        risk_level = "ALTO ⚠️"
    elif "MEDIO" in severities:
        risk_level = "MEDIO ⚡"
    elif total_open > 0:
        risk_level = "BAJO ℹ️"
    else:
        risk_level = "MÍNIMO / SEGURO ✅"

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Construir documento Markdown
    md_lines = [
        f"# 🛡️ {report_title}",
        f"**Fecha y Hora:** {now_str}  ",
        f"**Objetivo Evaluado:** `{target}`  ",
        f"**Nivel de Riesgo Global:** **{risk_level}**  ",
        f"**Tiempo de Escaneo:** `{elapsed} segundos`  ",
        f"**Comando Ejecutado:** `{command}`  ",
        "",
        "---",
        "",
        "## 1. Resumen Ejecutivo",
        f"Se realizó una auditoría de reconocimiento de servicios sobre el objetivo `{target}`. "
        f"Se detectaron **{hosts_up} host(s) activo(s)** y un total de **{total_open} puerto(s) en estado abierto**.",
        "",
        f"- **Hosts activos:** {hosts_up}",
        f"- **Puertos abiertos:** {total_open}",
        f"- **Hallazgos de seguridad identificados:** {len(findings)}",
        "",
        "---",
        "",
        "## 2. Detalle de Hosts y Puertos Detectados",
    ]

    for h in hosts:
        ip = h.get("ip")
        hnames = ", ".join(h.get("hostnames", [])) or "Sin hostname DNS"
        md_lines.append(f"### Host: `{ip}` ({hnames})")
        md_lines.append(f"**Estado:** `{h.get('state', 'unknown')}` | **Puertos abiertos:** {h.get('open_ports_count', 0)}")
        md_lines.append("")
        md_lines.append("| Puerto | Protocolo | Estado | Servicio | Producto / Versión |")
        md_lines.append("| :--- | :---: | :---: | :--- | :--- |")

        all_p = h.get("tcp_ports", []) + h.get("udp_ports", [])
        if not all_p:
            md_lines.append("| - | - | Sin puertos abiertos | - | - |")
        else:
            for p in all_p:
                port_str = str(p.get("port"))
                proto = p.get("protocol", "tcp").upper()
                st = p.get("state", "unknown")
                svc = p.get("service", "unknown")
                prod = f"{p.get('product', '')} {p.get('version', '')}".strip() or "N/D"
                md_lines.append(f"| `{port_str}` | {proto} | **{st}** | {svc} | {prod} |")
        md_lines.append("")

    md_lines.append("---")
    md_lines.append("")
    md_lines.append("## 3. Hallazgos y Evaluación de Seguridad")
    if not findings:
        md_lines.append("✅ **No se detectaron servicios de riesgo crítico o puertos vulnerables conocidos en el escaneo.**")
    else:
        for idx, f in enumerate(findings, 1):
            md_lines.append(f"### Hallazgo #{idx}: [{f['severity']}] Puerto `{f['port']}` ({f['service']})")
            md_lines.append(f"**Descripción:** {f['description']}")
            md_lines.append("")

    md_lines.append("---")
    md_lines.append("")
    md_lines.append("## 4. Recomendaciones de Remediación")
    md_lines.append("1. **Filtrado de Puertos Administrativos:** Aplicar reglas de firewall perimetral o de host (Windows Defender Firewall) para bloquear conexiones entrantes a puertos como 135, 139, 445 desde redes no confiables.")
    md_lines.append("2. **Principio de Mínimo Privilegio:** Cerrar cualquier servicio de depuración o de base de datos que no deba estar expuesto directamente a la red.")
    md_lines.append("3. **Cifrado de Comunicaciones:** Asegurar que todos los servicios web y APIs implementen TLS/HTTPS en lugar de HTTP plano.")
    md_lines.append("4. **Auditorías Periódicas:** Programar escaneos regulares desde este agente de IA para detectar cambios en la superficie de ataque del laboratorio.")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append(f"*Reporte generado automáticamente por el Agente de Auditoría de Red con FastMCP y python-nmap.*")

    report_content = "\n".join(md_lines)

    # Guardar en archivo
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_filename = f"auditoria_{target.replace('/', '_').replace(':', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path = os.path.join(reports_dir, report_filename)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return {
        "status": "success",
        "report_file": report_path,
        "filename": report_filename,
        "risk_level": risk_level,
        "markdown_content": report_content
    }

if __name__ == "__main__":
    # Inicia el servidor FastMCP usando transporte estándar stdio para agentes de IA
    mcp.run()

