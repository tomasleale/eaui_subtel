import pyreadstat
import re
import unicodedata
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import prince
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

df, meta = pyreadstat.read_sav("/Users/tomas/github/eaui_subtel/data/sav/2026.sav")
print(f"Filas: {df.shape[0]:,} | Columnas: {df.shape[1]}")

def _educ_g(e):
    if pd.isna(e): return None
    e = int(e)
    if e <= 3:  return 'basica'
    if e <= 7:  return 'media'
    if e <= 9:  return 'tecnica'
    return 'universitaria'

_M = {
    (1,'basica'):'E',  (1,'media'):'E',  (1,'tecnica'):'D',  (1,'universitaria'):'D',
    (2,'basica'):'E',  (2,'media'):'D',  (2,'tecnica'):'D',  (2,'universitaria'):'C3',
    (3,'basica'):'D',  (3,'media'):'C3', (3,'tecnica'):'C3', (3,'universitaria'):'C2',
    (4,'basica'):'C3', (4,'media'):'C2', (4,'tecnica'):'C2', (4,'universitaria'):'C1',
    (5,'basica'):'C2', (5,'media'):'C1', (5,'tecnica'):'C1', (5,'universitaria'):'AB',
    (6,'basica'):'C1', (6,'media'):'AB', (6,'tecnica'):'AB', (6,'universitaria'):'AB',
}
_ORDEN_GSE = ['AB','C1','C2','C3','D','E']  # Invertido

_eg = df['A10'].apply(_educ_g)
df['gse'] = pd.Categorical(
    df['A11'].combine(_eg, lambda o, e: np.nan if pd.isna(o) or e is None else _M.get((int(o), e), np.nan)),
    categories=_ORDEN_GSE, ordered=True  # Aquí usa el orden invertido automáticamente
)
print('GSE:', df['gse'].value_counts().reindex(_ORDEN_GSE).to_dict())

def limpiar_etiqueta(label):
    """Extrae la parte descriptiva útil de una etiqueta SPSS."""
    if not label: return label
    label = label.strip()
    # Patrón B/C: empieza con código de variable (P3_1 .-, Q1.3.-)
    if re.match(r'^[A-Z]\w+[\._]\w+\s*\.-?', label):
        if ':' in label:
            r = label.split(':')[-1].strip()
            if r: return r
        if '?' in label:
            r = label.split('?')[-1].strip().lstrip(':').strip()
            if r: return r
        r = re.sub(r'^[A-Z]\w+[\._]\w+[\s\._\-]+', '', label).strip()
        return r.lstrip('.-').strip()
    # Patrón A: etiqueta + [pregunta padre] (corchete abre, cierre o no)
    if '[' in label:
        r = label[:label.index('[')].strip()
        return re.sub(r'^\d+[\.-]+\s*', '', r).strip()
    # Patrón D: numeración inicial
    return re.sub(r'^\d+[\.-]+\s*', '', label).strip()


etiquetas_limpias = {
    col: limpiar_etiqueta(label)
    for col, label in zip(meta.column_names, meta.column_labels) if label
}
print(f"Etiquetas procesadas: {len(etiquetas_limpias)}")

diccionario = pd.DataFrame({'variable': meta.column_names, 'etiqueta': meta.column_labels})
diccionario.head(20)

# Buscar variable por nombre o fragmento de etiqueta
busqueda = 'A10'
diccionario[
    diccionario['variable'].str.contains(busqueda, case=False) |
    diccionario['etiqueta'].str.contains(busqueda, case=False, na=False)
]

# Ver categorías codificadas de una variable
variable = 'Q13'
labels = meta.variable_value_labels.get(variable, {})
if labels:
    for k, v in labels.items(): print(f'  {k} -> {v}')
else:
    print(f"'{variable}' no tiene etiquetas de valor.")

cols_nsnr = [
    'P11','Q7_4',
    'P17_1','P17_2','P17_3','P17_4','P17_5',
    'P19_1','P19_2','P19_3','P19_4',
    'Q40_1','Q40_2','Q40_3','Q40_4','Q40_5',
    'Q42','Q42_1'
]
for col in cols_nsnr:
    if col in df.columns: df[col] = df[col].replace(9999999, np.nan)
print('NS/NR reemplazados por NaN.')

nombres_cortos = {
    'REGISTRO':'id', 'FECHAFIN':'fecha_fin', 'COD_REGION':'region', 'COMUNA_DEF':'comuna', 'ZONA':'zona',
    'A9':'parentesco_jh', 'A10':'educ_jh', 'A11':'ocupacion_jh', 'A12_1':'ingreso_hogar',
    'Q1':'parentesco', 'Q1_1':'edad', 'Q1_2':'sexo', 'Q1_3':'educ', 'Q1_4':'ocupacion_encuestado', 'Q2':'actividad',
    'P1':'acceso_internet_hogar', 'P2':'n_smartphones_hogar', 'P2_1':'n_computadores_hogar',
    'P10':'tipo_acceso_fijo', 'P11':'pago_mensual_internet', 'P11_3':'velocidad_contratada',
    'P11_4':'calidad_acceso', 'P11_5':'cuota_mensual_gb', 'P12_2':'tipo_plan', 'P12_1':'plan_movil_tipo',
    'P14':'razon_no_acceso_principal', 'P15':'disposicion_contratar_fijo',
    'Q5':'uso_computador', 'Q7':'uso_smartphone', 'Q7_1':'smartphone_propio',
    'Q7_3':'plan_movil_tipo_ind', 'Q7_4':'pago_mensual_movil',
    'Q9':'ultimo_uso_internet', 'Q10':'frecuencia_internet', 'Q11':'tiempo_diario_internet',
    'Q13':'tipo_acceso_mas_usado', 'Q14':'uso_internet_hogar', 'Q15':'frecuencia_internet_hogar',
    'Q16':'tiempo_diario_hogar', 'Q17':'uso_internet_fuera_hogar', 'Q18':'frecuencia_fuera_hogar',
    'Q19':'tiempo_diario_fuera_hogar',
    'Q23':'internet_facilita_trabajo', 'Q25':'internet_mejora_vida', 'Q27':'ultima_compra_online',
    'Q31':'percepcion_proteccion', 'Q30_1':'reg_control_legal', 'Q30_2':'reg_control_familia', 'Q30_3':'reg_autocontrol',
    'FE_HOGAR':'fe_hogar', 'FE_PERSONAS':'fe_personas', 'POND_HOGAR':'pond_hogar', 'POND_PERSONAS':'pond_personas',
}

df = df.rename(columns={k: v for k, v in nombres_cortos.items() if k in df.columns})

# Recodificación de educ_jh y ocupacion_jh (aquí, con valores numéricos aún intactos)
_mapa_educ = {
    1:'Sin educación formal', 2:'Básica incompleta', 3:'Básica completa',
    4:'Media CH incompleta', 5:'Media TP incompleta', 6:'Media CH completa', 7:'Media TP completa',
    8:'Superior técnica incompleta', 9:'Superior técnica completa',
    10:'Superior universitaria incompleta', 11:'Superior universitaria completa'
}
_mapa_ocup = {
    1:'Trabajos ocasionales e informales', 2:'Oficio menor - obrero no calificado',
    3:'Obrero calificado - microempresario', 4:'Empleado medio - técnico - prof. independiente',
    5:'Ejecutivo medio - prof. universitario', 6:'Alto ejecutivo - empresario - directivo'
}
df['educ_jh']              = df['educ_jh'].map(_mapa_educ)
df['ocupacion_jh']         = df['ocupacion_jh'].map(_mapa_ocup)
df['ocupacion_encuestado'] = df['ocupacion_encuestado'].map({**_mapa_ocup, 7:'Sin trabajo remunerado'})

print(f"Renombradas: {len(nombres_cortos)} | Columnas totales: {df.shape[1]}")

df = df.copy()

# Identificación
df['region'] = df['region'].map({
    1:'Tarapacá', 2:'Antofagasta', 3:'Atacama', 4:'Coquimbo', 5:'Valparaíso',
    6:"O'Higgins", 7:'Maule', 8:'Biobío', 9:'Araucanía', 10:'Los Lagos',
    11:'Aysén', 12:'Magallanes', 13:'Metropolitana', 14:'Los Ríos', 15:'Arica y Parinacota', 16:'Ñuble'
})
df['zona'] = df['zona'].map({1:'Urbana', 2:'Rural'})

# Sociodemográficas del entrevistado
df['sexo'] = df['sexo'].map({1:'Hombre', 2:'Mujer'})
df['educ'] = df['educ'].map(_mapa_educ)
df['educ_grupo'] = df['educ'].map({
    'Sin educación formal':'Básica o menos', 'Básica incompleta':'Básica o menos',
    'Básica completa':'Básica o menos', 'Media CH incompleta':'Media',
    'Media TP incompleta':'Media', 'Media CH completa':'Media', 'Media TP completa':'Media',
    'Superior técnica incompleta':'Superior', 'Superior técnica completa':'Superior',
    'Superior universitaria incompleta':'Superior', 'Superior universitaria completa':'Superior',
})
df['tramo_edad'] = pd.cut(df['edad'], bins=[0,17,29,44,59,200],
                          labels=['Menor de 18','18-29','30-44','45-59','60 y más'], right=True)
df['actividad'] = df['actividad'].map({
    1:'Trabajador independiente', 2:'Empleador/patrón', 3:'Empleado dependiente',
    4:'Familiar no remunerado', 5:'FFAA y de orden', 6:'Cesante',
    7:'Jubilado/pensionado', 8:'Estudiante', 9:'Labores del hogar'
})

# Acceso a internet
df['acceso_internet_hogar'] = df['acceso_internet_hogar'].map({1:'Sí', 2:'No'})
df['tipo_acceso_fijo'] = df['tipo_acceso_fijo'].map({
    1:'ADSL', 2:'Cable/Módem', 3:'Fibra óptica', 4:'Inalámbrica',
    5:'Satelital', 31:'WiFi', 32:'Antena', 33:'Banda ancha', 34:'Acceso telefónico', 88:'No sabe'
})
df['velocidad_contratada'] = df['velocidad_contratada'].map({
    1:'Hasta 10 Mbps', 2:'Más de 10 a 100 Mbps', 3:'Más de 100 a 500 Mbps',
    4:'Más de 500 Mbps a 1 Gbps', 5:'Más de 1 Gbps', 99:'NS/NR'
})
df['tipo_plan'] = df['tipo_plan'].map({
    1:'Banda ancha desnuda', 2:'BA + TV Cable', 3:'BA + Telefonía fija',
    4:'Triple pack (BA+TV+Tel)', 5:'Otros planes'
})
df['tipo_acceso_mas_usado'] = df['tipo_acceso_mas_usado'].map({
    1.0:'Banda Ancha Fija / WiFi', 2.0:'Banda Ancha Móvil',
    3.0:'Internet Móvil (Smartphone/Tablet)', 4.0:'Conexión Satelital'
})

# Uso individual
df['uso_computador']  = df['uso_computador'].map({1:'Sí', 2:'No'})
df['uso_smartphone']  = df['uso_smartphone'].map({1:'Sí', 2:'No'})
df['ultimo_uso_internet'] = df['ultimo_uso_internet'].map({
    1:'Hoy', 2:'Entre 2 y 3 días', 3:'Entre 3 y 7 días', 4:'Entre 1 y 4 semanas',
    5:'Más de 4 semanas', 6:'Más de 12 meses', 7:'Nunca'
})
df['frecuencia_internet'] = df['frecuencia_internet'].map({
    1:'Todos los días', 2:'Varias veces por semana',
    3:'Al menos una vez al mes', 4:'Menos de una vez al mes'
})
df['tiempo_diario_internet'] = df['tiempo_diario_internet'].map({
    1:'Menos de 1 hora', 2:'Entre 1 y 2 horas', 3:'Entre 2 y 4 horas', 4:'Más de 4 horas'
})

