from sqlalchemy.orm import Session
import models
import schemas
import pandas as pd

#- EXCHANGE---------------------------------------------------------------------------#

#- EXCHANGE CONFIGURACION-------------------------------------------------------------#

def get_exchange_configuracion_all(db: Session):
    #trae todos los registros como figuran en la tabla de configuracion principal
    return db.query(models.Configuracion_exchange).all()

def get_exchange_configuracion_actual(db: Session):
    #devuelve la ultima configuracion sin join
    return db.query(models.Configuracion_exchange).order_by(models.Configuracion_exchange.id.desc()).first()

def get_exchange_configuracion_actual_joined(db: Session):
    #trae todos los registros de la tabla principal joined con los campos que tiene fk
    return db.query(models.Configuracion_exchange.id,models.Configuracion_exchange.n_days,models.Crypto.crypto,models.Period.period).filter(
    models.Configuracion_exchange.crypto_id==models.Crypto.id,models.Configuracion_exchange.period_id==models.Period.id    
    ).order_by(models.Configuracion_exchange.id.desc()).first()

def set_exchange_default_configuration(db: Session,configuracion_base:schemas.Configuracion_exchange_base):
    #establece la configuracion por default, partiendo de configuracion base en schemas
    db_configuracion = models.Configuracion_exchange(
                                            n_days=configuracion_base.n_days,
                                            period_id=configuracion_base.period_id,
                                            crypto_id=configuracion_base.crypto_id
                                            )
    db.add(db_configuracion)
    db.commit()
    db.refresh(db_configuracion)
    return db_configuracion

def get_all_exchange_configuracion_joined(db: Session):
    #trae toda las cofiguraciones cruzadas con la tabla de cryptos y periods
    return db.query(
        models.Configuracion_exchange.id,models.Configuracion_exchange.n_days,models.Crypto.crypto,models.Period.period).filter( #traemos las columnas que queremos y luego las joineamos
        models.Configuracion_exchange.crypto_id==models.Crypto.id,models.Configuracion_exchange.period_id==models.Period.id).all()

   

#-EXCHANGE_DATA ---------------------------------------------------------------------------#

def check_exchange_data(db:Session):
    #consultamos la existencia de valores OHLC en la cb_local
    return db.query(models.Exchange_data).all()

def get_exchange_df_from_db(db: Session):
    #consulta a la base de datos local que nos devuelve todos los registros de las 5 dimensiones del mercado
    return db.query(models.Exchange_data).with_entities(models.Exchange_data.Time, 
                                                       models.Exchange_data.Open, 
                                                       models.Exchange_data.High, 
                                                       models.Exchange_data.Low, 
                                                       models.Exchange_data.Close,
                                                       models.Exchange_data.Volume).all() 

#- STRATEGY N0 CONFIGURACION-------------------------------------------------------------#

def get_stg_N0_configuracion_actual(db: Session):
    return db.query(models.Configuracion_strategy_N0).all()

def set_stg_N0_default_configuration(db: Session,configuracion_base:schemas.Configuracion_strategy_N0_base):
    db_configuracion = models.Configuracion_strategy_N0(
                                            high_sma_sample=configuracion_base.high_sma_sample,
                                            high_sma_offset=configuracion_base.high_sma_offset,
                                            low_sma_sample=configuracion_base.low_sma_sample,
                                            low_sma_offset=configuracion_base.low_sma_offset
                                            )
    db.add(db_configuracion)
    db.commit()
    db.refresh(db_configuracion)
    return db_configuracion

def get_stg_N0_last_config_df_from_db(db: Session):
    #trae un solo resigtro

    return db.query(
        models.Configuracion_strategy_N0).order_by(
        models.Configuracion_strategy_N0.id.desc()).with_entities( 
                                                                models.Configuracion_strategy_N0.high_sma_sample,
                                                                models.Configuracion_strategy_N0.high_sma_offset,
                                                                models.Configuracion_strategy_N0.low_sma_sample,
                                                                models.Configuracion_strategy_N0.low_sma_offset
                                                        
                                                                ).first() 

def get_stg_N0_all_config_df_from_db(db: Session)->list:

    return db.query(models.Configuracion_strategy_N0).with_entities( 
                                                                models.Configuracion_strategy_N0.high_sma_sample,
                                                                models.Configuracion_strategy_N0.high_sma_offset,
                                                                models.Configuracion_strategy_N0.low_sma_sample,
                                                                models.Configuracion_strategy_N0.low_sma_offset
                                                               
                                                                ).all() 

