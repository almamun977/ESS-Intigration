
import shutil
import os
from datetime import timedelta, date
from helper import Helper


DAY_BACK = -1

today_date = date.today() + timedelta(days=(DAY_BACK))  #date.today()  # dd/mm/YY
FILE_NAME = today_date.strftime("%Y%m%d")+".csv"

DATA_DATE = date.today() + timedelta(days= DAY_BACK)
DATA_DATE_SQL = DATA_DATE.strftime("%d-%b-%Y")


FILE_PATH = "D:\ESS_DATA_EXPORT_LIVE\exportFiles\POS_GL_INTEGRATION_"+FILE_NAME
csv_file = open(r"D:\ESS_DATA_EXPORT_LIVE\exportFiles\POS_GL_INTEGRATION_"+FILE_NAME, "w")
ENCRYPT_FILE_NAME = "source_sale_"+FILE_NAME+".pgp"
#FILE_DIS = "/home/oicagent/POS/Inbound/ESS_INT421A/Source/source_sale_"+FILE_NAME+".pgp"
#FILE_DIS = "/home/users/OIC_TEST_USR/POS/Inbound/ESS_INT823/Source/POS_GL_INTEGRATION_"+FILE_NAME+".pgp"
FILE_DIS = "/POS/Inbound/ESSINT823/Source/POS_GL_INTEGRATION_"+FILE_NAME+".pgp"


SQLSTRING = """select d.DISTRIBUTORCODE,d.DISTRIBUTORNAME,c.remarks as description,
                case when t.ACCOUNTTYPEID=2  then round((c.amount/0.9),2) else round(c.AMOUNT,2) end total_commision,
                g.COMMISSION_MONTH as commision_month,g.COMMISSION_CATEGORY commision_category,g.COSTGL as cost_gl,g.ACCRUEDLIABILITIESGL as Accrued_Liabilities_GL,
                g.POSLIABILITIESGL as POS_Liabilities_GL,g.AITGL as AIT_GL,g.COSTCENTER Cost_center, TO_CHAR(a.TRANSACTIONDATE, 'DD-MM-YYYY') as Effective_Date,t.ACCOUNTTYPENAME
                from (
                    select p.PAYABLERECEIVEABLEID,
                    p.REMARKS,p.AMOUNT,DISTRIBUTORID from TBL1PAYABLERECEIVEABLEdetails p
                ) c
                join tbldistributor d on d.DISTRIBUTORID =c.DISTRIBUTORID
                join TBL1PAYABLERECEIVEABLE a on a.PAYABLERECEIVEABLEID=c.PAYABLERECEIVEABLEID
                join TBL1PAYABLERECEIVEABLE_INPUTGL g on a.TRANSACTIONREFNO=g.TRANSACTIONREFNO
                join TBL1ACCOUNTTYPE t on t.ACCOUNTTYPEID=a.ACCOUNTTYPEID
                where a.RECORDSTATUS='A' and a.TRANSACTIONDATE = to_date('"""+DATA_DATE_SQL+"""') """



def main(FILE_NAME,FILE_PATH, csv_file, FILE_DIS,SQLSTRING):
    try:
        Config = Helper(0)
        ExcelRowNum = Config.GenerateExcel(SQLSTRING,FILE_NAME,FILE_PATH,csv_file)

        if ExcelRowNum < 0:
            errorMessage = "ESS POS GL integration data Excel generates fail"
            i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
            print(errorMessage)

        else:
            isEncryp = Config.FileEncryptionWithKey(FILE_PATH, ENCRYPT_FILE_NAME)
            if isEncryp == 0:
                errorMessage = "ESS POS GL integration data File encryption fail"
                i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
                print(errorMessage)
                
            else:
                print("File Encryption done")
                isTransfer = Config.TransferFile(FILE_PATH,FILE_DIS,1)
                if isTransfer > 0:
                   errorMessage = "POS GL integration data uploaded to ESS"
                   i = Config.GenerateErrorLog(FILE_PATH, ExcelRowNum, FILE_DIS, errorMessage,'0', 0)
                   print(errorMessage)
                
                else:
                    errorMessage = "POS GL integration data not uploaded to ESS"
                    ii = Config.GenerateErrorLog(FILE_PATH, ExcelRowNum, FILE_DIS, errorMessage,'0', 0)
                    print(errorMessage)
        return True

    except Exception as e:
        errorMessage = "POS GL integration data got Exception Error, Python erro is: " + str(e)
        i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'8801907634879', 1)
        return False




result = main(FILE_NAME,FILE_PATH, csv_file, FILE_DIS,SQLSTRING )


if result == False:
    Config = Helper(0)
    errorMessage = "POS GL integration data got Exception Error:"
    i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
    print(errorMessage)

