import string
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.item import Item, Field

#Object to store scraped data in, probably a better way to do this
#TODO: Clean this
class TexasItem(Item):
    dateBirth        = Field()  
    dateRec          = Field()   
    dateOff          = Field()
    colorHair        = Field()
    colorEye         = Field()
    ageRec           = Field()
    ageOff           = Field()
    age              = Field()
    education        = Field()
    stateNative      = Field()
    county           = Field()
    countyNative     = Field()
    race             = Field()
    height           = Field()
    weight           = Field()
    name             = Field()
    gender           = Field()
    TDCJ             = Field()   
    finalStatement   = Field()
    offense          = Field()
    priorOcc         = Field()
    priorRec         = Field()
    summary          = Field()
    coDefends        = Field()
    vicim            = Field()
    mugshot          = Field()
    ident            = Field()

class MySpider(CrawlSpider):
    name = 'Texas'
    start_urls = ["http://www.tdcj.state.tx.us/stat/dr_executed_offenders.html"]
    allowed_domains = ['tdcj.state.tx.us']

    #Lookup table for converting between HTML names and internal data names
    lookup  =  {"Name":"name",
                "TDCJ Number":"TDCJ",
                "Date of Birth":"dateBirth",
                "Date Received":"dateRec",
                "Age (when    Received)":"ageRec",
                "Education Level (Highest Grade Completed)":"education",
                "Date of Offense":"dateOff",
                "Age (at the time    of Offense)":"ageOff",
                "Age":"age",
                "County":"county",
                "Race":"race",
                "Gender":"gender",
                "Hair Color":"colorHair",
                "Height":"height",
                "Weight":"weight",
                "Eye Color":"colorEye",
                "Native County":"countyNative",
                "Native State":"stateNative",
                "Prior Occupation":"priorOcc",
                "Prior Prison Record":"priorRec",
                "Summary of Incident":"summary",
                "Co-Defendants":"coDefends",
                "Race and Gender of Victim":"vicim"
               }


    #Links to be followed 
    rules = (
        Rule(SgmlLinkExtractor(allow=("dr_info" ), deny=("jpg","no_last_statement.html",)), callback='parse_item'),
    )

    #Main callback, all URLS pass through here and are sorted into the correct
    #parsing function
    def parse_item(self, response):
        if response.url.endswith("last.html"):
            return self.parse_lastwill(response)
        else:
            return self.parse_info(response)

    #Create a 2 item data type from last words
    def parse_lastwill(self, response):
        hxs         = HtmlXPathSelector(response)
        hxs         = hxs.select("//div[@id='body']/p/text()")
        statement   = ""
        item        = TexasItem()
        
        #Set the identifier
        item['ident'] = response.url[0:-9]

        #Parsing hacks, For loop WILL NOT iterate past data,
        #Reason: Len spits out odd numbers with xpath arrays
        for i in range(0, 50): 
            if string.find(hxs[i].extract(), "Last Statement:") != -1:
                statement = hxs[i+1].extract()
                break

        item['finalStatement'] = statement

        return item
    
    #Parse general data, returns a mainly filled item
    def parse_info(self, response):
        hxs     = HtmlXPathSelector(response)
        rows    = hxs.select("//table/tr")
        item    = TexasItem()

        #Remove the last from the identifing URL
        item['ident'] = response.url[0:-5]

        #Rip out the info, compare using lookup table
        for tr in rows:
            td  = tr.select("td/text()")
            l   = len(td)
            key = td[l-2].extract()
            val = td[l-1].extract()

            item[self.lookup[key]] = val

        values = hxs.select("//p/text()")
        keys = hxs.select("//p/span/text()")

        #Rip down the auxially data
        for i in range(len(keys)-1):
            key = keys[i].extract()
            val = values[i+1].extract()

            item[self.lookup[key]] = self.cleanString(val)

        #and lastly the mugshot
        hxs = hxs.select("//table/tr/td/img/@src")
        if len(hxs.extract()) >= 1:
            item['mugshot'] = "http://www.tdcj.state.tx.us/stat/dr_info/" + hxs.extract()[0]

        return item

    #Used for stripping newlines if problems arise
    def cleanString(self, string):
        string = string.replace("\r","")
        string = string.replace("\n","")
        return string
