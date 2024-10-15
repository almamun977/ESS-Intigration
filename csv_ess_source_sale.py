import shutil
import os
from datetime import timedelta, date
from helper import Helper


DAY_BACK = -1

today_date = date.today() + timedelta(days=(DAY_BACK))  #date.today()  # dd/mm/YY
FILE_NAME = today_date.strftime("%Y%m%d")+".csv"

DATA_DATE = date.today() + timedelta(days= DAY_BACK)
DATA_DATE_SQL = DATA_DATE.strftime("%d-%b-%Y")


FILE_PATH = "D:\ESS_DATA_EXPORT_LIVE\exportFiles\source_sale_"+FILE_NAME
csv_file = open(r"D:\ESS_DATA_EXPORT_LIVE\exportFiles\source_sale_"+FILE_NAME, "w")
ENCRYPT_FILE_NAME = "source_sale_"+FILE_NAME+".pgp"
#FILE_DIS = "/home/oicagent/POS/Inbound/ESS_INT421A/Source/source_sale_"+FILE_NAME+".pgp"
FILE_DIS = "/POS/Inbound/ESSINT421A/Source/source_sale_"+FILE_NAME+".pgp"



SQLSTRING = """SELECT source_transaction_identifier, source_transaction_number,
       source_transaction_line_number, sequence_number,
       buying_party_identifier, buying_party_name, product_number,
       source_product_reference, transaction_on, subinventory_code,
       priced_quantity
  FROM (SELECT i.invoiceid source_transaction_identifier,
               i.invoiceref source_transaction_number,
               ID.invoicedetailid source_transaction_line_number,
               ROW_NUMBER () OVER (PARTITION BY i.invoiceid ORDER BY ID.invoicedetailid)
                                                              sequence_number,
               c.customercode buying_party_identifier,
               c.customername buying_party_name,
               p.essproductcode product_number,
               p.productcode source_product_reference,
               TO_CHAR (i.invoicedate,
                        'YYYY-MM-DD HH24:MM:SS') transaction_on,
               w.warehousecode subinventory_code, ID.qty priced_quantity
          FROM (SELECT invoiceid, invoiceref, invoicedate, customerid
                  FROM tblinvoice
                 WHERE recordstatus <> 'C'
                                           AND TRUNC(invoicedate) between '01-Mar-2023' and '01-Mar-2024' --= to_date('"""+DATA_DATE_SQL+"""') 
               ) i
               JOIN
               (SELECT invoicedetailid, invoiceid, productid, qty
                  FROM tblinvoicedetail) ID ON ID.invoiceid = i.invoiceid
               JOIN tblcustomer c ON c.customerid = i.customerid
               JOIN tblproduct p ON p.productid = ID.productid
               JOIN
                (SELECT rfid, rfcode, warehouseid, RFRAISERID, RFSTATUS
                  FROM tblrfmain ) rfm ON rfm.rfcode = i.invoiceref
               JOIN tblwarehouse w ON w.warehouseid = rfm.warehouseid
               JOIN tblrfraiser rr on rfm.RFRAISERID=rr.RFRAISERID
               where rr.RFRAISERCODE not in  (select dai.CODE from TBLDISTRIBUTORALTERINTERNAL dai where dai.ISACTIVE='Y')                     
               )"""



def main(FILE_NAME,FILE_PATH, csv_file, FILE_DIS,SQLSTRING):
    try:
        Config = Helper(0)
        ExcelRowNum = Config.GenerateExcel(SQLSTRING,FILE_NAME,FILE_PATH,csv_file)

        if ExcelRowNum < 0:
            errorMessage = "ESS Sales order data Excel generates fail"
            i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
            print(errorMessage)

        else:
            isEncryp = Config.FileEncryptionWithKey(FILE_PATH, ENCRYPT_FILE_NAME)
            if isEncryp == 0:
                errorMessage = "ESS Sales order data File encryption fail"
                i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
                print(errorMessage)
                
            else:
                print("File Encryption done")
                isTransfer = 1 #Config.TransferFile(FILE_PATH,FILE_DIS)
                if isTransfer > 0:
                   errorMessage = "Sales order data uploaded to ESS"
                   i = Config.GenerateErrorLog(FILE_PATH, ExcelRowNum, FILE_DIS, errorMessage,'0', 0)
                   print(errorMessage)
                
                else:
                    errorMessage = "Sales order data not uploaded to ESS"
                    ii = Config.GenerateErrorLog(FILE_PATH, ExcelRowNum, FILE_DIS, errorMessage,'0', 0)
                    print(errorMessage)
        return True

    except Exception as e:
        errorMessage = "Sales order data got Exception Error, Python erro is: " + str(e)
        i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'8801907634879', 1)
        return False




result = main(FILE_NAME,FILE_PATH, csv_file, FILE_DIS,SQLSTRING )


if result == False:
    Config = Helper(0)
    errorMessage = "Sales order data got Exception Error:"
    i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
    print(errorMessage)