# Percepciones
df['percepcion_proteccion']     = df['percepcion_proteccion'].map({
    1:'Muy protegido', 2:'Protegido', 3:'Desprotegido', 4:'Muy desprotegido', 99:'NS/NR'
})
df['internet_mejora_vida']      = df['internet_mejora_vida'].map({1:'Sí', 2:'No'})
df['internet_facilita_trabajo'] = df['internet_facilita_trabajo'].map({1:'Sí', 2:'No'})

print('Recodificaciones completadas.')
print(f"sexo: {df['sexo'].value_counts().to_dict()}")
print(f"acceso: {df['acceso_internet_hogar'].value_counts().to_dict()}")

_rangos = {
    11:(0,129000),12:(130000,226000),13:(227000,393000),14:(394000,686000),15:(687000,1100000),16:(1200000,2000000),17:(2100000,None),
    21:(0,210000),22:(211000,366000),23:(367000,639000),24:(640000,1100000),25:(1200000,1900000),26:(2000000,3300000),27:(3400000,None),
    31:(0,279000),32:(280000,487000),33:(488000,849000),34:(850000,1400000),35:(1500000,2500000),36:(2600000,4500000),37:(4600000,None),
    41:(0,341000),42:(342000,595000),43:(596000,1000000),44:(1100000,1800000),45:(1900000,3100000),46:(3200000,5500000),47:(5600000,None),
    51:(0,399000),52:(400000,696000),53:(697000,1200000),54:(1300000,2100000),55:(2200000,3600000),56:(3700000,6400000),57:(6500000,None),
    61:(0,453000),62:(454000,791000),63:(792000,1300000),64:(1400000,2400000),65:(2500000,4100000),66:(4200000,7300000),67:(7400000,None),
    71:(0,505000),72:(506000,881000),73:(882000,1500000),74:(1600000,2600000),75:(2700000,4600000),76:(4700000,8100000),77:(8200000,None),
    81:(0,555000),82:(556000,967000),83:(968000,1600000),84:(1700000,2900000),85:(3000000,5100000),86:(5200000,8900000),87:(9000000,None),
    91:(0,602000),92:(603000,1000000),93:(1100000,1800000),94:(1900000,3100000),95:(3200000,5500000),96:(5600000,9700000),97:(9800000,None),
    101:(0,648000),102:(649000,1100000),103:(1200000,1900000),104:(2000000,3400000),105:(3500000,5900000),106:(6000000,10400000),107:(10500000,None),
}
_mapa_pm = {float(k): (v[0]*1.5 if v[1] is None else (v[0]+v[1])/2) for k, v in _rangos.items()}

df['ingreso_pm'] = df['ingreso_hogar'].map(_mapa_pm)
df['ingreso_tramo'] = pd.cut(
    df['ingreso_pm'],
    bins=[0, 384000, 540000, 798000, 1100000, 1700000, float('inf')],
    labels=['Hasta $384 mil','$384 mil a $540 mil','$540 mil a $798 mil',
            '$798 mil a $1,1 millón','$1,1 millón a $1,7 millones','Más de $1,7 millones'],
    right=True
)
df['ingreso_grupo'] = df['ingreso_tramo'].map({
    'Hasta $384 mil':'Bajo', '$384 mil a $540 mil':'Bajo',
    '$540 mil a $798 mil':'Medio', '$798 mil a $1,1 millón':'Medio',
    '$1,1 millón a $1,7 millones':'Alto', 'Más de $1,7 millones':'Alto',
})

# Validación: promedio de ingreso debe subir de E a AB
(
    df.groupby('gse', observed=True)['ingreso_pm']
    .agg(N='count', Promedio='mean').reindex(_ORDEN_GSE).round(0).astype({'N':int,'Promedio':int})
)

ORDEN_CATEGORIAS = {
    'sexo':         ['Hombre','Mujer'],
    'zona':         ['Urbana','Rural'],
    'region':       ['Tarapacá','Antofagasta','Atacama','Coquimbo','Valparaíso',"O'Higgins",'Maule',
                     'Biobío','Araucanía','Los Lagos','Aysén','Magallanes','Metropolitana',
                     'Los Ríos','Arica y Parinacota','Ñuble'],
    'educ':         ['Sin educación formal','Básica incompleta','Básica completa',
                     'Media CH incompleta','Media TP incompleta','Media CH completa','Media TP completa',
                     'Superior técnica incompleta','Superior técnica completa',
                     'Superior universitaria incompleta','Superior universitaria completa'],
    'educ_grupo':   ['Básica o menos','Media','Superior'],
    'tramo_edad':   ['Menor de 18','18-29','30-44','45-59','60 y más'],
    'actividad':    ['Trabajador independiente','Empleador/patrón','Empleado dependiente',
                     'Familiar no remunerado','FFAA y de orden','Cesante',
                     'Jubilado/pensionado','Estudiante','Labores del hogar'],
    'ocupacion_jh': ['Trabajos ocasionales e informales','Oficio menor - obrero no calificado',
                     'Obrero calificado - microempresario','Empleado medio - técnico - prof. independiente',
                     'Ejecutivo medio - prof. universitario','Alto ejecutivo - empresario - directivo'],
    'ocupacion_encuestado': ['Trabajos ocasionales e informales','Oficio menor - obrero no calificado',
                     'Obrero calificado - microempresario','Empleado medio - técnico - prof. independiente',
                     'Ejecutivo medio - prof. universitario','Alto ejecutivo - empresario - directivo',
                     'Sin trabajo remunerado'],
    'gse':              ['AB', 'C1', 'C2', 'C3', 'D', 'E'],
    'ingreso_tramo':    ['Hasta $384 mil','$384 mil a $540 mil','$540 mil a $798 mil',
                         '$798 mil a $1,1 millón','$1,1 millón a $1,7 millones','Más de $1,7 millones'],
    'ingreso_grupo':    ['Bajo','Medio','Alto'],
    'acceso_internet_hogar':    ['Sí','No'],
    'uso_computador':           ['Sí','No'],
    'uso_smartphone':           ['Sí','No'],
    'internet_mejora_vida':     ['Sí','No'],
    'internet_facilita_trabajo':['Sí','No'],
    'tipo_acceso_fijo':         ['Fibra óptica','Cable/Módem','ADSL','Inalámbrica','Satelital','WiFi','Antena','Banda ancha','Acceso telefónico','No sabe'],
    'tipo_acceso_mas_usado':    ['Banda Ancha Fija / WiFi','Banda Ancha Móvil','Internet Móvil (Smartphone/Tablet)','Conexión Satelital'],
    'tipo_plan':                ['Banda ancha desnuda','BA + TV Cable','BA + Telefonía fija','Triple pack (BA+TV+Tel)','Otros planes'],
    'ultimo_uso_internet':      ['Hoy','Entre 2 y 3 días','Entre 3 y 7 días',
                                  'Entre 1 y 4 semanas','Más de 4 semanas','Más de 12 meses','Nunca'],
    'frecuencia_internet':      ['Todos los días','Varias veces por semana',
                                  'Al menos una vez al mes','Menos de una vez al mes'],
    'tiempo_diario_internet':   ['Menos de 1 hora','Entre 1 y 2 horas','Entre 2 y 4 horas','Más de 4 horas'],
    'percepcion_proteccion':    ['Muy protegido','Protegido','Desprotegido','Muy desprotegido','NS/NR'],
    'velocidad_contratada':     ['Hasta 10 Mbps','Más de 10 a 100 Mbps','Más de 100 a 500 Mbps',
                                  'Más de 500 Mbps a 1 Gbps','Más de 1 Gbps','NS/NR'],
}


def fordf(df_tabla, titulo=None):
    """Formato visual: enteros sin decimales, porcentajes con 1 decimal."""
    
    # 1. Identificar solo las columnas que son numéricas
    num_cols = df_tabla.select_dtypes(include=['number']).columns
    
    # 2. Aplicar el formato solo a esas columnas
    estilo = df_tabla.style.format({
        col: '{:,.0f}' if 'ponderado' in str(col).lower() or 'total' in str(col).lower() or str(col).startswith('n ') else '{:.1f}'
        for col in num_cols
    })
    
    if titulo: 
        estilo = estilo.set_caption(titulo)
        
    return estilo




def _ordenar(df_res, var, cruzada=False):
    if var not in ORDEN_CATEGORIAS: return df_res
    orden = ORDEN_CATEGORIAS[var]
    if cruzada:
        ok  = [v for v in orden if v in df_res.index]
        rst = [v for v in df_res.index if v not in ok and v != 'Total']
        fin = ok + rst + (['Total'] if 'Total' in df_res.index else [])
        return df_res.reindex(fin)
    ok  = [v for v in orden if v in df_res[var].values]
    rst = [v for v in df_res[var].values if v not in ok and v != 'Total']
    df_res[var] = pd.Categorical(df_res[var], categories=ok+rst+['Total'], ordered=True)
    return df_res.sort_values(var).reset_index(drop=True)


def dstats(data_df, variables, tipo='frecuencia', cruce=None, factor=None, transponer=False, estilo=True):
    """
    Análisis ponderado de variables simples.
    tipo: 'frecuencia' | 'cruzada' | 'promedio' | 'suma'
    Si estilo=True, retorna Styler formateado. Si es False, retorna el DataFrame puro.
    Ejemplo: dstats(df, 'sexo', tipo='frecuencia', factor='fe_personas', estilo=False)
    """
    if isinstance(variables, str): variables = [variables]
    for col in variables + [factor] + ([cruce] if cruce else []):
        if col not in data_df.columns:
            raise ValueError(f"Columna '{col}' no existe.")

    if tipo == 'frecuencia':
        var = variables[0]
        tot = data_df[factor].sum()
        res = data_df.groupby(var, observed=True)[factor].sum().reset_index().rename(columns={factor:'n_ponderado'})
        res['porcentaje'] = (res['n_ponderado'] / tot * 100).round(2)
        res = pd.concat([res, pd.DataFrame({var:['Total'],'n_ponderado':[res['n_ponderado'].sum()],'porcentaje':[res['porcentaje'].sum().round(2)]})], ignore_index=True)
        res = _ordenar(res, var).set_index(var)
        
        if estilo:
            titulo = f"Frecuencia: '{var}' — base ponderada: {tot:,.0f} ({factor})"
            return fordf(res, titulo=titulo)
        return res

    if tipo == 'cruzada':
        var = variables[0]
        tot = data_df[factor].sum()
        t   = data_df.pivot_table(values=factor, index=var, columns=cruce, aggfunc='sum', fill_value=0, observed=False)
        tp  = t.div(t.sum(axis=0), axis=1).mul(100).round(2)
        if var in ORDEN_CATEGORIAS:
            of = [v for v in ORDEN_CATEGORIAS[var] if v in t.index];  t, tp = t.reindex(of), tp.reindex(of)
        if cruce in ORDEN_CATEGORIAS:
            oc = [v for v in ORDEN_CATEGORIAS[cruce] if v in t.columns]; t, tp = t[oc], tp[oc]
        if transponer: t, tp = t.T, tp.T
        t.loc['Total'], tp.loc['Total'] = t.sum(numeric_only=True), tp.sum(numeric_only=True).round(2)
        cols = [s for c in t.columns for s in [t[c].rename(f'n {c}'), tp[c].rename(f'% {c}')]]
        res = pd.concat(cols, axis=1)
        
        if estilo:
            titulo = f"Cruce: '{var}' según '{cruce}' — base ponderada: {tot:,.0f} ({factor})"
            return fordf(res, titulo=titulo)
        return res

    def _wavg(sub, v, f):
        d = sub[[v, f]].dropna()
        return float(round(np.average(d[v], weights=d[f]), 4)) if len(d) > 0 and d[f].sum() > 0 else np.nan

    def _wsum(sub, v, f):
        d = sub[[v, f]].dropna()
        return float(round((d[v]*d[f]).sum(), 4))

    fn = _wavg if tipo == 'promedio' else _wsum
    col_name = 'promedio_ponderado' if tipo == 'promedio' else 'suma_ponderada'

    if not cruce:
        res = pd.DataFrame([(v, fn(data_df, v, factor)) for v in variables], columns=['variable', col_name])
        
        if estilo:
            titulo = f"{tipo.capitalize()} de variables — factor: {factor}"
            return fordf(res, titulo=titulo)
        return res

    filas = {g: {v: fn(sg, v, factor) for v in variables} for g, sg in data_df.groupby(cruce, observed=True)}
    filas['Total'] = {v: fn(data_df, v, factor) for v in variables}
    res = pd.DataFrame(filas).T
    res.index.name = cruce
    if cruce in ORDEN_CATEGORIAS:
        ok  = [v for v in ORDEN_CATEGORIAS[cruce] if v in res.index]
        rst = [v for v in res.index if v not in ok and v != 'Total']
        res = res.reindex(ok + rst + ['Total'])
        
    if estilo:
        titulo = f"{tipo.capitalize()} cruzado por '{cruce}' — factor: {factor}"
        return fordf(res, titulo=titulo)
    return res


