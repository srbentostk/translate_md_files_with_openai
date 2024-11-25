import os
import threading
import time
from openai import OpenAI

# Diretórios de entrada e saída
input_dir = './arquivos_md'
output_dir = './arquivos_traduzidos'

# Garantir que o diretório de saída existe
os.makedirs(output_dir, exist_ok=True)

# Inicializar o cliente OpenAI
client = OpenAI()

# Eventos para controle do script
pause_event = threading.Event()
stop_event = threading.Event()

# Função para ouvir comandos do usuário


def input_listener():
    while not stop_event.is_set():
        user_input = input()
        if user_input.lower() == 'p':
            if not pause_event.is_set():
                pause_event.set()
                print("Script pausado. Digite 'r' para retomar ou 's' para parar.")
            else:
                print("O script já está pausado.")
        elif user_input.lower() == 'r':
            if pause_event.is_set():
                pause_event.clear()
                print("Script retomado.")
            else:
                print("O script não está pausado.")
        elif user_input.lower() == 's':
            stop_event.set()
            print("Script interrompido pelo usuário.")
        else:
            print(
                "Comando não reconhecido. Use 'p' para pausar, 'r' para retomar, 's' para parar.")

# Função para ler arquivos .md e traduzi-los


def traduzir_arquivos_md():
    for filename in os.listdir(input_dir):
        if stop_event.is_set():
            print("Processo interrompido.")
            break

        if filename.endswith('.md'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            # Ler o conteúdo do arquivo
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()

           # Preparar as mensagens para a API
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Você é um tradutor especializado em adaptar conteúdos para o português brasileiro. "
                        "Sua tarefa é traduzir o seguinte arquivo Markdown, que contém prompts do ChatGPT, "
                        "mantendo o formato original e ajustando o conteúdo para que faça sentido no contexto brasileiro. "
                        "Apenas forneça a tradução do arquivo, sem adicionar comentários ou explicações."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Por favor, traduza o seguinte conteúdo Markdown para o português brasileiro, "
                        "mantendo o formato e adaptando o contexto para a realidade brasileira:\n\n"
                        "```markdown\n"
                        f"{content}\n"
                        "```"
                    )
                }
            ]

            # Verificar se o script está pausado
            while pause_event.is_set():
                print("Script está pausado. Aguardando...")
                time.sleep(2)
                if stop_event.is_set():
                    print("Processo interrompido.")
                    return

            try:
                # Chamar a API da OpenAI
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2048,
                    top_p=1
                )

                # Extrair o conteúdo traduzido
                translated_content = response.choices[0].message.content

                # Salvar o conteúdo traduzido no arquivo de saída
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(translated_content)

                print(f"Arquivo traduzido: {filename}")

            except Exception as e:
                print(f"Erro ao traduzir {filename}: {e}")

    print("Processamento concluído.")

if __name__ == "__main__":
    # Iniciar o thread de escuta de comandos
    listener_thread = threading.Thread(target=input_listener, daemon=True)
    listener_thread.start()

    # Iniciar o processo de tradução
    traduzir_arquivos_md()
