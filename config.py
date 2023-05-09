#FUTURES ACCOUNT

FUTURES_API_KEY="M3b9K3Uo60qzmGZ4c0hRcPMEXjDyy6tRypUP9fFw2Rk1S3cGCDdhj6zorBRLigSA"
FUTURES_SECRET_KEY="wwV8fq890wXzaPuHK91q0Vdo2OnCvPAbd51SwQ5PhyNbsMFzCT9G59T07is0QRoX"

#AvAILABLE TIMEFRAMES
#(#1S IS NOT OPERABLE)

PERIODS = ["1m","3m","5m","15m","30m"]#,"1h","2h","4h","6h","8h","12h","1d","3d","1w","1M"]

#DEFAULT SETUP

DDBB_NAME="Backtesting_db"

PERIOD=3#--->5m
N_DAYS=30#--->Numero de dias a analizar
FUTURES_CRYPTO=11#--->BTCUSDT_PERP

#STRATEGY --->STG_N0

#SIMPLE_MOVING_AVERAGE_SETUP
STG0_HIGH_SMA_SAMPLE=12#--->based in high values
STG0_HIGH_SMA_OFFSET=3#--->based in high values
STG0_LOW_SMA_SAMPLE=12#--->based in low values
STG0_SLOW_SMA_OFFSET=3#--->based in low values

#MESSAGES

MENSAJE_1="no se encontraron datos en exchange_configuracion, es necesario setear configuracion en Exchange-set"
MENSAJE_2="Exchange no esa respondiendo, ---> Cambiar configuracion en /configuracion/ Setear configuracion <--- " 
MENSAJE_3="no se configuracion para strategy N0, es necesario setear configuracion en Strategy_N0-SET"
MENSAJE_4="no se encontraron valores OHLCV, intente actualizar la db local en Exchange-refresh"

