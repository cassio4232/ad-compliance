import os
import json
import streamlit as st
import tempfile
from analyzer import analyze_video_compliance, download_universal_video, get_local_ip

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

cfg = load_config()

secret_key = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        secret_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

initial_key = secret_key or cfg.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY", "")

st.set_page_config(
    page_title="AdCompliance Inspector | YouTube Ads & Demand Gen",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FF4B4B, #FF9900);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #A0AEC0;
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
    }
    .badge-standard {
        display: inline-block;
        background-color: rgba(255, 75, 75, 0.15);
        color: #FF4B4B;
        border: 1px solid #FF4B4B;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    .card-score {
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1.5rem;
    }
    .score-green {
        background-color: rgba(40, 167, 69, 0.15);
        border: 2px solid #28a745;
        color: #28a745;
    }
    .score-yellow {
        background-color: rgba(255, 193, 7, 0.15);
        border: 2px solid #ffc107;
        color: #ffc107;
    }
    .score-red {
        background-color: rgba(220, 53, 69, 0.15);
        border: 2px solid #dc3545;
        color: #dc3545;
    }
    .issue-box {
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 5px solid #FF4B4B;
        background-color: rgba(255, 255, 255, 0.03);
    }
    .action-plan-box {
        background-color: rgba(40, 167, 69, 0.08);
        border: 1px solid rgba(40, 167, 69, 0.3);
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://www.gstatic.com/images/branding/product/2x/google_ads_64dp.png", width=50)
    st.title("Configurações")
    
    local_ip = get_local_ip()
    st.info(f"📱 **Acesso no Celular (Rede Local):**\nhttp://{local_ip}:8501")
    
    api_key_input = st.text_input(
        "Chave Gemini API (AI Studio)",
        type="password",
        value=initial_key,
        help="Obtenha gratuitamente em https://aistudio.google.com"
    )
    if api_key_input and api_key_input != initial_key:
        cfg["gemini_api_key"] = api_key_input
        save_config(cfg)
        os.environ["GEMINI_API_KEY"] = api_key_input
        st.success("Chave salva com sucesso!")
    elif initial_key:
        os.environ["GEMINI_API_KEY"] = initial_key

    st.markdown("---")
    st.markdown("### 🎯 Padrão de Auditoria")
    st.caption("✅ Rigor máximo do leilão do **Google Ads / YouTube Ads / Demand Gen** aplicado invariavelmente a qualquer formato ou fonte de vídeo.")
    st.markdown("---")
    st.caption("Desenvolvido para Media Buyers de Tráfego Direto de Alta Performance.")

# Main
st.markdown('<div class="main-title">⚡ AdCompliance Inspector</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Perícia Algorítmica de Políticas do Google Ads e Prevenção de Limitação ("Elegível - Limitado")</div>', unsafe_allow_html=True)
st.markdown('<div class="badge-standard">🎯 PADRÃO RIGOROSO: YOUTUBE ADS & DEMAND GEN (Para qualquer fonte de vídeo)</div>', unsafe_allow_html=True)

tab_link, tab_upload = st.tabs(["🌐 Link do Vídeo (YouTube, CDN, Drive, MP4 direto)", "📁 Upload de Arquivo (.MP4 / .MOV / .WEBM)"])

temp_dir = tempfile.mkdtemp()

with tab_link:
    video_url = st.text_input(
        "Cole qualquer link de vídeo (YouTube, Shorts, Link direto .mp4, Google Drive, CDN, etc.):",
        placeholder="https://... (qualquer link de vídeo)"
    )
    btn_link = st.button("🚀 Auditar Vídeo pelo Link", use_container_width=True)

with tab_upload:
    uploaded_file = st.file_uploader(
        "Envie o arquivo de vídeo do seu PC ou direto da galeria do celular:",
        type=["mp4", "mov", "webm", "mkv", "avi"]
    )
    btn_upload = st.button("🚀 Auditar Arquivo de Vídeo", use_container_width=True)

should_analyze = False
target_path = None
active_key = os.environ.get("GEMINI_API_KEY", "")

if btn_link and video_url:
    if not active_key:
        st.error("⚠️ Insira sua Gemini API Key na barra lateral para iniciar a auditoria.")
    else:
        with st.spinner("📥 Baixando vídeo da URL fornecida..."):
            try:
                target_path = download_universal_video(video_url, temp_dir)
                should_analyze = True
            except Exception as e:
                st.error(f"Erro ao baixar o vídeo: {e}")

elif btn_upload and uploaded_file:
    if not active_key:
        st.error("⚠️ Insira sua Gemini API Key na barra lateral para iniciar a auditoria.")
    else:
        with st.spinner("💾 Carregando arquivo do vídeo..."):
            target_path = os.path.join(temp_dir, uploaded_file.name)
            with open(target_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            should_analyze = True

if should_analyze and target_path and os.path.exists(target_path):
    st.video(target_path)
    
    with st.spinner("🧠 Rodando perícia multimodal (Áudio ASR + Visão OCR + Matriz YouTube/Demand Gen)..."):
        try:
            results = analyze_video_compliance(target_path, active_key)
            
            score = results.get("score_saude", 50)
            status = results.get("status_geral", "ELEGIVEL_LIMITADO")
            
            if status == "APROVADO_TOTAL":
                score_class = "score-green"
                status_label = "🟢 100% ELEGÍVEL (LIVRE PARA ESCALA NO YOUTUBE ADS)"
            elif status == "ELEGIVEL_LIMITADO":
                score_class = "score-yellow"
                status_label = "🟡 ELEGÍVEL (LIMITADO) - RISCO DE ENTREGA TRAVADA NO LEILÃO"
            else:
                score_class = "score-red"
                status_label = "🔴 REPROVAÇÃO CRÍTICA / RISCO DE SUSPENSÃO"
                
            st.markdown(f"""
            <div class="card-score {score_class}">
                <div style="font-size: 2.5rem; font-weight: 900;">Score de Saúde: {score}/100</div>
                <div style="font-size: 1.3rem; margin-top: 0.5rem;">{status_label}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📋 Diagnóstico Executivo do Perito")
            st.write(results.get("diagnostico_executivo", "Auditoria finalizada."))
            
            # NOVO BLOCO: PLANO CIRÚRGICO DE RE-APROVAÇÃO
            plano = results.get("plano_reaprovacao", {})
            st.markdown("---")
            st.markdown("## 🎯 O QUE MUDAR EXATAMENTE NO VÍDEO PARA APROVAÇÃO")
            
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### ✂️ Cortes Obrigatórios de Edição")
                    cortes = plano.get("cortes_necessarios", [])
                    if cortes:
                        for c in cortes:
                            st.error(f"❌ {c}")
                    else:
                        st.success("Nenhum corte direto de trecho obrigatório.")
                        
                    st.markdown("#### 👁️ Ajustes de Elementos Visuais")
                    visuais = plano.get("alteracoes_visuais", [])
                    if visuais:
                        for v in visuais:
                            st.warning(f"⚠️ {v}")
                    else:
                        st.info("Visual limpo de acordo com as diretrizes.")

                with col2:
                    st.markdown("#### 🎙️ Ajustes de Locução & Legenda (Antes ➔ Depois)")
                    locucoes = plano.get("alteracoes_locucao_roteiro", [])
                    if locucoes:
                        for loc in locucoes:
                            st.markdown(f"🔄 **{loc}**")
                    else:
                        st.success("Locução dentro dos padrões.")

                    st.markdown("#### ⚖️ Disclaimer Obrigatório no Rodapé")
                    disclaimer = plano.get("disclaimer_obrigatorio", "")
                    if disclaimer:
                        st.code(disclaimer, language="markdown")
                    else:
                        st.caption("Nenhum disclaimer adicional obrigatório.")

            # DETALHAMENTO SEGUNDO A SEGUNDO
            problemas = results.get("problemas", [])
            st.markdown(f"### 🔍 Detalhamento Segundo a Segundo ({len(problemas)})")
            
            if not problemas:
                st.success("Nenhum problema detectado! O criativo está em conformidade total com o YouTube Ads.")
            else:
                for idx, p in enumerate(problemas, 1):
                    sev = p.get("severidade", "MEDIO")
                    sev_badge = "🔴 CRÍTICO" if sev == "CRITICO" else ("🟡 ALERTA DE LEILÃO" if sev == "MEDIO" else "🔵 BAIXO")
                    
                    st.markdown(f"""
                    <div class="issue-box">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-weight: bold; font-size: 1.1rem;">⏱️ [{p.get('timestamp_inicio')} - {p.get('timestamp_fim')}] • {p.get('tipo')}</span>
                            <span style="font-weight: bold;">{sev_badge}</span>
                        </div>
                        <p><strong>🚨 O que o robô pegou:</strong> <em>\"{p.get('trecho_identificado')}\"</em></p>
                        <p><strong>📜 Política Google Ads Violada:</strong> {p.get('politica_violada')}</p>
                        <p><strong>🤖 Como o Algoritmo Age:</strong> {p.get('mecanismo_algoritmico')}</p>
                        <div style="background-color: rgba(40, 167, 69, 0.12); border-left: 3px solid #28a745; padding: 0.8rem; border-radius: 4px; margin-top: 0.5rem;">
                            <strong>✅ O QUE MUDAR EXATAMENTE:</strong><br>{p.get('oque_mudar_exatamente', p.get('instrucao_edicao'))}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # SEÇÃO DE EXPORTAÇÃO PARA O WHATSAPP DO EDITOR
            st.markdown("---")
            st.markdown("### 📲 Comanda Pronta para o WhatsApp do Editor")
            comanda_whats = results.get("comanda_whatsapp_editor", "")
            if not comanda_whats:
                comanda_whats = "COMANDAS DE CORREÇÃO PARA O EDITOR (COMPLIANCE GOOGLE ADS):\n\n"
                for i, c in enumerate(cortes, 1):
                    comanda_whats += f"- Corte {i}: {c}\n"
                for i, loc in enumerate(locucoes, 1):
                    comanda_whats += f"- Ajuste de fala {i}: {loc}\n"
                for i, vis in enumerate(visuais, 1):
                    comanda_whats += f"- Ajuste visual {i}: {vis}\n"
                if disclaimer:
                    comanda_whats += f"\nInserir no rodapé: {disclaimer}\n"
                    
            st.text_area("Copie e cole direto no WhatsApp do seu editor de vídeo:", value=comanda_whats, height=180)
            
            # ROTEIRO CORRIGIDO COMPLETO
            roteiro_full = results.get("roteiro_completo_corrigido", "")
            if roteiro_full:
                with st.expander("📄 Ver Roteiro Completo Já Corrigido e Adaptado"):
                    st.write(roteiro_full)
            
        except Exception as e:
            st.error(f"Erro ao processar auditoria com a IA: {e}")
