from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import schemas
import crud
import pandas as pd
import exchange_data as bn_data
import uvicorn
import config as cf
from fastapi.responses import StreamingResponse 
from io import BytesIO 
#importamos las estrategias
import strategy_N0 as stg0

#crear tablas en la DB en base a models
models.Base.metadata.create_all(bind=engine)

app=FastAPI(title="Pepino Exchange & Backtesting!",description="Setea y corre tu backtesting",version=0.1)

#- CONECTION ---------------------------------------------------------------------------#

def get_db():#conexion a la BBDD---->para poder aplicar DEPENDS y crear sesiones
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#- HOME  ---------------------------------------------------------------------------#

@app.get("/",tags=[""], include_in_schema=False)
def home():
    """Devuelve un mensaje de bienvenida al proyecto"""
    
    return {"Welcome to Pepino Exchange & Backtesting!, please visit /docs"}

#- EXCHANGE ---------------------------------------------------------------------------#

@app.get("/exchange/all_cryptos", tags=["Exchange-show"])
def obtener_cryptos_operables(db: Session = Depends(get_db)):
    """Devuelve todos los contratos de pares futuros operables por el exchange"""

    symbols_df=bn_data.get_lista_cryptos()
    symbols_df.to_sql(name='exchange_crypto', con=engine, if_exists='replace',index=True)

    return symbols_df.to_dict()

@app.get("/exchange/all_timeframes", tags=["Exchange-show"])
def obtener_periods_operables(db: Session = Depends(get_db)):
    """Devuelve los timeframes operables en el exchange""" 

    periods_df=bn_data.get_lista_timeframes()
    periods_df.to_sql(name='exchange_period', con=engine, if_exists='replace',index=True)
    return periods_df.to_dict()

@app.post("/exchange/configuracion/",tags=["Exchange-set"],response_model=schemas.Configuracion_exchange)
def setear_configuracion(default_configuracion:schemas.Configuracion_exchange_base,db: Session = Depends(get_db)):
    """configuracion para extraer datos del exchange"""
    
    #1)actualizamos criptos en la local_db, tabla:exchange_crypto
    symbols_df=bn_data.get_lista_cryptos()
    symbols_df.to_sql(name='exchange_crypto', con=engine, if_exists='replace',index=True)

    #2)actualizamos timeframes en la local_db , tabla:exchange_period
    periods_df=bn_data.get_lista_timeframes()
    periods_df.to_sql(name='exchange_period', con=engine, if_exists='replace',index=True)

    #3)guardamos la informacion en la tabla: exchange_configuracion

    db_configuracion=crud.set_exchange_default_configuration(db,default_configuracion)

    return db_configuracion

@app.get("/exchange/configuracion/",tags=["Exchange-show"])
def obtener_configuracion_actual(db: Session = Depends(get_db)):
    """Devuelve configuracion actual para extraer datos del exchange""" 

    last_configuacion=crud.get_exchange_configuracion_actual_joined(db)
    print(last_configuacion)
    if last_configuacion==None:
        raise HTTPException(status_code=404, detail=cf.MENSAJE_1)
    return last_configuacion

