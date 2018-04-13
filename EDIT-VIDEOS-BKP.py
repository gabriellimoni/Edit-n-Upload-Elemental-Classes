# -*- coding: utf-8 -*-

import subprocess
from datetime import datetime
import sys
from time import sleep


def list_aulas_menu():
	print("")
	print("-- ESCOLHA A AULA --")
	print("agro -> MBA em Agronegócio")
	print("agro2 -> MBA em Agronegócio 172")
	print("agromkt  -> Oficina de Marketing no Agro")
	print("cop -> MBA em Cooperativas de Crédito")
	print("faz -> Gestão de Fazenda")
	print("esc -> MBA em Gestão Escolar")
	print("mkt -> MBA em Marketing")
	print("neg -> MBA em Gestão de Negócios")
	print("office -> Ferramentas do Office")
	print("pro -> MBA em Gestão de Projetos")
	print("var -> MBA em Varejo e Mercado de Consumo")
	print("--")
	
	aula = raw_input()
	print("--" + aula + "--")
	
	return aula
	
def list_num_intervalos():
	print("")
	print("-- QUANTAS PARTES SERÃO CORTADAS? --")
	
	return raw_input()

	
def list_intervalos(num_intervalos):
	print("")
	intervalos = ""
	
	for i in range(0,num_intervalos):
		# divide o conjunto de 2 tempos
		if i > 0:
			intervalos += ','
			
		print("-> Parte %", i+1)
		print("Digite o tempo inicial (HH MM SS)")
		tempo1 = raw_input().replace(" ", ":")
		
		print("Digite o tempo final (HH MM SS)")
		tempo2 = raw_input().replace(" ", ":")
		
		intervalos += tempo1 + ';' + tempo2
		
		print("")
	
	return intervalos
	
def list_input():
	print("")
	print("-- COLOQUE O NOME DO ARQUIVO BRUTO --")
	print("SEM O CAMINHO E SEM EXTENSAO")
	
	return raw_input()
	
def list_output():
	print("")
	print("-- COLOQUE O NOME DO ARQUIVO DESTINO --")
	print("SEM O CAMINHO E SEM EXTENSAO")
	
	return raw_input()
	
# executa comando bash
def run_command(command):
	subprocess.check_call(command, shell=True)
	
class Transmissao(object):
	
	def __init__(self, aula, intervalos, arquivo_bruto, arquivo_destino):
		self.aula = aula
		self.tempos = intervalos.split(",")
		self.arquivo_bruto = arquivo_bruto
		self.arquivo_destino = arquivo_destino
	
		self.sections = len(self.tempos)
		
		self.aula_dir = "/data/server/videos/"+aula+"/"
		self.aula_editada_dir = self.aula_dir + "aulas-editadas/"
	

	def cut_sections(self):
		ffmpeg_cut_command = 'ffmpeg -y -ss {TIME1} -i "{INPUT}.mp4" -t {TIME2} -vcodec copy -acodec copy "{DIR}/{SECTION}.mp4"'
		for section in range (1, self.sections + 1):
			time_1, time_2 = self.tempos[section-1].split(";")

			# converte as strings em tempos
			time_1 = datetime.strptime(time_1, "%H:%M:%S")
			time_2 = datetime.strptime(time_2, "%H:%M:%S")
			time_2 = time_2 - time_1

			# reconverte para string
			time_1 = datetime.strftime(time_1, "%H:%M:%S")
			#time_2 = datetime.strftime(time_2, "%H:%M:%S") #--> nao precisa pois e um deltatime
			
			# altera o comando
			cut_command = ffmpeg_cut_command \
								.replace("{TIME1}", time_1) \
								.replace("{TIME2}", str(time_2)) \
								.replace("{INPUT}", self.aula_dir + self.arquivo_bruto) \
								.replace("{DIR}", self.aula_dir) \
								.replace("{SECTION}", str(section))
			print(cut_command)
			run_command(cut_command)
			
	
	def concat_sections(self):
		mp4box_concat_command = 'MP4Box -v -force-cat {CONCAT_ORDER} -out "{OUTPUT}.mp4"'
		first_file = " {DIR}{SECTION}.mp4 "
		cat_files = " -cat {DIR}{SECTION}.mp4 "
		
		concat_files = ""
		
		# MONTA O COMANDO PARA CONCATENAR DE ACORDO COM A QUANTIDADE DE TEMPOS PASSADOS
		for section in range(1, self.sections+1):
			if section == 1:
				concat_files += first_file.replace("{DIR}", self.aula_dir).replace("{SECTION}", str(section))
			else:
				concat_files += cat_files.replace("{DIR}", self.aula_dir).replace("{SECTION}", str(section))
		
		concat_command = mp4box_concat_command \
									.replace("{CONCAT_ORDER}", concat_files) \
									.replace("{OUTPUT}", self.aula_editada_dir + self.arquivo_destino)
		print(concat_command)
		run_command(concat_command)
	
	def export_audio(self):
		ffmpeg_export_audio = 'ffmpeg -i "{INPUT}.mp4" -f mp3 -ab 192000 -vn "{OUTPUT}.mp3"'
		audio_command = ffmpeg_export_audio \
								.replace("{INPUT}", self.aula_editada_dir + self.arquivo_destino) \
								.replace("{OUTPUT}", self.aula_editada_dir + self.arquivo_destino)
		print(audio_command)
		run_command(audio_command)
		
	def upload_dropbox(self):
		dropbox_upload_command = '/data/server/dropbox/dropbox_uploader.sh upload "{INPUT}.mp4" "{DROPBOX_LOCATION}/{OUTPUT}.mp4"'
		dropbox_dir = '/Pasta da Equipe Pecege/AulasVideos/TEMPORARIOS/'
		upload_command = dropbox_upload_command \
								.replace("{INPUT}", self.aula_editada_dir + self.arquivo_destino) \
								.replace("{DROPBOX_LOCATION}", dropbox_dir) \
								.replace("{OUTPUT}", self.arquivo_destino)
		print(upload_command)
		run_command(upload_command)

		
