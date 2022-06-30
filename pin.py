import os, sys, json, getopt
from glob import glob
from pyhive import hive

# Diretorio onde estão as instâncias
CONFIG_DIR = "config/" 
# Caminho do file_description dentro da pasta da coleta
FILE_DESCRIPTION_PATH = "data/files/""file_description.jsonl" 

# Obtem instancias para os arquivos json na pasta config
def get_config_files(coleta_dir):
    # dicionario com instâncias
    instances = {}
    # Arquivos presentes no diretorio config
    instances_files = glob(coleta_dir + os.sep + CONFIG_DIR + os.sep + "*.json")

    for nome_arquivo in instances_files:
        with open(nome_arquivo) as in_file:
            instances[os.path.basename(nome_arquivo).split(".")[0]] = json.load(in_file)
    
    return instances

# Obtem dicionario com informações dos arquivos
def get_file_description(coleta_dir):
    
    nome_arquivo = coleta_dir + os.sep + FILE_DESCRIPTION_PATH
    
    file_description = {}

    with open(nome_arquivo) as in_file:
        for line in in_file:
            l = json.loads(line)
            file_description[l["file_name"]] = l
    
    return file_description

def join_file_description(coleta_dir, cod_cidade, file_content_group):
    instances = get_config_files(coleta_dir) #OK
    file_description = get_file_description(coleta_dir) #OK

    json_arquivos = {}
    
    for json_file in file_description:
        # Gera novo evento
        json_arquivos[json_file] = {}

        # Obtem a instancia do arquivo atualpara buscar info no respectivo arquivo de intancia
        instance_id = file_description[json_file]["instance_id"]
        
        # Junção dos Atributos
        json_arquivos[json_file]["source_name"] = instances[instance_id]["source_name"]
        json_arquivos[json_file]["base_url"] = instances[instance_id]["base_url"]
        json_arquivos[json_file]["crawler_id"] = file_description[json_file]["crawler_id"]
        json_arquivos[json_file]["instance_id"]  = instance_id
        json_arquivos[json_file]["crawled_at_date"] = file_description[json_file]["crawled_at_date"]
        json_arquivos[json_file]["url"] = file_description[json_file]["url"]
        json_arquivos[json_file]["referer"] = file_description[json_file]["referer"]
        json_arquivos[json_file]["type"] = file_description[json_file]["type"]
        json_arquivos[json_file]["data_path"] = instances[instance_id]["data_path"]
        json_arquivos[json_file]["file_name"] = file_description[json_file]["file_name"]
        json_arquivos[json_file]["full_path"] = instances[instance_id]["data_path"] + "/data/files/" + file_description[json_file]["file_name"]
        json_arquivos[json_file]["cod_ibge_cidade"] = cod_cidade
        json_arquivos[json_file]["file_content_group"] = file_content_group #licitacao, processo judicial, diario oficial, etc

    return json_arquivos

# Acessa o HIVE para obter informação da cidade
def get_cod_cidade(nome_cidade, user, password):
    
    #Create Hive connection 
    conn = hive.Connection(host="127.0.0.1", 
        port=10500, 
        username=user, 
        password=password, 
        auth="LDAP",
        database="edw_dev")

    consulta = """
        SELECT cod_ibge 
        FROM dim_ibge_municipio
        WHERE sigla_uf = 'MG' AND nome_cidade = '""" + nome_cidade.upper() + """'
    """

    cursor = conn.cursor()
    cursor.execute(consulta)
    cod_ibge_cidade = cursor.fetchone()

    if cod_ibge_cidade:
        return cod_ibge_cidade[0]
    else:
        return ""

    
def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hd:c:g:o:", ['help', 'diretorio=',
                                    'cidade=','group=','outdir='])
    except getopt.GetoptError:
        print ('pin.py -d <diretorio_coleta> -c <cidade> -g <grupo> -o <out_dir>')
        sys.exit(2)

    diretorio_coleta = ''
    nome_cidade = ''
    file_content_group = ''
    out_dir = ''

    for opt, arg in opts:
        if opt == '-h':
            print ('pin.py -d <diretorio_coleta> -c <cidade> -g <grupo> -o <outdir>')
            sys.exit()
        elif opt in ("-d", "--diretorio"):
            diretorio_coleta = arg
        elif opt in ("-c", "--cidade"):
            nome_cidade = arg
        elif opt in ("-g", "--grupo"):
            file_content_group = arg
        elif opt in ("-o", "--outdir"):
            out_dir = arg
    
    
    USER = os.getenv('PIN_USER')
    PASSWORD = os.getenv('PIN_PASSWORD')

    #Consulta o HIVE para obter informação da cidade
    cod_ibge_cidade = get_cod_cidade(nome_cidade, USER, PASSWORD)
    # Executa o parser
    pin = join_file_description(diretorio_coleta, cod_ibge_cidade, file_content_group)

    file_name = "pin_" + nome_cidade.lower() + "_" + file_content_group + ".jsonl"
    with open(os.path.join(out_dir, file_name), "w") as out_file:
        for key in pin:
            out_file.write(json.dumps(pin[key]) + "\n")

def testando():
    USER = os.getenv('PIN_USER')
    PASSWORD = os.getenv('PIN_PASSWORD')
    
    diretorio_coleta = "teste/"
    nome_cidade = "Uberaba"
    file_content_group = "" #licitacao, processo judicial, diario oficial, etc

    #Consulta o HIVE para obter informação da cidade
    cod_ibge_cidade = get_cod_cidade(nome_cidade, USER, PASSWORD)
    # Executa o parser
    pin = join_file_description(diretorio_coleta, cod_ibge_cidade, file_content_group)

    print(pin['ae1f06d6-2aff-4c90-90b5-16965e73dd74.pdf.pdf'])

if __name__ == "__main__":
    main(sys.argv[1:])
    
    
    