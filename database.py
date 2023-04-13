# -*- coding: utf-8 -*-
"""
Created on Sat Feb 18 17:51:22 2023

@author: bpank
"""

import pickle
import tarfile
import pandas as pd
from matplotlib import pyplot as plt
from ydata_profiling import ProfileReport
import numpy as np
from scipy.stats import f_oneway
from statsmodels.formula.api import ols
from statsmodels.stats.outliers_influence import variance_inflation_factor

tar = tarfile.open('finance.spydata', 'r')
tar.extractall()
extracted_files = tar.getnames()
for f in extracted_files:
   if f.endswith('.pickle'):
        with open(f, 'rb') as fdesc:
            finance = pickle.loads(fdesc.read())

tar = tarfile.open('result.spydata', 'r')
tar.extractall()
extracted_files = tar.getnames()
for f in extracted_files:
   if f.endswith('.pickle'):
        with open(f, 'rb') as fdesc:
            result = pickle.loads(fdesc.read())
    
#Adatbázis létrehozása
#Mérlegfőösszeg
data = pd.DataFrame(finance['balance']['Tárgyévi adat'])
data.rename(columns = {'Tárgyévi adat' : 'Mérlegfőösszeg'}, inplace = True)

#Hitel
data['Kötelezettségek'] = finance['credit_sum']['Tárgyévi adat']
data['Hátrasorolt kötelezettségek'] = finance['credit'][finance['credit']['Név'] == 'Hátrasorolt kötelezettségek']['Tárgyévi adat']
data['Rövid lejáratú kötelezettségek'] = finance['credit'][finance['credit']['Név'] == 'Rövid lejáratú kötelezettségek']['Tárgyévi adat']
data['Hosszú lejáratú kötelezettségek'] = finance['credit'][finance['credit']['Név'] == 'Hosszú lejáratú kötelezettségek']['Tárgyévi adat']

#Saját tőke
data['Saját tőke'] = finance['own_money']['Tárgyévi adat']

#Bevétel
data['Bevétel'] = finance['income_sum']['Tárgyévi adat']

data['Értékesítés nettó árbevétele'] = finance['income'][finance['income']['Név'] == 'Értékesítés nettó árbevétele']['Tárgyévi adat']
data['Egyéb bevételek'] = finance['income'][finance['income']['Név'] == 'Egyéb bevételek']['Tárgyévi adat']

#Ráfordítás
data['Ráfordítás'] = finance['expenditure_sum']['Tárgyévi adat']

data['Anyagjellegű ráfordítások'] = finance['expenditure'][finance['expenditure']['Név'] == 'Anyagjellegű ráfordítások']['Tárgyévi adat']
data['Személyi jellegű ráfordítások'] = finance['expenditure'][finance['expenditure']['Név'] == 'Személyi jellegű ráfordítások']['Tárgyévi adat']
data['Egyéb ráfordítások'] = finance['expenditure'][finance['expenditure']['Név'] == 'Egyéb ráfordítások']['Tárgyévi adat']

#Értékcsökkenési leírás
data['Értékcsökkenési leírás'] = finance['depreciation']['Tárgyévi adat']

#Pénzügyi eredmény
data['Adózás előtti eredmény'] = finance['tax_result'][finance['tax_result']['Név'] == 'Adózás előtti eredmény']['Tárgyévi adat']
data['Adózott eredmény'] = finance['tax_result'][finance['tax_result']['Név'] == 'Adózott eredmény']['Tárgyévi adat']

data_balance = data

#Eredmény
data = pd.merge(data, result['nb'], on = ['Cégjegyzékszám', 'Év'], how = 'left')

#Leíró statisztika
data.info()
data.describe()
data.isnull().sum()

#Data2 - üres sorok nélküli adatbázis
data.drop_duplicates(inplace = True)
data2 = data.dropna()
data2[['Helyezés', 'Lejátszott meccsek', 'Győzelem', 'Döntetlen', 'Vereség', 'Pontok', 'Lőtt gólok', 'Kapott gólok']] = data2[['Helyezés', 'Lejátszott meccsek', 'Győzelem', 'Döntetlen', 'Vereség', 'Pontok', 'Lőtt gólok', 'Kapott gólok']].astype(int)