def main():
	# vars "globais"
	num_aulas = 0;
	transmissoes = []

	
	# se forem passados os parâmetros por argumentos
	if( len(sys.argv) > 1 ):
	
		#### lista de variáveis necessárias ####
		
		# numero de aulas 1
		
		# transmissoes
		# 	aula 2 x índice da aula
		# 	numero de intervalos 3 x índice da aula
		# 	intervalos 4 x índice da aula
		# 	nome do arquivo input 5 x índice da aula
		# 	nome do arquivo output 6 x índice da aula
		
		############# fim lista #################
	
		num_aulas = int(sys.argv[1])
		idx = 1
		for i in range (0, num_aulas):
			idx+=1
			aula = sys.argv[idx] #--> curso
			idx+=1
			num_intervalos = sys.argv[idx]
			idx+=1
			intervalos = sys.argv[idx]
			idx+=1
			arquivo_bruto = sys.argv[idx]
			idx+=1
			arquivo_destino = sys.argv[idx]

			transmissoes.append(Transmissao(aula, intervalos, arquivo_bruto, arquivo_destino))
	
	


	# se for executado direto
	elif( len(sys.argv) == 1 ):

		print("Quantas aulas serão editadas?")
		num_aulas = int(raw_input())
		
		# popula as transmissoes
		for i in range (0, num_aulas):
			aula = list_aulas_menu() # pega a aula correta
			num_intervalos = int(list_num_intervalos()) # coleta a quantidade de intervalos que vai ter
			intervalos = list_intervalos(num_intervalos) # coleta os intervalos
			arquivo_bruto = list_input() # nome do arquivo bruto
			arquivo_destino = list_output() # nome do arquivo destino
			
			transmissoes.append(Transmissao(aula, intervalos, arquivo_bruto, arquivo_destino))
		
	
	################# OPERACOES ###################
	# executa cortes, junção e exportação do áudio
	for i in range (0, num_aulas):
		#corta
		transmissoes[i].cut_sections()
		
		#junta
		transmissoes[i].concat_sections()
		
		#exporta audio
		transmissoes[i].export_audio()
		
		sleep(60)
		
	
	# upa pro dropbox
	for i in range (0, num_aulas):
		print("drop nao")
		#sobe video
		#transmissoes[i].upload_dropbox()

	
	############### FIM OPERACOES #################

if __name__ == "__main__":
	main()