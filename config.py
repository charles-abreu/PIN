import os
# Usuario e senha do HIVE
os.environ["PIN_USER"] = ""
os.environ["PIN_PASSWORD"] = ""

#os.environ["HIVE_HOST"] = "localhost"
os.environ["HIVE_HOST"] = "hadoopmn-gsi-prod04.mpmg.mp.br"

# Diretorio onde estão os arquivos de intancias
os.environ["INSTANCE_DIR"] = "config/" 

# Caminho do file_description dentro da pasta da coleta
os.environ["FILE_DESCRIPTION_PATH"] = "data/files/file_description.jsonl"

#os.environ["PIN_KAFKA_BROKER"] = 'localhost:9099' 
os.environ["PIN_KAFKA_BROKER"] = 'hadoopdn-gsi-prod04.mpmg.mp.br:6667,hadoopdn-gsi-prod05.mpmg.mp.br:6667,hadoopdn-gsi-prod06.mpmg.mp.br:6667,hadoopdn-gsi-prod07.mpmg.mp.br:6667,hadoopdn-gsi-prod08.mpmg.mp.br:6667,hadoopdn-gsi-prod09.mpmg.mp.br:6667,hadoopdn-gsi-prod10.mpmg.mp.br:6667'
os.environ["PIN_KAFKA_TOPIC"] = 'nifi_pipeline_input_text_dev'
