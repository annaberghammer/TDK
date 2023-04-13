# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 22:08:46 2023

@author: bpank
"""

import pandas as pd
import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from lxml import etree

delay = 120

result_temp = []
nb1_df = pd.DataFrame()
nb2_df = pd.DataFrame()

nb1_url = 'https://www.eredmenyek.com/foci/magyarorszag/otp-bank-liga/archivum/'
nb2_url = 'https://www.eredmenyek.com/foci/magyarorszag/merkantil-bank-liga/archivum/'

url = [nb1_url, nb2_url]

for u in range(len(url)):

    #Weboldal megnyitása
    driver = webdriver.Chrome('./chromedriver')

    driver.get(url[u])
    
    time.sleep(1)
    
    #Weboldal betöltésének megvárása
    WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="tournament-page-archiv"]/div[2]/div[1]/a')))
    
    try:  
        WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
        
        driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click()
    except:
        pass
    
    for i in range(8):
        WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="tournament-page-archiv"]/div[2]/div[1]/a')))
        
        driver.find_element_by_xpath(f'//*[@id="tournament-page-archiv"]/div[{i + 2}]/div[1]/a').click()
        
        time.sleep(1)
    
        WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="li3"]')))
        
        driver.find_element_by_xpath('//*[@id="li3"]').click()
        
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="tournament-table-tabs-and-content"]/div[3]/div[1]/div/div/div[2]/div[1]/div[1]')))
        
        time.sleep(1)
        
        year = driver.find_element_by_xpath('//*[@id="mc"]/div[4]/div[1]/div[2]/div[2]').text
        
        n = len(driver.find_elements_by_xpath('//*[@id="tournament-table-tabs-and-content"]/div[3]/div[1]/div/div/div[2]/div'))
        
        for j in range(n):            
            place = driver.find_element_by_xpath(f'//*[@id="tournament-table-tabs-and-content"]/div[3]/div[1]/div/div/div[2]/div[{j + 1}]/div[1]').text
            
            team = driver.find_element_by_xpath(f'//*[@id="tournament-table-tabs-and-content"]/div[3]/div[1]/div/div/div[2]/div[{j + 1}]/div[2]').text
            
            number_of_matches = driver.find_element_by_xpath(f'//*[@id="tournament-table-tabs-and-content"]/div[3]/div[1]/div/div/div[2]/div[{i + 2}]/span[1]').text
            
            wins = driver.find_element_by_xpath(f'//*[@id="tournament-table-tabs-and-content"]/div[3]/div[1]/div/div/div[2]/div[{j + 1}]/span[2]').text
            
            draws = driver.find_element_by_xpath(f'//*[@id="tournament-table-tabs-and-content"]/div[3]/div[1]/div/div/div[2]/div[{j + 1}]/span[3]').text
            
            losses = driver.find_element_by_xpath(f'//*[@id="tournament-table-tabs-and-content"]/div[3]/div[1]/div/div/div[2]/div[{j + 1}]/span[4]').text
            
            goals = driver.find_element_by_xpath(f'//*[@id="tournament-table-tabs-and-content"]/div[3]/div[1]/div/div/div[2]/div[{j + 1}]/span[5]').text
            
            if (u == 1 and j == 18 and i in (2, 6)):
                points = driver.find_element_by_xpath('//*[@id="tournament-table-tabs-and-content"]/div[3]/div[1]/div/div/div[2]/div[19]/div[3]/span').text
                
            else:    
                points = driver.find_element_by_xpath(f'//*[@id="tournament-table-tabs-and-content"]/div[3]/div[1]/div/div/div[2]/div[{j + 1}]/span[6]').text
                
            time.sleep(1)
            
            row = []
            row = [year, place, team, number_of_matches, wins, draws, losses, goals, points]     
            result_temp.append(row)
            
            time.sleep(1)

        result_df = pd.DataFrame(result_temp)    
        
        if (u == 0):
            nb1_df = pd.concat([nb1_df, result_df])
            
        else:
            nb2_df = pd.concat([nb2_df, result_df])
            
        result_temp = []
        
        print(i)
        
        time.sleep(1)
        driver.back()
        time.sleep(3)
        driver.back()
        time.sleep(1)
    
    driver.close()
    
nb1_df.columns = ['Év', 'Helyezés', 'Csapat', 'Lejátszott meccsek', 'Győzelem', 'Döntetlen', 'Vereség', 'Gólok', 'Pontok']
nb1_df['Bajnokság'] = 'NB1'
nb1_df.set_index('Csapat', inplace = True)


nb2_df.columns = ['Év', 'Helyezés', 'Csapat', 'Lejátszott meccsek', 'Győzelem', 'Döntetlen', 'Vereség', 'Gólok', 'Pontok']
nb2_df['Bajnokság'] = 'NB2'
nb2_df.set_index('Csapat', inplace = True)

nb1_df['Bajnokság kezdete'] = nb1_df['Év'].str[:4]
nb1_df['Bajnokság vége'] = nb1_df['Év'].str[-4:]

nb2_df['Bajnokság kezdete'] = nb2_df['Év'].str[:4]
nb2_df['Bajnokság vége'] = nb2_df['Év'].str[-4:]

nb1_df['Év'] = nb1_df['Év'].str[:4]
nb2_df['Év'] = nb2_df['Év'].str[:4]

#Csapat adatok összekötése
team_df = pd.read_excel('csapatok.xlsx')
team_df.set_index('Csapat', inplace = True)

nb_df = pd.concat([nb1_df, nb2_df])
nb = pd.merge(nb_df, team_df, on = 'Csapat', how = 'left')
nb.reset_index(inplace = True)
nb.set_index(['Cégjegyzékszám','Év'], inplace = True)

nb['Helyezés'] = nb['Helyezés'].str.replace('.', '', regex = True)
nb['Lőtt gólok'] = nb['Gólok'].str.split(':').str[0]
nb['Kapott gólok'] = nb['Gólok'].str.split(':').str[1]
