import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import translators as ts
from bs4 import BeautifulSoup
import requests
import folium
import streamlit as st
import geopy
import statistics


with st.echo(code_location='below'):
    list_of_antidepressants=['Agomelatine','Nortriptyline','Amitriptyline','Vortioxetine','Escitalopram','Citalopram','Clomipramine','Duloxetine','Venlafaxine','Dosulepin','Doxepine','Reboxetine','Fluvoxamine','Fluoxetine','Imipramine','Isocarboxazid','Lofepramine','Sertraline','Moclobemide','Mianserin','Mirtazapine','Moclobemide','Trazodone','Phenelzine','Tranylcypromine','Paroxetine','Doxepin','Trimipramin']
    df_anti = pd.read_csv('Funny.csv')
    df_anti=df_anti.drop(columns=['Unnamed: 0','Practice','BNF Chapter','BNF Section','BNF Paragraph','BNF Sub-Paragraph','Unnamed: 17','Unnamed: 18'])
    types_of_antidepressants={'Agomelatine':'AA','Vortioxetin':'AA','Mianserin':'AA', 'Nortriptyline':'TCA','Amitriptyline':'TCA','Clomipramine':'TCA', 'Dosulepin':'TCA', 'Doxepine':'TCA', 'Imipramine':'TCA', 'Lofepramine':'TCA', 'Mirtazapine':'TCA', 'Trimipramin':'TCA','Escitalopram':'SSRI', 'Citalopram':'SSRI', 'Fluvoxamine':'SSRI', 'Fluoxetine':'SSRI', 'Sertraline':'SSRI', 'Paroxetine':'SSRI','Duloxetine':'SSNRI','Venlafaxine':'SNRI','Reboxetine':'NRI','Isocarboxazid':'MAOI', 'Moclobemide':'MAOI', 'Phenelzine':'MAOI', 'Tranylcypromine':'MAOI','Trazodone':'SARI'}
    df_anti['Antidepressant Type']=df_anti['VTM_NM'].map(types_of_antidepressants)
    series_stack=df_anti.groupby(['Year','Antidepressant Type'])['Antidepressant Type'].count().divide(df_anti.groupby(['Year','Antidepressant Type'])['Antidepressant Type'].count().sum(level='Year'))
    df_share=series_stack.to_frame().rename(columns={'Antidepressant Type':'Share'}).reset_index().pivot_table(values='Share',columns='Antidepressant Type',index='Year',aggfunc='first')

    df_share1=series_stack.to_frame().rename(columns={'Antidepressant Type':'Share'}).reset_index().pivot_table(values='Share',columns='Antidepressant Type',index='Year',aggfunc='first')
    df_share1.loc['Change between 2013-2019']=(((df_share.loc[2019]-df_share.loc[2013])/df_share.loc[2013])).apply(lambda x: f"{x:.0%}")
    df_share1.loc['Change between 2013-2019']=df_share1.loc['Change between 2013-2019'].str.rstrip('%').astype('float') / 100.0
    
    st.title("GPs Prescribing Antidepressants in Northern Ireland")
    st.caption("About Dataset: Датасет содержит информацию о всех рецептах, выданных врачами Северной Ирландии с 2013 по 2019 г. - из них выбраны те, что содержат лекарства из группы антидепрессантов, указанных в реестре Великобритании")        
    st.header("Types of Antidepressants")
    st.caption("AA - Atypical Antidepressants - Those that act in a manner that is different from any other types of antidepressants. Reserved for patients who do not respond to other medicine")
    st.caption("MAOIs - Monoamine oxidase inhibitors - MAOI is an older type of antidepressant that is rarely used nowadays. Comes with dietary restrictions because of the elevated tyramine levels in the blood")
    st.caption("NRI - Norepinephrine reuptake inhibitor - Contarary to the name, more widely used as a treatment to ADHD and Narcolepsy than to depression for their effect was proven to be indistinguishable from placebo")
    st.caption("SARIs - Serotonin antagonists and reuptake inhibitors")
    st.caption("SNRI - Serotonin-noradrenaline reuptake inhibitors - Were designed to be more potent in treating Major Depressive Disorder than their SSRI predecessors, though the evidence on that is uncertain")
    st.caption("SSRI - Serotonin-noradrenaline reuptake inhibitors - Most widely prescribed ones for the side effects vary from none to moderate")
    st.caption("TCAs - Tricyclic antidepressants - Used to treat BPD and OCD, as well as MAD")
    

    from matplotlib.pyplot import figure
    sns.set_theme()
    fig_1, (ax1,ax2)=plt.subplots(1, 2,figsize=(25,10))
    ax1.stackplot(df_share.index,df_share['AA'],df_share['MAOI'],df_share['NRI'],df_share['SARI'],df_share['SNRI'],df_share['SSNRI'],df_share['SSRI'],df_share['TCA'],labels=df_share.columns,colors=['steelblue','rosybrown', 'maroon', 'darkolivegreen', 'indigo','tan','slateblue','brown'])
    ax1.margins(0,0)
    ax1.legend(loc='upper left',prop={'size': 20})
    ax1.set_title('Proportion of prescriptions by antidepressant type',fontsize=20)
    ax1.set_xlabel('Year', fontsize = 17)
    ax1.set_ylabel('Proportion', fontsize = 17)
    sns.barplot(x=df_share1.columns, y=df_share1.loc['Change between 2013-2019'],palette=['steelblue','rosybrown', 'maroon', 'darkolivegreen', 'indigo','tan','slateblue','brown'])
    ax2.set_title('Change in the amount of presciptions',fontsize=20)
    ax2.set_xlabel('Antidepressant Type', fontsize = 17)
    ax2.set_ylabel('Change Between 2013-2019', fontsize = 17)
    st.pyplot(fig_1)
    st.caption("SNRIs are getting more popular as far as GPs prescription choice goes, the older ones such as MAOIs and TCAs are being substituted for ones that cause lsee concern on the matter of side effects") 
    

    df_anti['Actual Cost (£)'] = df_anti['Actual Cost (£)'].astype('str').str.replace(',','')
    df_anti['Actual Cost (£)'] = pd.to_numeric(df_anti['Actual Cost (£)'])
    df_anti['Total Quantity'] = df_anti['Total Quantity'].astype(str).str.replace(',','')
    df_anti['Total Quantity']=pd.to_numeric(df_anti['Total Quantity'])
    df_anti['Price per Tablet']=df_anti['Actual Cost (£)'].divide(df_anti['Total Quantity'])
    series_per_tablet=df_anti.groupby(['VTM_NM','Year'])['Price per Tablet'].mean()
    df_tablet=series_per_tablet.to_frame().reset_index().pivot_table(columns='VTM_NM',index='Year',aggfunc='first')
    df_tablet.columns=df_tablet.columns.droplevel()
    df_tablet=df_tablet.drop(columns=['-','Amitriptyline + Perphenazine'])
    df_tablet.loc['Average cost per tablet 2013-2019']=df_tablet.mean(axis=0)

    series_count=df_anti.groupby(['VTM_NM','Year'])['VTM_NM'].count()
    df_type_count=series_count.to_frame().rename(columns={'VTM_NM':'Amount of prescriptions'}).reset_index().pivot_table(columns='VTM_NM',index='Year',aggfunc='first')
    df_type_count.columns=df_type_count.columns.droplevel()
    df_type_count=df_type_count.drop(columns=['-','Amitriptyline + Perphenazine'])
    df_type_count.loc['Average amount of prescriptions']=df_type_count.mean(axis=0)
    clinical_eff={'Agomelatine':0.84, 'Amitriptyline':2.13, 'Citalopram':1.52, 'Clomipramine':1.49, 'Dosulepin':None, 'Doxepin':None, 'Duloxetine':1.85,'Escitalopram':1.68,'Fluoxetine':None,'Fluvoxamine':1.69,'Imipramine':None,'Isocarboxazid':None,'Lofepramine':None,'Mianserin':None,'Mirtazapine':1.89,'Moclobemide':None,'Nortriptyline':None,'Paroxetine':1.75,'Phenelzine':None,'Reboxetine':1.37,'Sertraline':1.67,'Tranylcypromine':None,'Trazodone':1.51,'Venlafaxine':None,'Vortioxetine':None}
    df_eff=pd.DataFrame(clinical_eff, index=['clinical eff',])
    df_t=df_eff.dropna(axis=1).append(df_type_count.loc['Average amount of prescriptions'])
    df_t=df_t.dropna(axis=1)

    fig_2,ax =plt.subplots(1,2,figsize=(15,7))
    sns.regplot(x=df_type_count.loc['Average amount of prescriptions'],y=df_tablet.loc['Average cost per tablet 2013-2019'],ax=ax[0])
    sns.regplot(x=df_t.loc['Average amount of prescriptions'],y=df_t.loc['clinical eff'],ax=ax[1])
    plt.ylabel('Clinical Efficacy')
    st.pyplot(fig_2)
    
    st.caption("Do GP's choices abide to the intuitive criterion? The more expensive the drug is the less amount of prescriptions are being made. Though the interconnection being present, it is still moderate for the effectiveness usually negates the expenses")
    st.caption("The interconnection between clinical efficacy, assigned to each drug over the course of 2018 Lancet's investigation, and number of yearly prescriptions is much more prominent")   

    import translators as ts
    ru_list=[]
    for i in list_of_antidepressants:
        ru_list.append(ts.google(i, from_language='en', to_language='ru'))
    ru_list[3]='Вортиоксетин'
    ru_list[10]='Доксепин'
    ru_list[11]='Ребоксетин'
    ru_list[24]='Транилципромин'
    ru_list[26]='Доксепин'

    df_rub=pd.read_csv('Rub Prices.csv')
    df_rub.drop(columns=['Unnamed: 0'])
    df_rub=df_rub.rename(index={0: 'Price on Russian Market'}).drop(columns=['Unnamed: 0'])
    df_rub=df_rub.rename(columns={'Агомелатин':'Agomelatine','Амитриптилин':'Amitriptyline','Вортиоксетин':'Vortioxetine','Эсциталопрам':'Escitalopram','Циталопрам':'Citalopram','Кломипрамин':'Clomipramine','Дулоксетин':'Duloxetine','Венлафаксин':'Venlafaxine','Ребоксетин':'Reboxetine','Флувоксамин':'Fluvoxamine', 'Флуоксетин':'Fluoxetine','Сертралин':'Sertraline','Миразапин':'Mirtazapine','Тразодон':'Trazodone','Пароксетин':'Paroxetine'})
    df_ri=df_rub.append(df_tablet.loc['Average cost per tablet 2013-2019']).dropna(axis=1)
    
    st.header("Is drug pricing in Russia and the UK consistent?")   
    st.caption("Let us scrape over the https://aptekamos.ru website in search of an average market for each drug in question") 
    fig_3, ax = plt.subplots()
    sns.regplot(x=df_ri.loc['Price on Russian Market'],y=df_ri.loc['Average cost per tablet 2013-2019'],ax=ax)
    st.pyplot(fig_3)
    
    st.caption("Mostly, yes. Though there are drugs that fall out of the confidence interval - Mirtazapine and Agomelatine") 

    df_sp=df_ri.append([df_t.loc['Average amount of prescriptions'],df_t.loc['clinical eff']]).dropna(axis=1).transpose().reset_index()
    df_sp['Antidepressant Type']=df_sp['index'].map(types_of_antidepressants)
    df_spider=df_sp.groupby(['Antidepressant Type']).mean().rename(columns={'clinical eff':'Clinical efficacy'}).reset_index()
    df_spider['Price on Russian Market']=df_spider['Price on Russian Market']/(df_spider.loc[3]['Price on Russian Market']/df_spider.loc[3]['Clinical efficacy'])
    df_spider['Average cost per tablet 2013-2019']=df_spider['Average cost per tablet 2013-2019']/(df_spider.loc[3]['Average cost per tablet 2013-2019']/df_spider.loc[3]['Clinical efficacy'])
    df_spider['Average amount of prescriptions']=df_spider['Average amount of prescriptions']/(df_spider.loc[3]['Average amount of prescriptions']/df_spider.loc[3]['Clinical efficacy'])
    
    st.header("Grading Antidepressant Types")           

    ##https://www.python-graph-gallery.com/391-radar-chart-with-several-individuals
    import numpy as np
    from numpy import pi
    categories=list(df_spider)[1:]
    N = len(categories)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    fig_4 = plt.figure(figsize=(8,8))
    ax = fig_4.add_subplot(111, polar=True)
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    plt.xticks(angles[:-1], categories)
    for i in range(5):
        values=df_spider.loc[i].drop('Antidepressant Type').values.flatten().tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=df_spider.loc[i]['Antidepressant Type'])
        ax.fill(angles, values, 'b', alpha=0.1)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    ax.tick_params(pad=70)
    st.pyplot(fig_4)
    st.caption("AAs being the most expensive ones, fail to deliver)
    st.caption("SSRIs are the run for the buck")
    st.caption("SSNRIs are dominating the market in terms of clinical efficacy, though, the evidence is flawed due to sample size being too small")  
           
    
 
    st.header("Your loved one is quite ill and suddenly disappears... Isn't it a chance for a road trip?")
    st.caption("Beneath is a route that one could possibly take in order to find a runaway - places that are known to be suicide cites")
    st.caption("Each next point is less remote from the nearest hospital than the previous one - criterion that runaway would have possibly regarded by the time he would disappear")
    st.caption("Starting Point: Archway Bridge")
    list_of_places=['Archway Bridge','Beachy Head','Cliffs of Moher','Clifton Suspension Bridge','Erskine Bridge','Forth Road Bridge','Foyle Bridge','Humber Bridge','Southerndown']
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="email@email.com")
    suicide_dict={}
    for i in list_of_places:
        location = geolocator.geocode(i)
        suicide_dict[i]=[location.latitude, location.longitude]
    suicide_hosp={'Archway Bridge':[51.56631088256836,-0.13862299919128418], 'Beachy Head':[50.78633499145508,0.2701840102672577],'Cliffs of Moher':[52.93609619140625,-9.315892219543457],'Clifton Suspension Bridge':[51.45405960083008,-2.615722417831421],'Erskine Bridge':[55.906349182128906,-4.426041603088379],'Forth Road Bridge':[55.974971,-3.587282],'Foyle Bridge':[52.676846,-7.2701426],'Humber Bridge':[53.739253997802734,-0.4501054497987309],'Southerndown':[51.51763153076172,-3.571686029434204]}
    dist_dict={}
    for i in suicide_dict:
        dist_dict[i]=(suicide_hosp[i][0]-suicide_dict[i][0])**2+(suicide_hosp[i][1]-suicide_dict[i][1])**2
    dist_dict={k: v for k, v in sorted(dist_dict.items(), key=lambda item: item[1])}
    ###https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    sorted_routes=[]
    for i in dist_dict:
        sorted_routes.append(suicide_dict[i])
    from branca.utilities import split_six
    state_geo = 'http://geoportal1-ons.opendata.arcgis.com/datasets/01fd6b2d7600446d8af768005992f76a_4.geojson'

    from streamlit_folium import folium_static
    m = folium.Map(location=[55, 4], zoom_start=5)
    for i in suicide_dict:
        folium.Marker(location=[suicide_dict[i][0], suicide_dict[i][1]], fill_color='#43d9de', radius=8 ).add_child(folium.Popup(i)).add_to(m)
        folium.PolyLine(sorted_routes, color="red", weight=5, opacity=1).add_to(m)
    folium_static(m)







