import pandas as pd
import strategy_N0_schemas as schemas
import exchange_data as bn_data
import config as cf

def strategy(binance_df:pd.DataFrame,
                    high_sma_sample:int,
                    high_sma_offset:int,
                    low_sma_sample:int,
                    low_sma_offset:int
                    )->pd.DataFrame:
    
    #source: https://www.youtube.com/watch?v=pXm6vsPaipI&t=265s

    #recordar que las variables OPEN, HIGH CLOSE LOW, DEBEN ESTAR EN FLOAT!!!!
   
    #1)high_SMA

    print(binance_df) 

    high_SMA=schemas.SMA((binance_df["High"]),high_sma_sample)
    binance_df["high_SMA"]=high_SMA.SMA
    binance_df["offset_high_SMA"]=schemas.SMA.sma_offset(high_SMA,high_sma_offset)


    #2)low_SMA

    low_SMA=schemas.SMA((binance_df["Low"]),low_sma_sample)
    binance_df["low_SMA"]=low_SMA.SMA
    binance_df["offset_low_SMA"]=schemas.SMA.sma_offset(low_SMA,low_sma_offset)


############################################################################################################################################################
    buy_status="Closed"
    sell_status="Closed"

    OP_B=[]
    OP_S=[]

    for i in range(0,binance_df.shape[0]):
        #BUY:

        #1)
        if buy_status=="Closed":
            #esperamos una señal de compra
            if binance_df["Close"][i]>binance_df["offset_high_SMA"][i]:
                buy_status="pre_open"
                op_b=schemas.OP(type="buy",op_reference_index=i,df=binance_df)
        #2)
        elif buy_status=="pre_open":
            #esperamos una confirmacion de compra
            if schemas.OP.op_confirmed(op_b,i=i,df=binance_df)==True:
                #compra confirmada!!!

                OP_B.append(op_b)
                buy_status="Open"
        #3)
        elif binance_df["Close"][i]<binance_df["offset_low_SMA"][i]:
            if buy_status=="Open":
            #esperamos señal de salida

                for op_b in OP_B:
                    if op_b.status=="Open":
                        schemas.OP.close_op(op_b,i,binance_df["Close"][i],binance_df)
                        buy_status="Closed"
            elif buy_status=="pre_open":
                buy_status="Closed"

        
        #SELL:
        #4)
        if sell_status=="Closed":
            #esperamos una señal de venta
            if binance_df["Close"][i]<binance_df["offset_low_SMA"][i]:
                sell_status="pre_open"
                op_s=schemas.OP(type="sell",op_reference_index=i,df=binance_df)
        #5)
        elif sell_status=="pre_open":
            #esperamos una confirmacion deventa
            if schemas.OP.op_confirmed(op_s,i=i,df=binance_df)==True:
                #compra confirmada!!!

                OP_S.append(op_s)
                sell_status="Open"
        #6)
        elif binance_df["Close"][i]>binance_df["offset_high_SMA"][i]:
            if sell_status=="Open":
                #esperamos señal de salida
                
                for op_s in OP_S:
                    if op_s.status=="Open":
                        schemas.OP.close_op(op_s,i,binance_df["Close"][i],binance_df)
                        sell_status="Closed"
            elif sell_status=="pre_open":
                sell_status="Closed"



    ALL_OP=OP_B+OP_S
    #juntamos las listas y luego las ordenamos por time in
    ALL_OP = schemas.OP.op_sorted_list_by_time_in(ALL_OP)

    all_df=[]
    for op in ALL_OP:
        all_df.append(op.__dict__)
    all_df=pd.DataFrame(all_df)

    return all_df

if __name__=="__main__":

    binance_df=bn_data.dataframe_trans_2(bn_data.get_the_last_200_days_info("BTCUSD_PERP","5m",30))
    print(binance_df.head(5)) 
    print (strategy(binance_df=binance_df,
                    high_sma_sample=cf.STG0_HIGH_SMA_SAMPLE,
                    high_sma_offset=cf.STG0_HIGH_SMA_OFFSET,
                    low_sma_sample=cf.STG0_LOW_SMA_SAMPLE,
                    low_sma_offset=cf.STG0_SLOW_SMA_OFFSET))
                



