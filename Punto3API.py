from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

conn = sqlite3.connect('clientes_tasa.db')
c = conn.cursor()
app = FastAPI()

class ClienteConsulta(BaseModel):
    num_documento: str

class Obligacion(BaseModel):
    radicado: int
    num_documento: int
    cod_segm_tasa: str
    cod_subsegm_tasa: str
    cal_interna_tasa: str
    id_producto: str
    tipo_id_producto: str
    valor_inicial: float
    fecha_desembolso: str
    plazo: float
    cod_periodicidad: float
    periodicidad: str
    saldo_deuda: float
    modalidad: str
    tipo_plazo: str
    nombre_producto: str
    tasa_asignada: float
    tasa_efectiva: float
    valor_final: float

class Final(BaseModel):
    id: int
    num_documento: str
    total_valor_final: float
    cantidad_productos: int

@app.get("/obligaciones/{num_documento}")
async def get_obligaciones(num_documento: str):
    c.execute("SELECT nombre_producto, tasa_efectiva, valor_final FROM obligaciones WHERE num_documento=?", (num_documento,))
    data = c.fetchall()
    if not data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return data

@app.get("/finales/{num_documento}")
async def get_final(num_documento: str):
    c.execute("SELECT * FROM finales WHERE num_documento=?", (num_documento,))
    data = c.fetchone()
    if not data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)