data2['Pontok2'] = data2['Pontok'] / data2['Lejátszott meccsek']

avg_nb1diff = (data2[data2['Bajnokság'] == 'NB1']['Pontok2'].max() - data2[data2['Bajnokság'] == 'NB1']['Pontok2'].min()) / data2[data2['Bajnokság'] == 'NB1']['Pontok2'].count()
avg_nb2diff = (data2[data2['Bajnokság'] == 'NB2']['Pontok2'].max() - data2[data2['Bajnokság'] == 'NB2']['Pontok2'].min()) / data2[data2['Bajnokság'] == 'NB2']['Pontok2'].count()
min_nb1 = data2[data2['Bajnokság'] == 'NB1']['Pontok2'].min()
max_nb2 = data2[data2['Bajnokság'] == 'NB2']['Pontok2'].max()
diff = max_nb2 - (min_nb1 - (avg_nb1diff + avg_nb2diff) / 2)
data2['Pontok3'] = np.where(data2['Bajnokság'] == 'NB1', data2['Pontok2'], data2['Pontok2'] - diff)

data2.info()
data2.describe()

profile1 = ProfileReport(data2, 
                        explorative=True,
                        correlations={"pearson":{"calculate": True},
                                      "spearman":{"calculate": True},
                                      "kendall":{"calculate": False},
                                      "cramers":{"calculate": False},
                                      "phi_k":{"calculate": False}},
                        interactions={'continuous':False})
profile1.to_file(output_file = 'profiling1.html')

#Mérlegen belüli összefüggések
profile2 = ProfileReport(data_balance, 
                        explorative=True,
                        correlations={"pearson":{"calculate": True},
                                      "spearman":{"calculate": True},
                                      "kendall":{"calculate": False},
                                      "cramers":{"calculate": False},
                                      "phi_k":{"calculate": False}},
                        interactions={'continuous':False})
profile2.to_file(output_file = 'profiling2.html')

balance_r2 = (data_balance.corr())**2

#Bajnokság és mérlegfőösszeg közötti kapcsolat
#varianciahányados
pivot1 = data2.groupby('Bajnokság')['Mérlegfőösszeg'].agg(['count', np.mean, np.std])
ssk1 = sum(pivot1['count'] * (pivot1['mean'] - data2['Mérlegfőösszeg'].mean())**2) / data2['Mérlegfőösszeg'].count()
ssb1 = sum(pivot1['std']**2 * pivot1['count']) / data2['Mérlegfőösszeg'].count()
sst1 = ssk1 + ssb1
h21 = ssk1 / ssb1

#anova
df1 = data2.groupby('Bajnokság')['Mérlegfőösszeg'].apply(list)
anova1 = f_oneway(*df1)
p1 = anova1[1]
#van összefüggés a között, hogy melyik bajnokságban játszik, és mekkora a mérlegfőösszege

#Mérlegfőösszeg százalékban meghatározott értékek
data3 = data2.copy()
data3['Kötelezettségek'] = data3['Kötelezettségek'] / data3['Mérlegfőösszeg']
data3['Hátrasorolt kötelezettségek'] = data3['Hátrasorolt kötelezettségek'] / data3['Mérlegfőösszeg']
data3['Rövid lejáratú kötelezettségek'] = data3['Rövid lejáratú kötelezettségek'] / data3['Mérlegfőösszeg']
data3['Hosszú lejáratú kötelezettségek'] = data3['Hosszú lejáratú kötelezettségek'] / data3['Mérlegfőösszeg']
data3['Saját tőke'] = data3['Saját tőke'] / data3['Mérlegfőösszeg']
data3['Bevétel'] = data3['Bevétel'] / data3['Mérlegfőösszeg']
data3['Értékesítés nettó árbevétele'] = data3['Értékesítés nettó árbevétele'] / data3['Mérlegfőösszeg']
data3['Egyéb bevételek'] = data3['Egyéb bevételek'] / data3['Mérlegfőösszeg']
data3['Ráfordítás'] = data3['Ráfordítás'] / data3['Mérlegfőösszeg']
data3['Anyagjellegű ráfordítások'] = data3['Anyagjellegű ráfordítások'] / data3['Mérlegfőösszeg']
data3['Személyi jellegű ráfordítások'] = data3['Személyi jellegű ráfordítások'] / data3['Mérlegfőösszeg']
data3['Egyéb ráfordítások'] = data3['Egyéb ráfordítások'] / data3['Mérlegfőösszeg']
data3['Értékcsökkenési leírás'] = data3['Értékcsökkenési leírás'] / data3['Mérlegfőösszeg']
data3['Adózás előtti eredmény'] = data3['Adózás előtti eredmény'] / data3['Mérlegfőösszeg']
data3['Adózott eredmény'] = data3['Adózott eredmény'] / data3['Mérlegfőösszeg']