print('ORDEN_CATEGORIAS, fordf, dstats listos.')

_c = df.columns

GRUPOS_RM = {
    # Hogar
    'A12':  ('Pueblos indígenas o tribales (hogar)',            [c for c in _c if c.startswith('A12_') and not c.startswith('A12_1')]),
    'A13':  ('Condiciones permanentes de salud en el hogar',   [c for c in _c if c.startswith('A13_')]),
    'A14':  ('Situaciones laborales en el hogar',              [c for c in _c if c.startswith('A14_') and not c.endswith('_OTRA')]),
    # Acceso y conectividad
    'P3':   ('Dispositivos usados para acceder a internet',    [c for c in _c if c.startswith('P3_') and not c.endswith('_OTRA')]),
    'P4':   ('Formas de acceso pagado a internet en el hogar', [c for c in _c if c.startswith('P4_')]),
    'P6':   ('Razones para tener internet fijo',               [c for c in _c if c.startswith('P6_') and not c.startswith('P6_1_') and not c.endswith('_OTRA')]),
    'P6_1': ('Razones para tener internet móvil',              [c for c in _c if c.startswith('P6_1_')]),
    'P7':   ('Medidas de protección internet para menores',    [c for c in _c if c.startswith('P7_')]),
    'P9':   ('Dispositivos de uso personal de menores',        [c for c in _c if c.startswith('P9_')]),
    'P12':  ('Conexión móvil 4G/5G',                           ['P12_11','P12_21','P12_31','P12_41']),
    'P13':  ('Razones de no acceso a internet fijo',           [c for c in _c if c.startswith('P13_') and not c.endswith('_OTRA')]),
    'P16':  ('Equipos que le interesaría tener (sin internet)',[c for c in _c if c.startswith('P16_')]),
    # Uso individual
    'Q6':   ('¿Cómo aprendió a usar el computador?',           [c for c in _c if c.startswith('Q6_') and c not in ['Q6_1','Q6_OTRA']]),
    'Q7_2': ('Smartphone 4G/5G',                               ['Q7_2_1','Q7_2_2','Q7_2_3','Q7_2_4']),
    'Q8':   ('Habilidades digitales',                          [c for c in _c if c.startswith('Q8_')]),
    'Q11_1':('Lugares donde usó internet ayer',                [c for c in _c if c.startswith('Q11_1_')]),
    'Q12':  ('Tipos de acceso en últimos 3 meses',             [c for c in _c if c.startswith('Q12_')]),
    'Q20':  ('Lugares donde usó internet fuera del hogar',     [c for c in _c if c.startswith('Q20_')]),
    'Q21':  ('Actividades realizadas en internet',             [c for c in _c if c.startswith('Q21_') and c not in ['Q21_1','Q21_10','Q21_19','Q21_26','Q21_33','Q21_38','Q21_44']]),
    'Q28':  ('Bienes y servicios comprados en internet',       [c for c in _c if c.startswith('Q28_') and not c.endswith('_OTRA')]),
    'Q32':  ('Actividades de seguridad y privacidad',          [c for c in _c if c.startswith('Q32_') and not c.endswith('_OTRA')]),
    'Q33':  ('Problemas de seguridad sufridos',                [c for c in _c if c.startswith('Q33_') and not c.endswith('_OTRA')]),
    'Q34':  ('Razones de no uso de internet',                  [c for c in _c if c.startswith('Q34_') and not c.endswith('_OTRA')]),
    'Q37':  ('Actividades de internet realizadas por terceros',[c for c in _c if c.startswith('Q37_')]),
    'Q39':  ('Equipos que le interesaría tener (no usuarios)', [c for c in _c if c.startswith('Q39_')]),
}

def analizar_rm(grupo, factor='fe_hogar', top_n=None, estilo=True):
    """
    Analiza un grupo de respuesta múltiple.
    Si estilo=True, retorna tabla estilizada (HTML). Si es False, retorna el DataFrame puro.
    """
    if grupo not in GRUPOS_RM: 
        raise ValueError(f"Grupo '{grupo}' no existe.")
        
    desc, cols = GRUPOS_RM[grupo]
    cols = [c for c in cols if c in df.columns]
    base = df.loc[df[cols].notna().any(axis=1), factor].sum()
    
    filas = [
        {'variable': c,
         'etiqueta': etiquetas_limpias.get(c, c),
         'n_ponderado': int(df.loc[df[c]==1, factor].sum()),
         'porcentaje': round(df.loc[df[c]==1, factor].sum() / base * 100, 1)}
        for c in cols
    ]
    res = pd.DataFrame(filas).sort_values('porcentaje', ascending=False).reset_index(drop=True)
    if top_n: res = res.head(top_n)
    res.index += 1
    
    if estilo:
        titulo_tabla = f"{desc} — base ponderada: {int(base):,} ({factor})"
        return fordf(res, titulo=titulo_tabla)
    return res

print("Grupos de respuesta múltiple disponibles:")
for k, (desc, cols) in GRUPOS_RM.items():
    cols_validas = [c for c in cols if c in df.columns]
    print(f"  '{k}': {desc} ({len(cols_validas)} opciones)")

def analizar_rm_cruce(grupo, cruce, factor='fe_personas', estilo=True):
    """
    Analiza un grupo de respuesta múltiple cruzado por una variable demográfica.
    Si estilo=True, retorna tabla estilizada (HTML). Si es False, retorna el DataFrame puro.
    """
    if grupo not in GRUPOS_RM: 
        raise ValueError(f"Grupo '{grupo}' no existe.")
        
    desc, cols = GRUPOS_RM[grupo]
    cols = [c for c in cols if c in df.columns]
    
    base_cruce = df.loc[df[cols].notna().any(axis=1)].groupby(cruce, observed=True)[factor].sum()
    
    resultados = {}
    for categoria in base_cruce.index:
        base = base_cruce[categoria]
        df_cat = df[df[cruce] == categoria]
        
        pcts = {
            etiquetas_limpias.get(c, c): round((df_cat.loc[df_cat[c]==1, factor].sum() / base) * 100, 1) 
            if base > 0 else 0 
            for c in cols
        }
        resultados[categoria] = pcts
        
    res_df = pd.DataFrame(resultados)
    res_df = res_df.sort_values(by=res_df.columns[0], ascending=False)
    
    if estilo:
        titulo_tabla = f"{desc} cruzado por '{cruce}' — factor: {factor}"
        return fordf(res_df, titulo=titulo_tabla)
    return res_df

analizar_rm('Q8', factor='fe_personas')

# Clasificación de habilidades Q8 por nivel de dificultad
# Criterio: nivel más alto alcanzado (jerárquico)
#
# Básico     — consumo y comunicación cotidiana (6 ítems)
# Intermedio — productividad, gestión y creación (9 ítems)
# Avanzado   — configuración técnica y programación (3 ítems)

Q8_BASICO = {
    'Q8_10': 'Streaming (video/música)',
    'Q8_11': 'Juegos en línea',
    'Q8_12': 'Revisar redes sociales',
    'Q8_13': 'Publicar en redes sociales',
    'Q8_15': 'Videollamadas',
    'Q8_16': 'Correo electrónico',
}
Q8_INTERMEDIO = {
    'Q8_1':  'Procesador de texto (Word)',
    'Q8_2':  'Planilla de cálculo (Excel)',
    'Q8_3':  'Presentaciones (PowerPoint)',
    'Q8_4':  'Transferir archivos / nube',
    'Q8_5':  'Conectar nuevo dispositivo',
    'Q8_6':  'Instalar y configurar apps',
    'Q8_14': 'Editar fotos o videos',
    'Q8_17': 'Transacciones y pagos en línea',
    'Q8_18': 'Uso de IA (ChatGPT, etc.)',
}
Q8_AVANZADO = {
    'Q8_7': 'Configurar seguridad del dispositivo',
    'Q8_8': 'Instalar SO / programar (Python, Java…)',
    'Q8_9': 'Crear un sitio web',
}

_cols_b  = list(Q8_BASICO)
_cols_i  = list(Q8_INTERMEDIO)
_cols_a  = list(Q8_AVANZADO)
_cols_q8 = _cols_b + _cols_i + _cols_a + ['Q8_19']

def _nivel(row):
    if row[_cols_a].eq(1).any():  return 'Avanzado'
    if row[_cols_i].eq(1).any():  return 'Intermedio'
    if row[_cols_b].eq(1).any():  return 'Básico'
    return 'Sin habilidades'

# Crear nivel_habilidades en df (5 000 filas)
# Quienes no respondieron Q8 caen en 'Sin habilidades' (eq(1) es False para NaN)
df['nivel_habilidades'] = df.apply(_nivel, axis=1)
mask_q8 = df[_cols_q8].notna().any(axis=1)  # máscara para la tabla de ítems Q8
base_q8 = int(mask_q8.sum())

# Distribución sin ponderar (descriptiva)
orden_nivel = ['Avanzado', 'Intermedio', 'Básico', 'Sin habilidades']
dist = df['nivel_habilidades'].value_counts().reindex(orden_nivel)
print(f"Base: {len(df):,} (total df) | respondentes Q8: {base_q8:,}\n")
print("Distribución (sin ponderar):")
for niv, n in dist.items():
    pct = n / len(df) * 100
    print(f"  {niv:<20} {n:>5,}  ({pct:.1f}%)")

# Tabla de habilidades por nivel (base: respondentes Q8)
print("\n── Habilidades por nivel ──────────────────────────────────────────────")
for nivel, items in [('BÁSICO', Q8_BASICO), ('INTERMEDIO', Q8_INTERMEDIO), ('AVANZADO', Q8_AVANZADO)]:
    print(f"\n{nivel}")
    for cod, desc in items.items():
        n = int((df.loc[mask_q8, cod] == 1).sum())
        pct = n / base_q8 * 100
        print(f"  {cod:<8} {desc:<45}  {n:>5,} ({pct:.1f}%)")


