from django.shortcuts import render
from django.http import HttpResponse
import ibm_db
import ibm_db_dbi
import matplotlib.pyplot as plt
import pandas as pd

from django.views.decorators.csrf import csrf_protect
@csrf_protect
def say_hello(request):
    if request.method == 'POST':
        input1 = request.POST.get('input1')
        input2 = request.POST.get('input2')
        dsn_hostname = "b70af05b-76e4-4bca-a1f5-23dbb4c6a74e.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud" 
        dsn_uid = "dqr97099"        
        dsn_pwd = "4SZoipiCe3Zxfu96"      
        dsn_driver = "{IBM DB2 ODBC DRIVER}"
        dsn_database = "bludb"            # e.g. "BLUDB"
        dsn_port = "32716"                # e.g. "32733" 
        dsn_protocol = "TCPIP"            # i.e. "TCPIP"
        dsn_security = "SSL"
        dsn = (
             "DRIVER={0};"
             "DATABASE={1};"
             "HOSTNAME={2};"
             "PORT={3};"
             "PROTOCOL={4};"
             "UID={5};"
             "PWD={6};"
             "SECURITY={7};").format(dsn_driver, dsn_database, dsn_hostname, dsn_port, dsn_protocol, dsn_uid, dsn_pwd,dsn_security)
        try:
            conn = ibm_db.connect(dsn, "", "")
            pconn = ibm_db_dbi.Connection(conn)
            selectQuery = "select * from car_details"
            cars = pd.read_sql(selectQuery, pconn)
            cars.rename(columns = {'EX_SHOWROOM_PRICE' : 'PRICE'}, inplace = True)
            cars.rename(columns={'ABS_(Anti-lock_Braking_System)':'ABS'},inplace=True)


            cars['PRICE'] = cars['PRICE'].str.replace(',', '')
            cars['PRICE'] = cars['PRICE'].str.replace('Rs. ', '')
            cars['PRICE'] = cars['PRICE'].astype(int)
            cars['DISPLACEMENT'] = cars['DISPLACEMENT'].str.replace(' cc', '')
            cars.DISPLACEMENT = cars.DISPLACEMENT.fillna(0)
            cars['DISPLACEMENT'] = cars['DISPLACEMENT'].astype(int)
            
            
            p=cars['PRICE']
            cars['CAR'] = cars['MAKE']+" "+cars['MODEL']+" "+cars['VARIANT']
            
            cars.drop(cars.columns[[0,1,2,3]], axis=1, inplace=True)
            cars['POWER']=cars['POWER'].str.extract(r"(\d+)")[0]
            cars['TORQUE']=cars['TORQUE'].str.extract(r"(\d+)")[0]
            
            cars['SEAT_HEIGHT_ADJUSTMENT']=cars['SEAT_HEIGHT_ADJUSTMENT'].replace("Electric Adjustment with Memory","10")
            cars['SEAT_HEIGHT_ADJUSTMENT']=cars['SEAT_HEIGHT_ADJUSTMENT'].fillna("0")
            cars['SEAT_HEIGHT_ADJUSTMENT']=cars['SEAT_HEIGHT_ADJUSTMENT'].replace("Electric Adjustment","8")
            cars['SEAT_HEIGHT_ADJUSTMENT']=cars['SEAT_HEIGHT_ADJUSTMENT'].replace("Semi Automatic Adjustment","6")
            cars['SEAT_HEIGHT_ADJUSTMENT']=cars['SEAT_HEIGHT_ADJUSTMENT'].replace("Manual Adjustment","4")
            
            cars['POWER']=cars['POWER'].fillna("0")
            cars['TORQUE']=cars['TORQUE'].fillna("0")
            cars['POWER']=cars['POWER'].astype('int')
            cars['TORQUE']=cars['TORQUE'].astype('int')

            def normalize(n,c):
                 min=cars[c].min()
                 max=cars[c].max()
                 std=cars[c].std()
                 return (n - min) / (max - min) * 10
            for n in ['POWER','TORQUE','DISPLACEMENT']:
                 cars[n]=cars[n].apply(lambda x : normalize(x,n))

            def category(c):
                 cars[c]=cars[c].str.replace("yes","10")
                 cars[c]=cars[c].str.replace("Yes","10")
                 cars[c]=cars[c].fillna("0")
            for i in ['TURBOCHARGER','CRUISE_CONTROL','DOOR_AJAR_WARNING']:
                 category(i)

            cars['CYLINDERS']=cars['CYLINDERS'].fillna(cars['CYLINDERS'].mean())
            cars['CYLINDERS']=(cars['CYLINDERS']/2).astype(int)
            cars.drop(cars.columns[[0]], axis=1, inplace=True)
            
            t=cars['CAR']
            cars = cars.apply(pd.to_numeric, errors='coerce')
            cars['Rating']=cars.sum(axis=1)
            cars['CAR']=t
            cars['PRICE']=p
            min=int(input1)
            max=int(input2)
           
            a=int(cars['PRICE'].max())
            b=int(cars['PRICE'].min())
            if(max>a or min<b):
                return HttpResponse("out of range")
            else:
                 temp=cars[(cars['PRICE'] >= min) & (cars['PRICE'] <= max)]
                 model=temp[temp.Rating==temp.Rating.max()]
                 return HttpResponse("the suitable car will be "+str(model['CAR'].iloc[0]))
        except:
            return HttpResponse("unnable to connect to database")
    else:
        return render(request, 'index.html')