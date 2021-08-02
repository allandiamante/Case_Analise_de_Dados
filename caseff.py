#Imports
import requests
import pandas as pd
import numpy as np

from unicodedata import normalize
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

#Acessando dados do excel
df_agencias = pd.read_excel(r"dados em xlsx/202106AGENCIAS.xlsx", sheet_name="Plan1")
df_pae = pd.read_excel(r"dados em xlsx/202106PAE.xlsx", sheet_name="plan1")
df_postos = pd.read_excel(r"dados em xlsx/202106POSTOS.xlsx", sheet_name="Plan1")


#Funções para arrumar apopulacao e criar TAG, auxiliando no merge de tabelas.
def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

def cria_tag(tag):
    return remover_acentos(tag.replace(")",'').replace("BRASILIA(",'').replace(' ','').replace("'",'').replace("-",'').upper())

def cria_lista_tag(coluna):
    list_cria_tag = []
    for linha in coluna:
        list_cria_tag.append(cria_tag(linha))
    return list_cria_tag

def arruma_populacao(coluna_pop):
    arruma_pop = []
    for linha in coluna_pop:
        arruma_pop.append(int(linha.replace('\xa0','')))
    return arruma_pop

def retirar_estado(df_filtrado_idhm):    
    list_estados=[]
    list_municipios=[]
    for i in df_filtrado_idhm['municipio']:
        list_estados.append(i[-3:-1])
        list_municipios.append(i[:-5])
 
    return list_estados,list_municipios

#Filtrando dados

df_agencias_filtrado = pd.DataFrame({'municipio' :cria_lista_tag(df_agencias['MUNICíPIO                                                   ']),
                               'estado': df_agencias['UF']})
df_postos_filtrado = pd.DataFrame({'municipio' :cria_lista_tag(df_postos['MUNICIPIO                                                   ']),
                               'estado': df_postos['UF']})
df_pae_filtrado = pd.DataFrame({'municipio' :cria_lista_tag(df_pae['MUNICIPIO                                                   ']),
                               'estado': df_pae['UF']})
df_total_nivel_bancario = pd.DataFrame({'qnt_agencias' : df_agencias_filtrado['municipio'],
                                       'qnt_postos' : df_postos_filtrado['municipio'],
                                       'qnt_pae' : df_pae_filtrado['municipio']})

#Acessando dados via web
option = Options()
option.headless = True
driver = webdriver.Firefox(options=option)

#Acessando conteudo via web
#Conteudo dos celulares
url = "https://www.teleco.com.br/nceluf.asp"
driver.get(url)
conteudo_celular = driver.find_element_by_id('conteudo_interna')
element = conteudo_celular.find_elements_by_tag_name('table')[2]
html_content_celular = element.get_attribute('outerHTML')
soup = BeautifulSoup(html_content_celular, 'html.parser')
tabela_cel = soup.find(name='table')
df_full_celular = pd.read_html(str(tabela_cel))[0]

#Conteudo dos idhm dos municipios
url2 = 'https://www.br.undp.org/content/brazil/pt/home/idh0/rankings/idhm-municipios-2010.html'
driver.get(url2)
conteudo_idhm = driver.find_element_by_class_name('tableizer-table')
html_content_idhm = conteudo_idhm.get_attribute('outerHTML')
soup = BeautifulSoup(html_content_idhm, 'html.parser')
tabela_idhm = soup.find(name='table')
df_full_idhm = pd.read_html(str(tabela_idhm))[0]

#Conteudo dos população dos municipios
url3 = "https://pt.wikipedia.org/wiki/Lista_de_municípios_do_Brasil_por_população_(2020)"
driver.get(url3)
conteudo_ibge = driver.find_element_by_class_name("wikitable")
html_content_ibge = conteudo_ibge.get_attribute('outerHTML')
soup = BeautifulSoup(html_content_ibge, 'html.parser')
tabela_ibge = soup.find(name='table')
df_full_ibge = pd.read_html(str(tabela_ibge))[0]


#Filtrando colunas
df_filtrado_celular = pd.DataFrame({'estado' :df_full_celular['Estado']['Estado'].tolist(),
                     'estado_populacao' :df_full_celular['Dez 2020  (milhares)']['Dez 2020  (milhares)'].tolist(),
                     'cel' :df_full_celular['Maio de 2021']['Nº Cel.'].tolist(),
                     'pre_pago' :df_full_celular['Maio de 2021']['Pré  Pagos'].tolist(),
                    'densidade' :df_full_celular['Maio de 2021']['Dens*'].tolist(),
                            
                    })[0:27]
