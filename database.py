from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#from settings import NOMBRE_BBDD
import config as cf

#especificamos la URL de la base de datos, en este la ubicacion del archivo de sqlite
SQLALCHEMY_DATABASE_URL = f'sqlite:///{cf.DDBB_NAME}.sqlite'
# Creamos el engine que nos permitira conectar con sqlite
# connect_args, parametros particulares pada cada base
engine=create_engine(SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread": False}) 
# engine=create_engine(SQLALCHEMY_DATABASE_URL,connect_args={}) 
# importamos el objeto base
# Cada Instancia de esta clase= una sesion 
# contra la base

SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False, 
                            bind=engine)

# La clase madre del ORM
# cada instancia de la clase 
# sera una objeto-tabla 
Base = declarative_base()