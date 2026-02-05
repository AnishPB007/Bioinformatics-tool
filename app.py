from __future__ import annotations

import json
import mimetypes
import re
import subprocess
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

APP_ROOT = Path(__file__).parent
R_SCRIPT = APP_ROOT / "r_backend.R"
STATIC_ROOT = APP_ROOT / "static"
TEMPLATES_ROOT = APP_ROOT / "templates"


@dataclass
class TaskResult:
    title: str
    result: str
    details: Optional[str] = None


def normalize_sequence(sequence: str) -> str:
    cleaned = re.sub(r"\s+", "", sequence).upper()
    return re.sub(r"[^ACGTUN]", "", cleaned)


def gc_content_python(sequence: str) -> float:
    if not sequence:
        return 0.0
    gc_count = sum(1 for base in sequence if base in {"G", "C"})
    return round((gc_count / len(sequence)) * 100, 2)


def reverse_complement(sequence: str) -> str:
    complement = str.maketrans("ACGTUN", "TGCAAN")
    return sequence.translate(complement)[::-1]


def translate_sequence(sequence: str) -> str:
    codon_table = {
        "TTT": "F",
        "TTC": "F",
        "TTA": "L",
        "TTG": "L",
        "CTT": "L",
        "CTC": "L",
        "CTA": "L",
        "CTG": "L",
        "ATT": "I",
        "ATC": "I",
        "ATA": "I",
        "ATG": "M",
        "GTT": "V",
        "GTC": "V",
        "GTA": "V",
        "GTG": "V",
        "TCT": "S",
        "TCC": "S",
        "TCA": "S",
        "TCG": "S",
        "CCT": "P",
        "CCC": "P",
        "CCA": "P",
        "CCG": "P",
        "ACT": "T",
        "ACC": "T",
        "ACA": "T",
        "ACG": "T",
        "GCT": "A",
        "GCC": "A",
        "GCA": "A",
        "GCG": "A",
        "TAT": "Y",
        "TAC": "Y",
        "TAA": "*",
        "TAG": "*",
        "CAT": "H",
        "CAC": "H",
        "CAA": "Q",
        "CAG": "Q",
        "AAT": "N",
        "AAC": "N",
        "AAA": "K",
        "AAG": "K",
        "GAT": "D",
        "GAC": "D",
        "GAA": "E",
        "GAG": "E",
        "TGT": "C",
        "TGC": "C",
        "TGA": "*",
        "TGG": "W",
        "CGT": "R",
        "CGC": "R",
        "CGA": "R",
        "CGG": "R",
        "AGT": "S",
        "AGC": "S",
        "AGA": "R",
        "AGG": "R",
        "GGT": "G",
        "GGC": "G",
        "GGA": "G",
        "GGG": "G",
    }
    amino_acids = []
    for i in range(0, len(sequence) - 2, 3):
        codon = sequence[i : i + 3]
        amino_acids.append(codon_table.get(codon, "X"))
    return "".join(amino_acids)