profile3 = ProfileReport(data3, 
                        explorative=True,
                        correlations={"pearson":{"calculate": True},
                                      "spearman":{"calculate": True},
                                      "kendall":{"calculate": False},
                                      "cramers":{"calculate": False},
                                      "phi_k":{"calculate": False}},
                        interactions={'continuous':False})
profile3.to_file(output_file = 'profiling3.html')

#Regresszió
#1. regresszió: eredeti adatokból
data_reg1 = data2.reset_index()
model1 = ols('Pontok3 ~ C(Év) + Mérlegfőösszeg + Q("Hátrasorolt kötelezettségek") + Q("Rövid lejáratú kötelezettségek") + Q("Hosszú lejáratú kötelezettségek") + Q("Saját tőke") + Q("Értékesítés nettó árbevétele") + Q("Egyéb bevételek") + Q("Anyagjellegű ráfordítások") + Q("Személyi jellegű ráfordítások") + Q("Egyéb ráfordítások") + Q("Értékcsökkenési leírás") + Q("Adózás előtti eredmény") + C(Bajnokság)', data = data_reg1)
reg1 = model1.fit()
reg1.summary2()
rnégyzet1 = float(reg1.summary2().tables[0].iloc[6, 1])
krnégyzet1 = float(reg1.summary2().tables[0].iloc[0, 3])

#2. regresszió: mérlegfőösszeg méret, minden más százalék
data_reg2 = data3.reset_index()
model2 = ols('Pontok3 ~ C(Év) + Mérlegfőösszeg + Q("Hátrasorolt kötelezettségek") + Q("Rövid lejáratú kötelezettségek") + Q("Hosszú lejáratú kötelezettségek") + Q("Saját tőke") + Q("Értékesítés nettó árbevétele") + Q("Egyéb bevételek") + Q("Anyagjellegű ráfordítások") + Q("Személyi jellegű ráfordítások") + Q("Egyéb ráfordítások") + Q("Értékcsökkenési leírás") + Q("Adózás előtti eredmény") + C(Bajnokság)', data = data_reg2)
reg2 = model2.fit()
reg2.summary2()
rnégyzet2 = float(reg2.summary2().tables[0].iloc[6, 1])
krnégyzet2 = float(reg2.summary2().tables[0].iloc[0, 3])

#3. regresszió: jobbra elnyúló változók logaritmussal
data4 = data3.copy()

