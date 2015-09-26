# -*- coding: utf-8 -*-

# Scrapy settings for Cucas project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'Cucas'

SPIDER_MODULES = ['Cucas.spiders']
NEWSPIDER_MODULE = 'Cucas.spiders'

ITEM_PIPELINES = {
	'Cucas.pipelines.CucasPipeline': 0
}
