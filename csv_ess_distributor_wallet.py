
import shutil
import os
from datetime import timedelta, date
from helper import Helper

DAY_BACK = -1


today_date = date.today() + timedelta(days=(DAY_BACK))  #date.today()  # dd/mm/YY
FILE_NAME = today_date.strftime("%Y%m%d")+".csv"

DATA_DATE = date.today() + timedelta(days= DAY_BACK)
DATA_DATE_SQL = DATA_DATE.strftime("%d-%b-%Y")


FILE_PATH = "D:\ESS_DATA_EXPORT_LIVE\exportFiles\distributor_wallet_"+FILE_NAME
csv_file = open(r"D:\ESS_DATA_EXPORT_LIVE\exportFiles\distributor_wallet_"+FILE_NAME, "w")
ENCRYPT_FILE_NAME = "distributor_wallet_"+FILE_NAME+".pgp"
#FILE_DIS = "/home/oicagent/POS/Inbound/ESS_INT820/Source/distributor_wallet_"+FILE_NAME+".pgp"
FILE_DIS = "/POS/Inbound/ESSINT820/Source/distributor_wallet_"+FILE_NAME+".pgp"

FILE_DIS_LOCAL = "//Bldhkappdev03/ESS_DUMP/distributor_wallet_"+FILE_NAME



SQLSTRING = """SELECT distinct BATCH_AMOUNT,DEPOSIT_DATE,TRANSMISSION_AMOUNT,RECEIPT_METHOD,CUSTOMER_ACCOUNT_NUMBER,TRANSACTION_REFERENCE,APPLIED_AMOUNT
FROM
        (
            SELECT 
                    ac.REQUESTAMOUNT AS BATCH_AMOUNT
                    ,r.rfid,r.rfcode
                    , TO_CHAR (I.INVOICEDATE, 'YYMMDD') AS DEPOSIT_DATE
                    , ac.REQUESTAMOUNT  TRANSMISSION_AMOUNT
                    , AT.accounttypename AS RECEIPT_METHOD
                    , ac.accountcode AS CUSTOMER_ACCOUNT_NUMBER
                    , r.rfcode AS TRANSACTION_REFERENCE
                    --, r.rftotal AS APPLIED_AMOUNT
                    ,ac.REQUESTAMOUNT AS APPLIED_AMOUNT
            FROM  tblrfmain r
            inner join tblinvoice i on R.RFCODE = I.INVOICEREF
            inner join    tbl1rfmaintransactionacc ac  on r.rfid = ac.rfid       
            inner join tbl1distributoraccount da ON ac.accountcode = da.accountcode
            inner join tbl1accounttype at ON da.accounttypeid = AT.accounttypeid
            where 1=1
            and TRUNC(I.INVOICEDATE  ) =  to_date('"""+DATA_DATE_SQL+"""') 
           and ac.requestamount > 0 
            and r.recordstatus <> 'C'   
            and i.RECORDSTATUS <> 'C' 
            and at.accounttypeid in (2,4,7,10)             
           
        )"""



def main(FILE_NAME,FILE_PATH, csv_file, FILE_DIS,SQLSTRING):
    try:
        Config = Helper(0)
        ExcelRowNum = Config.GenerateExcel(SQLSTRING,FILE_NAME,FILE_PATH,csv_file)

        if ExcelRowNum < 0:
            errorMessage = "ESS Distributor wallet data Excel generates fail"
            i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'8801907634879', 1)
            print(errorMessage)

        else:
            isEncryp = Config.FileEncryptionWithKey(FILE_PATH, ENCRYPT_FILE_NAME)
            if isEncryp == 0:
                errorMessage = "ESS Distributor wallet data File encryption fail"
                i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'8801907634879', 1)
                print(errorMessage)
                
            else:
                print("File Encryption done")
                isTransfer = 1 #Config.TransferFile(FILE_PATH,FILE_DIS)
                if isTransfer > 0 :
                   errorMessage = "Distributor wallet data uploaded to ESS: "
                   i = Config.GenerateErrorLog(FILE_PATH, ExcelRowNum, FILE_DIS, errorMessage,'8801907634879', 0)
                   j = Config.Transfer_local_location(FILE_PATH, FILE_DIS_LOCAL, "distributor wallet");
                   print(errorMessage)
                
                else:
                    errorMessage = "Distributor wallet data not uploaded to ESS: "
                    ii = Config.GenerateErrorLog(FILE_PATH, ExcelRowNum, FILE_DIS, errorMessage,'8801907634879', 0)
                    print(errorMessage)
        return True

    except Exception as e:
        errorMessage = "Distributor wallet data got Exception Error, Python erro is: " + str(e)
        i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'8801907634879', 1)
        print(errorMessage)
        return False




result = main(FILE_NAME,FILE_PATH, csv_file, FILE_DIS,SQLSTRING )


if result == False:
    Config = Helper(0)
    errorMessage = "Distributor wallet data got Exception Error:"
    i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'8801907634879', 1)
    print(errorMessage)
