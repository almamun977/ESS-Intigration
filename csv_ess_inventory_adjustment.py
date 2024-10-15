import shutil
import os
from datetime import timedelta, date
from helper import Helper

DAY_BACK = -1

today_date = date.today() + timedelta(days=(DAY_BACK))  #date.today()  # dd/mm/YY
FILE_NAME = today_date.strftime("%Y%m%d")+".csv"

DATA_DATE = date.today() + timedelta(days= DAY_BACK)
DATA_DATE_SQL = DATA_DATE.strftime("%d-%b-%Y")


FILE_PATH = "D:\ESS_DATA_EXPORT_LIVE\exportFiles\inventory_adjustment_"+FILE_NAME
csv_file = open(r"D:\ESS_DATA_EXPORT_LIVE\exportFiles\inventory_adjustment_"+FILE_NAME, "w")
ENCRYPT_FILE_NAME = "inventory_adjustment_"+FILE_NAME+".pgp"
#FILE_DIS = "/home/oicagent/POS/Inbound/ESS_INT410B/inventory_adjustment_"+FILE_NAME+".pgp"
FILE_DIS = "/POS/Inbound/ESSINT410B/Source/inventory_adjustment_"+FILE_NAME+".pgp"



SQLSTRING = """SELECT  ORGANIZATION_NAME,ITEM_NUMBER,TRANSACTION_QUANTITY,TRANSACTION_DATE,TRANSACTION_TYPE_NAME,TRANSACTION_REFERENCE
FROM
        (
            SELECT    ORGANIZATION_NAME, ITEM_NUMBER, TRANSACTION_QUANTITY, to_char( TRANSACTION_DATE ,'YYYY-MM-DD HH24:MM:SS')  TRANSACTION_DATE, TRANSACTION_TYPE_NAME, TRANSACTION_REFERENCE
            FROM 
                (
                    SELECT     w.warehousecode AS ORGANIZATION_NAME, P.ESSPRODUCTCODE AS ITEM_NUMBER
                            , pc.qty AS TRANSACTION_QUANTITY, pm.whproductiondate AS TRANSACTION_DATE
                            , 'CONV' as TRANSACTION_TYPE_NAME, pm.whproductioncode AS TRANSACTION_REFERENCE
                    FROM     (
                                SELECT    whproductionid , whproductioncode, whproductiondate, warehouseid,TOPRODUCTID
                                FROM     tblwhproductionmaster WHERE     TRUNC (whproductiondate)= to_date('"""+DATA_DATE_SQL+"""') 
                            ) pm
                    JOIN( SELECT whproductionid, productid, qty FROM     tblwhproductionchild ) pc ON pm.whproductionid = pc.whproductionid
                    JOIN     tblwarehouse w ON pm.warehouseid = w.warehouseid
                    --JOIN     tblproduct p ON p.productid = pm.TOPRODUCTID                    
                    JOIN tblproduct p ON p.productid = pc.productid
                    UNION ALL                    
                    SELECT     w.warehousecode AS ORGANIZATION_NAME, p.ESSPRODUCTCODE AS ITEM_NUMBER, pc.qty AS TRANSACTION_QUANTITY
                            , pm.whproductiondate AS TRANSACTION_DATE, 'PRO' as TRANSACTION_TYPE_NAME
                            , pm.whproductioncode AS TRANSACTION_REFERENCE
                    FROM (
                                SELECT  whproductionid, whproductioncode, whproductiondate, warehouseid,TOPRODUCTID
                                FROM     tblwhproductionmaster WHERE     TRUNC (whproductiondate)= to_date('"""+DATA_DATE_SQL+"""') 
                         ) pm
                    JOIN (SELECT whproductionid , productid , qty FROM tblwhproductionchild ) pc ON pm.whproductionid = pc.whproductionid
                    JOIN    tblwarehouse w ON pm.warehouseid = w.warehouseid
                    JOIN    tblproduct p ON p.productid = pm.TOPRODUCTID                    
                    --JOIN tblproduct p ON p.productid = pc.productid
                    UNION ALL                    
                    SELECT  cen.centercode AS ORGANIZATION_NAME, p.ESSPRODUCTCODE AS ITEM_NUMBER, c.qty AS TRANSACTION_QUANTITY, m.writeoffdate AS TRANSACTION_DATE
                        ,'Writeoff' AS TRANSACTION_TYPE_NAME , m.writeoffcode AS TRANSACTION_REFERENCE
                    FROM (SELECT writeoffid, writeoffdate, writeoffcode  FROM tblwriteoffmaster WHERE  TRUNC (writeoffdate)= to_date('"""+DATA_DATE_SQL+"""') 
                    ) m
                    JOIN (SELECT writeoffid, productid , qty , warehousecenterid  FROM     tblwriteoffchild   ) c ON m.writeoffid = c.writeoffid
                    JOIN  tblcenter cen ON cen.centerid = c.warehousecenterid
                    JOIN  tblproduct p ON c.productid = p.productid   
                    --JOIN test_tblproduct_ess p ON p.productid = c.productid
                )
            ORDER BY  TRANSACTION_REFERENCE
        )"""




def main(FILE_NAME,FILE_PATH, csv_file, FILE_DIS,SQLSTRING):
    try:
        Config = Helper(0)
        ExcelRowNum = Config.GenerateExcel(SQLSTRING,FILE_NAME,FILE_PATH,csv_file)

        if ExcelRowNum < 0:
            errorMessage = "ESS Inventory Adjustment data Excel generates fail"
            i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
            print(errorMessage)

        else:
            isEncryp = Config.FileEncryptionWithKey(FILE_PATH, ENCRYPT_FILE_NAME)
            if isEncryp == 0:
                errorMessage = "ESS Inventory Adjustment data File encryption fail"
                i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
                print(errorMessage)
                
            else:
                print("File Encryption done")
                isTransfer = Config.TransferFile(FILE_PATH,FILE_DIS)
                if isTransfer > 0 :
                   errorMessage = "Inventory Adjustment data uploaded to ESS"
                   i = Config.GenerateErrorLog(FILE_PATH, ExcelRowNum, FILE_DIS, errorMessage,'0', 0)
                   print(errorMessage)
                
                else:
                    errorMessage = "Inventory Adjustment not data uploaded to ESS"
                    ii = Config.GenerateErrorLog(FILE_PATH, ExcelRowNum, FILE_DIS, errorMessage,'0', 0)
                    print(errorMessage)
        return True

    except Exception as e:
        errorMessage = "Inventory Adjustment data got Exception Error, Python erro is: " + str(e)
        i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'8801907634879', 1)
        return False



result = main(FILE_NAME,FILE_PATH, csv_file, FILE_DIS,SQLSTRING )


if result == False:
    Config = Helper(0)
    errorMessage = "Inventory Adjustment data got Exception Error:"
    i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
    print(errorMessage)
