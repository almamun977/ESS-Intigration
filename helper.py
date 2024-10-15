import csv
import cx_Oracle
import shutil
import os
import gnupg
import pysftp 
import pgpy
from datetime import date
import paramiko
import time
import requests
 
class Helper:
   def __init__(self,val):
       self.val=val
       print("wllcome to Python ", self.val)
   
   def DBconfig(self):
       print("OralceDB Connection")
       con = cx_Oracle.connect('CFDB/test123@gzplorac-scan.banglalink.net:1580/POSDMSDB')
       return con
    
   def ExecuteSQL(SQLSTRING):
        con = DBconfig()
        cursor = con.cursor()
        r = cursor.execute(SQLSTRING)
        return cursor

   def GenerateErrorMessage(self, vMSISDN, vMSG):
            con = self.DBconfig()
            cursor = con.cursor()
            #dt_string = date.strftime("%d/%m/%Y %H:%M:%S")
            insrt_stmt = """insert into SMSGATEWAY.tblsend(APPLICATION, MSISDN, MESSAGE, CREATED, STATUS, DELIVERY_FLAG, UPDATE_TIME, DELIVERY_TIME, REPLY_ADDR, ERRORMSG) values(%S, %S,%S, :now, %S,%S,%S,%S,%S,%S)"""
            value = ('DMS', vMSISDN, vMSG, date.datetime.now(), 'N','','','','ERR_RT_SCH','')
            cursor.execute(insrt_stmt, value)
            conn.commit()

   def GenerateErrorLog(self, vFILENAME, vROWNUMBER, vDIS_LOCATION, vERROR_MESSAGE, vMSISDN, vISERROR):
            con = self.DBconfig()
            cursor = con.cursor()
            #dt_string = date.strftime("%d/%m/%Y %H:%M:%S")
            #insrt_stmt = """insert into ESS_FILE_TRANSFER_LOG(EXECUTE_AT, FILENAME, ROWNUMBER, DIS_LOCATION, ERROR_MESSAGE) values(%S, %S,%S, %S, %S)"""
            #value = ( vFILENAME, vROWNUMBER, vDIS_LOCATION,vERROR_MESSAGE)
            #cursor.execute(insrt_stmt, value)
            
            order_count = cursor.var(int)
            cursor.callproc('ESS_SAVE_FILE_LOG', [vFILENAME, vROWNUMBER, vDIS_LOCATION, vERROR_MESSAGE, vMSISDN, vISERROR, order_count])
            con.commit()
            return 0

   def GenerateExcel(self,SQLSTRING,FILE_NAME,FILE_PATH,csv_file):
       con = self.DBconfig()
       cursor = con.cursor()
       print("Task Start Main GenerateExcel")
       
       try:            
            writer = csv.writer(csv_file, delimiter=',', lineterminator="\n", quoting=csv.QUOTE_NONNUMERIC)
            #cursors = ExecuteSQL(SQLSTRING)
            r = cursor.execute(SQLSTRING)
            writer.writerow(i[0] for i in cursor.description)
            rownum = 0
            #print("Hellow world")
            #result = cursor.fetchone()
            #rownum = result[0]
            for row in cursor:
                writer.writerow(row)
                rownum = rownum+1
            return rownum
        
       except Exception as e:
           errorMessage = "File Excel generate Exception Error GenerateExcel: " + str(e)
           print(errorMessage)
           #ii = self.GenerateErrorLog("", 0, "", errorMessage,'8801907634879', 1)
           return 0

       finally:
            cursor.close()
            con.close()
            csv_file.close()

   def TransferFile(self,source, destination, destinationSFT=1):
       
        #import pysftp as sftp
        from paramiko import SSHClient
        result = 0

        if(destinationSFT == 1) :    # Test
            host='129.148.177.186'
            myuser='OIC_PROD_POS'
            password='BL#idcs#PRD#2022'
            PORT_NUM = 5019
        else :                      # Live
            host='129.148.176.45'
            myuser='OIC_UAT_POS'
            PORT_NUM = 10124
            
        print ("Define")   
        key_filename = "D:/ESS_DATA_EXPORT_LIVE/encryptionKey/NewKey/POS_SSH_private.txt"
        passphrase="welcome#1"
        encryptedFileName = source+".pgp"

        i = 1
        isTransfer = False
        _result = 0
        while(i < 4 and isTransfer == False ) :
            try :
                print ("connecting")
            
                # code Mamun
                mySSHK   = paramiko.RSAKey.from_private_key_file(key_filename,password=passphrase)
                sshcon   = paramiko.SSHClient()  # will create the object
                sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # no known_hosts error
                print ("connecting")
                #sshcon.connect(hostname, username=myuser, key_filename=mySSHK) # no passwd needed
                sshcon.connect(host, username=myuser, pkey=mySSHK,port=PORT_NUM,disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
                print("Connection succesfully stablished to FPT server... ")
                with sshcon.open_sftp() as sftp:
                    sftp.put(encryptedFileName, destination)
                print("File transfer done to FPT server... ")
                i = 4
                isTransfer = True
                _result =  1

            except Exception as e:
                errorMessage = "File Transfer Exception Error: " + str(e)
                print(errorMessage)
                ii = self.GenerateErrorLog(source, -1, "", errorMessage,'', 1)
                i = i+1
                isTransfer = False
                _result = -1
                time.sleep(5)
                
        return _result

   def FileEncryption(self,FILE_PATH):
       try:
           gpg = gnupg.GPG('C://Program Files (x86)/GnuPG/bin/gpg.exe')
           keyInput=gpg.gen_key_input(
               name_email='biodev02@banglalink.net',
               passphrase='iuytreadfghj98765sdfg76erty',
               key_type='RSA',
               key_length=4096
            )
           key=gpg.gen_key(keyInput)
           print(key)
           path=FILE_PATH
           with open(path,'rb')as f:
               status=gpg.encrypt_file(f,['almamun@primetechbd.com'],output=path+".Pgp")
           #print(status.ok)
           #print(status.stderr)
           return 1
       
       except:
            return 0

   def Transfer_local_location(self,source, destination, fileName):
       try:
           shutil.copyfile(source, destination)
           errorMessage = fileName+" File transfer done to FPT server... "
           #ii = self.GenerateErrorLog(source, rownum, destination, errorMessage,'', 0)
           print(errorMessage)
           return 1

       except Exception as e:
           errorMessage = fileName+" Transfer got Exception for(: "+source + str(e)
           ii = self.GenerateErrorLog(source, -1, destination, errorMessage,'', 1)
           print(errorMessage)
           return 0
       

   def FileEncryptionWithKey(self,FILE_PATH, ENCRYPT_FILE_NAME):
       try:
           NEW_FILENAME = FILE_PATH+".pgp"
           gpg = gnupg.GPG('C:/Program Files (x86)/GnuPG/bin/gpg.exe')
           #publicKeyFile='E:\ESS_DATA_EXPORT_LIVE\encryptionKey\POS-pub.asc'
           publicKeyFile='D:\ESS_DATA_EXPORT_TEST\encryptionKey\OIC_PROD_POS_KEY_pub.asc'
           pub_key, _ = pgpy.PGPKey.from_file(str(publicKeyFile))
           print(pub_key)
           path=FILE_PATH
           NEW_FILE_NAME = FILE_PATH+".pgp"
           f_t_e = pgpy.PGPMessage.new(str(path),file=True)
           encrypted_f_t_e = pub_key.encrypt(f_t_e)
           f=open(NEW_FILENAME,"w")
           f.write(str(encrypted_f_t_e))
           f.close()
           print("file")
           print(encrypted_f_t_e)

           return 1
       
       except Exception as e:
           errorMessage = "File Encryption Error: " + str(e)
           print(errorMessage)			
           return 0

