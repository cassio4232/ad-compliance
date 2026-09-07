Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\cassi\.gemini\antigravity\scratch\ad_compliance_app"
WshShell.Run "python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501", 0, False
WScript.Sleep 2000
WshShell.Run "http://localhost:8501"
