# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 22:24:34 2019
@author: Stefan Fuchs
"""
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

def accumulate_montly_occupation(excel_file, start_date = '2020-03-01', end_date = '2021-05-01'):
    """
    Expects an excel-file with at least the following columns/headers: 
        'geb. am' , 'Betreuungszeit', 'Betreuungsbeginn'
    """
    df = pd.read_excel(excel_file)
    df['geb. am'] = pd.to_datetime(df['geb. am'])
    df['Betreuungsbeginn'] = pd.to_datetime(df['Betreuungsbeginn'])
    df = df.rename(columns={"geb. am": "geb"})
    df['Betreuungsende'] = df.apply(lambda row: row.geb + pd.DateOffset(years=3), axis=1)
    print(df)    
    print(df.dtypes)    
    print(df.groupby('Betreuungszeit').count())
    time_index = pd.date_range(start_date, end_date, freq='MS')
    kinder_data = []
    for t in time_index:
        
        kinder_ganztags = 0
        kinder_halbtags = 0
        fachkraftstunden_soll = 0.0
        
        df["in17"] = df.apply(lambda row: (row.Betreuungsbeginn <= t) & (row.Betreuungsende > t) & ("17.00" in row.Betreuungszeit), axis=1)
        grouped_table = df.groupby('in17').count()        
        if True in grouped_table.index:
            fachkraftstunden_soll += grouped_table.loc[True][1]*50*0.2
            kinder_ganztags = grouped_table.loc[True][1]
        
        df["in14"] = df.apply(lambda row: (row.Betreuungsbeginn <= t) & (row.Betreuungsende > t) & ("14.00" in row.Betreuungszeit), axis=1)        
        grouped_table = df.groupby('in14').count()
        if True in grouped_table.index:
            fachkraftstunden_soll += grouped_table.loc[True][1]*30*0.2
            kinder_halbtags = grouped_table.loc[True][1]
            
        fachkraftstunden_soll *= 1.15
        fachkraftstunden_soll *= 1.09
        
        print("--------"+str(t)+"--------")
        print("7:00 - 17:00 : " + str(kinder_ganztags))
        print("7:00 - 14:00 : " + str(kinder_halbtags))        
        print("gesamt: " + str(kinder_ganztags + kinder_halbtags))        
        print("notwendige FKS: %5.2f " % (fachkraftstunden_soll))
        
        kinder_data.append({"date": t, 
                            "kinder_ganztags": kinder_ganztags, 
                            "kinder_halbtags": kinder_halbtags, 
                            "fachkraftstunden_soll" : fachkraftstunden_soll})
    return kinder_data

def plot_diagram(kinder_data):
    ticklabels      = [str(item["date"].month)+"/"+str(item["date"].year) for item in kinder_data]
    kinder_ganztags = [item["kinder_ganztags"] for item in kinder_data]
    kinder_halbtags = [item["kinder_halbtags"] for item in kinder_data]
    kinder_gesamt   = [item["kinder_ganztags"]+item["kinder_halbtags"] for item in kinder_data]
    fks_ist         = [41.5+40+35+40+20+30] * len(kinder_data)
    fks_soll        = [item["fachkraftstunden_soll"] for item in kinder_data]
    
    fig = plt.figure(figsize=(10,5))
    ax = plt.subplot(111)
    ax.set_ylim([0,25])
    ax.set_ylabel("Anzahl Kinder")
    ax.grid()
    ax.plot(kinder_ganztags,'-d')
    ax.plot(kinder_halbtags,'-d')
    ax.plot(kinder_gesamt,'-d')
    ax.set_xticks(np.arange(0,len(kinder_ganztags)))
    ax.set_xticklabels(ticklabels, rotation = 45)
    ax.legend(["7:00 - 17:00", "7:00 - 14:00", "alle"], loc=3)
    
    ax2 = ax.twinx()
    ax2.set_ylabel("Fachkraftstunden")
    ax2.set_ylim([0,230])
    ax2.plot(fks_ist,'--ok')
    ax2.plot(fks_soll,'--or')
    ax2.legend(["FKS ist (DF_35, AH_41, IM_40, MR_40, FS_30, MM_20)", "FKS soll"], loc=1)
    
    plt.show()

if __name__ == "__main__":
    kinder_data = accumulate_montly_occupation("file:///C:/Users/Stefan/Documents/Cloudstation/Krabbelstube/Kinderliste_Maerz_2020_simple.xls")
    plot_diagram(kinder_data)
    