df_filtrado_idhm = pd.DataFrame({'municipio' :df_full_idhm['Município'],
                     'idhm' :df_full_idhm['IDHM 2010'],
                                })
df_ibge_filtrado = pd.DataFrame({'tag': cria_lista_tag(df_full_ibge['Município']),
                                'municipio' :df_full_ibge['Município'],
                                 'estado': df_full_ibge['Unidade federativa'],
                                'pop_municipio': arruma_populacao(df_full_ibge['População'])
                                
                                })


#Corrigindo celulas

df_filtrado_celular.at[4,'estado_populacao'] = df_filtrado_celular['estado_populacao'][4]/1000
df_filtrado_celular.at[6,'estado_populacao'] = df_filtrado_celular['estado_populacao'][6]/1000
df_filtrado_celular.at[25,'estado_populacao'] = df_filtrado_celular['estado_populacao'][25]/1000
df_filtrado_celular.at[4,'cel'] = df_filtrado_celular['cel'][4]/1000
df_filtrado_celular.at[6,'cel'] = df_filtrado_celular['cel'][6]/1000
df_filtrado_celular.at[25,'cel'] = df_filtrado_celular['cel'][25]/1000
df_filtrado_celular.at[4,'pre_pago'] = df_filtrado_celular['pre_pago'][4]/1000
df_filtrado_celular.at[6,'pre_pago'] = df_filtrado_celular['pre_pago'][6]/1000
df_filtrado_celular.at[23,'pre_pago'] = df_filtrado_celular['pre_pago'][23]/1000
df_filtrado_celular.at[25,'pre_pago'] = df_filtrado_celular['pre_pago'][25]/1000

df_filtrado_celular.at[0,'estado'] = 'RJ'
df_filtrado_celular.at[1,'estado'] = 'ES'
df_filtrado_celular.at[2,'estado'] = 'MG'
df_filtrado_celular.at[3,'estado'] = 'AM'
df_filtrado_celular.at[4,'estado'] = 'RR'
df_filtrado_celular.at[5,'estado'] = 'PA'
df_filtrado_celular.at[6,'estado'] = 'AP'
df_filtrado_celular.at[7,'estado'] = 'MA'
df_filtrado_celular.at[8,'estado'] = 'BA'
df_filtrado_celular.at[9,'estado'] = 'SE'
df_filtrado_celular.at[10,'estado'] = 'PI'
df_filtrado_celular.at[11,'estado'] = 'CE'
df_filtrado_celular.at[12,'estado'] = 'RN'
df_filtrado_celular.at[13,'estado'] = 'PB'
df_filtrado_celular.at[14,'estado'] = 'PE'
df_filtrado_celular.at[15,'estado'] = 'AL'
df_filtrado_celular.at[16,'estado'] = 'PR'
df_filtrado_celular.at[17,'estado'] = 'SC'
df_filtrado_celular.at[18,'estado'] = 'RS'
df_filtrado_celular.at[19,'estado'] = 'MS'
df_filtrado_celular.at[20,'estado'] = 'MT'
df_filtrado_celular.at[21,'estado'] = 'GO'
df_filtrado_celular.at[22,'estado'] = 'DF'
df_filtrado_celular.at[23,'estado'] = 'TO'
df_filtrado_celular.at[24,'estado'] = 'RO'
df_filtrado_celular.at[25,'estado'] = 'AC'
df_filtrado_celular.at[26,'estado'] = 'SP'

driver.quit()

#Operações para criação de nova colunas relevantes
df_filtrado_celular = pd.DataFrame({'estado' :df_filtrado_celular['estado'],
                     'estado_populacao' :df_filtrado_celular['estado_populacao'],
                     'cel' :df_filtrado_celular['cel'],
                     'pos_pago' : df_filtrado_celular['cel' ] - df_filtrado_celular['pre_pago'],
                     'densidade' :df_filtrado_celular['densidade']
                    })
list_estados, list_municipios = retirar_estado(df_filtrado_idhm)
df_filtrado_idhm = pd.DataFrame({'municipio' :list_municipios,
                     'estado' :list_estados,
                     'idhm' :df_full_idhm['IDHM 2010'],                                 
                                })