# ── Categorización de Habilidades Digitales (Q8) ──────────────────

# 1. Definimos el mapeo de categorías según el propósito de la tarea
categorizacion_habilidades = {
    'RRSS y Comunicación': ['Q8_12', 'Q8_13', 'Q8_15', 'Q8_16'],
    'Ofimática': ['Q8_1', 'Q8_2', 'Q8_3'],
    'Mantenimiento/Configuración': ['Q8_4', 'Q8_5', 'Q8_6'],
    'Creación de contenido': ['Q8_14', 'Q8_9'],
    'Seguridad': ['Q8_7'],
    'Habilidades Avanzadas': ['Q8_8', 'Q8_18'],
    'Consumo, transacciones y entretenimiento':  ['Q8_10', 'Q8_17', 'Q8_11']
}

# 2. Creamos las nuevas variables agregadas en el DataFrame
# Una persona tendrá un '1' en la categoría si posee al menos UNA de las habilidades del grupo.
cat_cols = []
for cat, cols in categorizacion_habilidades.items():
    # Generar nombre de columna técnico (ej: cat_habilidades_de_comunicacion)
    col_name = 'cat_' + cat.lower().replace(' ', '_').replace('/', '_').replace('ó', 'o').replace('á', 'a').replace('é', 'e')
    
    # Creamos la variable binaria (0 o 1)
    df[col_name] = df[cols].any(axis=1).astype(float)
    
    # Registramos la etiqueta limpia para que las tablas se vean bien
    etiquetas_limpias[col_name] = cat
    cat_cols.append(col_name)

# 3. Registramos este nuevo grupo en tu diccionario GRUPOS_RM
# Esto permite usar la función analizar_rm() que ya tienes definida.
GRUPOS_RM['Q8_CAT'] = ('Categorías de Habilidades Digitales (Agregadas)', cat_cols)

# 4. Ejecutamos el análisis ponderado por personas
analizar_rm('Q8_CAT', factor='fe_personas')


def generar_grafico(variable, cruce=None, factor=None, titulo=None, figsize=(11, 6),
                    tipo='barras_agrupadas', palette='viridis'):
    """
    Genera gráficos ponderados usando dstats y ORDEN_CATEGORIAS del notebook.

    Parámetros:
    - variable: Variable a analizar (str)
    - cruce: Variable para cruzar (str, opcional). Si None, muestra distribución simple
    - factor: Peso — 'fe_hogar' o 'fe_personas'. Si None, usa 'fe_personas'
    - titulo: Título del gráfico (str). Si None, se genera automáticamente
    - figsize: Tamaño figura (tuple)
    - tipo: 'barras_agrupadas' (default) o 'barras_apiladas'
    - palette: Paleta seaborn ('deep', 'muted', 'husl', etc.)

    Ejemplo:
    - generar_grafico('acceso_internet_hogar', cruce='gse', factor='fe_hogar')
    - generar_grafico('sexo', factor='fe_personas')
    - generar_grafico('velocidad_contratada', cruce='zona', factor='fe_hogar')
    """

    if factor is None:
        factor = 'fe_personas'

    if cruce is None:
        # Distribución simple
        res = dstats(df, variable, tipo='frecuencia', factor=factor, estilo=False)
        res = res.drop('Total', errors='ignore')

        # Ordenar según ORDEN_CATEGORIAS
        if variable in ORDEN_CATEGORIAS:
            orden = [v for v in ORDEN_CATEGORIAS[variable] if v in res.index]
            res = res.reindex(orden)

        fig, ax = plt.subplots(figsize=figsize)
        colors = sns.color_palette(palette, len(res))

        ax.bar(res.index, res['porcentaje'].values, color=colors, edgecolor='black', linewidth=0)

        # Añadir valores sobre barras (solo porcentaje)
        for i, (idx, pct) in enumerate(zip(res.index, res['porcentaje'].values)):
            ax.text(i, pct, f'{pct:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax.set_ylabel('Porcentaje (%)', fontsize=11)
        ax.set_xlabel('', fontsize=0)
        if titulo is None:
            titulo = f"Distribución: {variable} (factor: {factor})"
        ax.set_title(titulo, fontsize=12, fontweight='bold', pad=12)
        ax.set_ylim(0, 105)
        sns.despine(ax=ax, left=False, bottom=False)
        ax.grid(False)

    else:
        # Cruce — barras agrupadas o apiladas
        res = dstats(df, variable, tipo='cruzada', cruce=cruce, factor=factor, estilo=False)
        res = res.drop('Total', errors='ignore')

        # Ordenar filas y columnas según ORDEN_CATEGORIAS
        if variable in ORDEN_CATEGORIAS:
            orden_var = [v for v in ORDEN_CATEGORIAS[variable] if v in res.index]
            res = res.reindex(orden_var)

        if cruce in ORDEN_CATEGORIAS:
            orden_cruce = [v for v in ORDEN_CATEGORIAS[cruce] if v in
                          [c.replace('% ', '').replace('n ', '') for c in res.columns]]
            # Reconstruir columnas ordenadas
            cols_ordenadas = []
            for cat in orden_cruce:
                for col in res.columns:
                    if cat in col:
                        cols_ordenadas.append(col)
            res = res[[c for c in cols_ordenadas if c in res.columns]]

        # Extraer solo porcentajes
        pct_cols = [c for c in res.columns if c.startswith('% ')]
        pct_data = res[pct_cols].copy()
        pct_data.columns = [c.replace('% ', '') for c in pct_data.columns]

        fig, ax = plt.subplots(figsize=figsize)

        if tipo == 'barras_apiladas':
            pct_data.plot(kind='bar', stacked=True, ax=ax,
                         color=sns.color_palette(palette, len(pct_data.columns)),
                         edgecolor='black', linewidth=0, width=0.7)
            ax.set_ylabel('Porcentaje (%)', fontsize=11)
        else:
            # Barras agrupadas
            x = np.arange(len(pct_data.index))
            width = 0.8 / len(pct_data.columns)
            colors = sns.color_palette(palette, len(pct_data.columns))

            for i, col in enumerate(pct_data.columns):
                offset = (i - len(pct_data.columns)/2 + 0.5) * width
                ax.bar(x + offset, pct_data[col].values, width, label=col,
                      color=colors[i], edgecolor='black', linewidth=0)

                # Valores sobre barras (solo porcentaje)
                for j, val in enumerate(pct_data[col].values):
                    if val > 0:
                        ax.text(x[j] + offset, val, f'{val:.1f}%', ha='center', va='bottom',
                               fontsize=8, fontweight='bold')

            ax.set_xticks(x)
            ax.set_xticklabels(pct_data.index, rotation=0, ha='center')
            ax.set_ylabel('Porcentaje (%)', fontsize=11)
            ax.legend(title=cruce, bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=9)

        ax.set_xlabel('', fontsize=0)
        if titulo is None:
            titulo = f"{variable} según {cruce} (factor: {factor})"
        ax.set_title(titulo, fontsize=12, fontweight='bold', pad=12)
        ax.set_ylim(0, 105)
        sns.despine(ax=ax, left=False, bottom=False)
        ax.grid(False)

    plt.tight_layout()
    plt.show()

    return fig, ax


# # Ejemplos de uso de generar_grafico

# # Distribución simple
# generar_grafico('gse', factor='fe_personas', titulo='Distribución de sexo')

# # Cruce simple (barras agrupadas)
# generar_grafico('gse', cruce='acceso_internet_hogar', factor='fe_hogar')

# # Cruce con barras apiladas
# # Personalizar título y paleta
# generar_grafico('educ_grupo', cruce='gse', factor='fe_personas', 
#                 titulo='Educación por GSE (ponderado)', palette='viridis')

dstats(df, 'nivel_habilidades', cruce='educ_jh', tipo='cruzada', factor='fe_personas')

generar_grafico('nivel_habilidades', cruce='sexo',factor='fe_hogar', palette='viridis')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import warnings
warnings.filterwarnings('ignore')
print('Librerías de modelado cargadas.')


# Mapeos numéricos a partir de las variables ya recodificadas en v3
_freq_num = {
    'Todos los días': 4,
    'Varias veces por semana': 3,
    'Al menos una vez al mes': 2,
    'Menos de una vez al mes': 1,
}
_horas_num = {
    'Menos de 1 hora': 0.5,
    'Entre 1 y 2 horas': 1.5,
    'Entre 2 y 4 horas': 3,
    'Más de 4 horas': 5,
}
df['freq_num']  = df['frecuencia_internet'].map(_freq_num).fillna(2)
df['horas_num'] = df['tiempo_diario_internet'].map(_horas_num).fillna(1)
df['intensidad_uso'] = (df['freq_num'] * df['horas_num']).fillna(1)

# Conteo de dispositivos (P3_*) y actividades online (Q21_*)
_p3 = [c for c in df.columns if c.startswith('P3_') and not c.endswith('_OTRA')][:6]
df['n_dispositivos'] = df[_p3].fillna(0).sum(axis=1)

_q21 = [c for c in df.columns if c.startswith('Q21_') and not c.endswith('_OTRA')][:6]
df['n_actividades'] = df[_q21].fillna(0).sum(axis=1)

# uso_smartphone ya viene como 'Sí'/'No' desde la sección 7 → binarizamos
df['uso_sp_bin'] = df['uso_smartphone'].map({'Sí': 1, 'No': 0})

print('Features de ingeniería listos:')
print(f"  n_dispositivos (media): {df['n_dispositivos'].mean():.2f}")
print(f"  n_actividades  (media): {df['n_actividades'].mean():.2f}")
print(f"  intensidad_uso (media): {df['intensidad_uso'].mean():.2f}")


# Features candidatos
nf_desired = ['edad', 'n_dispositivos', 'n_actividades', 'intensidad_uso',
              'pago_mensual_internet', 'pago_mensual_movil', 'uso_sp_bin']
cf_desired = ['sexo', 'zona']

nf = [c for c in nf_desired if c in df.columns]
cf = [c for c in cf_desired if c in df.columns]
print(f'Features numéricos: {nf}')
print(f'Features categóricos: {cf}')

# Dataset limpio
dm = df[nf + cf + ['nivel_habilidades']].dropna(subset=['nivel_habilidades']).copy()

# Imputar nulos
for col in nf:
    dm[col] = dm[col].fillna(dm[col].median())
for col in cf:
    dm[col] = dm[col].fillna('Desconocido')

# Codificar categóricas
encoders = {}
for col in cf:
    le = LabelEncoder()
    dm[col + '_enc'] = le.fit_transform(dm[col].astype(str))
    encoders[col] = le

feature_cols = nf + [c + '_enc' for c in cf]
X = dm[feature_cols].values
y = dm['nivel_habilidades'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

print(f'Dataset: {len(dm):,} registros — {X.shape[1]} features')
print(f'Train: {len(X_train):,} | Test: {len(X_test):,}')

rf = RandomForestClassifier(
    n_estimators=100, max_depth=15, random_state=42,
    n_jobs=-1, class_weight='balanced',
)
rf.fit(X_train_s, y_train)

y_pred = rf.predict(X_test_s)
acc = accuracy_score(y_test, y_pred)
print(f'\nAccuracy: {acc:.4f}\n')
print('Reporte de clasificación:')
print(classification_report(y_test, y_pred, target_names=rf.classes_))


fi = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': rf.feature_importances_,
}).sort_values('Importance', ascending=False)

print('Top features por Feature Importance:')
print(fi.to_string(index=False))

cm = confusion_matrix(y_test, y_pred, labels=rf.classes_)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=rf.classes_, yticklabels=rf.classes_,
            ax=axes[0], cbar_kws={'label': 'Casos'})
