import shutil
import os
from datetime import date
from system_monitoring_helper import Helper



def delete_old_files():
     Config = Helper(0)

     #\\Bldhkappdev03\Sales_System_Daily_Perfomance_Dump\POS_DMS_RSOAPP

def get_pos_voms_monitoring_data() :
    
    try:
        Config = Helper(0)
        today = date.today()  # dd/mm/YY
        FILE_NAME = "POS_VOMS_ACTIVATION.xlsx"
        FILE_PATH = "E:\SYS_MONITORING_DUMP\exportFiles\SYS_MON_"+FILE_NAME
        FILE_DIS = "//Bldhkappdev03/Sales_System_Daily_Perfomance_Dump/POS_DMS_RSOAPP/SYS_MON_"+FILE_NAME

        SQLSTRING = """  SELECT ACTIVATION_DATE, NVL(SUCCESS_ACTIVATION, 0) SUCCESS_ACTIVATION, NVL(FAIL_ACTIVATION,0) FAIL_ACTIVATION
                    FROM (
                            SELECT TO_CHAR(sysdate-1) ACTIVATION_DATE,
                                (select  count(l.SERIALNO) 
                                    from TBLWHISSUETHREADLOG yy,TBLSCSTATUSLOG l
                                    where yy.LOGID=l.LOGID and yy.WHISSUEDATE = trunc(sysdate-1)
                                ) SUCCESS_ACTIVATION,
                                (select count(1) from tblscstatuslog_e l 
                                    where trunc(l.LOGDATETIME) = trunc(sysdate-1)
                                )FAIL_ACTIVATION
                            FROM DUAL
                    )"""
        ExcelRowNum = Config.GenerateXLSX(SQLSTRING,FILE_NAME,FILE_PATH,FILE_DIS,1)

        if ExcelRowNum < 1:
            errorMessage = "System monitoring POS VOMS ACTIVATION excel generate fail"
            i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
            print(errorMessage)
        else :
            Config.TransferFile(FILE_PATH,FILE_DIS,ExcelRowNum )

    except Exception as e:
        errorMessage = "System monitoring Error get_pos_voms_monitoring_data: "+ str(e)
        print(errorMessage)

def get_pos_DBSSAPI_monitoring_data() :
    
    try:
        Config = Helper(0)
        today = date.today()  # dd/mm/YY
        FILE_NAME = "POS_DBSSAPI.xlsx"
        FILE_PATH = "E:\SYS_MONITORING_DUMP\exportFiles\SYS_MON_"+FILE_NAME
        FILE_DIS = "//Bldhkappdev03/Sales_System_Daily_Perfomance_Dump/POS_DMS_RSOAPP/SYS_MON_"+FILE_NAME

        SQLSTRING = """  SELECT REQUEST_DATE, (TOTAL_COUNT - FAILE_COUNT) SUCESS_COUNT, FAILE_COUNT, TOTAL_COUNT 
                        FROM(
                        SELECT TO_CHAR(SYSDATE-1) REQUEST_DATE,
                            (select count(1) DBSSAPI_FAIL_COUNT
                                from dbssapi_responselog l 
                                where  TRUNC(l.CREATEDDATE) = TRUNC(SYSDATE -1) AND l.RESPONSE_TEXT like '%STATUS_CODE: 1011%'
                            )FAILE_COUNT,
                            ( select count(1) Tot_DBSSAPI_Activation
                                from tbldbssapi_log l 
                                where trunc(l.REQUEST_TIME) = TRUNC(SYSDATE -1)
                            )TOTAL_COUNT
                        FROM DUAL
                        )"""
        ExcelRowNum = Config.GenerateXLSX(SQLSTRING,FILE_NAME,FILE_PATH,FILE_DIS,1)

        if ExcelRowNum < 1:
            errorMessage = "System monitoring POS DBSSAPI excel generate fail"
            i = Config.GenerateErrorLog(FILE_PATH, 0, FILE_DIS, errorMessage,'0', 1)
            print(errorMessage)
        else :
            Config.TransferFile(FILE_PATH,FILE_DIS,ExcelRowNum )

    except Exception as e:
        errorMessage = "System monitoring Error get_pos_DBSSAPI_monitoring_data: "+ str(e)
        print(errorMessage)

