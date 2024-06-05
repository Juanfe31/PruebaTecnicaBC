import pandas as pd

OC = pd.read_excel("Obligaciones_clientes.xlsx")
TP = pd.read_excel("tasas_productos.xlsx")

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

def main (OC, TP):
    OC= assign_nombre_producto(OC)
    OC= assign_tasa_respectiva(OC, TP)
    OC= assign_tasa_efectiva(OC)
    OC= assign_valor_final(OC)
    OCC= agrupacion_cliente(OC)
    
    with pd.ExcelWriter('ReporteTasasClientesPython.xlsx') as writer:
        OC.to_excel(writer, sheet_name='Obligaciones_clientes')
        OCC.to_excel(writer, sheet_name='Agrupado_clientes')
        TP.to_excel(writer, sheet_name='tasas_productos')

main(OC, TP)
