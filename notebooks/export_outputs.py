#!/usr/bin/env python3
"""
Exportar SOLO los outputs de cada celda del notebook a HTML
Uso: python export_outputs.py eaui2026_analisis_bloques_ordenado.ipynb
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def export_notebook_outputs(notebook_path):
    """Extrae outputs de notebook y genera HTML"""

    notebook_file = Path(notebook_path)
    if not notebook_file.exists():
        print(f"❌ Archivo no encontrado: {notebook_path}")
        return

    with open(notebook_file, encoding='utf-8') as f:
        nb = json.load(f)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = notebook_file.stem + f'_outputs_{timestamp}.html'

    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Outputs</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; margin-bottom: 10px; font-size: 2em; }
        .timestamp {
            color: #999;
            font-size: 0.9em;
            margin-bottom: 30px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        .cell-block {
            background: white;
            margin-bottom: 20px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .cell-header {
            background: #f0f0f0;
            padding: 12px 15px;
            border-left: 4px solid #007bff;
            font-weight: 600;
            color: #333;
            font-size: 0.95em;
        }
        .cell-outputs { padding: 15px; }
        .output { margin-bottom: 15px; }
        .output-label {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        pre {
            background: #f8f8f8;
            border: 1px solid #e0e0e0;
            padding: 12px;
            border-radius: 3px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.4;
        }
        .output-stream { color: #333; }
        .output-error { background: #fff3cd; color: #856404; }
        img {
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 3px;
            margin: 10px 0;
        }
        table { width: 100%; border-collapse: collapse; font-size: 0.9em; }
        table th, table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        table th { background: #f5f5f5; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Outputs - """ + notebook_file.stem + """</h1>
        <div class="timestamp">Generado: """ + datetime.now().strftime('%d/%m/%Y %H:%M:%S') + """</div>
"""

    cell_count = 0
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            if 'outputs' in cell and cell['outputs']:
                cell_count += 1
                html_content += f"""        <div class="cell-block">
            <div class="cell-header">📍 Celda {i}</div>
            <div class="cell-outputs">
"""

                for output in cell['outputs']:
                    output_type = output.get('output_type', 'unknown')

                    if output_type == 'stream':
                        text = ''.join(output.get('text', []))
                        html_content += f"""                <div class="output">
                    <div class="output-label">• {output.get('name', 'stdout').upper()}</div>
                    <pre class="output-stream">{text}</pre>
                </div>
"""

                    elif output_type == 'execute_result':
                        data = output.get('data', {})
                        if 'text/plain' in data:
                            text = ''.join(data['text/plain']) if isinstance(data['text/plain'], list) else data['text/plain']
                            html_content += f"""                <div class="output">
                    <div class="output-label">• Resultado</div>
                    <pre>{text}</pre>
                </div>
"""

                    elif output_type == 'display_data':
                        data = output.get('data', {})
                        if 'image/png' in data:
                            img_data = data['image/png']
                            if isinstance(img_data, list):
                                img_data = ''.join(img_data)
                            html_content += f"""                <div class="output">
                    <div class="output-label">• Imagen</div>
                    <img src="data:image/png;base64,{img_data}" alt="Output">
                </div>
"""
                        elif 'text/html' in data:
                            html_data = ''.join(data['text/html']) if isinstance(data['text/html'], list) else data['text/html']
                            html_content += f"""                <div class="output">
                    <div class="output-label">• HTML</div>
                    <div style="border: 1px solid #ddd; padding: 10px; border-radius: 3px;">
                        {html_data}
                    </div>
                </div>
"""

                    elif output_type == 'error':
                        ename = output.get('ename', 'Error')
                        evalue = output.get('evalue', '')
                        traceback = ''.join(output.get('traceback', []))
                        html_content += f"""                <div class="output">
                    <div class="output-label">• {ename}</div>
                    <pre class="output-error">{evalue}\n{traceback}</pre>
                </div>
"""

                html_content += """            </div>
        </div>
"""

    html_content += f"""        <div class="timestamp" style="margin-top: 40px; border-top: 2px solid #ddd; border-bottom: none;">
            Total: <strong>{cell_count}</strong> celdas | {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Outputs exportados a: {output_file}")
    print(f"   Celdas: {cell_count}")
    print(f"   Tamaño: {len(html_content) / 1024:.1f} KB")

if __name__ == '__main__':
    notebook = sys.argv[1] if len(sys.argv) > 1 else 'eaui2026_analisis_bloques_ordenado.ipynb'
    export_notebook_outputs(notebook)
