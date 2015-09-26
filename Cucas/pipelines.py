# -*- coding: utf-8 -*-
import re
import os
import openpyxl

def del_white_space(data):
	data = data.replace("\n", "")
	data = re.sub(r"\s+", " ", data)
	return data


class CucasPipeline(object):

	_header_school = [
		'School name', 'China University Ranking by MOE', 'City', 'Reason choose', 'Living expense',
		'Name course', 'Qualification awarded', 'Teaching language', 'Duration', 'Tuition fee',
		'Starting date', 'Application deadline', 'Application fee', 'Academic requirement',
		'Enrollment quota', 'Affiliated hospitals', 'English requirement', 'Admission difficulty',
		'HSK requirement', 'Overview', 'Application materials', 'Type money', 'Accommodation cost',
		'Tuition fee living', 'Other cost', 'Total cost']

	def process_item(self, item, spider):
		self.create_school_sheet(item)
		return item

	def create_school_sheet(self, item):
		if item:
			wb = openpyxl.Workbook()
			ws = wb.active
			ws.title = "University"
			ws.append(self._header_school)
			if item:
				# TODO: Add information for university
				school_info_row = []
				school_info_row.append(item['school_name'])
				school_info_row.append(item['ranking'])
				school_info_row.append(item['city'])
				school_info_row.append(item['reason'])
				school_info_row.append(item['living_expense'])
				if item["courses"]:
					for course in item["courses"]:
						# TODO: Add courses for university
						course_info_row = list(school_info_row)
						course_info_row.append(course["name_course"])
						course_info_row.append(course["qualification_awarded"])
						course_info_row.append(course["teaching_language"])
						course_info_row.append(course["duration"])
						course_info_row.append(course["tuition_fee"])
						course_info_row.append(course["starting_date"])
						course_info_row.append(course["application_deadline"])
						course_info_row.append(course["application_fee"])
						course_info_row.append(course["academic_requirement"])
						course_info_row.append(course["enrollment_quota"])
						course_info_row.append(course["affiliated_hospitals"])
						course_info_row.append(course["english_requirement"])
						course_info_row.append(course["admission_difficulty"])
						course_info_row.append(course["hsk_requirement"])
						course_info_row.append(course["overview"])
						course_info_row.append(course["application_materials"])
						course_info_row.append(course["type_money"])
						course_info_row.append(course["accommodation_cost"])
						course_info_row.append(course["tuition_fee_living"])
						course_info_row.append(course["other_cost"])
						course_info_row.append(course["total_cost"])
						ws.append(course_info_row)
				else:
					ws.append(school_info_row)

			name = r"\\" + del_white_space(item['school_name']).replace(",", "-") + ".xlsx"
			new_path_school = "Data\\" + str(item["index"]) + "_" + item['school_name']

			if not os.path.exists(new_path_school):
				os.makedirs(new_path_school)
			wb.save(new_path_school + name)


