import threading
import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
import argparse
from time import *
import random
import re
import os
from colorama import *
import pikepdf
import csv
from prettytable import PrettyTable,ALL
import zipfile
from PIL import Image,UnidentifiedImageError
from PIL.ExifTags import TAGS


###############################################  Parsing public proxies ################################################
def proxy_with_hidemy():
    return [r.get_text(':').split(' ')[0][:-1] for r in BeautifulSoup(requests.get('https://hidemy.name/ru/proxy-list/',headers={'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}).text,'html.parser').find('tbody')]
def proxy_with_fixtools():
    return [str(s['ip'])+':'+str(s['port']) for s in requests.get('http://api.foxtools.ru/v2/Proxy',params={'limit':'20'}).json()['response']['items']]
###############################################  Functions for uploading files ##############################################
#Downloads a file
def download(url):
    """Downloads a file"""
    return requests.get(url,stream=True,headers=header).content

#Путь для сохранения файлов
def path_to_save(argument):
    """Creates subfolders in the specified folder"""
    def create_folder(path):
        try:
            os.makedirs(path)    
        except FileExistsError:
            pass#os.makedirs(os.path.join(os.path.abspath(args.out)+'---'+strftime('%d_%B-%H_%M',strptime(ctime())),docs))
    if args.domain!=None:     
        for argdomain in args.domain:
            for docs in args.filetype: #Translates arguments into a list and creates folders
                path=os.path.join(args.output,argdomain+os.sep+docs) 
                create_folder(path)
            return path
    else: #If the domain is not specified, for example, downloading after an error
        path_from_link=os.path.join(args.output,argument.split('://')[-1].split('/')[0]) #Pulls the domain from the link and creates a folder with the domain name
        path2=os.path.join(path_from_link,argument.replace('\n','').split('/')[-1].split('.')[-1].strip()) #create subfolders
        create_folder(path2)
        return path2

#filename
def name(url):
    '''Defines the file name'''
    name=requests.utils.unquote(url).split('/')[-1]
    if '&' in name or '=' in name:
        name=''.join([f for f in name.split('&') if '.' in f]).split('\\')[-1]
    if '%' in name:
        name=name.replace(name.split('.')[0],'not_decoded')
    return name
#creating a file
def create_file(x):
    '''Downloads files'''
    with open(path_to_save(x)+os.sep+name(x),'wb')as document:#Divides the file name for example 1.doc by point and takes the last value,name(x).split('.')[-1]
        document.write(download(x))
        #for chunk in  download(x):
           # document.write(chunk)
    print(Fore.GREEN+'[+] '+str(requests.utils.unquote(x)).ljust(80),'downloading'+Style.RESET_ALL)

#########################################################  Google Parser  ########################################################

#sending a request and receiving html text
def collection_page(url):
    '''Sends a request to the specified url and returns the html code of the page'''
    try:
        
        if args._tor==True:
            print(Fore.YELLOW+'[+] Please wait.There is a connection to the TOR nodes...'+Style.RESET_ALL)
            while True:
                r=requests.get(url,headers=header,proxies={'http':'socks5://127.0.0.1:9050','https':'socks5://127.0.0.1:9050'})
                if r.status_code==200:
                    print(Fore.GREEN+'[+] '+url+'\t:\t'+str(r.status_code)+Style.RESET_ALL)
                    return r.text
                else:
                    print(Fore.RED+'[!] '+url+'\t:\t'+str(r.status_code)+Style.RESET_ALL)
                sleep(5)
        elif args._proxy!=None:#the fastest option for parsing, but you need a lot of proxy servers.A new random proxy address is taken from the file for each request
            def open_file_with_proxy(path):
                '''Reads a file with proxy servers'''
                try:
                    with open(path,'r') as proxy_file: #http://user@user10.0.0.1:3128,https://user@useer10.0.0.1:3128 
                        u = random.choice(proxy_file.readlines()).split(',')
                        proxy_proxy={u[0].split('://')[0]:u[0],u[1].split('://')[0]:u[1]}
                        return proxy_proxy
                except FileNotFoundError as not_found:
                    print(not_found)
            try:
                r=requests.get(url,headers=header,proxies=open_file_with_proxy(args._proxy),cookies=res)
                if r.status_code==200:
                    print(Fore.GREEN+'[+] '+url+'\t:\t'+str(r.status_code)+Style.RESET_ALL)
                    return r.text
                else:
                    print(Fore.RED+'[!] '+url+'\t:\t'+str(r.status_code)+Style.RESET_ALL)
            except:print(Fore.RED+'[!] Error.Check the proxy!'+Style.RESET_ALL)
            
        else:
            r=requests.get(url,headers=header,cookies=res)
            print(Fore.GREEN+'[+] '+url+'\t:\t'+str(r.status_code)+Style.RESET_ALL)
            sleep(random.uniform(args.wait,args.wait+10))
            if r.status_code==200:
                return r.text
            else:
                print(Fore.RED+'[!] CAPTCHA!!! I"m starting to parse through public proxies...'+Style.RESET_ALL)
                proxy_list=proxy_with_hidemy()+proxy_with_fixtools()
                while True:
                    try:
                        random_proxy=random.choice(proxy_list)
                        r=requests.get(url,headers=header,verify=False,proxies={'http':'http://'+random_proxy,'https':'https://'+random_proxy,'http':'socks5://'+random_proxy,'https':'socks5://'+random_proxy})
                        if r.status_code==200:
                            print(Fore.GREEN+'[+] '+url+'\t:\t'+str(r.status_code)+Style.RESET_ALL)
                            return r.text
                        else:
                            print(Fore.RED+'[!] The proxy is not valid'+Style.RESET_ALL)
                    except KeyboardInterrupt:
                        break
                    except ConnectionError:
                        pass
                
    except ConnectionError as error_connect:
        print(error_connect)
def parse_index_of(text):
    '''It goes through all the pages of Google's output, collecting links to documents in the index of folder'''
    if content_not_found(text)==True:
        print(Fore.GREEN+'[!] Found an open directory "Index of"! '+Style.RESET_ALL)
        for a in BeautifulSoup(text,'html.parser').find_all('a'):    
            try:
                href_attribute=a.get('href')  #Search for links that match the condition
                if args.domain in href_attribute  and href_attribute.startswith('http') and 'google' not in href_attribute:
                    m=href_attribute.rsplit('/',href_attribute.count('/')-3)[0] #Shortens the link to start searching from the root of directories
                    if m not in index_link: 
                        index_link.append(m) 
            except TypeError:
                pass
    else:print(Fore.YELLOW+'[!] No open directories found! '+Style.RESET_ALL)
    return index_link


def parsing_documents_on_index_of(url:str):
    ''' Recursive search of directories and documents in index of '''
    try:
        #return [url+'/'+k if k.endswith(file_extensions) else parsing_documents_on_index_of(url+'/'+k) for k in [datas for datas in [f.get('href') for f in BeautifulSoup(requests.get(url).text,'lxml').find('pre').find_all('a')] if '?' not in datas][1:]]
        soup=BeautifulSoup(collection_page(url),'html.parser')
        for z in [url+'/'+ttt for ttt in [kk.get('href') for kk in soup.find_all('a')] if '?' not in ttt and ttt!='/'  and ttt.endswith(file_extensions)]:
            threading.Thread(target=create_file,args=(z,)).start()
        [parsing_documents_on_index_of(url+'/'+xl) for xl in [ttt1 for ttt1 in [zn.get('href') for zn in soup.find_all('a')] if '?' not in ttt1 and ttt1!='/' and '/' in ttt1][1:]]
    except AttributeError:
        print('[!] By the link : '+url+' documents not found')

#parsing the resulting html page, selecting links to pages from there and checking for hidden results

def search_links_for_pages(text):
    '''Searches for links to a hidden page or the next page'''
    soup=BeautifulSoup(text,'html.parser')
    get_links_for_documents_from_url(text)
    try:
        pages=soup.find(href=re.compile('start')) 
        return 'https://www.google.com'+pages.get('href')
    except AttributeError:
         #Goes to the hidden page and takes a link to the next page from there
        try:
            filter_get=soup.find(href=re.compile('filter')).get('href')
            if 'google' not in filter_get:
                return 'https://www.google.com'+filter_get
                #return search_links_for_pages(collection_page(''+soup.find(href=re.compile('filter')).get('href')))             
        except AttributeError:
            pass

def get_links_for_documents_from_url(url):
    '''Gets links to files'''
    soup2=BeautifulSoup(url,'html.parser')
    for r in soup2.find_all('a'):
        try:
            if 'google' not in r.get('href') and r.get('href').startswith('http'):
                if r.get('href') not in links_for_docs:
                    links_for_docs.append(r.get('href'))
        except TypeError:
            pass


def content_not_found(result):
    """If there are no links to documents or pages.Then it looks for the li tag, which describes the recommendations.
    Retrieves all li tags from the page, sorting the contents in them, removing duplicate ones.Next, the length of the resulting set(set()) is compared
    with the number of recommendations (there are 4) and if the length is less than four, it returns True, which means that there are no recommendations (documents or link found) and you can parse"""
    if len(set([f.text for f in BeautifulSoup(result,'html.parser').find_all('li')][2:]))<4:
        return True
    else:return False

def user_break(text):
    with open('log_'+' '.join(ctime().replace(':','_').split(' ')[1:])+'.txt','w',encoding='utf-8') as error_file:
        try:
            error_file.write(text)
        except TypeError:
            try:
                error_file.write('\n'.join(text))
            except TypeError:
                error_file.write(str(text))
################################################   Parsing command line arguments   ###############################################
def type_arguments():
    '''Generates links for parsing based on arguments'''
    #Если список доменов и список типов файлов
    for dom in args.domain:
        for typef in args.filetype:
            yield f"https://www.google.com/search?q=site%3A{dom}+filetype%3A{typef}"

#########################################  Downloading documents using links from a file ################################
def files_for_download(path):
    '''File Selection'''
    def input_for_user():
        o=int(input(Fore.YELLOW+"Enter a number indicating the file : "+Style.RESET_ALL))
        return o
    print(Fore.YELLOW+'Available files :'+Style.RESET_ALL)
    list_access_files=[str(t)+'\t'+z for t,z in enumerate([i for i in os.listdir(path) if i.startswith('log')])]
    print(Fore.YELLOW+'\n'.join(list_access_files)+Style.RESET_ALL)
    try:
        return list_access_files[input_for_user()]
    except IndexError as ierror:
        print(Fore.RED+str(ierror)+Style.RESET_ALL)
def reader_files_with_links(path):
    '''Reads the file and returns a list of links'''
    with open(path,'r',encoding='utf-8') as flinks:
        return flinks.readlines() 

def restart():
    '''Downloads documents using links from a file'''
    ffd=files_for_download(os.getcwd())      
    if ffd !=None:
        for link_on_document in reader_files_with_links(' '.join(ffd.split('\t')[1:])): #the file name in this format is a digit\tfile
            threading.Thread(target=create_file,args=(link_on_document.replace('\n','').strip(),)).start()
    else:
        print(Fore.RED+'[!] File not found '+Style.RESET_ALL)
    
#####################################################  Collecting metadata #################################################

def transform_date(arg:str):
    if 'D:' in arg:
        arg=arg.strip()[2:]

        def transoframtion(parametr,offset=''):    
            return ' '.join([parametr[:4]]+[parametr[n:n+2] for n in range(4,len(parametr),2)]).replace(' ','/',2).replace(' ',':').replace(':',' ',1)+' + '+offset# [parametr[:4]]+[parametr[n:n+2] for n in range(4,len(parametr),2)]
        if '+' in arg:
            return transoframtion(arg.split('+')[0],offset=arg.split('+')[1].replace("'",':')[:-1])
        if '-' in arg:
            return transoframtion(arg.split('-')[0],offset=arg.split('-')[1].replace("'",':')[:-1])

        else:
            return transoframtion(arg[:-1]).strip()[:-1]
    else:return arg
####################################################### PDF  ############################################
def metapdf(path):
    try:
        pdf=pikepdf.Pdf.open(path)
    except pikepdf._qpdf.PdfError:
        pass
    else:        
        docinfo = pdf.docinfo
        docinfo['/file']=os.path.split(path)[-1]
        try:
            return {k.replace('/','').replace('[','_').replace(']',''):transform_date(str(v).strip()) for k,v in docinfo.items()}
        except NotImplementedError:
            pass
        # for key,val in docinfo.items():
    #     key=str(key).replace('/','')
    #     if 'D:' in str(val).strip():      
    #         val=str(val)
    #         val=transform_date(val)
    #     return dict(key,val)
#################################################  xlsx,docx,pptx parsing  ################################################
def extract_xml_file_from_docx(path):
    '''Returns metadata from docx,xlsx,pptx files'''
    try:
        with zipfile.ZipFile(path) as doc:
            with doc.open('docProps/core.xml','r') as f:
                return parsing_xml(f.read().decode('utf-8'),path) 
    except zipfile.BadZipFile:
        pass

def parsing_xml(file,path):
    '''Parses xml files and edits metadata'''
    def redact_time_create_document(parametr:str):
        if ':' in parametr and '-' in parametr:
            return  ' - '.join(parametr[:-1].split('T'))
        else:
            return parametr
    try:
        return {**{s.name.split(':')[1]:redact_time_create_document(s.text) for s in BeautifulSoup(file,'lxml').find('cp:coreproperties').find_all_next()},**{'file':os.path.basename(path)}}
    except AttributeError:
        pass

# def redact_dict(_dict:dict,_keys):
# #     return {_keys:_dict.get(_keys,'')}
    # try:
    #     return {_keys:_dict[_keys]}
    # except KeyError:
    #     return {_keys:''}
##########################################################  IMAGES #####################################################################
def exif_image(path):
    """Reading metadata from an image"""
    def decoding(arg): 
        '''Decoding bytes into a string'''
        if isinstance(arg,bytes):
            try:
                return arg.decode().strip()
            except UnicodeDecodeError:
                pass
        else:
            return arg

    def icc_profile_redact(dictionary:dict):
        '''Editing the icc_profile key from a dictionary with metadata about png format'''
        try:
            dictionary['icc_profile']=','.join([xl for xl in [re.sub('[!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]',' ',m[3:]) for m in str(dictionary.get('icc_profile')).split('\\')]if xl!='' and len(xl.strip())>3 and not xl.islower()][:-16])
            return dictionary
        except KeyError:
            return dictionary
    if path.endswith('.png'):
        return icc_profile_redact({**Image.open(path).info,**{'file':os.path.basename(path)}})
    else:
        try:
            return {**{TAGS.get(tag):decoding(tags) for tag,tags in Image.open(path).getexif().items() },**{'file':os.path.basename(path)}}
        except UnidentifiedImageError as identification_error:
            print(identification_error)  

########################################################## Writing to a file ##########################################################
def detect_save():
    '''Determining the entered file extension and file name for the report'''
    if args.save==None: #If the file name is not specified.then it will take from the argument with the domain, if there is no domain, then the current date and time
        if args.domain!=None:
            return 'report '+args.domain+'.'+args.extensions
        else:
            return 'report '+'_'.join(ctime(time()).replace(':','-').split(' ')[1:-1])+'.'+args.extensions
    else:  #IF the name and extension are specified, it will return it,if only the file name is specified, it will add the extension specified in the extension argument
        if '.csv' in args.save or '.json' in args.save or '.txt' in args.save or '.html' in args.save:
            return args.save
        else:return args.save+'.'+args.extensions
def search_path(path,ex):
    '''Returns absolute paths to documents from which metadata will be extracted'''
    for x,z,c in os.walk(path):
        for v in c:
            if v.endswith(ex): 
                yield os.path.join(x,v)
def detect_func(extensions,path_for_file):
    '''Defines a function by file extension'''
    funct=''
    if extensions=='xlsx' or extensions=='docx':
        funct=extract_xml_file_from_docx(path_for_file)
    elif extensions=='pdf':
        funct=metapdf(path_for_file)
    elif extensions=='jpeg' or extensions=='jpg' or extensions=='gif' or extensions=='png' or extensions=='bmp' or extensions=='tif' or extensions=='tiff' or extensions=='jpe' or extensions=='jfif':
        funct=exif_image(path_for_file)
    return funct

def pretty(dictionary): 
    emt=[]
    tables=PrettyTable() 
    # tables.title=extens #HEADER TABLE
    tables.hrules=ALL #Specifies that there should be a horizontal line in the rows
    if type(dictionary)==list:    
        s=[met for met in dictionary  if type(met) is not None and type(met)!=None and met!=None and met!='']
        for i in s:
            [emt.append(r) for r in list(i.keys()) if r not in emt]
        tables.field_names=emt
        tables._max_width={l:30 for l in emt}
        for u in s:           
            tables.add_row([u.get(j,'') for j in emt])
        return tables
    else:
        tables.field_names=list(dictionary.keys())
        tables.add_row(dictionary.values())
        return tables
def csv_writer(dictionarys):
    ''' Recording in csv format'''
    csv_file=open(detect_save(),'a',encoding='cp1251',newline='')    
    
    if type(dictionarys)==list:
        emtc=[]
        cs=[metc for metc in dictionarys  if type(metc) is not None and type(metc)!=None and metc!=None and metc!='']
        for ic in cs:
            [emtc.append(rc) for rc in list(ic.keys()) if rc not in emtc]        
        writer=csv.DictWriter(csv_file,delimiter=';',fieldnames=emtc)
        writer.writeheader() 
        for txs in cs:
            try:
                writer.writerow(txs)
            except UnicodeEncodeError:
                pass
    else:
        writer=csv.DictWriter(csv_file,delimiter=';',fieldnames=list(dictionarys))
        writer.writeheader()
        try:
            writer.writerow(dictionarys)
        except UnicodeEncodeError:
            pass
    csv_file.close()


def txtsave(table):
    '''Recording in txt format'''
    with open(detect_save(),'a',encoding='utf-8') as f:
        f.write(table.get_string())
        f.write('\n')
def html_writer(text):
    '''Recording in html format'''
    with open(detect_save(),'w',encoding='utf-8') as html_text:
        html_text.write(text.get_html_string(attributes={'border':'2','cellspacing':'2'}))
def json_writer(table):
    '''Writing to json'''
    with open(detect_save(),'w',encoding='utf-8') as js:
        js.write(table.get_json_string())
def extra(func):
    funct_file_extension=''
    if args.extensions==None:
        funct_file_extension=print(pretty(func))
    elif args.extensions=='txt':
        funct_file_extension=txtsave(pretty(func))
    elif args.extensions=='json':
        funct_file_extension==json_writer(pretty(func))
    elif args.extensions=='html':
        funct_file_extension==html_writer(pretty(func))
    elif args.extensions=='csv':
        funct_file_extension==csv_writer(func)
if __name__=="__main__":
    init()
    print(Style.BRIGHT+Fore.BLUE+

'''  
     __  __        _            ____        _
    |  \/  |  ___ | |_   __ _  / ___|  ___ | |_
    | |\/| | / _ \| __| / _` || |  _  / _ \| __|
    | |  | ||  __/| |_ | (_| || |_| ||  __/| |_
    |_|  |_| \___| \__| \__,_| \____| \___| \__|
    
    '''+Style.RESET_ALL)
    #Объявление аргументов командной строки
    parser=argparse.ArgumentParser(epilog='''
------------------------------------------------------------------------------------    
 
Usage examples:
1.Extracting metadata from documents:
    python MetaFinder.py -e paths --if Paths are folders, it will search them for documents corresponding to the extension.
    python MetaFinder.py -e paths -f docx pdf - extracts information from documents with the docx and pdf extension. 
2. Downloading documents, followed by analysis:
    python MetaFinder.py -d domain/list domains -- downloads documents with extensions : doc,docx,ppt,xlsx,xls,csv,jpg,jpeg,bmp from the specified domain/domains. 
    python MetaFinder.py -d domains -f docx pdf -- downloads docx and pdf documents from the specified domain/domains. 
    python MetaFinder.py -d domains -f docx -w 30 -c 1 -ex html -s result -- downloading docx documents from the specified domain only from the first page,
        with an interval between requests of 30 seconds and the output of the result in an html document result.html .
    python MetaFinder.py -d domains --tor --will download doc,docx,ppt,xlsx,xls,csv,jpg,jpeg,bmp documents via the TOR network from the specified domain.
3.Downloading documents using links from a file
    python MetaFinder.py --restart 

    ''',formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d',dest='domain',nargs='+',help='Specify a domain or a list of domains separated by a space.Example: mail.ru yandex.ru.')
    parser.add_argument('-f',dest='filetype',nargs='+',help='List the file types to download separated by a space.By default:doc,docx,ppt,xlsx,xls,csv,jpg,jpeg,bmp ',default=['doc','xls','ppt','csv','docx', 'xlsx', 'jpg', 'jpeg', 'bmp'])
    parser.add_argument('-c',dest='count',help='The number of pages viewed.By default, it searches on all pages.')
    parser.add_argument('-w',dest='wait',type=int,help='Waiting time between requests.By default, the random value is from 30 seconds to 90',default=random.uniform(30,90))
    parser.add_argument('-o',dest='output',help='The path to the folder to save the files to is saved in this directory by default',default=os.getcwd())#default=os.path.join(os.environ['USERPROFILE'],'Desktop'))
    parser.add_argument('--tor',dest='_tor',action='store_true',help='Redirects all traffic through the TOR network') 
    parser.add_argument('--proxy',dest='_proxy',help='Connecting a proxy from a file.Specify the path to the file as an argument.Proxy format: "http": "http://user:pass@10.10.1.10:3128/","https": "https://user:pass@10.10.1.10:3128/" ')
    parser.add_argument('-e','--extract',dest='extract',nargs='+',help='Can be used on already downloaded documents to extract metadata from them')
    parser.add_argument('--restart',dest='restart',action='store_true',help="Downloads documents using links from a file")
    parser.add_argument('-ex','--extension',dest='extensions',help='The format of the report file.The following options are available json/txt/csv/html',choices=['json','txt','csv','html'])
    parser.add_argument('-s','--save',dest='save',help='Report file',nargs='?')
    args=parser.parse_args()
        
    #list with user-agents
    list_agents=random.choice(['Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36', 
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36', 
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36', 
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36', 
    'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36', 
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36', 
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36', 
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36', 
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36', 
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36', 
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'])
    header={'user-agent':list_agents} #header
    res=requests.get('https://google.com/',headers=header).cookies.get_dict() #request for cookies
    links_for_docs=[]    
    if args.extract: #Checking whether an argument is entered to extract metadata from files or a list of files
        for arguments_for_extract in args.extract: 
            if os.path.isdir(arguments_for_extract):
                lists_exetension=[position for position in [format_extension if format_extension in ['jpeg', 'jpg', 'gif', 'png', 'bmp', 'tif', 'tiff', 'jpe', 'jfif','pdf','docx','xlsx','pptx'] else print(Fore.RED+'[!] The '+format_extension.upper()+' format is not supported!'+Style.RESET_ALL) for format_extension in args.filetype ] if position!=None and position is not None]
                extra([detect_func(ui,inc) for ui in lists_exetension for inc in search_path(arguments_for_extract,ui)])
            else:
                extra(detect_func(arguments_for_extract.split('.')[-1],arguments_for_extract)) 
    elif args.restart: #if the program failed with an error last time, then you can download files from saved links or substitute your own list of files for download
        restart()

    elif args.domain!= None:
        ####This part is for finding an open directory
        index_link=[]
        file_extensions=('.pdf','.doc', '.docx', '.ppt', '.xlsx', '.xls', '.csv', '.jpg', '.jpeg', '.bmp', '.png', '.tif', '.htm', '.html', '.xml', '.php', '.bak', '.js', '.css')
        for linker_index_of in args.domain:
            link_index_of='https://www.google.com/search?q=site%3A'+linker_index_of+'+intitle%3AIndex+of'
            parse_index_of(collection_page(link_index_of))
            for fu in index_link:
                th2=threading.Thread(target=parsing_documents_on_index_of,args=(fu,),daemon=True).start()
        for s in type_arguments(): ###URL
            text_html=collection_page(s)
            #get_links_for_documents_from_url(text_html) #Extracts links to documents from the received html page
            kx=search_links_for_pages(text_html) #Retrieves links to pages, if any
            c=0
            while True:
                if 'start' in kx:
                    request_on_page_from_list_links=collection_page(re.sub('start=\d\d','start='+str(c),kx))
                else:
                    request_on_page_from_list_links=collection_page(kx+'&start='+str(c))
                if content_not_found(request_on_page_from_list_links)==False: 
                    print(Fore.RED+'[!] The documents of '+kx.split('&')[0].split(":")[-1].upper()+' not found'+Style.RESET_ALL)  
                    break
                else: #If links to documents are found, it collects them and immediately downloads the found documents
                    get_links_for_documents_from_url(request_on_page_from_list_links)
                    for link__docum in links_for_docs:
                        th=threading.Thread(target=create_file,args=(link__docum,))
                        th.start()
                        th.join()                            
                if args.count!=None:    
                    if c==int(args.count)*10:
                        break

                c+=10
                        # except KeyboardInterrupt:
                        #     user_break(links_for_docs)
                        #     exit()
            print(Fore.GREEN+'[+] Analyzing documents...'+Style.RESET_ALL)   
            lists_exetension=[position for position in [format_extension if format_extension in ['jpeg', 'jpg', 'gif', 'png', 'bmp', 'tif', 'tiff', 'jpe', 'jfif','pdf','docx','xlsx','pptx'] else print(Fore.RED+'[!] The '+format_extension.upper()+' format is not supported!'+Style.RESET_ALL) for format_extension in args.filetype ] if position!=None and position is not None]
            if lists_exetension==[] or lists_exetension==None:
                print(Fore.RED+'[!] No documents were found for analysis'+Style.RESET_ALL)
            else:
                extra([detect_func(uix,include2) for uix in lists_exetension for include2 in search_path(args.output,uix)])
    if args.extensions!=None:
        print(Fore.GREEN+'[+] Completed.The data was written to a file '+detect_save()+Style.RESET_ALL)