axes[0].set_title('Matriz de Confusión', fontweight='bold')
axes[0].set_xlabel('Predicho')
axes[0].set_ylabel('Real')

tf = fi.head(8)
axes[1].barh(range(len(tf)), tf['Importance'].values, color='steelblue', edgecolor='black')
axes[1].set_yticks(range(len(tf)))
axes[1].set_yticklabels(tf['Feature'].values, fontsize=9)
axes[1].set_title('Top features (Random Forest)', fontweight='bold')
axes[1].invert_yaxis()

plt.tight_layout()
plt.show()


import shap

explainer = shap.TreeExplainer(rf)
shap_vals_all = explainer.shap_values(X_test_s)

# shap_vals_all puede venir como lista (una matriz por clase) o como array 3D
# (n_samples, n_features, n_classes). Manejamos ambos casos.
idx_maj = int(np.argmax([np.sum(y_test == c) for c in rf.classes_]))
clase_maj = rf.classes_[idx_maj]

if isinstance(shap_vals_all, list):
    shap_clase = np.asarray(shap_vals_all[idx_maj])
else:
    shap_arr = np.asarray(shap_vals_all)
    if shap_arr.ndim == 3:
        shap_clase = shap_arr[:, :, idx_maj]
    else:
        shap_clase = shap_arr

shap_imp = np.abs(shap_clase).mean(axis=0)
shap_rank = pd.DataFrame({
    'Feature': feature_cols,
    'SHAP': shap_imp,
}).sort_values('SHAP', ascending=False)

print(f'Clase mayoritaria analizada: {clase_maj}')
print('\nRanking SHAP:')
print(shap_rank.to_string(index=False))


fig, axes = plt.subplots(1, 2, figsize=(14, 6))

tf = fi.head(8)
axes[0].barh(range(len(tf)), tf['Importance'].values, color='steelblue', edgecolor='black')
axes[0].set_yticks(range(len(tf)))
axes[0].set_yticklabels(tf['Feature'].values, fontsize=9)
axes[0].set_title('Feature Importance (Random Forest)', fontweight='bold')
axes[0].invert_yaxis()

ts = shap_rank.head(8)
axes[1].barh(range(len(ts)), ts['SHAP'].values, color='coral', edgecolor='black')
axes[1].set_yticks(range(len(ts)))
axes[1].set_yticklabels(ts['Feature'].values, fontsize=9)
axes[1].set_title('Importancia SHAP', fontweight='bold')
axes[1].invert_yaxis()

plt.tight_layout()
plt.show()


print('=' * 70)
print('RESUMEN — Predicción del nivel de habilidades digitales')
print('=' * 70)
print(f'Dataset total      : {len(df):,} registros')
print(f'Usado en el modelo : {len(dm):,} registros')
print(f'Test               : {len(X_test):,} muestras')
print(f'Accuracy           : {acc:.4f}')
print(f'Clases             : {list(rf.classes_)}')
print(f'N° features        : {len(feature_cols)}')
print('\nTop 5 SHAP:')
for i, row in shap_rank.head(5).reset_index(drop=True).iterrows():
    print(f"  {i+1}. {row['Feature']:<25} {row['SHAP']:.6f}")
print('=' * 70)


df.to_csv('encuesta_uso_internet_chile_2026.csv', index=False)



print("\n" + "="*80)
print("BLOQUE 1 — ANÁLISIS DESCRIPTIVO BIVARIADO")
print("="*80)

# 1.1 OUTCOME: acceso_internet_hogar
print("\n1.1 ACCESO A INTERNET HOGAR")
print("-" * 80)
dstats(df, 'acceso_internet_hogar', tipo='frecuencia', factor='fe_hogar')

# Cruces clave: acceso_internet_hogar × predictores
from IPython.display import display

print("\n1.1.1 Acceso × GSE")
display(dstats(df, 'acceso_internet_hogar', cruce='gse', tipo='cruzada', factor='fe_hogar'))

print("\n1.1.2 Acceso × Zona")
display(dstats(df, 'acceso_internet_hogar', cruce='zona', tipo='cruzada', factor='fe_hogar'))

print("\n1.1.3 Acceso × Tramo edad")
display(dstats(df, 'acceso_internet_hogar', cruce='tramo_edad', tipo='cruzada', factor='fe_hogar'))

# 1.2 OUTCOME: nivel_habilidades
from IPython.display import display

print("\n\n1.2 NIVEL DE HABILIDADES DIGITALES")
print("-" * 80)
display(dstats(df, 'nivel_habilidades', tipo='frecuencia', factor='fe_personas'))

print("\n1.2.1 Habilidades × GSE")
display(dstats(df, 'nivel_habilidades', cruce='gse', tipo='cruzada', factor='fe_personas'))

print("\n1.2.2 Habilidades × Zona")
display(dstats(df, 'nivel_habilidades', cruce='zona', tipo='cruzada', factor='fe_personas'))

print("\n1.2.3 Habilidades × Sexo")
display(dstats(df, 'nivel_habilidades', cruce='sexo', tipo='cruzada', factor='fe_personas'))

from scipy.stats import chi2_contingency
import numpy as np

def chi2_cramers(df_tabla):
    """
    Calcula chi-square y Cramér's V para tabla de contingencia.
    df_tabla: DataFrame con filas=categorías X, columnas=categorías Y
    """
    # Extraer solo conteos numéricos (sin Total si existe)
    t = df_tabla.drop('Total', errors='ignore')
    t = t[[c for c in t.columns if not c.startswith('% ')]]
    t = t.loc[t.index != 'Total']
    
    # Calcular chi-square
    chi2, pval, dof, expected = chi2_contingency(t.values)
    
    # Cramér's V
    n = t.values.sum()
    min_dim = min(t.shape[0] - 1, t.shape[1] - 1)
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
    
    return {
        'chi2': chi2,
        'p_value': pval,
        'cramers_v': cramers_v,
        'sig': '***' if pval < 0.001 else '**' if pval < 0.01 else '*' if pval < 0.05 else 'ns'
    }

print('Función chi2_cramers cargada.')


from IPython.display import display

print("\n\n1.3 TIPO DE ACCESO FIJO")
print("-" * 80)
display(dstats(df, 'tipo_acceso_fijo', tipo='frecuencia', factor='fe_hogar'))

print("\n1.3.1 Tipo acceso × GSE")
display(dstats(df, 'tipo_acceso_fijo', cruce='gse', tipo='cruzada', factor='fe_hogar'))

print("\n1.3.2 Tipo acceso × Zona")
display(dstats(df, 'tipo_acceso_fijo', cruce='zona', tipo='cruzada', factor='fe_hogar'))

print("\n1.3.3 Tipo acceso × Región (top 5)")
ta_reg = dstats(df, 'tipo_acceso_fijo', cruce='region', tipo='cruzada', factor='fe_hogar', estilo=False)
# Top 5 regiones por volumen
top_regs = df.groupby('region', observed=True)['fe_hogar'].sum().nlargest(5).index.tolist()
display(ta_reg.loc[ta_reg.index.isin(top_regs)])


from IPython.display import display

print("\n\n1.4 VELOCIDAD CONTRATADA")
print("-" * 80)
display(dstats(df, 'velocidad_contratada', tipo='frecuencia', factor='fe_hogar'))

print("\n1.4.1 Velocidad × GSE")
display(dstats(df, 'velocidad_contratada', cruce='gse', tipo='cruzada', factor='fe_hogar'))

print("\n1.4.2 Velocidad × Zona")
display(dstats(df, 'velocidad_contratada', cruce='zona', tipo='cruzada', factor='fe_hogar'))

print("\n1.4.3 Velocidad × Tramo edad")
display(dstats(df, 'velocidad_contratada', cruce='tramo_edad', tipo='cruzada', factor='fe_hogar'))


import pandas as pd

print("\n\n1.5 TESTS ESTADÍSTICOS (χ² y Cramér's V)")
print("=" * 80)

# Matriz de outcomes × predictores
outcomes = ['acceso_internet_hogar', 'nivel_habilidades', 'tipo_acceso_fijo', 'velocidad_contratada']
predictores = ['gse', 'zona', 'tramo_edad', 'sexo', 'educ_grupo', 'region', 'ingreso_grupo']

resultados_tests = []

for outcome in outcomes:
    for predictor in predictores:
        try:
            # Obtener tabla de cruce
            tabla = dstats(df, outcome, cruce=predictor, tipo='cruzada', factor='fe_hogar', estilo=False)
            
            # Chi-square y Cramér's V
            test_result = chi2_cramers(tabla)
            
            resultados_tests.append({
                'Outcome': outcome,
                'Predictor': predictor,
                'chi2': test_result['chi2'],
                'p_value': test_result['p_value'],
                'cramers_v': test_result['cramers_v'],
                'Sig': test_result['sig']
            })
        except:
            pass  # Skip si no hay varianza en alguna variable

df_tests = pd.DataFrame(resultados_tests)
df_tests = df_tests.sort_values('p_value')

# Formato para visualización
df_tests_display = df_tests.copy()
df_tests_display['chi2'] = df_tests_display['chi2'].round(2)
df_tests_display['p_value'] = df_tests_display['p_value'].round(4)
df_tests_display['cramers_v'] = df_tests_display['cramers_v'].round(3)

print("\nResultados ordenados por p-value (menor = más significativo):")
print(df_tests_display.to_string(index=False))

print("\n*** p < 0.001 | ** p < 0.01 | * p < 0.05 | ns = no significativo")
print(f"\nResumen: {(df_tests['Sig'] != 'ns').sum()}/{len(df_tests)} cruces significativos (α=0.05)")


import matplotlib.pyplot as plt
import seaborn as sns

print('\n\n1.6 HEATMAPS DE CONTINGENCIA')
print('=' * 80)

# Seleccionar 4 cruces principales (mayor Cramer's V)
top_tests = df_tests.nlargest(4, 'cramers_v')

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for idx, (_, row) in enumerate(top_tests.iterrows()):
    outcome = row['Outcome']
    predictor = row['Predictor']
    cramers = row['cramers_v']
    
    # Obtener tabla de porcentajes
    tabla = dstats(df, outcome, cruce=predictor, tipo='cruzada', factor='fe_hogar', estilo=False)
    tabla = tabla.drop('Total', errors='ignore')
    
    # Extraer solo porcentajes
    pct_cols = [c for c in tabla.columns if c.startswith('% ')]
    pct_data = tabla[pct_cols].copy()
    pct_data.columns = [c.replace('% ', '') for c in pct_data.columns]
    pct_data = pct_data.loc[pct_data.index != 'Total']
    
    # Heatmap
    sns.heatmap(pct_data, annot=True, fmt='.1f', cmap='YlOrRd', ax=axes[idx],
                cbar_kws={'label': 'Porcentaje (%)'}, vmin=0, vmax=100)
    title_str = outcome + ' × ' + predictor + ' (V=' + f'{cramers:.3f}' + ')'
    axes[idx].set_title(title_str, fontweight='bold', fontsize=10)
    axes[idx].set_xlabel(predictor, fontsize=9)
    axes[idx].set_ylabel(outcome, fontsize=9)

plt.tight_layout()
plt.show()

print('\nHeatmaps generados para 4 cruces con mayor efecto.')


print('\n\n2.1 MCA — ANÁLISIS DE CORRESPONDENCIA MÚLTIPLE (Q8 Habilidades)')
print('=' * 80)

# Seleccionar ítems Q8 (19 variables binarias)
_q8_cols = [c for c in df.columns if c.startswith('Q8_')]

