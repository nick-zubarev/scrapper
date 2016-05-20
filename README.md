# scrapper

### Installation

Install system dependencies

    ./dependencies.sh

Create virtualenvironment & make project directory

    virtualenv env
    mkdir source

Clone project from repository

    git clone https://github.com/nick-zubarev/scrapper.git ./source

Activate environment and install requirements

    source env/bin/activate
    pip install -r source/requirements.txt

#### Spiders

 - **tg** - courses.theguardian.com
 - **st** - springest.com
 - **hc** - hotcourses.com
 - **zoom** - zoominfo.com
