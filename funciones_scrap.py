#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import html
import urllib
import requests
import lxml.html
import BeautifulSoup
import pandas as pd 
import string
from pyvirtualdisplay import Display
import time
import datetime


def get_cookies(url):
    # coding: utf-8
    from selenium import webdriver
    #display = Display(visible=0, size=(800, 600))
    #display.start()
    driver = webdriver.PhantomJS()
    driver.get(url)
    cookies_list = driver.get_cookies()
    driver.quit()
    #display.stop()
    cookies=''
    for cookie in cookies_list:
        valor=cookie['value'].encode('utf-8')
        #print valor
        cookies=cookies+str(cookie['name']) +'='+valor+'; '

    return cookies[0:len(cookies)-2]
    

def scrap_day(day,cookies):
    
    #Lengueta: tdUno, saca por rol
    #Lengueta: tdDos, saca por dia
    #Lengueta: tdTres, saca por nombre
    
    url='http://civil.poderjudicial.cl/CIVILPORWEB/AtPublicoDAction.do?'    
    options = {
	'TIP_Consulta': 3,
	'TIP_Lengueta': "tdDos",
	'RUC_Tribunal': "3",
	'FEC_Desde': day,
	'FEC_Hasta': day,
	'SEL_Litigantes': 0,
	'COD_Tribunal': 259,
	'irAccionAtPublico': "Consulta",
	'cpMonth': 11,
	'cpYear': 2014
     }

    url_input=url+urllib.urlencode(options)
    head={'Cookie':cookies}
    dat=requests.get(url_input,headers=head)
    print url_input


def scrap_rut(rutnum,dv,cookies):
    dv=dv.upper()
    url='http://civil.poderjudicial.cl/CIVILPORWEB/AtPublicoDAction.do?'
    options = {
  'TIP_Consulta': 2,
  'TIP_Lengueta': "tdTres",
  'RUC_Tribunal': "3",
  'FEC_Desde': "20/11/2014",
  'FEC_Hasta': "20/11/2014",
  'SEL_Litigantes': 0,
  'irAccionAtPublico': "Consulta",
  'RUT_Consulta': rutnum,
  'RUT_DvConsulta': dv
  }
    url_input=url+urllib.urlencode(options)
    head={'Cookie':cookies}
    dat=requests.get(url_input,headers=head)
    return dat

def scrap_rol(rol,cod_tribunal,cookies):
    
    #Lengueta: tdUno, saca por rol
    #Lengueta: tdDos, saca por dia
    #Lengueta: tdTres, saca por nombre
    #Ingresar rol formato "C-1234-123"
    url='http://civil.poderjudicial.cl/CIVILPORWEB/AtPublicoDAction.do?'
    options = {
  'TIP_Consulta': 1,
  'TIP_Lengueta': "tdUno",
  'RUC_Tribunal': "3",
  'FEC_Desde': "20/11/2014",
  'FEC_Hasta': "20/11/2014",
  'SEL_Litigantes': 0,
  'irAccionAtPublico': "Consulta",
  'RUT_Consulta': '15959326',
  'RUT_DvConsulta': '6',
  'TIP_Causa':rol.split('-')[0],
  'ROL_Causa':rol.split('-')[1],
  'ERA_Causa':rol.split('-')[2],
  'COD_Tribunal': cod_tribunal
  }
     
    url_input=url+urllib.urlencode(options)
    head={'Cookie':cookies}
    dat=requests.get(url_input,headers=head)
    return dat

def get_links(dat):
    #Para una consulta al PJ CIVIL saca los links de las causas asociadas
    links=[]
    link_html=lxml.html.fromstring(dat.text)
    for link in link_html.xpath('//a/@href'): # select the url in href for all a tags(links)
        links.append('http://civil.poderjudicial.cl' + link)
    return links

def html_dat(dat):
            soup = BeautifulSoup.BeautifulSoup(dat.text)
            tablas = soup.findAll('table')
            return tablas
         
def extrae_id(link):
        info=link.split('&')[1:]
        n=len(info)
        id_causa={}
        for i in info[0:(n-1)]:
            id_causa[str(i.split('=')[0])]=str(i.split('=')[1])
        id_causa['link']=link
        return id_causa['CRR_IdCausa']
       
    
def extrae_lit(tablas):
        lit=[]
        for row in tablas[11].findAll('tr'):
            info={}    
            info['tipo']=str(row.findAll('td')[0].string).strip()
            info['rut']=str(row.findAll('td')[1].string).strip()
            info['persona']=str(row.findAll('td')[2].string).strip()
            info['nombre']=str(row.findAll('td')[3].string).strip()
            lit.append(info)
        return lit
        
def extrae_rut(tablas):
        lit=[]
        for row in tablas[11].findAll('tr'):  
            rut=str(row.findAll('td')[1].string).strip()
            lit.append(rut)
        return lit
    