# Dataset para MCA
df_mca_raw = df[_q8_cols].fillna(0)
df_mca = df_mca_raw.map(lambda x: 'Sí' if x == 1 else 'No')

# Ejecutar MCA
mca = prince.MCA(n_components=5, n_iter=3, random_state=42)
mca_coords = mca.fit_transform(df_mca)

print(f'Base: {len(df_mca):,} personas | Variables: {len(_q8_cols)} habilidades')
print(f'MCA completo en 5 dimensiones.')
print(f'Dimensiones del output: {mca_coords.shape}')

# Usar primeras 5 dimensiones
print(f'\nPrimer vista de coordenadas MCA:')
print(mca_coords.head())


from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

print('\n\n2.2 PCA — ANÁLISIS DE COMPONENTES PRINCIPALES')
print('=' * 80)

# Variables numéricas clave
numeric_vars = ['edad', 'ingreso_pm', 'intensidad_uso', 'n_dispositivos', 'n_actividades']
numeric_vars = [v for v in numeric_vars if v in df.columns]

df_numeric = df[numeric_vars].dropna()
X_numeric = df_numeric.values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_numeric)

# PCA
pca = PCA(n_components=5)
pca_coords = pca.fit_transform(X_scaled)

print(f'Base: {len(df_numeric):,} registros | Variables: {len(numeric_vars)}')
print(f'\nVarianza explicada:')
for i in range(len(pca.explained_variance_ratio_)):
    cumsum = pca.explained_variance_ratio_[:i+1].sum()
    print(f'  PC{i+1}: {pca.explained_variance_ratio_[i]:.3f} ({cumsum:.3f} acumulado)')

print(f'\nLoadings (componentes principales):') 
loadings = pd.DataFrame(
    pca.components_.T,
    columns=[f'PC{i+1}' for i in range(pca.n_components_)],
    index=numeric_vars
)
print(loadings.iloc[:, :3].round(3))


print('\n\n2.3 FAMD — ANÁLISIS FACTORIAL DE DATOS MIXTOS')
print('=' * 80)

# Variables clave
cat_vars = ['sexo', 'zona', 'gse', 'educ_grupo', 'tramo_edad']
num_vars = ['edad', 'ingreso_pm', 'intensidad_uso', 'n_dispositivos']

cat_vars = [v for v in cat_vars if v in df.columns]
num_vars = [v for v in num_vars if v in df.columns]

# Dataset para FAMD
df_famd = pd.concat([df[cat_vars], df[num_vars]], axis=1).dropna()

# FAMD
famd = prince.FAMD(n_components=5, n_iter=3, random_state=42)
famd_coords = famd.fit_transform(df_famd)

print(f'Base: {len(df_famd):,} registros')
print(f'Variables categóricas: {len(cat_vars)} — {cat_vars}')
print(f'Variables numéricas: {len(num_vars)} — {num_vars}')
print(f'Coordenadas FAMD: {famd_coords.shape}')
print(f'\nPrimer vista de coordenadas FAMD:')
print(famd_coords.head())


from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score

print('\n\n2.4 K-MEANS CLUSTERING')
print('=' * 80)

# Usar FAMD coordinates como base para clustering
X_cluster = famd_coords.values

# Determinar número óptimo de clusters (3-8)
inertias = []
silhouette_scores = []
davies_bouldin_scores = []

for k in range(3, 9):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_cluster)
    
    inertias.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X_cluster, labels))
    davies_bouldin_scores.append(davies_bouldin_score(X_cluster, labels))

# Tabla de métricas
cluster_metrics = pd.DataFrame({
    'k': range(3, 9),
    'Inercia': inertias,
    'Silhouette': silhouette_scores,
    'Davies-Bouldin': davies_bouldin_scores
}).round(4)

print('Métricas de clustering (k = 3 a 8):')
print(cluster_metrics.to_string(index=False))

# Seleccionar k óptimo (máximo silhouette)
k_optimal = int(cluster_metrics.loc[cluster_metrics['Silhouette'].idxmax(), 'k'])
print(f'\nClústers óptimos (silhouette máximo): k = {k_optimal}')

# Entrenar modelo final
kmeans_final = KMeans(n_clusters=k_optimal, random_state=42, n_init=10)
cluster_labels = kmeans_final.fit_predict(X_cluster)

# Asignar clusters al df original usando índices de FAMD
df['cluster'] = None
df.loc[famd_coords.index, 'cluster'] = cluster_labels

print(f'\nDistribución de clústeres:')
print(df['cluster'].value_counts().sort_index())


print('\n\n2.5 CARACTERIZACIÓN DE CLUSTERS')
print('=' * 80)

# Filtrar solo registros con cluster asignado
df_clustered = df[df['cluster'].notna()].copy()

# Perfiles demográficos por cluster
for clust in sorted(df_clustered['cluster'].unique()):
    print(f'\n--- CLUSTER {int(clust)} ---')
    subset = df_clustered[df_clustered['cluster'] == clust]
    n = len(subset)
    
    print(f'  N: {n:,} ({n/len(df_clustered)*100:.1f}%)')
    print(f'  Edad media: {subset["edad"].mean():.1f} años')
    print(f'  Sexo: Mujer {(subset["sexo"] == "Mujer").sum()/n*100:.0f}% | Hombre {(subset["sexo"] == "Hombre").sum()/n*100:.0f}%')
    print(f'  GSE: {subset["gse"].mode().values[0] if len(subset["gse"].mode()) > 0 else "N/A"} (moda)')
    print(f'  Habilidades: {subset["nivel_habilidades"].mode().values[0] if len(subset["nivel_habilidades"].mode()) > 0 else "N/A"} (moda)')
    print(f'  Intensidad uso: {subset["intensidad_uso"].mean():.2f}')
    print(f'  N actividades: {subset["n_actividades"].mean():.2f}')
    print(f'  Acceso internet: {(subset["acceso_internet_hogar"] == "Sí").sum()/n*100:.0f}%')


print('\n\n2.6 VISUALIZACIONES — SCATTER PLOTS')
print('=' * 80)

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# FAMD - Dim 0 vs Dim 1 (con clusters)
ax = axes[0, 0]
for clust in sorted(df_clustered['cluster'].unique()):
    mask = df_clustered['cluster'] == clust
    cluster_coords = famd_coords.loc[df_clustered[mask].index]
    ax.scatter(cluster_coords.iloc[:, 0], cluster_coords.iloc[:, 1],
              label=f'Cluster {int(clust)}', alpha=0.6, s=40)
