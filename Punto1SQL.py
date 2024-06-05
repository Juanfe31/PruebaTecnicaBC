import pandas as pd
import sqlite3

OC = pd.read_excel("Obligaciones_clientes.xlsx")
TP = pd.read_excel("tasas_productos.xlsx")

OC['fecha_desembolso'] = pd.to_datetime(OC['fecha_desembolso'])

conn = sqlite3.connect('clientes_tasa.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS tasas (
        cod_segmento TEXT,
        segmento TEXT,
        cod_subsegmento TEXT,
        calificacion_riesgos TEXT,
        tasa_cartera REAL,
        tasa_operacion_especifica REAL,
        tasa_hipotecario REAL,
        tasa_leasing REAL,
        tasa_sufi REAL,
        tasa_factoring REAL,
        tasa_tarjeta REAL,
        PRIMARY KEY (cod_segmento, cod_subsegmento, calificacion_riesgos)
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS obligaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        radicado BIGINT,
        num_documento BIGINT,
        cod_segm_tasa TEXT,
        cod_subsegm_tasa TEXT,
        cal_interna_tasa TEXT,
        id_producto TEXT,
        tipo_id_producto TEXT,
        valor_inicial REAL,
        fecha_desembolso TIMESTAMP,
        plazo REAL,
        cod_periodicidad DECIMAL(5,0),
        periodicidad TEXT,
        saldo_deuda REAL,
        modalidad TEXT,
        tipo_plazo TEXT,
        nombre_producto TEXT,
        FOREIGN KEY (cod_segm_tasa, cod_subsegm_tasa, cal_interna_tasa) REFERENCES tasas(cod_segmento, cod_subsegmento, calificacion_riesgos)
    )
''')

c.execute('ALTER TABLE obligaciones ADD COLUMN tasa_asignada REAL')
c.execute('ALTER TABLE obligaciones ADD COLUMN tasa_efectiva REAL')
c.execute('ALTER TABLE obligaciones ADD COLUMN valor_final REAL')


OC.to_sql('obligaciones', conn, if_exists='append', index=False)
TP.to_sql('tasas', conn, if_exists='append', index=False)


query_TP = "SELECT * FROM tasas"  
TP_df = pd.read_sql_query(query_TP, conn)

query_OC = "SELECT * FROM obligaciones" 
OC_df = pd.read_sql_query(query_OC, conn)

def get_nombre_producto(identificador):
    dividido = identificador.split("-")
    nombre_producto = dividido[-1].strip().lower().split()[0]
    return nombre_producto

def assign_nombre_producto(OC):
  OC["nombre_producto"] = OC["id_producto"].apply(get_nombre_producto)
  return OC

def assign_tasa_respectiva(OC, TP):
    def find_tasa(row):
        lookup_seg = row['cod_segm_tasa']
        lookup_subseg = row['cod_subsegm_tasa']
        lookup_cal = row['cal_interna_tasa']

        filtro_tasa = TP[(TP['cod_segmento'] == lookup_seg) &
                         (TP['cod_subsegmento'] == lookup_subseg) &
                         (TP['calificacion_riesgos'] == lookup_cal)]
        if not filtro_tasa.empty:
            return filtro_tasa.iloc[0]['tasa_' + row['nombre_producto']]
        else:
            return 0
    OC['tasa_asignada'] = OC.apply(find_tasa, axis=1)
    return OC
 
def assign_tasa_efectiva(OC):
    def find_tasa_efectiva(row):
        map_periodicidad = {
            'MENSUAL': 1,
            'BIMENSUAL': 2,
            'TRIMESTRAL': 3,
            'SEMESTRAL': 6,
            'ANUAL': 12
            }
        periodicidad = map_periodicidad[row['periodicidad']]
        n = 12/periodicidad
        t=row['tasa_asignada']
        return (1+ t)**(1/n)-1
    OC['tasa_efectiva'] = OC.apply(find_tasa_efectiva, axis=1)
    return OC

def assign_valor_final(OC):
    def find_valor_final(row):
        return row['valor_inicial']*row['tasa_efectiva']
    OC['valor_final'] = OC.apply(find_valor_final, axis=1)
    return OC

def agrupacion_cliente(OC):
    agrupado= OC.groupby('num_documento').agg({
    'valor_final': 'sum',
    'nombre_producto': 'count'
    }).reset_index()

    agrupado.rename(columns={'nombre_producto': 'cantidad_productos', 'valor_final': 'total_valor_final'}, inplace=True)
    return agrupado[agrupado['cantidad_productos'] >= 2]

OC_df=assign_nombre_producto(OC_df)
OC_df=assign_tasa_respectiva(OC_df, TP_df)
OC_df=assign_tasa_efectiva(OC_df)
OC_df=assign_valor_final(OC_df)
OCG_df=agrupacion_cliente(OC_df)

c.execute('''
    CREATE TABLE finales (
        id INTEGER PRIMARY KEY,
        num_documento TEXT,
        total_valor_final REAL,
        cantidad_productos INTEGER
    )
''')


OC_df.to_sql('obligaciones', conn, if_exists='replace', index=False)
TP_df.to_sql('tasas', conn, if_exists='replace', index=False)
OCG_df.to_sql('finales', conn, if_exists='replace', index=False)


