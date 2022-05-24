# MetaGet

A program for extracting metadata from documents

Opportunities:
```
1. It can work through the Tora network, private and public proxies.
2. Bypasses the captcha, through public proxies.
3. Can download documents by links from a file.
4. Searches for open index of directories and downloads files from them.
5. A unique algorithm for a more thorough search of documents (it also searches on hidden pages and downloads all documents by default).
6. Can extract metadata from documents.
7. Uses random headers with user-agent.For each request, it substitutes cookies and random time between requests, thereby reducing the chance of receiving a captcha.
8. The result can be written in json, csv, html or txt files, beautifully designed in the form of a table.(When writing a report to json, there may be problems with encoding Russian characters!)
9. Multithreaded downloading of found files.
```

Options:
```
-d - Domain.You can specify multiple domains, separated by a space.
-f is the file format for downloading or analysis.You can specify multiple arguments, separated by a space.
 By default, downloads files with the extension doc,xls,ppt,csv,docx, xlsx, jpg, jpeg, bmp.
 It can extract metadata from files with extensions: jpeg, jpg, gif, png, bmp, tif, tiff, jpe, jfif,pdf,docx,xlsx,pptx.
-c is the number of pages.
-w is the waiting time between requests.By default, a random value is taken in the range from 30 to 90 seconds
-o -The path where to save the found documents.By default, a folder will be created with the name from the domain 
 and documents will be saved in folders in it.
--tor - Indicates that you need to parse through tor networks.Tor must be installed.Specified without arguments.
--proxy - Parsing via private proxies.The argument must specify the path to the file with proxy addresses.
 Proxy format: "http": "http://user:pass@10.10.1.10:3128 /","https": "https://user:pass@10.10.1.10:3128 /" .
--restart - Downloads the document
```

Usage examples:
```
1.Extracting metadata from documents:
    python3 MetaGet.py -e paths --if Paths are folders, it will search them for documents corresponding to the extension.
    python3 MetaGet.py -e paths -f docx pdf - extracts information from documents with the docx and pdf extension. 
2. Downloading documents, followed by analysis:
    python3 MetaGet.py -d domain/list domains -- downloads documents with extensions : doc,docx,ppt,xlsx,xls,csv,jpg,jpeg,bmp from the specified domain/domains. 
    python3 MetaGet.py -d domains -f docx pdf -- downloads docx and pdf documents from the specified domain/domains. 
    python3 MetaGet.py -d domains -f docx -w 30 -c 1 -ex html -s result -- downloading docx documents from the specified domain only from the first page,
        with an interval between requests of 30 seconds and the output of the result in an html document result.html .
    python3 MetaGet.py -d domains --tor --will download doc,docx,ppt,xlsx,xls,csv,jpg,jpeg,bmp documents via the TOR network from the specified domain.
3.Downloading documents using links from a file
    python3 MetaGet.py --restart 
```

Instructions for installing the TOR service.
For Windows:
```
    1.Download the Expert Bundle from the official website https://www.torproject.org/ru/download/tor/
    2.Unpack the downloaded archive to any convenient location.
    3.Open a command prompt, go to the Tor folder and run tor with the command tor.exe .
    !If you close the console, the tor process ends.To make it work all the time, you need to run it as a service:
        go to the tor folder, if there is no torrc file, create it and write it to it:
    
    SOCKSPort 9050 
    GeoIPFile C:\tor\geoip 
    GeoIPv6File C:\tor\geoip6
    MaxCircuitDirtiness 60 
    
    If there is already a torrc file, add these lines to the end of the file
    Open a command prompt and type the following command: file path tor.exe --service install(for example,C:\Tor\tor.exe --service install)
    Start the tor service C:\Tor\tor.exe --service install -options -f "C:\Tor\torrc " 
    C:\Tor\tor.exe --service start
    to stop the service, enter C:\Tor\tor.exe --service stop
```
For Linux:
```
    1.Install tor with the command: sudo apt install tor
    2.Start the service: sudo systemctl start tor
    3.Add to the file /etc/tor/torrc MaxCircuitDirtiness 60 
```
Tested on windows 10 pro and Kali Linux

_ONLY DOCUMENT FORMATS ARE SUPPORTED IN THIS VERSION.:jpeg, jpg, gif, png, bmp, tif, tiff, jpe, jfif,pdf,docx,xlsx,pptx_
