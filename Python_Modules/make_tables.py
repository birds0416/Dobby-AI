import numpy as np
import warnings
warnings.filterwarnings("ignore")
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import mrc_extractor
from mrc_extractor import MRC_EXTRACTION
import pandas as pd
from word2number import w2n

query_dict_ex={'table_top': {
	'Participants':'who are the attendees at the meeting?',
	'Topic':'what was the main topic of the meeting?',
    'num_agendas':'How many agendas?',
    'num_act_items_1':'How many action items for the first agenda?', # 이후 일괄 처리 --> 질문 생성 함수 만들기
    'num_act_items_2':'How many action items for the second agenda?' # 이후 일괄 처리 --> 질문 생성 함수 만들기
	},
 'table_main1': {
    'Discussion Topic':'what was the topic of the first agenda?',
	'Presenter':'who was the presenter of the first agenda?',
	'Conclusion':'what was the conclusion of the first agenda?'
 },
  'table_main1_1':{
	'Action Items':'what was the first action item for the first agenda ?',
	'Person Responsible':'who was responsible for the first action item  of the first agenda?',
	'Deadline':'what was the deadline of the first action item of the first agenda?'
  },
    'table_main1_2':{
	'Action Items':'what was the second action item for the first agenda ?',
	'Person Responsible':'who was responsible for the second action item  of the first agenda?',
	'Deadline':'what was the deadline of the second action item of the first agenda?'
  },
 'table_main2': {
    'Discussion Topic':'what was the topic of the second agenda?',
	'Presenter':'who was the presenter of the second agenda?',
	'Conclusion':'what was the conclusion of the second agenda?'
 },
  'table_main2_1':{
	'Action Items':'what was the first action item for the second agenda ?',
	'Person Responsible':'who was responsible for the first action item  of the second agenda?',
	'Deadline':'what was the deadline of the first action item of the second agenda?'
  },
    'table_main2_2':{
	'Action Items':'what was the second action item for the second agenda ?',
	'Person Responsible':'who was responsible for the second action item  of the second agenda?',
	'Deadline':'what was the deadline of the second action item of the second agenda?'
  }
}


## number  처리할것 
#질문 부분 수정
class make_tables:

	def __init__(self, queries_dict, full_context, type='PPC'):
		self.date = full_context[:10] 
		self.full_context =  full_context[22:]
		# if type=='PPC':
		# 	self.num_act_items, self.num_agendas = list(MRC_EXTRACTION.get_topN_answers( \
		# 		['How many action items for the first agenda?','How many agendas?'], self.full_context).values())  #모델 학습 후 query로 몇개인지 찾기

		#질문 수정할 것
		queries=[list(x.values()) for x in  list(queries_dict.values())]
		queries = [item for sublist in queries for item in sublist]

		mrc = MRC_EXTRACTION(queries, self.full_context)
		
		answers_list=mrc.get_topN_answers()

		temp_df = pd.DataFrame(queries_dict)
		self.answers_dict=temp_df.replace(answers_list).to_dict()
		self.answers_dict['Date']=self.date
		try: 
			self.num_agendas=w2n.word_to_num(self.answers_dict['table_top']['num_agendas'])
			self.num_act_items={}
			for i in range(1, 1+self.num_agendas):
				try: 
					self.num_act_items[i]=w2n.word_to_num(self.answers_dict['table_top']['num_act_items'+str(i)])
				except:
					self.num_act_items[i]=0
		except:
			self.num_agendas=0



	# 회의록 공통 질문 및 agenda 내 첫번째 table용
	def make_table_top(self, items=['Topic','Participants', 'Date'], loc='table_top'):

		html_string = '<table class="table table-bordered">'

		for item in items:
			temp='<tr><td><strong>'+item+'</strong></td>'
			html_string+=temp
			if item=='Date':
				answer_str = '<td>'+self.answers_dict[item]+'</td></tr>' 
			else:
				answer_str = '<td>'+self.answers_dict[loc][item]+'</td></tr>' 

			html_string+=answer_str

		html_string+='</table>'

		return html_string


	# agenda의 두번째 table용
	def make_table_mid(self, n_act_items=0,items=['Action Items','Person Responsible', 'Deadline'], loc='table_main1'):

		if n_act_items==0:
			return ''
		html_string = '<table class="table addel table-bordered" id="addel"><tr>'

		for item in items:
			html_string += '<td><strong>'+item+'</strong></td>'

		html_string+='</tr><tr>'

		for i in range(1,1+n_act_items):
			for item in items:
				answer = '<td>'+self.answers_dict[loc+'_'+str(i)][item]+'</td>' # 답 나오게 수정
				html_string += answer

		html_string+='</tr>'

		html_string+='<input type="button" class="float" value="Add" id="addrow2"></table>'

		return html_string


	# 각 Agenda table 생성용

	def make_table_final(self, type='PPC'):

		html_string = self.make_table_top()
		label = ''
		if type=='PPC':  
			label = 'Agenda'
		for i in range(1, 1+self.num_agendas):
			loc='table_main'+str(i)
			html_string += '<label><strong>'+label+' '+str(i)+'</strong></label>'
			html_string += self.make_table_top(items=['Presenter', 'Discussion Topic', 'Conclusion'], loc=loc)# 이후 적절한 query로 수정
			html_string += self.make_table_mid(self.num_act_items[i], loc=loc) # 수정

		html_string += '<table class="table table-bordered"><tr><td><strong>Additional Notes</strong></td></tr><tr><td></td></tr></table>' # 수정
		return html_string



if __name__ == "__main__":
	main()



