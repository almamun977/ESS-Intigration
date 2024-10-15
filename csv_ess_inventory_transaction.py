import shutil
import os
from datetime import timedelta, date
from helper import Helper

DAY_BACK = -1

today_date = date.today() + timedelta(days=(DAY_BACK))  #date.today()  # dd/mm/YY
FILE_NAME = today_date.strftime("%Y%m%d")+".csv"

DATA_DATE = date.today() + timedelta(days= DAY_BACK)
DATA_DATE_SQL = DATA_DATE.strftime("%d-%b-%Y")


FILE_PATH = "D:\ESS_DATA_EXPORT_LIVE\exportFiles\inventory_transaction_"+FILE_NAME
csv_file = open(r"D:\ESS_DATA_EXPORT_LIVE\exportFiles\inventory_transaction_"+FILE_NAME, "w")
ENCRYPT_FILE_NAME = "inventory_transaction_"+FILE_NAME+".pgp"
#FILE_DIS = "/home/oicagent/POS/Inbound/ESS_INT423/Sub_Inv_Order/Source/inventory_transaction_"+FILE_NAME+".pgp"
FILE_DIS = "/POS/Inbound/ESSINT423/Sub_Inv_Order/Source/inventory_transaction_"+FILE_NAME+".pgp"


SQLSTRING = """SELECT   ORGANIZATION_NAME,TRANSACTION_REFERENCE,SOURCE_HEADER_ID,SOURCE_LINE_ID,SUBINVENTORY_CODE,TRANSFER_SUBINVENTORY,ITEM_NUMBER,TRANSACTION_QUANTITY,TRANSACTION_DATE, TRANSACTION_TYPE_NAME as TRANSACTION_TYPE

FROM    (
            SELECT  'BL Central Warehouse' AS ORGANIZATION_NAME
                    , 'BL Regional Transfer' TRANSACTION_TYPE_NAME
                    --, tm.transfercode AS TRANSACTION_REFERENCE
                    ,tm.TRANSFERRECEIVECODE AS TRANSACTION_REFERENCE
                    --, tm.transferid AS SOURCE_HEADER_ID
                    ,tm.TRANSFERRECEIVEID AS SOURCE_HEADER_ID
                    , tc.childid AS SOURCE_LINE_ID
                    , TO_CHAR(tm.transferdate,'YYYY-MM-DD HH24:MM:SS') AS TRANSACTION_DATE
                    , w.warehousecode AS SUBINVENTORY_CODE
                    , w1.warehousecode AS TRANSFER_SUBINVENTORY
                    , p.ESSPRODUCTCODE AS ITEM_NUMBER
                    , tc.qty AS TRANSACTION_QUANTITY
            FROM     (
                       SELECT  transferid
                               --, transfercode
                               ,rm.TRANSFERRECEIVEID
                               ,rm.TRANSFERRECEIVECODE
                               , m.transferdate
                               , m.fromwarehousecenterid
                               , m.towarehousecenterid
                       FROM    tbltransfermaster m,tbltransferreceivemaster rm
                       WHERE   m.TRANSFERCODE=rm.TRANSFERCODE and m.fromwarehouseorcenter = 'W'
                       AND     m.towarehouseorcenter = 'W'
                       AND     m.fromwarehousecenterid <> 43
                       AND     m.towarehousecenterid <> 43
                       AND     TRUNC(TRANSFERDATE) = to_date('"""+DATA_DATE_SQL+"""') 
                    ) tm
            JOIN     (  
                       SELECT  childid
                               , transferid
                               , productid
                               , qty 
                       FROM tbltransferchild
                    ) tc
            ON tc.transferid = tm.transferid
            --JOIN test_tblproduct_ess p --tblproduct p
            JOIN tblproduct p --tblproduct p
            ON p.productid = tc.productid
            JOIN tblwarehouse w
            ON w.warehouseid = tm.fromwarehousecenterid
            JOIN tblwarehouse w1
            ON w1.warehouseid = tm.towarehousecenterid
            
            UNION ALL
            
            SELECT  'BL Central Warehouse' AS ORGANIZATION_NAME
                    , 'BL Shop Transfer' TRANSACTION_TYPE_NAME
                    --, tm.transfercode AS TRANSACTION_REFERENCE
                    ,tm.TRANSFERRECEIVECODE AS TRANSACTION_REFERENCE
                    --, tm.transferid AS SOURCE_HEADER_ID
                    ,tm.TRANSFERRECEIVEID AS SOURCE_HEADER_ID
                    , tc.childid AS SOURCE_LINE_ID
                    , TO_CHAR(tm.transferdate,'YYYY-MM-DD HH24:MM:SS') AS TRANSACTION_DATE
                    , c.centercode AS SUBINVENTORY_CODE
                    , c1.centercode AS TRANSFER_SUBINVENTORY
                    , p.ESSPRODUCTCODE AS ITEM_NUMBER
                    , tc.qty AS TRANSACTION_QUANTITY
            FROM     (
                       SELECT  transferid
                               --, transfercode
                               ,rm.TRANSFERRECEIVEID
                               ,rm.TRANSFERRECEIVECODE
                               , transferdate
                               , m.fromwarehousecenterid
                               , m.towarehousecenterid
                       FROM    tbltransfermaster m,tbltransferreceivemaster rm
                       WHERE   m.TRANSFERCODE=rm.TRANSFERCODE and  m.fromwarehouseorcenter = 'C'
                       AND     m.towarehouseorcenter = 'C'
                       AND     TRUNC(TRANSFERDATE) = to_date('"""+DATA_DATE_SQL+"""') 
                    ) tm
            JOIN     (  
                       SELECT  childid
                               , transferid
                               , productid
                               , qty 
                       FROM tbltransferchild
                    ) tc
            ON tc.transferid = tm.transferid
           -- JOIN test_tblproduct_ess p --tblproduct p
             JOIN tblproduct p --tblproduct p
            ON p.productid = tc.productid
            JOIN tblcenter c
            ON c.centerid = tm.fromwarehousecenterid
            JOIN tblcenter c1
            ON c1.centerid = tm.towarehousecenterid
        )"""