def get_dms_SIM_SC_issue_data() :
    
    try:
        Config = Helper(0)
        today = date.today()  # dd/mm/YY
        FILE_NAME = "DMS_SIM_SC_ISSUE.xlsx"
        FILE_PATH = "E:\SYS_MONITORING_DUMP\exportFiles\SYS_MON_"+FILE_NAME
        FILE_DIS = "//Bldhkappdev03/Sales_System_Daily_Perfomance_Dump/POS_DMS_RSOAPP/SYS_MON_"+FILE_NAME

        SQLSTRING = """ SELECT ISSUE_DATE, NVL(SC_COUNT,0) SC_COUNT, NVL(SIM_COUNT,0) SIM_COUNT
                    FROM (
                    SELECT TO_CHAR(SYSDATE-1) ISSUE_DATE,(
                        select count(1)as SCCOUNT from scstatus 
                        where issuedate >= TO_DATE(TO_DATE(SYSDATE-1,'DD-MM-YY') || ' 00:00:00','DD-MM-YY HH24:MI:SS')
                        AND issuedate <= TO_DATE(TO_DATE(SYSDATE-1,'DD-MM-YY') || ' 23:59:59','DD-MM-YY HH24:MI:SS') 
                      )SC_COUNT,  
                      (
                        select count(1)as SCCOUNT from SIMSTATUS 
                            where issuedate >= TO_DATE(TO_DATE(SYSDATE-1,'DD-MM-YY') || ' 00:00:00','DD-MM-YY HH24:MI:SS')
                        AND issuedate <= TO_DATE(TO_DATE(SYSDATE-1,'DD-MM-YY') || ' 23:59:59','DD-MM-YY HH24:MI:SS') 
                      )SIM_COUNT
                     FROM DUAL
                    )"""
        ExcelRowNum = Config.GenerateXLSX(SQLSTRING,FILE_NAME,FILE_PATH,FILE_DIS,2)

        if ExcelRowNum < 1:
            errorMessage = "System monitoring DMS SIM SC issue count excel generate fail"
            i = Config.GenerateErrorLog(FILE_PATH, -1, FILE_DIS, errorMessage,'0', 2)
            print(errorMessage)
        else :
            Config.TransferFile(FILE_PATH,FILE_DIS,ExcelRowNum )

    except Exception as e:
        errorMessage = "System monitoring Error get_dms_SIM_SC_issue_data: "+ str(e)
        print(errorMessage)

def get_RSO_APP_itop_up_ISSUE_data() :
    
    try:
        Config = Helper(0)
        today = date.today()  # dd/mm/YY
        FILE_NAME = "RSO_APP_ITOP_UP_ISSUE.xlsx"
        FILE_PATH = "E:\SYS_MONITORING_DUMP\exportFiles\SYS_MON_"+FILE_NAME
        FILE_DIS = "//Bldhkappdev03/Sales_System_Daily_Perfomance_Dump/POS_DMS_RSOAPP/SYS_MON_"+FILE_NAME

        SQLSTRING = """ SELECT ISSUE_DATE, SUCCESS, FAIL ,(SUCCESS + FAIL) TOTAL_HIT, (ROUND((SUCCESS * 100)/(SUCCESS + FAIL),2)) SUCCESS_P
                    , (ROUND((FAIL * 100)/(SUCCESS + FAIL),2)) FAIL_P
                    FROM (
                        SELECT ISSUE_DATE, nvl(SUCCESS,0) SUCCESS,nvl(FAIL,0) FAIL
                        FROM (
                            SELECT  TO_CHAR(SYSDATE-1) ISSUE_DATE,  (
                                select  count(1) total
                                from top_up_issue i
                                where trunc(i.ISSUE_DATE) = trunc(sysdate-1) and i.ISSUE_STATUS in (1,2)
                                group by trunc(i.ISSUE_DATE)
                            ) SUCCESS,
                            (
                                select  count(1) total
                                from top_up_issue i
                                where trunc(i.ISSUE_DATE) = trunc(sysdate-1) and i.ISSUE_STATUS NOT in (1,2)
                                group by trunc(i.ISSUE_DATE)
                             )FAIL
                        FROM DUAL
                        )
                    )"""
        ExcelRowNum = Config.GenerateXLSX(SQLSTRING,FILE_NAME,FILE_PATH,FILE_DIS,2)
        #print("GenerateXLSX done: "+str(ExcelRowNum))
        if ExcelRowNum < 1:
            errorMessage = "System monitoring RSO APP itop-up excel generate fail "+ str(ExcelRowNum)
            i = Config.GenerateErrorLog(FILE_PATH, -1, FILE_DIS, errorMessage,'0', 1)
            print(errorMessage)
        else :
            #print("Ready for transfer: "+str(ExcelRowNum))
            Config.TransferFile(FILE_PATH,FILE_DIS,ExcelRowNum )

    except Exception as e:
        errorMessage = "System monitoring Error get_RSO_APP_itop_up_ISSUE_data: "+ str(e)
        print(errorMessage)


try:
    Config = Helper(0)
    sms = Config.delete_old_files()
    get_pos_voms_monitoring_data()
    get_dms_SIM_SC_issue_data()
    get_RSO_APP_itop_up_ISSUE_data()
    get_pos_DBSSAPI_monitoring_data()
    
    today = date.today()
    errorMessage = "System Monitoring data uploaded done for "+  today.strftime("%Y-%m-%d")
    ii = Config.GenerateErrorLog('', 0, 0, errorMessage,'', 1)
    print(errorMessage)

except Exception as e:
    errorMessage = "System Monitoring data got Exception Error, Python erro is: " + str(e)
    ii = Config.GenerateErrorLog('', 0, -1, errorMessage,'', 2)
