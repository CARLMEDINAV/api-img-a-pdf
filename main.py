import io
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from PIL import Image

app = FastAPI(title="Convertidor de Imagen a PDF")


@app.post("/convertir-pdf")
async def imagen_a_pdf(file: UploadFile = File(...)):
    # 1. Validación estricta del archivo de entrada
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No se proporcionó ningún archivo."
        )
    
    # Validar que sea una imagen admitida antes de procesar
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato no soportado. Debe ser una imagen JPG, JPEG o PNG."
        )

    img = None
    pdf_buffer = None

    try:
        # 2. Leer los bytes en memoria RAM
        contents = await file.read()

        # 3. Convertir imagen a RGB de forma volátil
        img = Image.open(io.BytesIO(contents)).convert("RGB")

        # 4. Guardar en un buffer en memoria
        pdf_buffer = io.BytesIO()
        img.save(pdf_buffer, format="PDF")
        pdf_bytes = pdf_buffer.getvalue()

        # 5. Retornar los bytes directamente a n8n de forma segura
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=convertido.pdf"
            },
        )

    except Exception as e:
        # 6. Seguridad de Logs: Ocultamos el mensaje de error técnico 'str(e)' del cliente externo
        print(f"⚠️ Error interno en Convertidor: Ocurrido durante la transformación a PDF.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error interno al procesar y convertir la imagen a PDF."
        )

    finally:
        # 7. Garantía de Destrucción: Forzar el cierre de flujos de memoria en Render
        if img:
            img.close()
        if pdf_buffer:
            pdf_buffer.close()
        await file.close()
