
import shutil
import os
from datetime import timedelta, date
from helper import Helper


DAY_BACK = -1

today_date = date.today() + timedelta(days=(DAY_BACK))  #date.today()  # dd/mm/YY
FILE_NAME = today_date.strftime("%Y%m%d")+".csv"

DATA_DATE = date.today() + timedelta(days= DAY_BACK)
DATA_DATE_SQL = DATA_DATE.strftime("%d-%b-%Y")


FILE_PATH = "D:\ESS_DATA_EXPORT_LIVE\exportFiles\supply_order_"+FILE_NAME
csv_file = open(r"D:\ESS_DATA_EXPORT_LIVE\exportFiles\supply_order_"+FILE_NAME, "w")
ENCRYPT_FILE_NAME = "supply_order_"+FILE_NAME+".pgp"
#FILE_DIS = "/home/oicagent/POS/Inbound/ESS_INT423/Transfer_Order/Source/supply_order_"+FILE_NAME+".pgp"
FILE_DIS = "/POS/Inbound/ESSINT423/Transfer_Order/Source/supply_order_"+FILE_NAME+".pgp"


SQLSTRING = """
SELECT source_header_id receiving_master_header_id, interface_batch_number,
       line_number, item_number, quantity,
       destination_organization_code destination,
       source_organization_code SOURCE,
       TO_CHAR (need_by_date, 'YYYY-MM-DD HH24:MM:SS') need_by_date
  FROM (SELECT trm.transferreceiveid AS source_header_id,
               trm.transferreceivecode AS interface_batch_number,
               tc.childid AS line_number, p.essproductcode AS item_number,
               tc.qty AS quantity,
               w1.warehousecode destination_organization_code,
               w.warehousecode source_organization_code,
               '' AS destination_subinventory_code,
               '' AS source_subinventory_code,
               trm.transferreceivedate need_by_date
          FROM (SELECT m.transfercode, m.fromwarehousecenterid, m.transferid,
                       towarehousecenterid
                  FROM tbltransfermaster m
                 WHERE 
                       (m.fromwarehousecenterid = 43
                        OR m.fromwarehouseorcenter = 'W'
                       )
                   AND (towarehouseorcenter = 'W' OR towarehousecenterid = 43
                       )) tm
               JOIN
               (SELECT childid, transferid, productid, qty
                  FROM tbltransferchild) tc ON tc.transferid = tm.transferid
               JOIN tblproduct p ON p.productid = tc.productid
               JOIN tblwarehouse w ON w.warehouseid = tm.fromwarehousecenterid
               JOIN tblwarehouse w1 ON w1.warehouseid = tm.towarehousecenterid
               JOIN tbltransferreceivemaster trm
               ON trm.transfercode = tm.transfercode
               where trunc(trm.TRANSFERRECEIVEDATE)=to_date('"""+DATA_DATE_SQL+"""') 
        UNION ALL
        SELECT trm.transferreceiveid AS source_header_id,
               trm.transferreceivecode AS interface_batch_number,
               tc.childid AS line_number, p.essproductcode AS item_number,
               tc.qty AS quantity,
               c1.centercode destination_organization_code,
               w.warehousecode source_organization_code,
               '' AS destination_subinventory_code,
               '' AS source_subinventory_code,
               trm.transferreceivedate need_by_date
          FROM (SELECT m.transfercode, m.transferid, m.fromwarehousecenterid,
                       m.towarehousecenterid
                  FROM tbltransfermaster m
                 WHERE m.fromwarehouseorcenter = 'W'
                   AND m.towarehouseorcenter = 'C') tm
               JOIN
               (SELECT childid, transferid, productid, qty
                  FROM tbltransferchild) tc ON tc.transferid = tm.transferid
               JOIN tblproduct p ON p.productid = tc.productid
               JOIN tblwarehouse w ON w.warehouseid = tm.fromwarehousecenterid
               JOIN tblcenter c1 ON c1.centerid = tm.towarehousecenterid
               JOIN tbltransferreceivemaster trm
               ON trm.transfercode = tm.transfercode
               where trunc(trm.TRANSFERRECEIVEDATE)=to_date('"""+DATA_DATE_SQL+"""') 
        UNION ALL
        SELECT trm.transferreceiveid AS source_header_id,
               trm.transferreceivecode AS interface_batch_number,
               tc.childid AS line_number, p.essproductcode AS item_number,
               tc.qty AS quantity,
               w1.warehousecode destination_organization_code,
               c.centercode source_organization_code,
               '' AS destination_subinventory_code,
               '' AS source_subinventory_code,
               trm.transferreceivedate need_by_date
          FROM (SELECT m.transferid, m.transfercode, m.fromwarehousecenterid,
                       m.towarehousecenterid
                  FROM tbltransfermaster m
                 WHERE  m.fromwarehouseorcenter = 'C'
                   AND m.towarehouseorcenter = 'W') tm
               JOIN
               (SELECT childid, transferid, productid, qty
                  FROM tbltransferchild) tc ON tc.transferid = tm.transferid
               JOIN tblproduct p ON p.productid = tc.productid
               JOIN tblcenter c ON c.centerid = tm.fromwarehousecenterid
               JOIN tblwarehouse w1 ON w1.warehouseid = tm.towarehousecenterid
               JOIN tbltransferreceivemaster trm
               ON trm.transfercode = tm.transfercode
               where trunc(trm.TRANSFERRECEIVEDATE)=to_date('"""+DATA_DATE_SQL+"""') 
               )"""







def main(FILE_NAME,FILE_PATH, csv_file, FILE_DIS,SQLSTRING):
    try:
        Config = Helper(0)
        ExcelRowNum = Config.GenerateExcel(SQLSTRING,FILE_NAME,FILE_PATH,csv_file)

        if ExcelRowNum < 0:
            errorMessage = "ESS Supply order data Excel generates fail"
            i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
            print(errorMessage)

        else:
            isEncryp = Config.FileEncryptionWithKey(FILE_PATH, ENCRYPT_FILE_NAME)
            if isEncryp == 0:
                errorMessage = "ESS Supply order data File encryption fail"
                i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
                print(errorMessage)
                
            else:
                print("File Encryption done")
                isTransfer = Config.TransferFile(FILE_PATH,FILE_DIS)
                if isTransfer > 0:
                   errorMessage = "Supply order data uploaded to ESS"
                   i = Config.GenerateErrorLog(FILE_PATH, ExcelRowNum, FILE_DIS, errorMessage,'0', 0)
                   print(errorMessage)
                
                else:
                    errorMessage = "Supply order data not uploaded to ESS"
                    ii = Config.GenerateErrorLog(FILE_PATH, ExcelRowNum, FILE_DIS, errorMessage,'0', 0)
                    print(errorMessage)
        return True

    except Exception as e:
        errorMessage = "Supply order data got Exception Error, Python erro is: " + str(e)
        i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'8801907634879', 1)
        return False


result = main(FILE_NAME,FILE_PATH, csv_file, FILE_DIS,SQLSTRING )


if result == False:
    Config = Helper(0)
    errorMessage = "Supply order data got Exception Error:"
    i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
    print(errorMessage)

