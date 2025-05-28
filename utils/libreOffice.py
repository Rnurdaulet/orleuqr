import subprocess
from pathlib import Path

def convert_docx_to_pdf(input_path: Path, output_dir: Path) -> Path | None:
    result = subprocess.run([
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "--headless", "--convert-to", "pdf",
        str(input_path), "--outdir", str(output_dir)
    ], capture_output=True)

    if result.returncode == 0:
        return output_dir / (input_path.stem + ".pdf")
    else:
        print("LibreOffice error:", result.stderr.decode())
        return None