def extrae_info(tablas):
    
            #!/usr/bin/env python
            # -*- coding: utf-8 -*-
            info={}    
            info['estado_adm']=str(tablas[2].findAll('tr')[1]).split('Est.Adm.:')[1].split('</')[0].strip().replace('<font color="red"><b>','')
            info['etapa']=str(tablas[2].findAll('tr')[2].findAll('td')[0].string).split(':')[1].strip()
            info['Tribunal']=str(tablas[2].findAll('tr')[3].findAll('td')[0].string).split(':')[1].strip()
            info['nombre']=str(tablas[2].findAll('tr')[0].findAll('td')[1].string).strip()
            info['proc']=str(tablas[2].findAll('tr')[1].findAll('td')[1].string).split(':')[1].strip()            
            info['Fecha_ing']=str(tablas[2].findAll('tr')[0].findAll('td')[2].string).split(':')[1].strip()            
            info['ubicacion']=str(tablas[2].findAll('tr')[1].findAll('td')[2].string).split(':')[1].strip()
            info['estado_proc']=str(tablas[2].findAll('tr')[2].findAll('td')[1].string).split(':')[1].strip()
            
            #PDF 
            if str(tablas[2]).find('Show')>0:
                l=tablas[2].findAll('tr')[3].findAll('td')[1]
                a='http://civil.poderjudicial.cl'+str(l).split('(')[1].split(')')[0].replace('amp;','').replace("'",'')
            else:
                a='Sin documento'
                
            info['texto_demanda']=a
            
            info['foja']=str(tablas[2].findAll('tr')[0].findAll('td')[0].string).split(':')[1].strip()
            
            return info

def extrae_hist(tablas):
            #!/usr/bin/env python
            # -*- coding: utf-8 -*-
            historia=[]
    
            
            for i in tablas[9].findAll('tr'):
                hist={}
                #hist['folio']=str(i.findAll('td')[0].string).strip()
                
                #documento
                a=i.findAll('td')[1]
                
                if str(a).find('Show')>0:            
                    hist['link_doc']='http://civil.poderjudicial.cl'+str(a).split('(')[1].split(')')[0].replace('amp;','').replace("'",'')
                else:
                    hist['link_doc']='Sin documento'
                
                
                hist['etapa']=str(i.findAll('td')[2].string).strip()
                hist['tramite']=str(i.findAll('td')[3].string).strip()
                hist['descripcion']=str(i.findAll('td')[4].string).strip()
                hist['fecha']=str(i.findAll('td')[5].string).strip()
                
                hist['foja']=str(i.findAll('td')[0].string).strip()
                
                historia.append(hist)
            return historia

def rut_scraper(rutnum,dv,cookies):
    
    tabla={}    
    
    dat_rut=scrap_rut(rutnum,dv,cookies)
    if dat_rut.status_code==200:
        
        links=get_links(dat_rut)
        n=len(links)

        if n>100:
            print "Demasiadas Causas: " + str(n-1) + " causas, solo las primeras 100 serán mostradas"
            n=100
        else:    
            print "El rut tiene: " + str(n-1) + " causas"
        if n>1:  
            for i in range(1,n):
                print i    
                tiempo=datetime.datetime.now()
                if tiempo.hour>=0 and tiempo.hour<7:
                    print "Sistema fuera de servicio"
                    break
                else:
                    
                    
                    try:
                        dat = requests.get(links[i])
                        if dat.status_code==200:
                
                            tablas=html_dat(dat)
                            
                            id_causa=extrae_id(links[i])
                            info=extrae_info(tablas)
                            rut_litigantes=extrae_rut(tablas)
                            litigantes=extrae_lit(tablas)
                            historia=extrae_hist(tablas)

                            
                            tabla[i]={'info':info,
                                             'rut_litigantes':rut_litigantes,
                                             'litigantes':litigantes,
                                             'historia':historia,
                                             'id_causa':id_causa
                                            }
                
                        else:
                            print 'Error:'+' '+str(dat.status_code)
                            error={'link':datos.link[i],'code':dat.status_code,'time':datetime.datetime.now()}
                            log.append(error)
                
                    except requests.exceptions.Timeout:
                        print 'Error: Time out'
                        error={'link':datos.link[i],'code':'Time Out','time':datetime.datetime.now()}
                        log.append(error)
                
                    except requests.exceptions.ConnectionError:
                        print 'Error: Conection Error'
                        error={'link':datos.link[i],'code':'Conection Error','time':datetime.datetime.now()}
                        log.append(error)        
        else:
            print "Rut sin causas"
    else:
        print 'Error RUT:'+' '+str(dat.status_code)
    
    
    n1=len(tabla)
    resumen=pd.DataFrame()
    if n1>0:
        for i in range(1,n1):
            dic_resumen={}
            n2=len(tabla[i]['litigantes'])
            for j in range(0,n2):
                if tabla[i]['litigantes'][j]['rut']==rutnum+'-'+dv:
                    dic_resumen['tipo']=tabla[i]['litigantes'][j]['tipo']
                if tabla[i]['litigantes'][j]['tipo']=='DTE.':
                    dic_resumen['dte']=tabla[i]['litigantes'][j]['nombre']
            dic_resumen['proceso']=tabla[i]['info']['proc']
            dic_resumen['estado']=tabla[i]['info']['estado_adm']
            dic_resumen['fecha']=tabla[i]['info']['Fecha_ing']
            resumen=resumen.append(dic_resumen,ignore_index=True)
                
    
    tabla['resumen']=resumen
    return tabla