@app.get("/exchange/",tags=["Exchange-refresh"])
def actualizar_data_en_DB_local(db: Session = Depends(get_db)):
    """extrae datos del exchange y los almacena en una base de datos local"""

    #debemos verificar que existe algun registro en la base de datos
    last_configuacion=crud.get_exchange_configuracion_actual_joined(db)
    print(last_configuacion)
    if last_configuacion==None:
        raise HTTPException(status_code=404, detail=cf.MENSAJE_1)
   
    #con last configuracion, podemos parametrizar la funcion get_the_last_200_days_info 
    #con  get_the_last_200_days_info obtenemos el df con la info del exchange
    #nos conectamos a la API del exchange y traemos los ultimos n_dias
    
    try:
        binance_df=bn_data.get_the_last_200_days_info(
                                                    crypto=last_configuacion.crypto,
                                                    period=last_configuacion.period,
                                                    n_days=last_configuacion.n_days)
        #filtramos el dataframe obtenido y solo dejamos los valores que nos interesan
        binance_df=bn_data.dataframe_trans_to_ORM(binance_df)
    except Exception as e:
         raise HTTPException(status_code=400, detail=cf.MENSAJE_2+str(e))

    #mi_df=pd.DataFrame(
    #     {
    #    "Open_time":['Juan', 'Maria', 'Pedro'],
    #    "Open":[1, 2, 3],
    #    "High":[1, 2, 3],
    #    "Low":[1, 2, 3],
    #    "Close":[1, 2, 3],
    #    "Volume":[1, 2, 3]
    #     })
    #guarda en la tabla "exchange_data", mediante la conxion engine, 
    #mi_df.to_sql(name='exchange_data', con=engine, if_exists='replace',index=False)
    
    #grabamos la info del dataframe en una base de datos, para acceder a las posibles combinaciones de nuestra configuracion
    #->name='exchange_data'->nombre de la tabla donde se escribiran los datos
    #->con=engine ->nombre de la conexion a la base de datos
    #->if_exists='replace' -> condicion "si_existe, en este caso la reeplazamos tod el contenido de la tabla por uno nuevo
    #->index=True ->utilizamos el indice del dataframe, y lo guardamos, en nuestro caso es el "Open time"
   
    binance_df.to_sql(name='exchange_data', con=engine, if_exists='replace',index=True)

    initial_time=(list(binance_df["Time"])[0])
    final_time=(list(binance_df["Time"])[-1])
    
    return {f"Se guradaron los datos de {last_configuacion.crypto} en period={last_configuacion.period} desde {initial_time} hasta {final_time}"}
    
