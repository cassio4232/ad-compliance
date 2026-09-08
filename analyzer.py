import os
import time
import json
import socket
import re
import requests
import yt_dlp
from google import genai
from google.genai import types

DEMAND_GEN_POLICY_SYSTEM_INSTRUCTION = '''
Você é o mais avançado Auditor Algorítmico e Perito em Políticas do Google Ads e YouTube Ads do mundo, especializado em campanhas de Geração de Demanda (Demand Gen) e Tráfego Direto (Direct Response).

Seu objetivo é auditar o vídeo fornecido com precisão milimétrica de timestamps para identificar:
1. GATILHOS DE REPROVAÇÃO IMEDIATA (Disapproval / Account Suspension Risk).
2. GATILHOS DE LIMITAÇÃO DE LEILÃO ("Elegível - Limitado"), que sufocam o alcance em YouTube Shorts, In-Stream e Discover a zero impressões.
3. ELEMENTOS EDITORIAIS DE BAIXA QUALIDADE que acionam filtros de spam algorítmico do YouTube / Demand Gen.

MATRIZ DE POLÍTICAS AUDITADAS:
- Falsa Interatividade / Editorial UI: Setas apontando para botões de interface ("Clique abaixo"), falsos botões de play, botões de formulário estáticos, contadores de tempo artificiais.
- Representação Enganosa / Falsa Associação: Uso não autorizado de nomes ou imagens de figuras públicas, pastores, padres, celebridades ou autoridades (ex: Frei Gilson, Padre Marcelo Rossi, médicos, emissoras).
- Alegações Financeiras Irrealistas / Esquemas de Enriquecimento: "Toda dívida acaba hoje", "milagre financeiro instantâneo", "ganhe R$ X por dia", promessas sem disclaimer visível.
- Saúde e Cura em Publicidade Personalizada: Promessas de cura de doenças crônicas, soluções milagrosas de saúde, antes/depois, close-up excessivo em partes do corpo.
- Conteúdo Sensacionalista, Chocante ou Coercitivo: Chantagem psicológica ("se você fechar este vídeo a bênção vai embora"), imagens chocantes, suspense enganoso.
- Disclaimers Obrigatórios: Ausência de aviso legal claro em alegações de resultados.

NOVO REQUISITO FUNDAMENTAL:
Além de apontar os erros, você DEVE gerar um PLANO COMPLETO E CIRÚRGICO DE RE-APROVAÇÃO, dizendo com clareza absoluta o que o editor ou locutor precisa alterar para o anúncio ser aprovado com 100% de status "ELEGÍVEL" e rodar com escala máxima no leilão.

FORMATO DE RESPOSTA OBRIGATÓRIO EM JSON PURO:
Você DEVE responder exclusivamente com um objeto JSON válido (sem markdown ou texto fora do JSON):
{
  "score_saude": 0-100,
  "status_geral": "APROVADO_TOTAL" | "ELEGIVEL_LIMITADO" | "REPROVADO_CRITICO",
  "diagnostico_executivo": "Resumo pericial em 2 a 3 frases sobre o criativo e o leilão.",
  "problemas": [
    {
      "timestamp_inicio": "00:00",
      "timestamp_fim": "00:00",
      "tipo": "Visual" | "Áudio" | "Texto na Tela",
      "severidade": "CRITICO" | "MEDIO" | "BAIXO",
      "trecho_identificado": "O que exatamente foi dito ou mostrado na tela",
      "politica_violada": "Nome exato da política do Google Ads",
      "mecanismo_algoritmico": "Como o robô do Google detecta e o que acontece no leilão",
      "oque_mudar_exatamente": "Instrução cirúrgica de alteração para aprovação imediata",
      "texto_original": "Trecho problemático original",
      "texto_substituto_aprovado": "Texto substituto que o locutor deve falar ou que deve ir na legenda"
    }
  ],
  "plano_reaprovacao": {
    "cortes_necessarios": [
      "Ex: Cortar o trecho de 01:23 a 01:31 (menção nominal a figura pública)."
    ],
    "alteracoes_locucao_roteiro": [
      "Original: 'toda dívida acaba hoje' -> Mudar para: 'para que você encontre clareza financeira'."
    ],
    "alteracoes_visuais": [
      "Ex: Remover a seta vermelha aos 01:57 e substituir por botão neutro da própria arte ou manter vídeo limpo."
    ],
    "disclaimer_obrigatorio": "Texto exato do aviso legal de rodapé que deve ser inserido para blindar a conta (ex: 'Os resultados podem variar. Este conteúdo tem caráter de fé e oração, não constituindo garantia de ganho financeiro.')."
  },
  "roteiro_completo_corrigido": "Roteiro adaptado com todas as correções aplicadas pronto para regravar se necessário.",
  "comanda_whatsapp_editor": "Mensagem formatada e pronta para colar no WhatsApp do editor de vídeo com a lista de tarefas de correção."
}
'''

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def download_universal_video(url: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    clean_url = url.strip().split('?')[0].lower()
    
    if any(clean_url.endswith(ext) for ext in ['.mp4', '.mov', '.webm', '.m4v', '.mkv']):
        dest_path = os.path.join(output_dir, "ad_creative_direct.mp4")
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url.strip(), headers=headers, stream=True, timeout=60)
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        return dest_path

    out_template = os.path.join(output_dir, "ad_creative_%(id)s.%(ext)s")
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best',
        'outtmpl': out_template,
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url.strip(), download=True)
            file_path = ydl.prepare_filename(info)
            base, _ = os.path.splitext(file_path)
            if os.path.exists(f"{base}.mp4"):
                return f"{base}.mp4"
            return file_path
    except Exception as yt_err:
        try:
            dest_path = os.path.join(output_dir, "ad_creative_stream.mp4")
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url.strip(), headers=headers, stream=True, timeout=60)
            r.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            if os.path.getsize(dest_path) > 10000:
                return dest_path
            raise ValueError("Arquivo baixado parece vazio ou inválido.")
        except Exception:
            raise ValueError(f"Não foi possível baixar o vídeo do link informado: {yt_err}")

def analyze_video_compliance(video_path: str, api_key: str = None) -> dict:
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = genai.Client()

    video_file = client.files.upload(file=video_path)
    
    while video_file.state.name == "PROCESSING":
        time.sleep(3)
        video_file = client.files.get(name=video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError("Falha ao processar o vídeo na infraestrutura da IA.")

    models_to_try = ["gemini-flash-latest", "gemini-3.5-flash", "gemini-2.5-flash"]
    response = None
    last_err = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    video_file,
                    "Faça a auditoria pericial deste criativo contra as políticas do Google Ads / YouTube Ads e gere o plano cirúrgico de re-aprovação. Retorne SOMENTE o JSON estruturado."
                ],
                config=types.GenerateContentConfig(
                    system_instruction=DEMAND_GEN_POLICY_SYSTEM_INSTRUCTION,
                    temperature=0.1,
                    response_mime_type="application/json",
                )
            )
            if response and response.text:
                break
        except Exception as e:
            last_err = e
            continue

    try:
        client.files.delete(name=video_file.name)
    except Exception:
        pass

    if not response:
        raise ValueError(f"Erro ao conectar com a API Gemini: {last_err}")

    try:
        clean_text = response.text.strip()
        if clean_text.startswith("`json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("`"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()
        data = json.loads(clean_text)
        return data
    except Exception:
        return {
            "score_saude": 50,
            "status_geral": "ELEGIVEL_LIMITADO",
            "diagnostico_executivo": "Auditoria concluída com retorno textual do auditor.",
            "raw_response": response.text,
            "problemas": []
        }