def main(FILE_NAME,FILE_PATH, csv_file, FILE_DIS,SQLSTRING):
    try:
        Config = Helper(0)
        ExcelRowNum = Config.GenerateExcel(SQLSTRING,FILE_NAME,FILE_PATH,csv_file)

        if ExcelRowNum < 0:
            errorMessage = "ESS Inventory transaction data Excel generates fail"
            i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
            print(errorMessage)

        else:
            isEncryp = Config.FileEncryptionWithKey(FILE_PATH, ENCRYPT_FILE_NAME)
            if isEncryp == 0:
                errorMessage = "ESS Inventory transaction data File encryption fail"
                i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
                print(errorMessage)
                
            else:
                print("File Encryption done")
                isTransfer = Config.TransferFile(FILE_PATH,FILE_DIS)
                if isTransfer > 0:
                   errorMessage = "Inventory transaction data uploaded to ESS"
                   i = Config.GenerateErrorLog(FILE_PATH, ExcelRowNum, FILE_DIS, errorMessage,'0', 0)
                   print(errorMessage)
                
                else:
                    errorMessage = "Inventory transaction data not uploaded to ESS"
                    ii = Config.GenerateErrorLog(FILE_PATH, ExcelRowNum, FILE_DIS, errorMessage,'0', 0)
                    print(errorMessage)
        return True

    except Exception as e:
        errorMessage = "Inventory transaction data got Exception Error, Python erro is: " + str(e)
        i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'8801907634879', 1)
        return False


result = main(FILE_NAME,FILE_PATH, csv_file, FILE_DIS,SQLSTRING )


if result == False:
    Config = Helper(0)
    errorMessage = "Inventory transaction data got Exception Error:"
    i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
    print(errorMessage)