@app.get("/exchange/configuracion/descarga",tags=["Exchange-download"])
def descargar_configuracion_exchange_actual(db: Session = Depends(get_db)):
    """genera un archivo excel con la  ultima configuracion de extraccion de datos"""
    
    last_configuacion=crud.get_exchange_configuracion_actual_joined(db)
    print(last_configuacion)
    if last_configuacion==None:
        raise HTTPException(status_code=404, detail=cf.MENSAJE_1)

    #adecuamos la ultima configuracion para poder generar un df adecuado
    last_configuacion_df=pd.DataFrame(list(last_configuacion))
    titles=["id","n_days","crypto","period"]
    last_configuacion_df=last_configuacion_df.transpose()
    last_configuacion_df.columns=titles
   
    buffer = BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        last_configuacion_df.to_excel(writer, index=False)

    return  StreamingResponse(
        BytesIO(buffer.getvalue()),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": f"attachment; filename=last_configuacion_df.xls"})
    
@app.get("/exchange/descarga/",tags=["Exchange-download"])
def descargar_OHLC_desde_DB_local(db: Session = Depends(get_db)):
    """genera un archivo con los valores OHLCV"""

    #debemos chequear que existen los valores de OHLC en la db_local (tabal de exchange data)
    db_exhcange_data=crud.check_exchange_data(db)
    if db_exhcange_data==[]:
        raise HTTPException(status_code=400, detail=cf.MENSAJE_4)

    #debemos verificar que existe algun registro en la base de datos
    db_configuracion_all=crud.get_exchange_configuracion_all(db)
    if db_configuracion_all==[]:
        raise HTTPException(status_code=404, detail=cf.MENSAJE_1)

    #DDBB to dataframe
    exchange_df=crud.get_exchange_df_from_db(db)
    
    #de la DDBB traemos una lista de diccionarios que debemos convertier en un df
    exchange_df=pd.DataFrame(exchange_df)

    #eliminamos los duplicados
    exchange_df.drop_duplicates(inplace=True)

    #creamos un objeto buffer, del tipo BytesIO donde guardaremos el df en formato excel
    buffer = BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        exchange_df.to_excel(writer, index=False)

    return  StreamingResponse(
            BytesIO(buffer.getvalue()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment; filename=exchange_df.xls"})

#- BACKTEST STRATEGY N0 ---------------------------------------------------------------------------#

@app.post("/strategy_N0/configuracion/",tags=["Strategy_N0-set"],response_model=schemas.Configuracion_strategy_N0)
def setear_configuracion_strategy_N0(default_configuracion:schemas.Configuracion_strategy_N0,db: Session = Depends(get_db)):

    db_configuracion=crud.set_stg_N0_default_configuration(db,default_configuracion)
    if db_configuracion==[]:
        raise HTTPException(status_code=404, detail=cf.MENSAJE_3)
    return db_configuracion

@app.get("/strategy_N0/configuracion",tags=["Strategy_N0-show"],response_model=schemas.Configuracion_strategy_N0)
def obtener_configuracion_strategy_N0_actual(db: Session = Depends(get_db)):
    db_configuracion=crud.get_stg_N0_configuracion_actual(db)
    if db_configuracion==[]:
        raise HTTPException(status_code=404, detail=cf.MENSAJE_3)
    last_configuacion=crud.get_stg_N0_configuracion_actual(db)[-1]
    return last_configuacion

@app.get("/strategy_N0/configuracion/descarga",tags=["Strategy_N0-download"])
def descargar_configuracion_strategy_N0_actual(db: Session = Depends(get_db)):
    db_configuracion=crud.get_stg_N0_configuracion_actual(db)
    if db_configuracion==[]:
        raise HTTPException(status_code=404, detail=cf.MENSAJE_3)
    all_configuraciones=crud.get_stg_N0_all_config_df_from_db(db)
    #last_configuacion_df=pd.DataFrame(db_configuracion)    
    all_configuraciones_df=pd.DataFrame(all_configuraciones)
    df_last = all_configuraciones_df.tail(1).copy()
    
    #print(df_last)
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        df_last.to_excel(writer, index=False)
   
    return  StreamingResponse(
            BytesIO(buffer.getvalue()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment; filename=df_last.xls"})

@app.get("/strategy_N0/descarga",tags=["Strategy_N0-download"])
def Descargar_resultados_strategy_N0(db: Session = Depends(get_db)):

    #debemos chequear que existen los valores de OHLC en la db_local (tabal de exchange data)
    db_exhcange_data=crud.check_exchange_data(db)
    if db_exhcange_data==[]:
        raise HTTPException(status_code=400, detail=cf.MENSAJE_4)

    #buscamos la configuracion actual
    db_configuracion=crud.get_stg_N0_configuracion_actual(db)
    if db_configuracion==[]:
        raise HTTPException(status_code=404, detail=cf.MENSAJE_3)
    
    #en caso de existir una configuracion, traemos la ultima para continuar
    last_configuacion=crud.get_stg_N0_configuracion_actual(db)[-1]

    #DDBB to dataframe
    binance_df=crud.get_exchange_df_from_db(db)
    
    #de la DDBB traemos una lista de diccionarios que debemos convertier en un df
    binance_df=pd.DataFrame(binance_df)

    #eliminamos los duplicados
    binance_df.drop_duplicates(inplace=True)
    print(binance_df)
    #cambiamos el indice, de id a Time, para poder aplicar la estrategia
    binance_df.set_index("Time", inplace=True)

    all_df=stg0.strategy(
                        binance_df=binance_df,
                        high_sma_sample=last_configuacion.high_sma_sample,
                        high_sma_offset=last_configuacion.high_sma_offset,
                        low_sma_sample=last_configuacion.low_sma_sample,
                        low_sma_offset=last_configuacion.low_sma_offset
                        )

    #creamos un objeto buffer, del tipo BytesIO donde guardaremos el df en formato excel
    buffer = BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        all_df.to_excel(writer, index=False)

    return  StreamingResponse(
            BytesIO(buffer.getvalue()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment; filename=all_df.xls"})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)