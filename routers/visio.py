import os
import shutil
import subprocess

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

router = APIRouter(prefix="/visio", tags=["visio"])


@router.post("/view")
async def view_visio(file: UploadFile = File(...)):
    # 1. Сохраняем входящий файл во временную папку
    temp_name = f"temp_{file.filename}"
    with open(temp_name, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 2. Вызываем LibreOffice для конвертации в PDF
        # На Mac путь обычно такой, если ставили официально
        soffice_path = '/Applications/LibreOffice.app/Contents/MacOS/soffice'

        result = subprocess.run([
            soffice_path,
            '--headless',
            '--convert-to', 'pdf',
            temp_name,
            '--outdir', '.'
        ], capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(status_code=500,
                                detail=f"Ошибка конвертации: {result.stderr}")

        # 3. Ищем созданный PDF (имя будет таким же, но с расширением .pdf)
        # Убираем любое исходное расширение и ставим .pdf
        base_name = os.path.splitext(temp_name)[0]
        pdf_path = f"{base_name}.pdf"

        if not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=500,
                detail="PDF файл не был создан")

        with open(pdf_path, "rb") as f:
            pdf_content = f.read()

        # 4. Чистим за собой
        os.remove(temp_name)
        os.remove(pdf_path)

        return Response(content=pdf_content, media_type="application/pdf")

    except Exception as e:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise HTTPException(status_code=500, detail=str(e))
