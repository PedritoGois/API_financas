import tkinter as tk
import threading
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import plotly.graph_objects as go
import plotly.io as pio
import time
import webbrowser

# Chave da API
API_KEY = 'E8AQRQQNNS0KAWGC'
symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
ts = TimeSeries(key=API_KEY, output_format='pandas')

def fetch_data(symbol):
    data, _ = ts.get_intraday(symbol=symbol, interval='1min', outputsize='compact')
    data = data.sort_index()
    data['SMA'] = data['4. close'].rolling(window=5).mean()
    return data

def atualizar():
    primeiro_abrir = True

    while True:
        try:
            divs_html = ""
            buttons_html = ""
            scripts_js = ""

            for i, symbol in enumerate(symbols):
                data = fetch_data(symbol)

                # Gera gráfico
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data.index, y=data['4. close'], mode='lines+markers', name='Preço Atual'))
                fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], mode='lines', name='SMA (5)', line=dict(dash='dash')))
                fig.update_layout(title=f'{symbol} - Preço em tempo real', xaxis_title='Horário', yaxis_title='Preço')

                # Exporta gráfico como HTML parcial
                html_chart = pio.to_html(fig, include_plotlyjs=False, full_html=False)

                # Cria uma div para esse gráfico
                div_id = f"grafico_{symbol}"
                display_style = "block" if i == 0 else "none"  # mostra o primeiro
                divs_html += f'<div id="{div_id}" style="display:{display_style}">{html_chart}</div>\n'

                # Cria botão no menu
                buttons_html += f'<button onclick="mostrarGrafico(\'{div_id}\')">{symbol}</button>\n'

            # JavaScript para alternar gráficos
            scripts_js = f"""
            <script>
            function mostrarGrafico(id) {{
                var divs = {str([f"grafico_{s}" for s in symbols])};
                divs.forEach(function(divId) {{
                    document.getElementById(divId).style.display = (divId === id) ? 'block' : 'none';
                }});
            }}
            </script>
            """

            # HTML completo
            html_final = f"""
            <html>
            <head>
                <meta http-equiv="refresh" content="30">
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {{
                        display: flex;
                        margin: 0;
                        font-family: Arial, sans-serif;
                    }}
                    .sidebar {{
                        width: 200px;
                        background: #1f2937;
                        padding: 10px;
                        height: 100vh;
                        color: white;
                        display: flex;
                        flex-direction: column;
                    }}
                    .sidebar button {{
                        margin: 5px 0;
                        padding: 10px;
                        background-color: #4b5563;
                        color: white;
                        border: none;
                        cursor: pointer;
                    }}
                    .sidebar button:hover {{
                        background-color: #6b7280;
                    }}
                    .content {{
                        flex: 1;
                        padding: 20px;
                        background: #f3f4f6;
                        overflow: auto;
                    }}
                </style>
            </head>
            <body>
                <div class="sidebar">
                    <h3>🧭 Ações</h3>
                    {buttons_html}
                </div>
                <div class="content">
                    {divs_html}
                </div>
                {scripts_js}
            </body>
            </html>
            """

            # Escreve no arquivo
            with open("monitor.html", "w", encoding="utf-8") as f:
                f.write(html_final)

            # Abre só na primeira vez
            if primeiro_abrir:
                webbrowser.open_new_tab("monitor.html")
                primeiro_abrir = False

        except Exception as e:
            print("Erro ao atualizar dados:", e)

        time.sleep(30)

def iniciar_interface():
    root = tk.Tk()
    root.title("Monitor Financeiro")

    label = tk.Label(root, text="Clique para iniciar o monitoramento em tempo real", font=('Arial', 12))
    label.pack(pady=10)

    botao = tk.Button(root, text="Iniciar", command=lambda: threading.Thread(target=atualizar).start(),
                      font=('Arial', 12), bg='green', fg='white')
    botao.pack(pady=10)

    root.mainloop()

if __name__ == '__main__':
    iniciar_interface()