data4['Mérlegfőösszeg'] = np.log(data4['Mérlegfőösszeg'])
data4['Hosszú lejáratú kötelezettségek'] = np.where(data4['Hosszú lejáratú kötelezettségek'] == 0, 0, np.log(data4['Hosszú lejáratú kötelezettségek']))
data4['Hátrasorolt kötelezettségek'] = np.where(data4['Hátrasorolt kötelezettségek'] == 0, 0, np.log(data4['Hátrasorolt kötelezettségek']))
data4['Rövid lejáratú kötelezettségek'] = np.where(data4['Rövid lejáratú kötelezettségek'] == 0, 0, np.log(data4['Rövid lejáratú kötelezettségek']))
data4['Értékesítés nettó árbevétele'] = np.where(data4['Értékesítés nettó árbevétele'] == 0, 0, np.log(data4['Értékesítés nettó árbevétele']))
data4['Egyéb bevételek'] = np.where(data4['Egyéb bevételek'] == 0, 0, np.log(data4['Egyéb bevételek']))
data4['Anyagjellegű ráfordítások'] = np.where(data4['Anyagjellegű ráfordítások'] == 0, 0, np.log(data4['Anyagjellegű ráfordítások']))
data4['Személyi jellegű ráfordítások'] = np.where(data4['Személyi jellegű ráfordítások'] == 0, 0, np.log(data4['Személyi jellegű ráfordítások']))
data4['Egyéb ráfordítások'] = np.where(data4['Egyéb ráfordítások'] == 0, 0, np.log(data4['Egyéb ráfordítások']))
data4['Értékcsökkenési leírás'] = np.where(data4['Értékcsökkenési leírás'] == 0, 0, np.log(data4['Értékcsökkenési leírás']))

profile4 = ProfileReport(data4, 
                        explorative=True,
                        correlations={"pearson":{"calculate": True},
                                      "spearman":{"calculate": True},
                                      "kendall":{"calculate": False},
                                      "cramers":{"calculate": False},
                                      "phi_k":{"calculate": False}},
                        interactions={'continuous':False})
profile4.to_file(output_file = 'profiling4.html')

data_reg3 = data4.reset_index()
model3 = ols('Pontok3 ~ C(Év) + Mérlegfőösszeg + Q("Hátrasorolt kötelezettségek") + Q("Rövid lejáratú kötelezettségek") + Q("Hosszú lejáratú kötelezettségek") + Q("Saját tőke") + Q("Értékesítés nettó árbevétele") + Q("Egyéb bevételek") + Q("Anyagjellegű ráfordítások") + Q("Személyi jellegű ráfordítások") + Q("Egyéb ráfordítások") + Q("Értékcsökkenési leírás") + Q("Adózás előtti eredmény") + C(Bajnokság)', data = data_reg3)
reg3 = model3.fit()
reg3.summary2()
rnégyzet3 = float(reg3.summary2().tables[0].iloc[6, 1])
krnégyzet3 = float(reg3.summary2().tables[0].iloc[0, 3])

#4. regresszió: hátrasorolt kötelezettségek nélkül és hosszú kötelezettség dummy változóként
data5 = data4.copy()
data5['Hosszú lejáratú kötelezettségek'] = np.where(data5['Hosszú lejáratú kötelezettségek'] != 0, 1, 0)

data_reg4 = data5.reset_index()
model4 = ols('Pontok3 ~ C(Év) + Mérlegfőösszeg + Q("Rövid lejáratú kötelezettségek") + Q("Hosszú lejáratú kötelezettségek") + Q("Saját tőke") + Q("Értékesítés nettó árbevétele") + Q("Egyéb bevételek") + Q("Anyagjellegű ráfordítások") + Q("Személyi jellegű ráfordítások") + Q("Egyéb ráfordítások") + Q("Értékcsökkenési leírás") + Q("Adózás előtti eredmény") + C(Bajnokság)', data = data_reg4)
reg4 = model4.fit()
reg4.summary2()
rnégyzet4 = float(reg4.summary2().tables[0].iloc[6, 1])
krnégyzet4 = float(reg4.summary2().tables[0].iloc[0, 3])

#5. regresszió: outlier értékek kitörlése 
pmin = []
pmax = []
data_outlier = pd.DataFrame()

data6 = data5.copy()
for c in data6.columns[0:16]:
    if ((c != 'Hosszú lejáratú kötelezettségek') and (c != 'Hátrasorolt kötelezettségek')):
        down, up = np.percentile(data6[c], [10, 90])
        pmin.append(down)
        pmax.append(up)

i = 0

for c in data6.columns[0:16]:
    if ((c != 'Hosszú lejáratú kötelezettségek') and (c != 'Hátrasorolt kötelezettségek')):
        data6 = data6[data6[c] <= pmax[i] + 1 * (pmax[i]-pmin[i])]
        data6 = data6[data6[c] >= pmin[i] - 1 * (pmax[i]-pmin[i])]
        i = i + 1

