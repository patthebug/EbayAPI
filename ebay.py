
import json
import csv
import urllib2
import sys
from bs4 import BeautifulSoup
import unicodedata
from ebaysdk import finding

def PopulateBooksDict(itemURL, booksDict, row, searchResult, count, flag):
     request  = urllib2.Request(str(itemURL))
     try:
        page = urllib2.urlopen(request)
     except urllib2.URLError, e:
         if hasattr(e, 'reason'):
             print 'Failed to reach url'
             print 'Reason: ', e.reason
             sys.exit()
         elif hasattr(e, 'code'):
             if e.code == 404:
                 print 'Error: ', e.code
                 sys.exit()
     soup = BeautifulSoup(page.read())
     tempStr = unicodedata.normalize('NFKD', soup.text).encode('ascii','ignore')
     ISBN = tempStr[tempStr.find('ISBN-10:') + 11 : tempStr.find('ISBN-10:') + 21]
     if(row[0] == ISBN):
         if(flag == 0):
             if(row[1] in booksDict):
                 booksDict[row[0]].append(searchResult['item'][count])
             else:
                 booksDict[row[0]] = []
                 booksDict[row[0]].append(searchResult['item'][count])
         else:
             if(row[1] in booksDict):
                 booksDict[row[0]].append(searchResult['item'])
             else:
                 booksDict[row[0]] = []
                 booksDict[row[0]].append(searchResult['item'])


def ReadData():
    with open('data', 'rb') as csvfile:
         booksDict = {}
         csvReader = csv.reader(csvfile, delimiter=',', quotechar='|')
         next(csvReader, None)
         counter = 0
         for row in csvReader:
             title = row[2].replace('"', '')
             api = finding(appid='Universi-ab00-4257-afba-7d353c3c7d4d')
             api.execute('findItemsAdvanced', {'keywords': title})
             searchResults = json.loads(api.response_json())
             if('errorMessage' in searchResults):
                 if(str(searchResults['errorMessage']['error']['errorId']['value']) == '6'):
                    break

             searchResult = searchResults['searchResult']
             if(searchResult.has_key('item')):
                 if(len(searchResult['item']) > 0):
                     for count in range(int(searchResults['searchResult']['count']['value'])):
                         if(int(searchResult['count']['value']) == 1):
                             if('condition' in searchResult['item']):
                                 if(searchResult['item']['condition']['conditionDisplayName']['value'] == 'Brand New'):
                                    counter += 1
                                    itemURL = searchResult['item']['viewItemURL']['value']
                                    print str(counter) + itemURL
                                    PopulateBooksDict(itemURL, booksDict, row, searchResult, count, 1)
                         elif('condition' in searchResult['item'][count]):
                             if(searchResult['item'][count]['condition']['conditionDisplayName']['value'] == 'Brand New'):
                                 counter += 1
                                 itemURL = searchResult['item'][count]['viewItemURL']['value']
                                 print str(counter) + itemURL
                                 if(counter == 98):
                                     x=0
                                 PopulateBooksDict(itemURL, booksDict, row, searchResult, count, 0)
                         else:
                             continue

    WriteOutput(booksDict)


def WriteOutput(booksDict):
    with open('workfile.csv', 'wb') as csvfile:
        csvWriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for key in booksDict:
            minPrice = 0.0
            minCount = 0
            for count in range(len(booksDict[key])):
                price = float(booksDict[key][count]['sellingStatus']['currentPrice']['value'])
                if(count == 0):
                    minPrice = price
                elif(price < minPrice):
                    minPrice = price
                    minCount = count
            tempList = []
            tempList = [key, unicodedata.normalize('NFKD', booksDict[key][minCount]['title']['value']).encode('ascii','ignore'),
                        unicodedata.normalize('NFKD', booksDict[key][minCount]['sellingStatus']['currentPrice']['value']).encode('ascii','ignore')]
            csvWriter.writerow([x for x in tempList])

def main():
    ReadData()

main()


