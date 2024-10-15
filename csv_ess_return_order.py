
import shutil
import os
from datetime import timedelta, date
from helper import Helper


DAY_BACK = -1

today_date = date.today() + timedelta(days=(DAY_BACK))  #date.today()  # dd/mm/YY
FILE_NAME = today_date.strftime("%Y%m%d")+".csv"

DATA_DATE = date.today() + timedelta(days= DAY_BACK)
DATA_DATE_SQL = DATA_DATE.strftime("%d-%b-%Y")


FILE_PATH = "D:\ESS_DATA_EXPORT_LIVE\exportFiles\wh_return_"+FILE_NAME
csv_file = open(r"D:\ESS_DATA_EXPORT_LIVE\exportFiles\wh_return_"+FILE_NAME, "w")
ENCRYPT_FILE_NAME = "wh_return_"+FILE_NAME+".pgp"
#FILE_DIS = "/home/oicagent/POS/Inbound/ESS_INT421C/Source/return_"+FILE_NAME+".pgp"
FILE_DIS = "/POS/Inbound/ESSINT421C/Source/return_"+FILE_NAME+".pgp"


SQLSTRING = """  select  distinct  
            rm.whreturncode AS return_code
        ,   to_char( rm.whreturndate ,'YYYY/MM/DD HH24:MM:SS') AS return_date
        ,   r.rfraisercode AS  distributor_code
        ,   rm.whreturnid AS return_id
        ,(select cc.CHILDID from tblwhreturnchild cc where cc.WHRETURNID=rm.WHRETURNID and cc.PRODUCTID=p.PRODUCTID and rownum<2) AS return_child_id
        ,   ROW_NUMBER() OVER (PARTITION BY rm.whreturnid order by 1 ) AS seq
        ,   p.ESSPRODUCTCODE AS product_code
        ,   vd.RETURNQTY return_qty
        ,   rm.returnreason
        ,   w.warehousecode AS warehousecode        
        ,   rf.rfcode AS rf_code        
        ,TO_CHAR(rf.rfdate, 'YYYY/MM/DD HH24:MM:SS') rf_date
        ,i.INVOICEID as ORIGINAL_SOURCE_TRANS_ID
        ,d.INVOICEDETAILID as ORIGINAL_SOURCE_TRANS_LINE_ID
        from tblreturnvalchallendetails vd
        JOIN tblproduct p     ON p.PRODUCTCODE = vd.PCODE
        join tblwhreturnmaster rm on vd.RETURNORDER=rm.WHRETURNCODE    
        JOIN tblrfmain rf ON rf.rfcode = vd.issuerfno
        JOIN tblrfraiser r ON r.rfraiserid = rf.RFRAISERID      
        join
        (   select I.INVOICEID,I.INVOICEREF  from tblinvoice i WHERE i.RECORDSTATUS   <> 'C'
            union
            select Ia.INVOICEID,Ia.INVOICEREF from tblinvoice_arc ia WHERE ia.RECORDSTATUS <> 'C'
        )I on I.INVOICEREF = rf.RFCODE                
        join
        (   select IND.INVOICEDETAILID, IND.INVOICEID,ind.PRODUCTID  from tblinvoicedetail IND
            union
            select INDA.INVOICEDETAILID, INDA.INVOICEID,inda.PRODUCTID from tblinvoicedetail_arc INDA
        )D on D.INVOICEID = I.INVOICEID and d.PRODUCTID=p.PRODUCTID
        JOIN tblwarehouse w    ON w.warehouseid = rm.warehousecenterid
        WHERE 1=1
        and TRUNC(whreturndate)  = to_date('"""+DATA_DATE_SQL+"""')        
        --rm.WHRETURNCODE in ('RT23DHK00845','RT23DHK00846','RT23DHK00847')
        order by rm.WHRETURNCODE, seq """



def main(FILE_NAME,FILE_PATH, csv_file, FILE_DIS,SQLSTRING):
    try:
        Config = Helper(0)
        ExcelRowNum = Config.GenerateExcel(SQLSTRING,FILE_NAME,FILE_PATH,csv_file)

        if ExcelRowNum < 0:
            errorMessage = "ESS Return order data Excel generates fail"
            i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
            print(errorMessage)

        elif ExcelRowNum == 0:
            errorMessage = "ESS Return order data Excel generates with 0 row"
            i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 0)
            print(errorMessage)
        
        else:
            isEncryp = Config.FileEncryptionWithKey(FILE_PATH, ENCRYPT_FILE_NAME)
            if isEncryp == 0:
                errorMessage = "ESS Return order data File encryption fail"
                i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
                print(errorMessage)
                
            else:
                print("File Encryption done")
                isTransfer = Config.TransferFile(FILE_PATH,FILE_DIS)
                if isTransfer > 0:
                   errorMessage = "Return order data uploaded to ESS"
                   i = Config.GenerateErrorLog(FILE_PATH, ExcelRowNum, FILE_DIS, errorMessage,'0', 0)
                   print(errorMessage)
                
                else:
                    errorMessage = "Return order data not uploaded to ESS"
                    ii = Config.GenerateErrorLog(FILE_PATH, ExcelRowNum, FILE_DIS, errorMessage,'0', 0)
                    print(errorMessage)
        return True

    except Exception as e:
        errorMessage = "Return order data got Exception Error, Python erro is: " + str(e)
        i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'8801907634879', 1)
        return False

print("Task Start")
result = main(FILE_NAME,FILE_PATH, csv_file, FILE_DIS,SQLSTRING )


if result == False:
    Config = Helper(0)
    errorMessage = "Return order data got Exception Error:"
    i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
    print(errorMessage)

