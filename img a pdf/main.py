import io
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response
from PIL import Image

app = FastAPI(title="Convertidor de Imagen a PDF")


@app.post("/convertir-pdf")
async def imagen_a_pdf(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(
            status_code=400, detail="No se proporcionó ningún archivo."
        )

    try:
        # 1. Leer los bytes
        contents = await file.read()

        # 2. Convertir imagen a RGB
        img = Image.open(io.BytesIO(contents)).convert("RGB")

        # 3. Guardar en buffer
        pdf_buffer = io.BytesIO()
        img.save(pdf_buffer, format="PDF")
        pdf_bytes = pdf_buffer.getvalue()  # Extraemos los bytes directamente

        # 4. Retornar los bytes directamente a n8n
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=convertido.pdf"
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al procesar la imagen: {str(e)}"
        )