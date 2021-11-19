###  BAAMSAT CAMERA PAYLOAD AUTO MODE ###

import pandas as pd

class AutoMode():
    def __init__(self,df_name):
        self.df = pd.read_pickle(df_name)
    
    def print_command_list(self):
        print(self.df)
        return self.df.to_string()

    def add_command(self,command,length=None):
        new_row = {'command':command,'length':length}
        self.df = self.df.append(new_row,ignore_index = True)

    def delete_command(self,number):
        try:
            self.df = self.df.drop(number)
            self.df = self.df.reset_index(drop=True)
        except:
            pass
    
    def save_command_history(self):
        self.df.to_pickle("./command_AutoMode.pkl")
    
    def read_command(self):
        try:
            command = self.df["command"][0]
            length = self.df["length"][0]
            self.delete_command(0)
            if length == None:
                return command,None
            else:
                return command, length
        except:
            return None,None



