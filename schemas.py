
from pydantic import BaseModel,conint
import config as cf
import exchange_data as bn_data

#- FUTURES_CRYPTO--------------------------------------------------------------------------------#

class   Crypto_base(BaseModel):
    crypto:str

class Crypto(Crypto_base):
    id:int
    class Config:
        orm_mode=True


#- PERIODD --------------------------------------------------------------------------------#

class Period_base(BaseModel):
    period:str

class Period(Period_base):
    id:int
    class Config:
        orm_mode=True


#- CONFIGURACION EXCHANGE------------------------------------------------------------------------#

class Configuracion_exchange_base(BaseModel):
    
    #MAIN
    #el tipo conint represeta los limites inferior y superior 
    n_days: conint(ge=1, le=200)=cf.N_DAYS #---> El numero de dias debe estar comprendido entre 1 y 200 dias
    period_id:conint(ge=1,le=bn_data.get_lista_cryptos().shape[0])=cf.PERIOD#---> El limite superior de id_cryptos es movil y depende de los pares que la plataforma tenga disponibles
    crypto_id:conint(ge=1,le=bn_data.get_lista_timeframes().shape[0])=cf.FUTURES_CRYPTO#---> El limite superior depende de los timeframe operables habilitatos en config
 
class Configuracion_exchange(Configuracion_exchange_base):
    id:int
    class Config:
        orm_mode=True

#- EXCHANGE ------------------------------------------------------------------------#

#original data:
#["Open time","Open","High","Low","Close","Volume","Close time","Quote asset volume","Number of trades","Taker buy base asset volume","Taker buy quote asset volume","ignore"]
class Exchange_data_base(BaseModel):
    Time:str
    Open:float
    High:float
    Low:float
    Close:float
    Volume:float


class Binance_data(Exchange_data_base):
    id:int
    class Config:
        orm_mode=True

#- CONFIGURACION STRATEGY N0------------------------------------------------------------------------#

class Configuracion_strategy_N0_base(BaseModel):
    
    #MAIN
   
    #SIMPLE_MOVING_AVERAGE_SETUP
    #adoptamos como valor superior 1000, a modo practico, pero podria adoptarse uno superior
    high_sma_sample: conint(ge=1, le=1000)=cf.STG0_HIGH_SMA_SAMPLE
    high_sma_offset:conint(ge=1, le=1000)=cf.STG0_HIGH_SMA_OFFSET
    low_sma_sample:conint(ge=1, le=1000)=cf.STG0_LOW_SMA_SAMPLE
    low_sma_offset:conint(ge=1, le=1000)=cf.STG0_SLOW_SMA_OFFSET

class Configuracion_strategy_N0(Configuracion_strategy_N0_base):
    id:int
    class Config:
        orm_mode=True





