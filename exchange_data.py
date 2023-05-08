from binance.cm_futures import CMFutures
from datetime import date,datetime
import time
import datetime
import config as cf
import pandas as pd
import config as cf

def get_lista_cryptos()->pd.DataFrame:
    """crea una conexion a la api del exchange y extrae 
       los pares operables de futuros, los devuelve como
       un dataframe"""
    
    client = CMFutures(key=cf.FUTURES_API_KEY, secret=cf.FUTURES_SECRET_KEY)
    info=client.account()
    #extraemos la lista de cryptos disponibles del objeto cliente
    serie_symbol=pd.DataFrame(info['positions'])["symbol"]
    #convertimos la serie en un df
    df_symbol=serie_symbol.to_frame(name="crypto")
    # Renombrar índice, para que comience desde 1
    id_columna = list(range(1, len(df_symbol)+1))
    df_symbol['id'] = id_columna
    #df_symbol = df_symbol.rename(index=lambda x: x+1)
    df_symbol=df_symbol.set_index('id')
    return df_symbol

def get_lista_timeframes()->pd.DataFrame:
    """crea un dataframe con los timeframe operables
       en el exchange"""
    #trabajamos en los periods indicados en config
    periods=cf.PERIODS
    #creamos un df a partir de la lista periods
    df_periods=pd.DataFrame(periods)
    #renombramos la unica columna 
    df_periods.columns=["period"]
    #renombramos los indices para que empiece en 1
    #df_periods = df_periods.rename(index=lambda x: x+1)
    id_columna = list(range(1, len(df_periods)+1))
    df_periods['id'] = id_columna
    #df_symbol = df_symbol.rename(index=lambda x: x+1)
    df_periods=df_periods.set_index('id')

    return df_periods

def str_to_unix_time(strtime:str):
    """Devuelve fecha en formato unixtime  a partir de
    una fecha en str,
    ej: "2020,12,24",
    strtime:str
    """
    try:
        #separamos el string de entrada y casteamos cada elemento a int
        anio,mes,dia=map(int,strtime.split(","))
        #creamos la fecha a partir de los datos ingresados
        date_time = date(anio, mes, dia)
        #convertinos la fecha a unixtime
        unix_time=time.mktime(date_time.timetuple())
        #adecuamos a int y milisegundos
        unix_time=int(unix_time)*1000
        return unix_time
    except Exception as e:
        print("ingrese una fecha a partir de 1970 en fomrato 'anio,mes,dia', ej:2020,12,24", e)

def unix_time_to_datetime(unix_time:int):

    unix_time=unix_time/1000#para convertir a segundos
    return datetime.datetime.fromtimestamp(unix_time)

def get_the_last_200_days_info(crypto:str,period:str,n_days=int)->pd.DataFrame:
        """crea una conexion a la api del exchange y extrae datos 
            segun los parametros y devuelve un dataframe"""
        
        #main setup
        crypto=crypto
        period=period

        fecha_actual = datetime.datetime.now().date()
        dias_a_restar = datetime.timedelta(n_days)
        fecha_resultado = fecha_actual - dias_a_restar

        start_time=str_to_unix_time(fecha_resultado.strftime('%Y,%m,%d'))
        
        finish_time=str_to_unix_time(fecha_actual.strftime('%Y,%m,%d'))

        client = CMFutures(key=cf.FUTURES_API_KEY, secret=cf.FUTURES_SECRET_KEY)

        output_df=pd.DataFrame()

        #traemos 500 velas, de las cuales usaremos la ULTIMA  es la referencia, y la primera se utilizara para solicitar el resto
        #debemos traer desde atras para adelante los valores, para poder armar todo el dataframe

        binance_df=pd.DataFrame(client.klines(symbol=crypto,interval=period,startTime=start_time,endTime=finish_time))

        binance_titles=["Open time","Open","High","Low","Close","Volume","Close time","Quote asset volume","Number of trades","Taker buy base asset volume","Taker buy quote asset volume","ignore"]
        binance_df.columns=binance_titles

        #debemos buscar los tiempos en los limites del dataframe

        inicial_requested_unix_time=dict(binance_df.iloc[0])["Open time"]#contenido de la primera vela
        final_requested_unix_time=dict(binance_df.iloc[499])["Open time"]#contenido de la ultima vela

        output_df=binance_df


        if inicial_requested_unix_time>=start_time:
            repeat=True
            while repeat==True:
                try:
                    #es decir que todavia no se alcanzo el starttime, debemos volver a solicitar las barras

                    binance_df=pd.DataFrame(client.klines(symbol=crypto,interval=period,startTime=start_time,endTime=inicial_requested_unix_time))
                    binance_titles=["Open time","Open","High","Low","Close","Volume","Close time","Quote asset volume","Number of trades","Taker buy base asset volume","Taker buy quote asset volume","ignore"]
                    binance_df.columns=binance_titles

                    #agregamos los nuevos datos al dataframe existente
                    output_df = pd.concat([binance_df, output_df], ignore_index=True)#, keys=['nuevo', 'viejo'])

                    #debemos buscar los tiempos en los limites del dataframe
                    inicial_requested_unix_time=dict(binance_df.iloc[0])["Open time"]
                    final_requested_unix_time=dict(binance_df.iloc[499])["Open time"]

                    if inicial_requested_unix_time<=start_time:

                        repeat=False

                except Exception as e:

                    repeat=False

        output_df.drop_duplicates()

        return output_df

