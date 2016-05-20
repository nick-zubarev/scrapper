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
 - **zoom** - zoominfo.com
 
#### Parsing

    source env/bin/activate
    cd project/
    scrapy crawl [SPIDER_NAME]
    
For example hotcourses

    source env/bin/activate
    cd project/
    scrapy crawl hc
