from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import zipfile
import os
import shutil
import uuid
import hashlib
import logging
from pathlib import Path
import redis
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

UPLOAD_DIR = Path("uploads")
ZIP_DIR = Path("zips")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ZIP_DIR.mkdir(parents=True, exist_ok=True)

REDIS_URL = os.getenv("REDIS_HOST", "redis://localhost:6379/0")

try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
    r.ping()
    logger.info("✅ Conectado ao Redis com sucesso!")
except redis.ConnectionError as e:
    logger.error(f"❌ Erro ao conectar ao Redis: {e}")
    raise SystemExit("❌ Falha crítica: Redis não está acessível. Encerrando aplicação.")

scheduler = BackgroundScheduler()
scheduler.start()


def generate_secure_token(package_id: str):
    return hashlib.sha256(package_id.encode()).hexdigest()[:16]


def delete_file(file_path, token):
    try:
        if Path(file_path).exists():
            os.remove(file_path)
            logger.info(f"🗑 Arquivo deletado: {file_path}")
        else:
            logger.warning(f"⚠️ Arquivo já foi removido: {file_path}")

        r.delete(token)
        logger.info(f"🔴 Token {token} removido do Redis")

    except Exception as e:
        logger.error(f"❌ Erro ao deletar arquivo: {e}")


@app.post("/upload/")
async def upload_files(files: list[UploadFile] = File(...)):
    if not files:
        return JSONResponse(status_code=400, content={"error": "Nenhum arquivo enviado."})

    try:
        package_id = str(uuid.uuid4())
        folder_path = UPLOAD_DIR / package_id
        folder_path.mkdir(parents=True, exist_ok=True)

        for file in files:
            file_path = folder_path / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        zip_filename = f"{package_id}.zip"
        zip_path = ZIP_DIR / zip_filename
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zipf:
            for file in folder_path.iterdir():
                zipf.write(file, arcname=file.name)

        shutil.rmtree(folder_path)

        secure_token = generate_secure_token(package_id)
        r.setex(secure_token, 7200, zip_path.as_posix())

        scheduler.add_job(delete_file, 'date', run_date=datetime.now() + timedelta(hours=2),
                          args=[zip_path, secure_token])

        logger.info(f"✅ Arquivo ZIP criado com sucesso: {zip_path}")
        return {
            "message": "Arquivo enviado com sucesso!",
            "download_link": f"https://sobe-ai.pedrovs.dev/download/{secure_token}"
        }

    except Exception as e:
        logger.error(f"❌ Erro ao processar upload: {e}")
        return JSONResponse(status_code=500, content={"error": "Erro interno ao processar o upload."})


@app.get("/download/{token}")
async def download_file(token: str):
    try:
        zip_path = r.get(token)
        if not zip_path or not Path(zip_path).exists():
            return JSONResponse(status_code=404, content={"error": "Arquivo expirado ou inválido"})

        return FileResponse(zip_path, filename=f"{token}.zip", media_type='application/zip')

    except redis.RedisError as e:
        logger.error(f"❌ Erro ao acessar o Redis: {e}")
        return JSONResponse(status_code=500, content={"error": "Erro interno ao acessar o Redis."})