def dataframe_trans_to_ORM(dataframe:pd.DataFrame)->pd.DataFrame:
    """adecual el dataframe para crear una columna id, para el mapeo del ORM"""

    #En caso de existir indices duplicados , los eliminamos
    dataframe.drop_duplicates()

    # Selecciona todas las filas y las 6 primeras columnas, y nos queda asi
    #["Open time","Open","High","Low","Close","Volume"]
    dataframe = dataframe.iloc[:, :6] 

    #convertimos la primera fila que esta en formato unix time ms a datetime
    
    dataframe["Open time"] = pd.to_datetime(dataframe["Open time"], unit='ms')

    #establecemosla columna "Open time como indice del dataaframe"

    id_columna = list(range(1, len(dataframe)+1))
    dataframe['id'] = id_columna

    #dataframe=dataframe.set_index("Open time")

    dataframe["Open"] = dataframe["Open"].astype(float)
    dataframe["High"] = dataframe["High"].astype(float)
    dataframe["Low"] = dataframe["Low"].astype(float)
    dataframe["Close"] = dataframe["Close"].astype(float)
    dataframe["Volume"] = dataframe["Volume"].astype(float)

    dataframe = dataframe.rename(columns={'Open time': 'Time'})

    dataframe=dataframe.set_index('id')

    return dataframe

def dataframe_trans_to_testing(dataframe:pd.DataFrame)->pd.DataFrame:
    """Convierte directo de binance a un formato aplicable al testing"""

    #En caso de existir indices duplicados , los eliminamos
    dataframe.drop_duplicates()

    # Selecciona todas las filas y las 6 primeras columnas, y nos queda asi
    #["Open time","Open","High","Low","Close","Volume"]
    dataframe = dataframe.iloc[:, :6] 
    
    #convertimos la primera fila que esta en formato unix time ms a datetime
   
    dataframe["Open time"] = pd.to_datetime(dataframe["Open time"], unit='ms')
    #establecemosla columna "Open time como indice del dataaframe"

    dataframe["Open"] = dataframe["Open"].astype(float)
    dataframe["High"] = dataframe["High"].astype(float)
    dataframe["Low"] = dataframe["Low"].astype(float)
    dataframe["Close"] = dataframe["Close"].astype(float)
    dataframe["Volume"] = dataframe["Volume"].astype(float)

    dataframe.rename(columns={'Open time': 'Time'},inplace=True)

    print(dataframe)

    return dataframe

def dataframe_trans_2(dataframe:pd.DataFrame)->pd.DataFrame:
    """Convierte directo de binance a un formato aplicable al testing"""

    #En caso de existir indices duplicados , los eliminamos
    dataframe.drop_duplicates()

    # Selecciona todas las filas y las 6 primeras columnas, y nos queda asi
    #["Open time","Open","High","Low","Close","Volume"]
    dataframe = dataframe.iloc[:, :6]

    #convertimos la primera fila que esta en formato unix time ms a datetime
    dataframe["Open time"] = pd.to_datetime(dataframe["Open time"], unit='ms')
 
    dataframe["Open"] = dataframe["Open"].astype(float)
    dataframe["High"] = dataframe["High"].astype(float)
    dataframe["Low"] = dataframe["Low"].astype(float)
    dataframe["Close"] = dataframe["Close"].astype(float)
    dataframe["Volume"] = dataframe["Volume"].astype(float)

    dataframe.rename(columns={'Open time': 'Time'},inplace=True)

    return dataframe

if __name__=="__main__":

    print(get_lista_cryptos())
    print(get_lista_timeframes())
    print(get_the_last_200_days_info("BTCUSD_PERP","5m",30))
    print(dataframe_trans_2(get_the_last_200_days_info("BTCUSD_PERP","5m",30)))