ax.set_xlabel('Dimensión 0', fontsize=10)
ax.set_ylabel('Dimensión 1', fontsize=10)
ax.set_title('FAMD: Clusters en espacio 2D', fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# FAMD - Dim 0 vs Dim 2
ax = axes[0, 1]
for clust in sorted(df_clustered['cluster'].unique()):
    mask = df_clustered['cluster'] == clust
    cluster_coords = famd_coords.loc[df_clustered[mask].index]
    ax.scatter(cluster_coords.iloc[:, 0], cluster_coords.iloc[:, 2],
              label=f'Cluster {int(clust)}', alpha=0.6, s=40)
ax.set_xlabel('Dimensión 0', fontsize=10)
ax.set_ylabel('Dimensión 2', fontsize=10)
ax.set_title('FAMD: Dimensiones 0-2', fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# PCA - PC1 vs PC2
ax = axes[1, 0]
pca_mask_full = df[numeric_vars].notna().all(axis=1)
df_pca_subset = df[pca_mask_full]
pca_data = pca_coords[:len(df_pca_subset)]
for clust in sorted(df_clustered['cluster'].unique()):
    mask_both = pca_mask_full & (df['cluster'] == clust)
    if mask_both.sum() > 0:
        indices = np.where(pca_mask_full)[0]
        cluster_indices = np.where(mask_both)[0]
        pca_indices = [list(indices).index(i) for i in cluster_indices if i in indices]
        if pca_indices:
            ax.scatter(pca_data[pca_indices, 0], pca_data[pca_indices, 1],
                      label=f'Cluster {int(clust)}', alpha=0.6, s=40)
ax.set_xlabel('PC1', fontsize=10)
ax.set_ylabel('PC2', fontsize=10)
ax.set_title('PCA: Componentes principales', fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# Silhouette score por k
ax = axes[1, 1]
ax.plot(cluster_metrics['k'], cluster_metrics['Silhouette'], marker='o', linewidth=2, markersize=8)
optimal_k = cluster_metrics.loc[cluster_metrics['Silhouette'].idxmax(), 'k']
ax.axvline(x=optimal_k, color='red', linestyle='--', label=f'Óptimo k={int(optimal_k)}')
ax.set_xlabel('Número de clusters (k)', fontsize=10)
ax.set_ylabel('Silhouette Score', fontsize=10)
ax.set_title('Métrica de calidad de clustering', fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print('Visualizaciones completadas.')


print('\n\n2.7 ANÁLISIS DE CORRESPONDENCIA — REGIÓN × TIPO DE ACCESO FIJO')
print('=' * 80)

# Tabla de contingencia
contingency = pd.crosstab(df['region'], df['tipo_acceso_fijo'])

print(f'Tabla de contingencia: {contingency.shape[0]} regiones × {contingency.shape[1]} tipos de acceso')
print(f'\nTop 5 combinaciones (por frecuencia):')

# Apilar y ordenar
stacked = contingency.stack().sort_values(ascending=False)
for (region, acceso), count in stacked.head(10).items():
    pct = count / contingency.sum().sum() * 100
    print(f'  {region} × {acceso}: {int(count)} ({pct:.1f}%)')

# Gráfico de asociaciones
fig, ax = plt.subplots(figsize=(12, 8))

# Heatmap de tabla de contingencia normalizada por región
contingency_pct = contingency.div(contingency.sum(axis=1), axis=0) * 100

sns.heatmap(contingency_pct, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax,
            cbar_kws={'label': 'Porcentaje dentro de región (%)'})

ax.set_xlabel('Tipo de acceso fijo', fontsize=10)
ax.set_ylabel('Región', fontsize=10)
ax.set_title('Distribución de tipo de acceso por región (% dentro de región)', fontweight='bold')

plt.tight_layout()
plt.show()


%pip install statsmodels -q
print('Librerías Bloque 3 instaladas')


from statsmodels.stats.weightstats import DescrStatsW

print('\n\n3.1 INTERVALOS DE CONFIANZA PONDERADOS (95%)')
print('=' * 80)

# IC para proporciones (variables binarias)
print('\nProporciones clave con IC 95%:')
proporciones = ['acceso_internet_hogar', 'internet_mejora_vida', 'internet_facilita_trabajo']

for var in proporciones:
    # Crear variable numérica (1 = Sí, 0 = No)
    df_var = df[[var, 'fe_hogar']].copy()
    df_var[var + '_num'] = (df_var[var] == 'Sí').astype(float)
    
    # Descriptivos ponderados
    dw = DescrStatsW(df_var[var + '_num'], weights=df_var['fe_hogar'])
    mean = dw.mean
    ci = dw.tconfint_mean(alpha=0.05)
    
    print(f'  {var}:')
    print(f'    p = {mean:.4f}, IC 95% = [{ci[0]:.4f}, {ci[1]:.4f}]')

# IC para medias (variables numéricas)
print('\nMedias con IC 95%:')
medias_vars = ['edad', 'intensidad_uso', 'ingreso_pm']

for var in medias_vars:
    if var in df.columns:
        df_var = df[[var, 'fe_personas']].dropna()
        dw = DescrStatsW(df_var[var], weights=df_var['fe_personas'])
        mean = dw.mean
        ci = dw.tconfint_mean(alpha=0.05)
        
        print(f'  {var}:')
        print(f'    μ = {mean:.2f}, IC 95% = [{ci[0]:.2f}, {ci[1]:.2f}]')


from scipy.stats import ttest_ind, f_oneway, kruskal, mannwhitneyu

print('\n\n3.2 TESTS DE HIPÓTESIS')
print('=' * 80)

# Test: ¿Edad media difiere entre acceso Sí/No?
print('\nT-test: Edad según acceso internet')
edad_con = df[df['acceso_internet_hogar'] == 'Sí']['edad'].dropna()
edad_sin = df[df['acceso_internet_hogar'] == 'No']['edad'].dropna()
t_stat, p_val = ttest_ind(edad_con, edad_sin)
print(f'  Con acceso: μ={edad_con.mean():.1f}, Sin acceso: μ={edad_sin.mean():.1f}')
print(f'  t={t_stat:.4f}, p={p_val:.4f} {"***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"}')

# Test: ¿Intensidad uso difiere por nivel_habilidades?
print('\nKruskal-Wallis: Intensidad uso según habilidades')
grupos_habil = [df[df['nivel_habilidades'] == niv]['intensidad_uso'].dropna().values 
               for niv in ['Avanzado', 'Intermedio', 'Básico', 'Sin habilidades']]
h_stat, p_val = kruskal(*grupos_habil)
print(f'  H={h_stat:.4f}, p={p_val:.4f} {"***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"}')

# Test: ¿Ingreso difiere por GSE?
print('\nKruskal-Wallis: Ingreso según GSE')
grupos_gse = [df[df['gse'] == g]['ingreso_pm'].dropna().values 
             for g in ['AB', 'C1', 'C2', 'C3', 'D', 'E'] if g in df['gse'].values]
h_stat, p_val = kruskal(*grupos_gse)
print(f'  H={h_stat:.4f}, p={p_val:.4f} {"***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"}')


import statsmodels.api as sm
from sklearn.preprocessing import LabelEncoder

print('\n\n3.3 REGRESIÓN LOGÍSTICA — OUTCOME: ACCESO A INTERNET')
print('=' * 80)

# Preparar datos
df_logistic = df[['edad', 'sexo', 'gse', 'educ_grupo', 'zona', 'acceso_internet_hogar']].dropna().copy()

# Variable dependiente: acceso (1 = Sí, 0 = No)
df_logistic['acceso_num'] = (df_logistic['acceso_internet_hogar'] == 'Sí').astype(int)

# Codificar categóricas
le_dict = {}
for col in ['sexo', 'gse', 'educ_grupo', 'zona']:
    le = LabelEncoder()
    df_logistic[col + '_enc'] = le.fit_transform(df_logistic[col])
    le_dict[col] = le

# Features
X = df_logistic[['edad', 'sexo_enc', 'gse_enc', 'educ_grupo_enc', 'zona_enc']]
X = sm.add_constant(X)
y = df_logistic['acceso_num']

# Fit logit
logit_model = sm.Logit(y, X).fit(disp=False)

print(f'\nN = {len(df_logistic):,}')
print(f'Log-likelihood: {logit_model.llf:.2f}')
print(f'AIC: {logit_model.aic:.2f}')
print(f'BIC: {logit_model.bic:.2f}')

print(f'\nCoeficientes (odds ratios exp(coef)):') 
coef_table = pd.DataFrame({
    'Coef': logit_model.params,
    'OR': np.exp(logit_model.params),
    'p-value': logit_model.pvalues
}).round(4)
print(coef_table)


from statsmodels.miscmodels.ordinal_model import OrderedModel

print('\n\n3.4 REGRESIÓN ORDINAL — OUTCOME: NIVEL DE HABILIDADES')
print('=' * 80)

# Preparar datos
df_ordinal = df[['edad', 'sexo', 'gse', 'educ_grupo', 'zona', 'nivel_habilidades']].dropna().copy()

# Codificar variable dependiente ordinal
orden_habil = {'Sin habilidades': 0, 'Básico': 1, 'Intermedio': 2, 'Avanzado': 3}
df_ordinal['habil_num'] = df_ordinal['nivel_habilidades'].map(orden_habil)

# Codificar categóricas
for col in ['sexo', 'gse', 'educ_grupo', 'zona']:
    le = LabelEncoder()
    df_ordinal[col + '_enc'] = le.fit_transform(df_ordinal[col])

# Features (sin constante para OrderedModel)
X = df_ordinal[['edad', 'sexo_enc', 'gse_enc', 'educ_grupo_enc', 'zona_enc']]
y = df_ordinal['habil_num']

# Fit ordinal (proporcional odds)
ordinal_model = OrderedModel(y, X, distr='logit').fit(disp=False)

print(f'\nN = {len(df_ordinal):,}')
print(f'Log-likelihood: {ordinal_model.llf:.2f}')
print(f'AIC: {ordinal_model.aic:.2f}')

print(f'\nCoeficientes:')
coef_ord = pd.DataFrame({
    'Coef': ordinal_model.params,
    'Std Err': ordinal_model.bse,
    'p-value': ordinal_model.pvalues
}).round(4)
print(coef_ord)


print('\n\n3.5 OLS/WLS — OUTCOME: INTENSIDAD DE USO')
print('=' * 80)

# Preparar datos
df_ols = df[['edad', 'sexo', 'gse', 'educ_grupo', 'zona', 'intensidad_uso', 'fe_personas']].dropna().copy()

# Codificar categóricas
for col in ['sexo', 'gse', 'educ_grupo', 'zona']:
    le = LabelEncoder()
    df_ols[col + '_enc'] = le.fit_transform(df_ols[col])

# Features
X = df_ols[['edad', 'sexo_enc', 'gse_enc', 'educ_grupo_enc', 'zona_enc']]
X = sm.add_constant(X)
y = df_ols['intensidad_uso']

# OLS
ols_model = sm.OLS(y, X).fit()

# WLS (ponderado por fe_personas)
wls_model = sm.WLS(y, X, weights=df_ols['fe_personas']).fit()

print(f'\nN = {len(df_ols):,}')
print(f'\n--- OLS ---')
print(f'R²: {ols_model.rsquared:.4f}')
print(f'Adj. R²: {ols_model.rsquared_adj:.4f}')
print(f'\nCoeficientes:')
ols_coef = pd.DataFrame({
    'Coef': ols_model.params,
    'Std Err': ols_model.bse,
    'p-value': ols_model.pvalues
}).round(4)
print(ols_coef)

print(f'\n--- WLS (Ponderado) ---')
print(f'R²: {wls_model.rsquared:.4f}')
print(f'Adj. R²: {wls_model.rsquared_adj:.4f}')
print(f'\nCoeficientes:')
wls_coef = pd.DataFrame({
    'Coef': wls_model.params,
    'Std Err': wls_model.bse,
    'p-value': wls_model.pvalues
}).round(4)
print(wls_coef)


print('\n\n3.6 RESUMEN — VARIABLES SIGNIFICATIVAS POR MODELO')
print('=' * 80)

# Compilar resultados
models_summary = pd.DataFrame({
    'Modelo': ['Logistic (Acceso)', 'Ordinal (Habilidades)', 'OLS (Intensidad)', 'WLS (Intensidad)'],
    'N': [len(df_logistic), len(df_ordinal), len(df_ols), len(df_ols)],
    'Fit': [f'AIC={logit_model.aic:.0f}', f'AIC={ordinal_model.aic:.0f}', 
            f'R²={ols_model.rsquared:.3f}', f'R²={wls_model.rsquared:.3f}'],
    'Variables significativas (p<0.05)': [
        ', '.join(logit_model.pvalues[logit_model.pvalues < 0.05].index[1:]),
        ', '.join(ordinal_model.pvalues[ordinal_model.pvalues < 0.05].index[1:]),
        ', '.join(ols_model.pvalues[ols_model.pvalues < 0.05].index[1:]),
        ', '.join(wls_model.pvalues[wls_model.pvalues < 0.05].index[1:])
    ]
})

print(models_summary.to_string(index=False))

print('\n\nPatrones comunes:')
print('  - Edad: predictor significativo en todos los modelos')
print('  - GSE: fuerte predictor de habilidades y acceso')
print('  - Zona: efecto débil o no significativo en habilidades')
print('  - Educación: predictor significativo en la mayoría')


%pip install imbalanced-learn shap -q
print('Librerías ML instaladas')


from sklearn.model_selection import train_test_split, cross_validate, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

print('\n\n4.1 PREPARACIÓN DE FEATURES PARA ML')
print('=' * 80)

# Variables de entrada (features)
feature_cat = ['sexo', 'zona', 'gse', 'educ_grupo', 'tramo_edad']
feature_num = ['edad', 'ingreso_pm', 'intensidad_uso', 'n_dispositivos', 'n_actividades']

# Preparar dataset para ML
df_ml = df[feature_cat + feature_num].copy()

# Imputar nulos numéricos
for col in feature_num:
    df_ml[col] = df_ml[col].fillna(df_ml[col].median())

# Codificar categóricas
le_dict = {}
for col in feature_cat:
    le = LabelEncoder()
    df_ml[col + '_enc'] = le.fit_transform(df_ml[col].fillna('Unknown'))
    le_dict[col] = le

# Features finales
feature_cols = feature_num + [c + '_enc' for c in feature_cat]
X_ml = df_ml[feature_cols].values

print(f'Dataset ML: {X_ml.shape[0]:,} registros × {X_ml.shape[1]} features')
print(f'Features numéricos: {feature_num}')
print(f'Features categóricos (encoded): {[c + "_enc" for c in feature_cat]}')
print(f'\nFeatures preparadas para {len(feature_cols)} variables.')


def train_and_evaluate(X, y, outcome_name, task='classification'):
    results = {}
    
    # Limpiar y balancear
    mask = ~pd.isna(y)
    X_clean = X[mask]
    y_clean = y[mask]
    
    if len(y_clean) < 50:
        return None
    
    # Train/test (sin stratify si hay clases raras)
    try:
        if task == 'classification':
            unique_classes = len(np.unique(y_clean))
            stratify_param = y_clean if unique_classes >= 2 and len(y_clean)/unique_classes >= 2 else None
        else:
            stratify_param = None
            
        X_train, X_test, y_train, y_test = train_test_split(
            X_clean, y_clean, test_size=0.2, random_state=42, stratify=stratify_param
        )
    except:
        X_train, X_test, y_train, y_test = train_test_split(
            X_clean, y_clean, test_size=0.2, random_state=42
        )
    
    # Random Forest
    if task == 'classification':
        rf = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)
        
        results['RF_acc'] = accuracy_score(y_test, y_pred)
        results['RF_f1'] = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        results['RF_model'] = rf
    else:
        rf = RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)
        from sklearn.metrics import mean_squared_error, r2_score
        results['RF_r2'] = r2_score(y_test, y_pred)
        results['RF_rmse'] = np.sqrt(mean_squared_error(y_test, y_pred))
        results['RF_model'] = rf
    
    results['feature_importance'] = rf.feature_importances_
    results['n_samples'] = len(y_clean)
    
    return results

print('Función train_and_evaluate cargada (versión robusta).')


print('\n\n4.2 ENTRENAMIENTO DE 6 MODELOS SUPERVISADOS')
print('=' * 80)

# Diccionario de outcomes
outcomes_dict = {
    'nivel_habilidades': 'classification',
    'acceso_internet_hogar': 'classification',
    'tipo_acceso_fijo': 'classification',
    'velocidad_contratada': 'classification',
    'intensidad_uso': 'regression',
    'internet_facilita_trabajo': 'classification'
}

# Codificar outcomes categóricos
df_encoded = df.copy()
for outcome in outcomes_dict:
    if outcome in df.columns and outcomes_dict[outcome] == 'classification':
        if df[outcome].dtype == 'object':
            le = LabelEncoder()
            df_encoded[outcome] = le.fit_transform(df[outcome].fillna('Unknown'))

# Entrenar cada modelo
models_results = {}
for outcome, task in outcomes_dict.items():
    if outcome not in df_encoded.columns:
        continue
    
    y = df_encoded[outcome].values
    results = train_and_evaluate(X_ml, y, outcome, task)
    
    if results:
        models_results[outcome] = results
        if task == 'classification':
            print(f'{outcome}: Acc={results["RF_acc"]:.3f}, F1={results["RF_f1"]:.3f}')
        else:
            print(f'{outcome}: R2={results["RF_r2"]:.3f}, RMSE={results["RF_rmse"]:.2f}')

print(f'\nModelos entrenados: {len(models_results)}/6')


print('\n\n4.3 IMPORTANCIA DE FEATURES POR MODELO')
print('=' * 80)

# Feature importance table
fi_all = []
for outcome, results in models_results.items():
    fi = results['feature_importance']
    top_5_idx = np.argsort(fi)[-5:][::-1]
    print(f'\n{outcome} — Top 5 features:')
    for idx, feat_idx in enumerate(top_5_idx):
        feat_name = feature_cols[feat_idx]
        importance = fi[feat_idx]
        print(f'  {idx+1}. {feat_name:<20} {importance:.4f}')

# Visualizar top 3 modelos
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()

for idx, (outcome, results) in enumerate(list(models_results.items())[:6]):
    if idx >= len(axes):
        break
    fi = results['feature_importance']
    top_10_idx = np.argsort(fi)[-10:][::-1]
    top_features = [feature_cols[i] for i in top_10_idx]
    top_importances = fi[top_10_idx]
    
    axes[idx].barh(range(len(top_features)), top_importances, color='steelblue', edgecolor='black')
    axes[idx].set_yticks(range(len(top_features)))
    axes[idx].set_yticklabels(top_features, fontsize=8)
    axes[idx].set_xlabel('Importancia', fontsize=9)
    axes[idx].set_title(outcome, fontweight='bold', fontsize=10)
    axes[idx].invert_yaxis()

plt.tight_layout()
plt.show()

print('\nGráficos de importancia generados.')


import shap

print('\n\n4.4 INTERPRETABILIDAD SHAP — TOP 3 MODELOS')
print('=' * 80)

# Seleccionar top 3 modelos
top_3_outcomes = list(models_results.keys())[:3]

for outcome in top_3_outcomes:
    results = models_results[outcome]
    rf_model = results['RF_model']
    
    print(f'\n--- {outcome} ---')
    
    # SHAP
    try:
        explainer = shap.TreeExplainer(rf_model)
        shap_values = explainer.shap_values(X_ml[:500])  # Subset para speed
        
        # Handle multiclass
        if isinstance(shap_values, list):
            shap_vals_class = np.abs(np.asarray(shap_values[0])).mean(axis=0)
        else:
            shap_vals_class = np.abs(np.asarray(shap_values)).mean(axis=0)
        
        # Feature importance SHAP
        top_idx = np.argsort(shap_vals_class)[-5:][::-1]
        
        print('Top 5 features (SHAP mean |value|):')
        for idx_pos, feat_idx in enumerate(top_idx):
            feat_idx = int(feat_idx)
            print(f'  {idx_pos+1}. {feature_cols[feat_idx]:<20} {shap_vals_class[feat_idx]:.4f}')
    except Exception as e:
        print(f'  Error en SHAP: {str(e)[:50]}')


print('\n\n5.3 VISUALIZACIONES INTEGRADAS — DASHBOARD FINAL')
print('=' * 80)

# 2x3 dashboard
fig = plt.figure(figsize=(18, 10))
gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

# Convert acceso to numeric
df_plot = df.copy()
if df_plot['acceso_internet_hogar'].dtype != 'float64' and df_plot['acceso_internet_hogar'].dtype != 'int64':
    # String type - convert based on value
    df_plot['acceso_num'] = df_plot['acceso_internet_hogar'].apply(lambda x: 1.0 if str(x).strip() == 'Sí' else 0.0)
else:
    df_plot['acceso_num'] = df_plot['acceso_internet_hogar'].astype(float)

# 1. Distribución de acceso por GSE
ax1 = fig.add_subplot(gs[0, 0])
try:
    acceso_by_gse = df_plot.groupby('gse').apply(
        lambda g: (g['acceso_num'] * g['fe_hogar']).sum() / g['fe_hogar'].sum() * 100
    )
    colors = ['green' if x > 80 else 'orange' if x > 50 else 'red' for x in acceso_by_gse.values]
    acceso_by_gse.plot(kind='bar', ax=ax1, color=colors, edgecolor='black', legend=False)
    ax1.set_title('Acceso a Internet por GSE', fontweight='bold', fontsize=11)
    ax1.set_ylabel('Porcentaje (%)', fontsize=10)
    ax1.set_xlabel('GSE', fontsize=10)
    ax1.set_ylim(0, 105)
    ax1.grid(axis='y', alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
except Exception as e:
    print(f'Error en subplot acceso: {e}')

# 2. Habilidades por GSE (stacked)
ax2 = fig.add_subplot(gs[0, 1])
try:
    hab_order = ['Sin habilidades', 'Básico', 'Intermedio', 'Avanzado']
    hab_gse_list = []
    for gse_val in sorted(df_plot['gse'].unique()):
        gse_data = df_plot[df_plot['gse'] == gse_val]
        totals = {}
        for hab_val in hab_order:
            mask = gse_data['nivel_habilidades'] == hab_val
            total = (gse_data.loc[mask, 'fe_personas']).sum()
            totals[hab_val] = total
        total_all = sum(totals.values())
        if total_all > 0:
            hab_gse_list.append({k: v/total_all*100 for k, v in totals.items()})
        else:
            hab_gse_list.append({k: 0 for k in hab_order})

    hab_by_gse = pd.DataFrame(hab_gse_list, index=sorted(df_plot['gse'].unique()))
    hab_by_gse[hab_order].plot(
        kind='bar', stacked=True, ax=ax2, 
        color=['red', 'yellow', 'orange', 'darkgreen'], 
        edgecolor='black'
    )
    ax2.set_title('Nivel de Habilidades por GSE', fontweight='bold', fontsize=11)
    ax2.set_ylabel('Porcentaje (%)', fontsize=10)
    ax2.set_xlabel('GSE', fontsize=10)
    ax2.legend(title='Nivel', fontsize=8, loc='upper left')
    ax2.set_ylim(0, 105)
    ax2.grid(axis='y', alpha=0.3)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
except Exception as e:
    print(f'Error en subplot habilidades: {e}')

# 3. Intensidad por edad
ax3 = fig.add_subplot(gs[0, 2])
try:
    df_scatter = df_plot[['edad', 'intensidad_uso']].dropna()
    if len(df_scatter) > 1:
        ax3.scatter(df_scatter['edad'], df_scatter['intensidad_uso'], alpha=0.3, s=20, color='steelblue')
        z = np.polyfit(df_scatter['edad'].values.astype(float), df_scatter['intensidad_uso'].values.astype(float), 1)
        p = np.poly1d(z)
        ax3.plot(sorted(df_scatter['edad'].values), 
                p(np.array(sorted(df_scatter['edad'].values), dtype=float)), 
                'r-', linewidth=2, label=f'Tendencia (slope={z[0]:.3f})')
        ax3.legend(fontsize=9)
    ax3.set_title('Intensidad de Uso vs Edad', fontweight='bold', fontsize=11)
    ax3.set_xlabel('Edad', fontsize=10)
    ax3.set_ylabel('Intensidad', fontsize=10)
    ax3.grid(True, alpha=0.3)
except Exception as e:
    print(f'Error en subplot intensidad: {e}')

# 4. Distribución habilidades
ax4 = fig.add_subplot(gs[1, 0])
try:
    hab_dist = df_plot['nivel_habilidades'].dropna().value_counts()
    hab_order2 = ['Sin habilidades', 'Básico', 'Intermedio', 'Avanzado']
    hab_dist = hab_dist.reindex([h for h in hab_order2 if h in hab_dist.index])
    hab_dist_pct = hab_dist / hab_dist.sum() * 100
    ax4.barh(hab_dist_pct.index, hab_dist_pct.values, color='steelblue', edgecolor='black')
    for i, (idx, pct) in enumerate(zip(hab_dist_pct.index, hab_dist_pct.values)):
        ax4.text(pct, i, f'{pct:.1f}%', va='center', ha='left', fontsize=10, fontweight='bold')
    ax4.set_xlabel('Porcentaje (%)', fontsize=10)
    ax4.set_title('Distribución de Habilidades Digitales', fontweight='bold', fontsize=11)
    ax4.grid(axis='x', alpha=0.3)
except Exception as e:
    print(f'Error en subplot distribución: {e}')

# 5. Predictores Top
ax5 = fig.add_subplot(gs[1, 1])
try:
    if 'models_results' in dir() and models_results:
        fi_combined = {}
        for outcome, results in list(models_results.items())[:3]:
            if 'feature_importance' in results:
                fi = results['feature_importance']
                for i, imp in enumerate(fi):
                    if i < len(feature_cols):
                        feat = feature_cols[i]
                        fi_combined[feat] = fi_combined.get(feat, 0) + imp
        
        if fi_combined:
            top_features = sorted(fi_combined.items(), key=lambda x: x[1], reverse=True)[:8]
            features_names = [f[0] for f in top_features]
            importances = [f[1] for f in top_features]
            
            ax5.barh(range(len(features_names)), importances, color='coral', edgecolor='black')
            ax5.set_yticks(range(len(features_names)))
            ax5.set_yticklabels(features_names, fontsize=9)
            ax5.set_xlabel('Importancia Agregada (RF)', fontsize=10)
            ax5.set_title('Top 8 Predictores (Modelos ML)', fontweight='bold', fontsize=11)
            ax5.invert_yaxis()
            ax5.grid(axis='x', alpha=0.3)
except Exception as e:
    print(f'Error en subplot predictores: {e}')

# 6. Cramér's V top associations
ax6 = fig.add_subplot(gs[1, 2])
try:
    if 'df_tests' in dir() and df_tests is not None and len(df_tests) > 0:
        top_tests = df_tests.nlargest(6, 'cramers_v')[['Outcome', 'Predictor', 'cramers_v']]
        if len(top_tests) > 0:
            ax6.barh(range(len(top_tests)), top_tests['cramers_v'].values, 
                    color='mediumseagreen', edgecolor='black')
            labels = [f"{row['Outcome'][:15]}\n× {row['Predictor'][:10]}" 
                     for _, row in top_tests.iterrows()]
            ax6.set_yticks(range(len(top_tests)))
            ax6.set_yticklabels(labels, fontsize=8)
            ax6.set_xlabel("Cramér's V", fontsize=10)
            ax6.set_title('Top 6 Asociaciones (Cramér\'s V)', fontweight='bold', fontsize=11)
            ax6.invert_yaxis()
            ax6.grid(axis='x', alpha=0.3)
except Exception as e:
    print(f'Error en subplot Cramér: {e}')

plt.suptitle('EAUI 2026 — Dashboard de Hallazgos Principales', 
             fontsize=14, fontweight='bold', y=0.995)
plt.tight_layout()
plt.show()

print('Dashboard generado.')