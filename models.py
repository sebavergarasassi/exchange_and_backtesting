from sqlalchemy import  Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Crypto(Base):
    __tablename__="exchange_crypto"
    id= Column(Integer, primary_key=True, index=True,unique=True)
    crypto=Column(String,index=True)
    crypto_id=relationship("Configuracion_exchange",back_populates="crypto")

class Period(Base):
    __tablename__="exchange_period"
    id= Column(Integer, primary_key=True, index=True,unique=True)
    period=Column(String,index=True)
    period_id=relationship("Configuracion_exchange",back_populates="period")
    
class Configuracion_exchange(Base):
    __tablename__="exchange_configuracion"
    id= Column(Integer, primary_key=True, index=True,unique=True)
    n_days=Column(Integer,index=True)

    crypto_id=Column(Integer,ForeignKey("exchange_crypto.id"))
    crypto=relationship("Crypto",back_populates="crypto_id")

    period_id=Column(Integer,ForeignKey("exchange_period.id"))
    period=relationship("Period",back_populates="period_id")

    

class Exchange_data(Base):
    __tablename__="exchange_data"
    id= Column(Integer, primary_key=True, index=True,unique=True)
    Time=Column(String,index=True)
    Open=Column(Float,index=True)
    High=Column(Float,index=True)
    Low=Column(Float,index=True)
    Close=Column(Float,index=True)
    Volume=Column(Float,index=True)


###########################################################################################
class Configuracion_strategy_N0(Base):
    __tablename__="configuracion_strategy_N0"

    #VOLUMEN_MOVING_AVERAGE_SETUP
    id= Column(Integer, primary_key=True, index=True,unique=True)
    #SIMPLE_MOVING_AVERAGE_SETUP
    high_sma_sample=Column(Integer,index=True)
    high_sma_offset=Column(Integer,index=True)
    low_sma_sample=Column(Integer,index=True)
    low_sma_offset=Column(Integer,index=True)






    

   