data_outlier = pd.concat([data5, data6]).drop_duplicates(keep = False)

data_reg5 = data6.reset_index()
model5 = ols('Pontok3 ~ C(Év) + Mérlegfőösszeg + Q("Rövid lejáratú kötelezettségek") + Q("Hosszú lejáratú kötelezettségek") + Q("Saját tőke") + Q("Értékesítés nettó árbevétele") + Q("Egyéb bevételek") + Q("Anyagjellegű ráfordítások") + Q("Személyi jellegű ráfordítások") + Q("Egyéb ráfordítások") + Q("Értékcsökkenési leírás") + Q("Adózás előtti eredmény") + C(Bajnokság)', data = data_reg5)
reg5 = model5.fit()
reg5.summary2()
rnégyzet5 = float(reg5.summary2().tables[0].iloc[6, 1])
krnégyzet5 = float(reg5.summary2().tables[0].iloc[0, 3])


#6. regresszió: hosszú lejáratú kötelezettség nélkül
model6 = ols('Pontok3 ~ C(Év) + Mérlegfőösszeg + Q("Rövid lejáratú kötelezettségek") + Q("Saját tőke") + Q("Értékesítés nettó árbevétele") + Q("Egyéb bevételek") + Q("Anyagjellegű ráfordítások") + Q("Személyi jellegű ráfordítások") + Q("Egyéb ráfordítások") + Q("Értékcsökkenési leírás") + Q("Adózás előtti eredmény") + C(Bajnokság)', data = data_reg5)
reg6 = model6.fit()
reg6.summary2()
rnégyzet6 = float(reg6.summary2().tables[0].iloc[6, 1])
krnégyzet6 = float(reg6.summary2().tables[0].iloc[0, 3])

#7. regresszió: egyéb bevételek és ráfordítás nélkül
model7 = ols('Pontok3 ~ C(Év) + Mérlegfőösszeg + Q("Rövid lejáratú kötelezettségek") + Q("Saját tőke") + Q("Értékesítés nettó árbevétele") + Q("Anyagjellegű ráfordítások") + Q("Személyi jellegű ráfordítások") + Q("Értékcsökkenési leírás") + Q("Adózás előtti eredmény") + C(Bajnokság)', data = data_reg5)
reg7 = model7.fit()
reg7.summary2()
rnégyzet7 = float(reg7.summary2().tables[0].iloc[6, 1])
krnégyzet7 = float(reg7.summary2().tables[0].iloc[0, 3])

#8. regresszió: évek nélkül
model8 = ols('Pontok3 ~ Mérlegfőösszeg + Q("Rövid lejáratú kötelezettségek") + Q("Saját tőke") + Q("Értékesítés nettó árbevétele") + Q("Anyagjellegű ráfordítások") + Q("Személyi jellegű ráfordítások") + Q("Értékcsökkenési leírás") + Q("Adózás előtti eredmény") + C(Bajnokság)', data = data_reg5)
reg8 = model8.fit()
reg8.summary2()
rnégyzet8 = float(reg8.summary2().tables[0].iloc[6, 1])
krnégyzet8 = float(reg8.summary2().tables[0].iloc[0, 3])

#9. regresszió: adózás előtti eredmény eltolásával és logaritmizálásával
data7 = data6.copy()
data7['Adózás előtti eredmény'] = data7['Adózás előtti eredmény'] + 1

data7['Adózás előtti eredmény'] = np.where(data7['Adózás előtti eredmény'] == 0, 0, np.log(data7['Adózás előtti eredmény']))

data_reg6 = data7.reset_index()

model9 = ols('Pontok3 ~ Mérlegfőösszeg + Q("Rövid lejáratú kötelezettségek") + Q("Saját tőke") + Q("Értékesítés nettó árbevétele") + Q("Anyagjellegű ráfordítások") + Q("Személyi jellegű ráfordítások") + Q("Értékcsökkenési leírás") + Q("Adózás előtti eredmény") + C(Bajnokság)', data = data_reg6)
reg9 = model9.fit()
reg9.summary2()
rnégyzet9 = float(reg9.summary2().tables[0].iloc[6, 1])
krnégyzet9 = float(reg9.summary2().tables[0].iloc[0, 3])

