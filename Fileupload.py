import pysftp as sftp

# path = './unnamed.jpg' + sys.argv[1]    #hard-coded
# localpath = sys.argv[1]

host='129.148.177.186'
username='OIC_UAT_POS'
password='BL#idcs#2022'
PORT ='5017'

cnopts = sftp.CnOpts()
cnopts.hostkeys = None

try:
    with sftp.Connection(host=host, username=username, password=password, port=5017, cnopts=cnopts) as sftp:
       print("Connection succesfully stablished ... ")
       sftp.put('E:/ESS_DATA_EXPORT_TEST/exportFiles/distributor_wallet_20220622.csv','/home/users/OIC_UAT_POS/distributor_wallet_20220622.csv')  # upload file to public/ on remote

    print ('Upload done.')

except Exception as e:
    print(str(e))