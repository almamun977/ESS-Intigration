import csv
import cx_Oracle
import shutil
import os
from datetime import date
import pandas as pd
import glob
import xlsxwriter



class Helper:
   def __init__(self,val):
       self.val=val
       #print("wllcome to Python ", self.val)
   
   def DBconfigPOS(self):
       #print("OralceDB Connection")
       con = cx_Oracle.connect('CFDB/test123@172.16.10.73:2634/PRODPOS2')
       return con

   def DBconfigDMS(self):
       #print("OralceDB Connection")
       con = cx_Oracle.connect('DMSPHASE4/DMSPHASE4@172.16.10.73:2634/PRODPOS2')
       return con
    
   def ExecuteSQL(SQLSTRING, DB):
       if DB == 1 :
           con = DBconfigPOS()
       else :
            con = DBconfigDMS()

       cursor = con.cursor()
       r = cursor.execute(SQLSTRING)
       return cursor

   def GenerateErrorMessage(self, vMSISDN, vMSG):
            con = self.DBconfig()
            cursor = con.cursor()
            #dt_string = date.strftime("%d/%m/%Y %H:%M:%S")
            insrt_stmt = """insert into SMSGATEWAY.tblsend(APPLICATION, MSISDN, MESSAGE, CREATED, STATUS, DELIVERY_FLAG, UPDATE_TIME, DELIVERY_TIME, REPLY_ADDR, ERRORMSG) values(%S, %S,%S, :now, %S,%S,%S,%S,%S,%S)"""
            value = ('DMS', vMSISDN, vMSG, date.datetime.now(), 'N','','','','ERR_SYS_MON','')
            cursor.execute(insrt_stmt, value)
            conn.commit()

   def GenerateErrorLog(self, vFILENAME, vROWNUMBER, vDIS_LOCATION, vERROR_MESSAGE, vMSISDN, vISERROR):
            con = self.DBconfigDMS()
            cur = con.cursor()
            order_count = cur.var(int)
            cur.callproc('SAVE_SYS_MON_DATA_TRANSFER_LOG', [vFILENAME, vROWNUMBER, vDIS_LOCATION, vERROR_MESSAGE, vMSISDN, vISERROR, order_count])
            con.commit()
            return 0

   def GenerateCSV(self,SQLSTRING,FILE_NAME,FILE_PATH, FILE_DIS, DB):

       csv_file = open(r"E:\SYS_MONITORING_DUMP\exportFiles\SYS_MON_"+FILE_NAME, "w")
 
       if DB == 1 :
           con = self.DBconfigPOS()
       else :
            con = self.DBconfigDMS()       

       cursor = con.cursor()
       print("Task Start for csv generate : "+ FILE_NAME)
       
       try:            
            writer = csv.writer(csv_file, delimiter=',', lineterminator="\n", quoting=csv.QUOTE_NONNUMERIC)
            r = cursor.execute(SQLSTRING)            
            rownum = 0
            #rownum = cursor.rowcount

            writer.writerow(i[0] for i in cursor.description)
            for row in cursor:
                writer.writerow(row)
                rownum = rownum+1

            #self.TransferFile(FILE_PATH,FILE_DIS,rownum )
            return rownum
        
       except Exception as e:
           errorMessage = "System monitoring Excel generate got Exception Error for ("+FILE_NAME+" ): " + str(e)
           print(errorMessage)
           ii = self.GenerateErrorLog(FILE_PATH, -1, "", errorMessage,'0', 1)
           return -1

       finally:
            cursor.close()
            con.close()
            csv_file.close()


   def GenerateXLSX(self,SQLSTRING,FILE_NAME,FILE_PATH, FILE_DIS, DB):
       row = 0

       try:
           if DB == 1 :
               con = self.DBconfigPOS()

           else :
                con = self.DBconfigDMS()       

           with pd.ExcelWriter(FILE_PATH, engine="xlsxwriter", options = {'strings_to_numbers': True, 'strings_to_formulas': False}) as writer:
                try:
                    df = pd.read_sql(SQLSTRING, con)
                    df.to_excel(writer, sheet_name = "Sheet1", header = True, index = False)
                    print("File saved successfully!")
                    row = len(df.axes[0])
                except:
                    print("There is an error")

           return row

       except Exception as e:
           errorMessage = "System monitoring Excel generate got Exception Error for ("+FILE_NAME+" ): " + str(e)
           print(errorMessage)
           ii = self.GenerateErrorLog(FILE_PATH, -1, "", errorMessage,'0', 1)
           return -1

       finally:
            #cursor.close()
            con.close()
            return row
            #workbook.close()
   

   def TransferFile(self,source, destination, rownum):
       try:
           shutil.copyfile(source, destination)
           errorMessage = "File transfer done to FPT server... "
           #ii = self.GenerateErrorLog(source, rownum, destination, errorMessage,'', 0)
           print(errorMessage)
           return 1

       except Exception as e:
           errorMessage = "System monitoring file Transfer got Exception for(: "+source + str(e)
           ii = self.GenerateErrorLog(source, -1, destination, errorMessage,'', 1)
           print(errorMessage)
           return 0


   def delete_old_files(self):
        files = glob.glob('\\Bldhkappdev03\Sales_System_Daily_Perfomance_Dump\POS_DMS_RSOAPP/*.xlsx')
        files_local = glob.glob('E:\SYS_MONITORING_DUMP\exportFiles\*.xlsx')

        for f in files:
            os.remove(f)
                
        for fl in files_local:          
                os.remove(fl)







   