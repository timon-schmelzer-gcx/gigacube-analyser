export PATH="/usr/local/opt/python/libexec/bin:$PATH"
cd /Users/tschmelzer/Code/private/gigacube/scraper
/Users/tschmelzer/.poetry/bin/poetry run scrapy crawl volume -o data/volumes.jl
