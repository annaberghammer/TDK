# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 17:15:56 2022

@author: bpank
"""

import pandas as pd
import numpy as np
import time
from selenium import webdriver
from webdriver_auto_update import check_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from lxml import etree
import os

delay = 30

try:
    driver = webdriver.Chrome(str(os.getcwd()) + '\chromedriver.exe')
    driver.close()
except:
    check_driver(str(os.getcwd()))

balance_df = pd.DataFrame()
result_df = pd.DataFrame()

#Csapatok adatainak a beolvasása
team_df = pd.read_excel('csapatok.xlsx')

#Csapatok adatainak letöltése
for j in team_df['Cégjegyzékszám']:
    team = j
    
    #Weboldal megnyitása
    driver = webdriver.Chrome(str(os.getcwd()) + '\chromedriver.exe')
    driver.get('https://e-beszamolo.im.gov.hu/oldal/kezdolap')
    
    time.sleep(1)

    #Weboldal betöltésének megvárása
    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.NAME, 'firmNumber')))
    
    #Cégjegyzékszám betöltése
    driver.find_element_by_name('firmNumber').send_keys(team)
    
    time.sleep(1)
    
    #Nem vagyok robot megnyitása
    iframe = driver.find_element_by_xpath('//*[@id="g-recaptcha"]/div/div/iframe')
    driver.switch_to.frame(iframe)
    driver.find_element_by_id('recaptcha-anchor').click()
    
    #https://powerdynamite.medium.com/how-to-bypass-recaptcha-v3-with-selenium-python-7e71c1b680fc
    #Nem vagyok robot kitöltése
    ######################################################################
    
    ######################################################################
    
    #Nem vagyok robot kitöltésének megvárása
    driver.switch_to.default_content()
    
    WebDriverWait(driver, 120).until(
    EC.element_to_be_clickable((By.ID, 'btnSubmit')))
    
    time.sleep(1)
    
    #Keresés
    driver.find_element_by_id('btnSubmit').click()
    
    #Felhasználási feltételek kitöltése
    WebDriverWait(driver, delay).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="acceptCheck"]')))
    
    driver.find_element_by_xpath('//*[@id="acceptCheck"]').click()
    driver.find_element_by_xpath('//*[@id="acceptModal"]').click()
    
    time.sleep(1)
    
    #Túl sok kérés érkezett kezelése
    error_text = ''
    
    try:
        WebDriverWait(driver, delay).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="search-result-table"]/tbody/tr/td[1]/a')))
    except:
        pass
    
    try:
        error_text = driver.find_element_by_xpath('//*[@id="searchResult"]/div[1]').text
    except:
        pass
    
    if ('Túl sok kérés érkezett rövid időn belül az IP címről. Kérem várjon néhány percet, majd ismételje meg a kérést!' in error_text):
        time.sleep(180)
        
        #driver.refresh()
        
        #Weboldal betöltésének megvárása
        #WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.NAME, 'firmNumber')))
        
        #Cégjegyzékszám betöltése
        #driver.find_element_by_name('firmNumber').send_keys(team)
        
        #time.sleep(1)
                
        #Nem vagyok robot megnyitása
        iframe = driver.find_element_by_xpath('//*[@id="g-recaptcha"]/div/div/iframe')
        driver.switch_to.frame(iframe)
        driver.find_element_by_id('recaptcha-anchor').click()
        
        #https://powerdynamite.medium.com/how-to-bypass-recaptcha-v3-with-selenium-python-7e71c1b680fc
        #Nem vagyok robot kitöltése
        ##################################################################
        
        ##################################################################
        
        #Nem vagyok robot kitöltésének megvárása
        driver.switch_to.default_content()
        
        WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.ID, 'btnSubmit')))
        
        time.sleep(1)
        
        #Keresés
        driver.find_element_by_id('btnSubmit').click()
    
    #Csapat adatainak megnyitása
    WebDriverWait(driver, delay).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="search-result-table"]/tbody/tr/td[1]/a')))
    
    driver.find_element_by_xpath('//*[@id="search-result-table"]/tbody/tr/td[1]/a').click()
    
    #Összes beszámolónak a megszámolása
    n = len(driver.find_elements_by_xpath('//*[@id="pnlBalances"]/div'))
    
    for i in range(n):
        time.sleep(1)
        
        WebDriverWait(driver, delay).until(
        EC.element_to_be_clickable((By.XPATH, f'//*[@id="pnlBalances"]/div[{i + 1}]/a')))
        
        #Általános üzleti évetzáró beszámolók megnyitása
        name = driver.find_element_by_xpath(f'//*[@id="pnlBalances"]/div[{i + 1}]/a').text
        
        if (name != 'Általános üzleti évet záró'):
            continue
        
        driver.find_element_by_xpath(f'//*[@id="pnlBalances"]/div[{i + 1}]/a').click()
        
        #Túl sok kérés kezelése
        try:
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="balancePrint"]/table[2]/tbody')))
            
        except:
            time.sleep(150)
            driver.refresh()
        
        try:
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="balancePrint"]/table[2]/tbody')))
            
        except:
            time.sleep(150)
            driver.refresh()
        
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="balancePrint"]/table[2]/tbody')))
            
        #Üzleti beszámoló éve
        year = driver.find_element_by_xpath('//*[@id="cover"]/table/tbody/tr/td').text
        year = year[:4]
        
        #Üzleti beszámoló adatai
        html = driver.page_source    
        soup = BeautifulSoup(html, 'html.parser')
                
        number_of_tables = len(soup.find_all('table', attrs = {'class' : "AttachmentTable repeat-header repeat-footer"}))
        
        #Mérleg adatok
        balance_temp = []
        
        balance_table = soup.find_all('table', attrs = {'class' : "AttachmentTable repeat-header repeat-footer"})[number_of_tables - 2]
        
        balance_body = balance_table.find_all('tbody')[2]
                
        balance_rows = balance_body.find_all('tr')
        
        for r in balance_rows:
            cols = r.find_all('td')
            row = [c.text.strip() for c in cols]
            try:
                row[2] = row[2].replace('\xa0', '')
                row[3] = row[3].replace('\xa0', '')
                row[4] = row[4].replace('\xa0', '')
            except:
                pass
            
            try:
                row[1] = row[1].split('\n')[1]
                
            except:
                pass
    
            row.pop(0)        
            
            if (len(row) == 3):
                row = [row[0], row[1], '', row[2]]
    
            balance_temp.append(row)
            
        balance_temp_df = pd.DataFrame(balance_temp)
        balance_temp_df['year'] = year
        balance_temp_df['team'] = team
        
        balance_df = pd.concat([balance_temp_df, balance_df])
        
        #Eredménykimutatés adatok
        result_temp = []
        
        result_table = soup.find_all('table', attrs = {'class' : "AttachmentTable repeat-header repeat-footer"})[number_of_tables - 1]
        
        result_body = result_table.find_all('tbody')[2]
        
        result_rows = result_body.find_all('tr')
        
        for r in result_rows:
            cols = r.find_all('td')
            row = [c.text.strip() for c in cols]
            try:
                row[2] = row[2].replace('\xa0', '')
                row[3] = row[3].replace('\xa0', '')
                row[4] = row[4].replace('\xa0', '')
            except:
                pass
            
            try:
                row[1] = row[1].split('\n')[1]
            except:    
                pass
            
            row.pop(0)
            
            if (len(row) == 3):
                row = [row[0], row[1], '', row[2]]
    
            result_temp.append(row)
            
        result_temp_df = pd.DataFrame(result_temp)
        result_temp_df['year'] = year
        result_temp_df['team'] = team
        
        result_df = pd.concat([result_temp_df, result_df])
        
        driver.back()
        
    driver.close()

#Mérleg adatok
balance_df.columns = ['Név', 'Előző évi adat', 'Módosítások', 'Tárgyévi adat', 'Év', 'Cégjegyzékszám']
balance_df['Előző évi adat'] = pd.to_numeric(balance_df['Előző évi adat'])
balance_df['Módosítások'] = pd.to_numeric(balance_df['Módosítások'])
balance_df['Tárgyévi adat'] = pd.to_numeric(balance_df['Tárgyévi adat'])

#Eredménykimutatás adatok
result_df.columns = ['Név', 'Előző évi adat', 'Módosítások', 'Tárgyévi adat', 'Év', 'Cégjegyzékszám']
result_df['Előző évi adat'] = pd.to_numeric(result_df['Előző évi adat'])
result_df['Módosítások'] = pd.to_numeric(result_df['Módosítások'])
result_df['Tárgyévi adat'] = pd.to_numeric(result_df['Tárgyévi adat'])

#Mérlegfőösszeg
balance = balance_df[balance_df['Név'] == 'Eszközök (aktívák) összesen']
balance.set_index(['Cégjegyzékszám', 'Év'], inplace = True)

#Hitelek - rövid, hosszú lejáratú
credit = balance_df[balance_df['Név'].isin(['Hátrasorolt kötelezettségek', 'Hosszú lejáratú kötelezettségek', 'Rövid lejáratú kötelezettségek'])]
credit_sum = credit.groupby(['Cégjegyzékszám', 'Év'])[['Előző évi adat', 'Módosítások', 'Tárgyévi adat']].sum()

credit.set_index(['Cégjegyzékszám', 'Év'], inplace = True)

#Saját tőke
own_money = balance_df[balance_df['Név'].str.contains('Saját tőke')]

own_money.set_index(['Cégjegyzékszám', 'Év'], inplace = True)

#Bevétel
income = result_df[result_df['Név'].isin(['Értékesítés nettó árbevétele', 'Egyéb bevételek'])]
income_sum = income.groupby(['Cégjegyzékszám', 'Év'])[['Előző évi adat', 'Módosítások', 'Tárgyévi adat']].sum()

income.set_index(['Cégjegyzékszám', 'Év'], inplace = True)

#Ráfordítások
expenditure = result_df[result_df['Név'].isin(['Anyagjellegű ráfordítások', 'Személyi jellegű ráfordítások', 'Egyéb ráfordítások'])]
expenditure_sum = expenditure.groupby(['Cégjegyzékszám', 'Év'])[['Előző évi adat', 'Módosítások', 'Tárgyévi adat']].sum()

expenditure.set_index(['Cégjegyzékszám', 'Év'], inplace = True)

#Értékcsökkenési leírás
depreciation = result_df[result_df['Név'] == 'Értékcsökkenési leírás']

depreciation.set_index(['Cégjegyzékszám', 'Év'], inplace = True)

#Eredmény
tax_result = result_df[result_df['Név'].isin(['Adózás előtti eredmény', 'Adózott eredmény'])]

tax_result.set_index(['Cégjegyzékszám', 'Év'], inplace = True)

