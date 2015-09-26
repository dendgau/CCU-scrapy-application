# -*- coding: utf-8 -*-
import scrapy
import requests
import logging
from scrapy import Selector
from selenium import webdriver

DEFAULT_DOMAIN = ""
INDEX = 0


class ScrapCucas(scrapy.Spider):
	name = "cc"
	allowed_domains = [""]
	start_urls = [
		""
	]
	top_ranking = []
	top_index = []

	def parse(self, response):
		self.get_top_ranking(self.get_html(link="http://www.cucas.edu.cn/studyinchina/top/2015_MOE_Ranking_5.html"))

		titles_selector = response.xpath(
			'/html/body/div[contains(@class, "xxSeaMain")]/dl[contains(@class, "xxSeaList")]')
		locations_selector = response.xpath(
			'/html/body/div[contains(@class, "xxSeaMain")]/div[contains(@class, "xxSeaText_1")]')

		if titles_selector:
			for index, element in enumerate(titles_selector):
				link_school = DEFAULT_DOMAIN + element.xpath('dt/a/@href').extract()[0]
				information_school = self.get_school_information(
					self.get_html(link=link_school), link_school=link_school, index=str(index + 1)
				)
				if information_school:
					information_school["index"] = str(index + 1)
					yield information_school

	@staticmethod
	def get_html(link, type="html"):
		html_data = requests.get(link).text
		return Selector(text=html_data, type=type)

	@staticmethod
	def get_html_with_selenium(link, type="html"):
		browser = webdriver.Firefox()
		browser.get(link)
		html_source = browser.page_source
		browser.quit()
		return Selector(text=html_source, type=type)

	def get_top_ranking(self, response):
		top_ranking_selector = response.xpath(
			'/html/body/div[contains(@id, "content")]/div[contains(@class, "main")]'
			'/div[contains(@class, "list")]/div[contains(@class, "bottom")]'
			'/div[contains(@class, "left")]/table[contains(@class, "box")]/tr'
		)

		if top_ranking_selector:
			for index, row in enumerate(top_ranking_selector):
				if index > 3:
					school_name_selector = row.xpath("td[2]/p/a/text()")
					index_selector = row.xpath("td[1]/text()")
					if school_name_selector:
						school_name = str(school_name_selector.extract()[0])
						school_name = school_name.strip()
						self.top_ranking.append(school_name)

						index = str(index_selector.extract()[0])
						index = index.strip()
						self.top_index.append(index)
				elif index == 1:
					self.top_ranking.append(top_ranking_selector[1].extract()[0])
					self.top_index.append(1)
				elif index == 2:
					self.top_ranking.append(top_ranking_selector[2].extract()[0])
					self.top_index.append(2)
				elif index == 3:
					self.top_ranking.append(top_ranking_selector[3].extract()[0])
					self.top_index.append(3)

	@classmethod
	def get_school_information(cls, response, **kwargs):
		school_name_selector = response.xpath(
			'//div[contains(@class, "ScHeadBox")]/div[contains(@class, "ScHead")]'
			'/div[contains(@class, "scTitle")]/h2')

		if school_name_selector:
			school_name = str(school_name_selector.xpath('text()').extract()[0])
			school_name = school_name.strip()
			new_path_school = "Data\\" + kwargs.get("index") + "_" + school_name

			import os
			if not os.path.exists(new_path_school):
				city = cls.get_city(response)
				reason = cls.get_reason(response)
				living_expense = cls.get_living_expense(response)
				courses = cls.get_courses(response)
				ranking = str(cls.top_index[cls.top_ranking.index(school_name)]) if school_name in cls.top_ranking else ""
				# rating = cls.get_rating(cls.get_html_with_selenium(kwargs.get("link_school")))
				return {
					"school_name": school_name,
					"ranking": ranking,
					"city": city,
					"reason": reason,
					"living_expense": living_expense,
					"courses": courses,
					"index": ""
				}
			else:
				logging.warning("The %s have been scraped" % school_name)
				return {}

	@classmethod
	def get_city(cls, response):
		city_selector = response.xpath(
			'//div[contains(@class, "ScHeadBox")]/div[contains(@class, "ScHead")]'
			'/div[contains(@class, "scTitle")]/div[contains(@class, "wordClass")]'
			'/div[contains(@class, "studySelect")]/div[contains(@id, "city_name")]/a')

		return str(city_selector.xpath('text()').extract()[0]) if city_selector else ""

	@classmethod
	def get_reason(cls, response):
		reason_study_selector = response.xpath(
			'//div[contains(@class, "ScMainBox")]/div[contains(@class, "ScMain")]'
			'/div[contains(@class, "ScMindL")]/div[contains(@class, "ScMindText")]'
		)

		if reason_study_selector.xpath('ul/li'):
			reason_study_array = reason_study_selector.xpath('ul/li/text()').extract()
			reason_study = ("".join(reason_study_array)).strip() if reason_study_array else ""
		else:
			reason_study = reason_study_selector.extract()[0]
		return reason_study

	@classmethod
	def get_rating(cls, response):
		average_rating = response.xpath(
			'//div[contains(@class, "ScMainBox")]/div[contains(@class, "ScMain")]'
			'/div[contains(@class, "ScMindR")]/div[contains(@class, "ScMindRBox")]'
			'/div[contains(@class, "StarTitle16")]/span[contains(@id, "score")]'
			'/input[contains(@name, "score")]/@value').extract()[0]

		teaching_rating = response.xpath(
			'//div[contains(@class, "ScMainBox")]/div[contains(@class, "ScMain")]'
			'/div[contains(@class, "ScMindR")]/div[contains(@class, "ScMindRBox")]'
			'/dl[contains(@class, "StarList")]/dd/span[contains(@id, "Teaching")]'
			'/input[contains(@name, "score")]/@value').extract()[0]

		accommodation_rating = response.xpath(
			'//div[contains(@class, "ScMainBox")]/div[contains(@class, "ScMain")]'
			'/div[contains(@class, "ScMindR")]/div[contains(@class, "ScMindRBox")]'
			'/dl[contains(@class, "StarList")]/dd/span[contains(@id, "Accommodatain")]'
			'/input[contains(@name, "score")]/@value').extract()[0]

		food_rating = response.xpath(
			'//div[contains(@class, "ScMainBox")]/div[contains(@class, "ScMain")]'
			'/div[contains(@class, "ScMindR")]/div[contains(@class, "ScMindRBox")]'
			'/dl[contains(@class, "StarList")]/dd/span[contains(@id, "Diet")]'
			'/input[contains(@name, "score")]/@value').extract()[0]

		environment_rating = response.xpath(
			'//div[contains(@class, "ScMainBox")]/div[contains(@class, "ScMain")]'
			'/div[contains(@class, "ScMindR")]/div[contains(@class, "ScMindRBox")]'
			'/dl[contains(@class, "StarList")]/dd/span[contains(@id, "Environmental")]'
			'/input[contains(@name, "score")]/@value').extract()[0]

		administration_rating = response.xpath(
			'//div[contains(@class, "ScMainBox")]/div[contains(@class, "ScMain")]'
			'/div[contains(@class, "ScMindR")]/div[contains(@class, "ScMindRBox")]'
			'/dl[contains(@class, "StarList")]/dd/span[contains(@id, "Administration")]'
			'/input[contains(@name, "score")]/@value').extract()[0]

		curriculum_rating = response.xpath(
			'//div[contains(@class, "ScMainBox")]/div[contains(@class, "ScMain")]'
			'/div[contains(@class, "ScMindR")]/div[contains(@class, "ScMindRBox")]'
			'/dl[contains(@class, "StarList")]/dd/span[contains(@id, "Curriculum")]'
			'/input[contains(@name, "score")]/@value').extract()[0]

		money_rating = response.xpath(
			'//div[contains(@class, "ScMainBox")]/div[contains(@class, "ScMain")]'
			'/div[contains(@class, "ScMindR")]/div[contains(@class, "ScMindRBox")]'
			'/dl[contains(@class, "StarList")]/dd/span[contains(@id, "Money")]'
			'/input[contains(@name, "score")]/@value').extract()[0]

		return {
			'average_rating': str(average_rating) if average_rating else str('0'),
			'teaching_rating': str(teaching_rating) if teaching_rating else str('0'),
			'accommodation_rating': str(accommodation_rating) if accommodation_rating else str('0'),
			'food_rating': str(food_rating) if food_rating else str('0'),
			'environment_rating': str(environment_rating) if environment_rating else str('0'),
			'administration_rating': str(administration_rating) if administration_rating else str('0'),
			'curriculum_rating': str(curriculum_rating) if curriculum_rating else str('0'),
			'money_rating': str(money_rating) if money_rating else str('0')
		}

	@classmethod
	def get_living_expense(cls, response):
		living_expense = response.xpath(
			'//div[contains(@class, "ScMainBox")]/div[contains(@class, "ScMain")]'
			'/div[contains(@class, "ScMindR")]/div[contains(@class, "ScMindRliv")]/h2/strong/text()'
		).extract()[0]

		return str(living_expense) if living_expense else ""

	@classmethod
	def get_courses(cls, response):
		courses_list = []
		course_types_selector = response.xpath(
			'//div[contains(@class, "ScMainBox")]/div[contains(@class, "ScMain")]'
			'/div[contains(@class, "ScMindL")]/div[contains(@class, "ScPopList")]'
			'/dl')

		if course_types_selector:
			for type in course_types_selector:
				link_more = type.xpath('dt/a/@href').extract()[0]
				if link_more:
					# Load more courses in type
					link_more = DEFAULT_DOMAIN + link_more
					course_selector = (cls.get_html(link=link_more)).xpath(
						'//div[contains(@class, "erMain")]/div[contains(@class, "erRight")]'
						'/div[contains(@class, "resConBox")]/dl[contains(@class, "resCon")]'
					)
					if course_selector:
						# Foreach <dl>
						for index, course in enumerate(course_selector):
							# Just get body, remove header in table
							if index > 0:
								links_courses_selector = course.xpath('dt/a')
								if links_courses_selector:
									link_course_detail_selector = links_courses_selector.xpath('@href').extract()[0]
									link_course_detail_selector = DEFAULT_DOMAIN + link_course_detail_selector

									course_detail = cls.get_course_detail(cls.get_html(link_course_detail_selector))
									courses_list.append(course_detail)
								else:
									links_courses_selector = course.xpath(
										'dd/ul[contains(@class, "resConLlist")]'
									)

									if links_courses_selector:
										for link in links_courses_selector:
											link_course_detail_selector = link.xpath('a/@href').extract()[0]
											link_course_detail_selector = DEFAULT_DOMAIN + link_course_detail_selector

											course_detail = cls.get_course_detail(cls.get_html(link_course_detail_selector))
											courses_list.append(course_detail)
		return courses_list

	@classmethod
	def get_course_detail(cls, response):
		info_common = response.xpath(
			'//div[contains(@class, "ScMainKc")]/div[contains(@class, "CourseLeft")]'
			'/div[contains(@class, "CivBox")]/div[contains(@class, "CivLeft")]'
			'/dl[contains(@class, "CivList")]/dd'
		)

		name_course_selector = response.xpath(
			'//div[contains(@class, "ScMainKc")]/div[contains(@class, "CourseLeft")]'
			'/div[contains(@class, "erTiele")]/strong/text()').extract()

		if name_course_selector:
			name_course = name_course_selector[0] if name_course_selector else ""

			qualification_awarded = teaching_language = duration = tuition_fee = starting_date = application_deadline = application_fee = \
				enrollment_quota = affiliated_hospitals = english_requirement = admission_difficulty = hsk_requirement = academic_requirement = ""
			if info_common:
				def get_info_detail(response):
					return (response.xpath('span/text()').extract()[0]).strip()

				for element in info_common:
					_id = element.xpath("span/@id").extract()[0]
					if _id == "correction_1":
						qualification_awarded = get_info_detail(element)
					elif _id == "correction_2":
						teaching_language = get_info_detail(element)
					elif _id == "correction_3":
						duration = get_info_detail(element)
					elif _id == "correction_4":
						tuition_fee = get_info_detail(element)
					elif _id == "correction_5":
						starting_date = get_info_detail(element)
					elif _id == "correction_7":
						application_deadline = get_info_detail(element)
					elif _id == "correction_8":
						application_fee = get_info_detail(element)
					elif _id == "correction_9":
						academic_requirement = get_info_detail(element)
					elif _id == "correction_10":
						enrollment_quota = get_info_detail(element)
					elif _id == "correction_11":
						affiliated_hospitals = get_info_detail(element)
					elif _id == "correction_12":
						english_requirement = get_info_detail(element)
					elif _id == "correction_13":
						admission_difficulty = get_info_detail(element)
					elif _id == "correction_14":
						hsk_requirement = get_info_detail(element)

			overview_selector = response.xpath(
				'//div[contains(@class, "ScMainKc")]/div[contains(@class, "CourseLeft")]'
				'/div[contains(@class, "bs-example")]/div[contains(@class, "scrollspy-example")]/div[1]'
			).extract()
			overview = (overview_selector[0]).strip() if overview_selector else ""

			application_materials_selector = response.xpath(
				'//div[contains(@class, "ScMainKc")]/div[contains(@class, "CourseLeft")]'
				'/div[contains(@class, "bs-example")]/div[contains(@class, "scrollspy-example")]'
				'/div[contains(@id, "howtoapply")]/ul[contains(@class, "materials")]'
			).extract()
			application_materials = (application_materials_selector[0]).strip() if application_materials_selector else ""

			fees_common_selector = response.xpath(
				'//div[contains(@class, "ScMainKc")]/div[contains(@class, "CourseLeft")]'
				'/div[contains(@class, "bs-example")]/div[contains(@class, "scrollspy-example")]'
				'/div[contains(@id, "fees")]'
			)
			type_money_selector = fees_common_selector.xpath('table[3]/tr[2]/td[1]/text()').extract()
			if type_money_selector:
				type_money = (type_money_selector[0]).strip()
				type_money = type_money.split("(")[1]
				type_money = type_money.split(")")[0]
			else:
				type_money = ""

			amount = len(fees_common_selector.xpath('table[3]/tr[1]/th'))
			accommodation_cost = fees_common_selector.xpath('table[3]/tr[2]/td[%s]/text()' % str(amount)).extract()[0]
			tuition_fee_living = fees_common_selector.xpath('table[3]/tr[3]/td[%s]/text()' % str(amount)).extract()[0]
			other_cost = fees_common_selector.xpath('table[3]/tr[4]/td[%s]/text()' % str(amount)).extract()[0]
			total_cost = fees_common_selector.xpath('table[3]/tr[5]/td[%s]/span/text()' % str(amount)).extract()[0]

			return {
				"name_course": name_course,
				"qualification_awarded": qualification_awarded,
				"teaching_language": teaching_language,
				"duration": duration,
				"tuition_fee": tuition_fee,
				"starting_date": starting_date,
				"application_deadline": application_deadline,
				"application_fee": application_fee,
				"academic_requirement": academic_requirement,
				"enrollment_quota": enrollment_quota,
				"affiliated_hospitals": affiliated_hospitals,
				"english_requirement": english_requirement,
				"admission_difficulty": admission_difficulty,
				"hsk_requirement": hsk_requirement,
				"overview": overview,
				"application_materials": application_materials,
				"type_money": type_money,
				"accommodation_cost": accommodation_cost,
				"tuition_fee_living": tuition_fee_living,
				"other_cost": other_cost,
				"total_cost": total_cost
			}
		return {}



