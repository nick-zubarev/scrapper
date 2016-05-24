# scrapper

### Installation

Install system dependencies

    ./dependencies.sh

Create virtualenvironment & make project directory

    virtualenv env
    mkdir source

Clone project from repository into directory named **project**

    git clone https://github.com/nick-zubarev/scrapper.git ./project

Activate environment and install requirements

    source env/bin/activate
    pip install -r project/requirements.txt

#### Spiders

 - **tg** - courses.theguardian.com
 - **st** - springest.com
 - **hc** - hotcourses.com
 - **zoom** - zoominfo.com - *only for completion empty columns parsed in other spiders*
 
#### Parsing

    source env/bin/activate
    cd project/
    scrapy crawl [SPIDER_NAME]
    
For example hotcourses

    source env/bin/activate
    cd project/
    scrapy crawl hc

##### Parsing proxy options

By default proxies arn't used. But if you see some errors like **Error 403** or **Error 400** you can start scrapping with proxy. If you want to forced disable proxy

    scrapy crawl [SPIDER_NAME] -a noproxy=true

For forcing use proxy

    scrapy crawl [SPIDER_NAME] -a proxy=true