#Função de nivel de bancarização.
def calcular_nivel_bancarizacao(df_ibge_filtrado,df_total_nivel_bancario):    
    list_nb=[]
    for i in range(len(df_ibge_filtrado['tag'])):
        list_nb.append((sum(df_ibge_filtrado['tag'][i] == df_total_nivel_bancario['qnt_agencias'])
        + sum(df_ibge_filtrado['tag'][i] == df_total_nivel_bancario['qnt_postos'])
        + sum(df_ibge_filtrado['tag'][i] == df_total_nivel_bancario['qnt_pae']))/df_ibge_filtrado['pop_municipio'][i]) 
    return list_nb

#Criando tabela que contem os niveis como coluna.
list_nb = calcular_nivel_bancarizacao(df_ibge_filtrado,df_total_nivel_bancario)
df_nb = pd.DataFrame({'tag': df_ibge_filtrado['tag'],
                        'municipio' :df_ibge_filtrado['municipio'],
                        'estado' :df_ibge_filtrado['estado'],
                        'pop_municipio': df_ibge_filtrado['pop_municipio'],
                        'nivel_bancarizacao': list_nb})

#Merge das tabelas


merge_idhm_celular = pd.merge(df_filtrado_idhm, df_filtrado_celular, how = 'inner', on = 'estado')
list_cria_tag =  cria_lista_tag(merge_idhm_celular['municipio'])
merge_idhm_celular.insert(0,"tag", list_cria_tag)
df_nb_2 = pd.DataFrame({'tag': df_ibge_filtrado['tag'],
                        'pop_municipio': df_ibge_filtrado['pop_municipio'],
                        'nivel_bancarizacao': list_nb})   

#Segundo merge juntando o nivel_bancarizacao
merge_idhm_celular_2 = pd.merge(merge_idhm_celular, df_nb_2, how = 'inner', on = 'tag')

#Função para criar os cps
def cp_municipal(pop_municipios):
    list_cp = []
    cp= {5000 : 5, 20000: 10, 100000: 15, 500000 : 20 , 99999999: 25}
    for pop_municipio in pop_municipios:
        i=1
        for valor in cp:            
            if(pop_municipio <= valor):
                list_cp.append(i*5)
                break;
            i=i+1
    return list_cp

#Criando CP para os respectivos municipios
list_cria_cp = cp_municipal(merge_idhm_celular_2['pop_municipio'])
merge_idhm_celular_2.insert(1,"cp", list_cria_cp)


#Função para gerar numero de clientes convertidos
#((idhm ^ cp) * ( (população do municipio / % densidade de cel por habitante do estado) * (pos_pago_estado / cel_estado) ) * 100)

def cria_lista_final(lista_semifinal):
    list_pc_final = []
    list_convertido = []
    for i in range(len(lista_semifinal)):        
        #Função que retorna pc e convertido por municipio
        pc = ((merge_idhm_celular_2.loc[i]['idhm']/1000)**merge_idhm_celular_2.loc[i]['cp']) * (((merge_idhm_celular_2.loc[i]['pop_municipio']/(merge_idhm_celular_2.loc[i]['densidade']/10000)*(merge_idhm_celular_2.loc[i]['pos_pago'] / merge_idhm_celular_2.loc[i]['cel']))/(merge_idhm_celular_2.loc[i]['pop_municipio']))/1.5) * 100
        list_pc_final.append(pc)
        list_convertido.append((pc/100)*merge_idhm_celular_2.loc[i]['pop_municipio'])
    return list_pc_final, list_convertido
    
lista_pc, list_convertido = cria_lista_final(merge_idhm_celular_2)    
merge_idhm_celular_2.insert(1,"pc", lista_pc)
merge_idhm_celular_2.insert(2,"convertidos", list_convertido)
merge_idhm_celular_2 = merge_idhm_celular_2.sort_values(by=['convertidos'], ascending=False)

#Entrega Final Tabela e Lista
resultado_final_tabela = pd.DataFrame({'Nome da Cidade': merge_idhm_celular_2['municipio'],
                        'Estado': merge_idhm_celular_2['estado'],
                        'População': merge_idhm_celular_2['pop_municipio'],     
                        'Nível de bancarizacao': merge_idhm_celular_2['nivel_bancarizacao'],
                        'Clientes Convertidos': merge_idhm_celular_2['convertidos']
                               })   
resultado_final_lista = [resultado_final_tabela.values.tolist()]

print(resultado_final_lista[0][0])