#10. regresszió: adózás előtti eredmény nélkül
model10 = ols('Pontok3 ~ Mérlegfőösszeg + Q("Rövid lejáratú kötelezettségek") + Q("Saját tőke") + Q("Értékesítés nettó árbevétele") + Q("Anyagjellegű ráfordítások") + Q("Személyi jellegű ráfordítások") + Q("Értékcsökkenési leírás") + C(Bajnokság)', data = data_reg6)
reg10 = model10.fit()
reg10.summary2()
result = reg10.summary2()
rnégyzet10 = float(reg10.summary2().tables[0].iloc[6, 1])
krnégyzet10 = float(reg10.summary2().tables[0].iloc[0, 3])

#eltérő-e a hatás NB2-ben a személyi jellegű ráfordításra
data_reg7 = data_reg6.copy()
data_reg7['Bajnokság2'] = np.where(data_reg6['Bajnokság'] == 'NB1', data_reg6['Személyi jellegű ráfordítások'] * 0, data_reg6['Személyi jellegű ráfordítások'])
model11 = ols('Pontok3 ~ Mérlegfőösszeg + Q("Rövid lejáratú kötelezettségek") + Q("Saját tőke") + Q("Értékesítés nettó árbevétele") + Q("Anyagjellegű ráfordítások") + Q("Személyi jellegű ráfordítások") + Q("Értékcsökkenési leírás") + C(Bajnokság) + Bajnokság2', data = data_reg7)
reg11 = model11.fit()
reg11.summary2()
rnégyzet11 = float(reg11.summary2().tables[0].iloc[6, 1])
krnégyzet11 = float(reg11.summary2().tables[0].iloc[0, 3])

#VIF 9
data_vif = data_reg6
data_vif = data_vif.join(pd.get_dummies(data_vif['Bajnokság'])['NB2'])

X9 = data_vif[['Mérlegfőösszeg', 'Rövid lejáratú kötelezettségek', 'Saját tőke', 'Értékesítés nettó árbevétele', 'Anyagjellegű ráfordítások', 'Személyi jellegű ráfordítások', 'Értékcsökkenési leírás', 'Adózás előtti eredmény', 'NB2']]

vif_data9 = pd.DataFrame()
vif_data9['változó'] = X9.columns
  
vif_data9["VIF"] = [variance_inflation_factor(X9.values, i)
                   for i in range(len(X9.columns))]

#VIF 10
X10 = data_vif[['Mérlegfőösszeg', 'Rövid lejáratú kötelezettségek', 'Saját tőke', 'Értékesítés nettó árbevétele', 'Anyagjellegű ráfordítások', 'Személyi jellegű ráfordítások', 'Értékcsökkenési leírás', 'NB2']]

vif_data10 = pd.DataFrame()
vif_data10['változó'] = X10.columns
  
vif_data10["VIF"] = [variance_inflation_factor(X10.values, i)
                   for i in range(len(X10.columns))]

#Error értékek
error = []

data_error = data_reg5.copy()
data_error['Bajnokság'] = np.where(data_error['Bajnokság'] == 'NB1', 0, 1)

for i in range(len(data_error)):
    y = reg10.params[0] + reg10.params[1] * data_error['Bajnokság'][i] + reg10.params[2] * data_error['Mérlegfőösszeg'][i] + reg10.params[3] * data_error['Rövid lejáratú kötelezettségek'][i] + reg10.params[4] * data_error['Saját tőke'][i] + reg10.params[5] * data_error['Értékesítés nettó árbevétele'][i] + reg10.params[6] * data_error['Anyagjellegű ráfordítások'][i] + reg10.params[7] * data_error['Személyi jellegű ráfordítások'][i] + reg10.params[8] * data_error['Értékcsökkenési leírás'][i]
    
    error.append(y)