def run_r_gc_content(sequence: str) -> Optional[float]:
    if not R_SCRIPT.exists():
        return None
    try:
        completed = subprocess.run(
            ["Rscript", str(R_SCRIPT), sequence],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    output = completed.stdout.strip()
    try:
        return float(output)
    except ValueError:
        return None


def detect_task(message: str) -> Optional[str]:
    if re.search(r"gc\s*content", message, re.IGNORECASE):
        return "gc_content"
    if re.search(r"reverse\s*complement", message, re.IGNORECASE):
        return "reverse_complement"
    if re.search(r"translate|protein", message, re.IGNORECASE):
        return "translate"
    return None


def extract_sequence(message: str) -> Optional[str]:
    match = re.search(r"([ACGTUNacgtun\s]{12,})", message)
    if not match:
        return None
    return normalize_sequence(match.group(1))


def answer_question(message: str) -> Dict[str, Any]:
    task = detect_task(message)
    sequence = extract_sequence(message)

    if task == "gc_content" and sequence:
        r_value = run_r_gc_content(sequence)
        gc_value = r_value if r_value is not None else gc_content_python(sequence)
        details = "Computed with R" if r_value is not None else "Computed with Python"
        return TaskResult(
            title="GC Content",
            result=f"{gc_value}%",
            details=f"Sequence length: {len(sequence)}. {details}.",
        ).__dict__

    if task == "reverse_complement" and sequence:
        return TaskResult(
            title="Reverse Complement",
            result=reverse_complement(sequence),
            details=f"Sequence length: {len(sequence)}.",
        ).__dict__

    if task == "translate" and sequence:
        return TaskResult(
            title="Protein Translation",
            result=translate_sequence(sequence),
            details="Translated in-frame from the first base (standard codon table).",
        ).__dict__

    knowledge = (
        "I can help with experimental design, omics analysis, assay selection, and"
        " interpretation. Ask me to summarize pathways, suggest controls, interpret"
        " sequencing metrics, or perform quick sequence calculations (GC content,"
        " reverse complement, translation)."
    )

    tools = (
        "Common tools include: wet lab (PCR/qPCR, CRISPR, flow cytometry,"
        " Western blot, ELISA, microscopy) and computational (BLAST, Bowtie,"
        " STAR, Seurat, DESeq2, GATK, Galaxy, Bioconductor). I can explain when"
        " to use each and interpret outputs."
    )

    response = {
        "title": "Biotechnology Assistant",
        "result": knowledge,
        "details": tools,
    }

    if task and not sequence:
        response["details"] = (
            "I can run that task. Please include the sequence (A/C/G/T/U) in your"
            " message so I can compute it directly."
        )

    if "workflow" in message.lower() or "protocol" in message.lower():
        response["result"] = (
            "Provide the goal, sample type, and constraints. I will draft a full"
            " workflow with controls, reagents, and analysis steps so you can run"
            " the experiment end-to-end."
        )

    return response


def build_task_response(task_name: str, sequence: str) -> Dict[str, Any]:
    if task_name == "gc_content" and sequence:
        r_value = run_r_gc_content(sequence)
        gc_value = r_value if r_value is not None else gc_content_python(sequence)
        details = "Computed with R" if r_value is not None else "Computed with Python"
        return {
            "title": "GC Content",
            "result": f"{gc_value}%",
            "details": f"Sequence length: {len(sequence)}. {details}.",
        }

    if task_name == "reverse_complement" and sequence:
        return {
            "title": "Reverse Complement",
            "result": reverse_complement(sequence),
            "details": f"Sequence length: {len(sequence)}.",
        }

    if task_name == "translate" and sequence:
        return {
            "title": "Protein Translation",
            "result": translate_sequence(sequence),
            "details": "Translated in-frame from the first base (standard codon table).",
        }

    return {"error": "Unsupported task or missing sequence."}


class BioinformaticsHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, status: int = 200) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_type, _ = mimetypes.guess_type(path.name)
        body = path.read_bytes()
        self.send_response(status)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_file(TEMPLATES_ROOT / "index.html")
            return
        if parsed.path.startswith("/static/"):
            file_path = STATIC_ROOT / parsed.path.replace("/static/", "", 1)
            self._send_file(file_path)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        payload = self._read_json()

        if parsed.path == "/ask":
            message = str(payload.get("message", "")).strip()
            if not message:
                self._send_json({"error": "Please enter a question or task."}, status=400)
                return
            response = answer_question(message)
            self._send_json(response)
            return

        if parsed.path == "/task":
            task_name = str(payload.get("task", "")).strip()
            sequence = normalize_sequence(str(payload.get("sequence", "")))
            response = build_task_response(task_name, sequence)
            status = 200 if "error" not in response else 400
            self._send_json(response, status=status)
            return

        self.send_error(HTTPStatus.NOT_FOUND)


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = HTTPServer((host, port), BioinformaticsHandler)
    print(f"Biotechnology assistant running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run_server()
