import pandas as pd

class SMA():
    def __init__(self,price:list,sample:int):
        self.price=price
        self.sample=sample
        self.SMA=price.rolling(window=sample).mean()

    def sma_offset(self,offset:int):
        self.offset_SMA = self.SMA.shift(periods=offset)
        return self.offset_SMA
        
class OP():

    def __init__(self,type:str,op_signal_index:int,df:pd.DataFrame):
        self.type=type#buy or sell
        self.status="pre_Open"
        self.op_signal_index=op_signal_index
        self.op_signal_price=df["Close"][op_signal_index]
        self.op_signal_time=df.index[op_signal_index]

    def op_confirmed(self,i:int,df:pd.DataFrame):
        #df:indeX['Open', 'High', 'Low', 'Close', 'Volume', 'high_SMA','low_SMA']
        
        if self.type=="buy":
            candel_values=[df['Open'][i],df['High'][i],df['Low'][i],df['Close'][i]]
            confirmed=False
            #debemos analizar los valores, si alguno es mayor, abre la operacion
            for value in candel_values:
                if value>self.op_signal_price:
                    confirmed=True
                    self.index_in=i
                    self.price_in=value
                    self.time_in=df.index[i]
                    self.status="Open"
            return confirmed
        
        if self.type=="sell":
            candel_values=[df['Open'][i],df['High'][i],df['Low'][i],df['Close'][i]]
            confirmed=False
            #debemos analizar los valores, si alguno es menor, abre la operacion
            for value in candel_values:
                if value<self.op_signal_price:
                    confirmed=True
                    self.index_in=i
                    self.price_in=value
                    self.time_in=df.index[i]
                    self.status="Open"
            return confirmed
        
    def open_op(self,i:int,df:pd.DataFrame):
        self.index_in=i
        self.price_in=df["Close"][i]
        self.time_in=df.index[i]
        self.status="Open"

    def close_op(self,i:int,price_out:float,df:pd.DataFrame):
        self.index_out=i
        self.price_out=price_out
        self.time_out=df.index[i]
        self.status="Closed"

        if self.type=="buy":
            self.pips_res=self.price_out-self.price_in

        if self.type=="sell":
            self.pips_res=self.price_in-self.price_out
 

    @staticmethod
    def op_sorted_list_by_time_in(op_list):
        sorted_list=[]
        sorted_list = sorted(op_list, key=lambda x: x.index_in)
        return sorted_list

if __name__ == "__main__":
    df = pd.DataFrame({'A': [1, 2, 3,4,5,6], 'B': [4, 5, 6,7,8,9]})
    media=SMA(df['A'],2)
    df["high_SMA"]=media.SMA
    print(df)





