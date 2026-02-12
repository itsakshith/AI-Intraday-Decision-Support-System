import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_fetcher import fetch_market_data
from indicators import calculate_rsi, calculate_macd, calculate_ema, calculate_bollinger_bands
from patterns import detect_patterns
from decision_engine import generate_signals

# Page Configuration
st.set_page_config(page_title="Intraday Market Decision Support", layout="wide")

st.title("📈 AI-Based Intraday Market Decision Support System")
st.markdown("### Market Data & Technical Indicators")

# Sidebar for User Input
st.sidebar.header("Data Settings")
ticker = st.sidebar.text_input("Enter Ticker Symbol", value="^NSEI")
period = st.sidebar.selectbox("Period", options=["1d", "5d", "1mo"], index=0)
interval = st.sidebar.selectbox("Interval", options=["1m", "5m", "15m", "1h", "1d"], index=1)

st.sidebar.header("Technical Indicators")
show_ema = st.sidebar.checkbox("Show EMA", value=True)
ema_period = st.sidebar.slider("EMA Period", 10, 200, 20)
show_bb = st.sidebar.checkbox("Show Bollinger Bands", value=True)
show_rsi = st.sidebar.checkbox("Show RSI", value=True)
show_macd = st.sidebar.checkbox("Show MACD", value=False)
show_signals = st.sidebar.checkbox("Show Trade Signals (Rule-Based)", value=True)

st.sidebar.header("Pattern Recognition")
show_patterns = st.sidebar.expander("Candlestick Patterns", expanded=False)
with show_patterns:
    show_doji = st.checkbox("Show Doji", value=False)
    show_hammer = st.checkbox("Show Hammer", value=False)
    show_engulfing = st.checkbox("Show Engulfing", value=False)

if st.sidebar.button("Fetch Data"):
    with st.spinner(f"Fetching data for {ticker}..."):
        fetched_df = fetch_market_data(ticker, period, interval)
        
        if not fetched_df.empty:
            st.session_state['market_data'] = fetched_df
            st.session_state['ticker'] = ticker
            st.success(f"Successfully fetched {len(fetched_df)} rows.")
        else:
            st.error("No data found! Please check the ticker symbol and try again.")
            st.info("Note: Indian stocks usually require '.NS' suffix (e.g., RELIANCE.NS). Indices like Nifty 50 use '^NSEI'.")

# Check if data exists in session state
if 'market_data' in st.session_state:
    df = st.session_state['market_data'].copy()
    current_ticker = st.session_state.get('ticker', ticker)
    
    # Calculate Indicators
    # Note: decision_engine requires specific columns. We ensure they are calculated if signals are requested.
    
    # Always calculate basics if Signals are ON
    # STRICT INDEPENDENCE: Calculate ONLY if toggled
    
    if show_ema:
        df['EMA'] = calculate_ema(df, period=ema_period)
    if show_bb:
        df['BB_Upper'], df['BB_Lower'] = calculate_bollinger_bands(df)
    if show_rsi:
        df['RSI'] = calculate_rsi(df)
    if show_macd:
        df['MACD'], df['MACD_Signal'], df['Hist'] = calculate_macd(df)
        
    # Pattern Recognition
    if show_doji or show_hammer or show_engulfing:
        df = detect_patterns(df)
        
    # Decision Engine Signals
    if show_signals:
        try:
            df = generate_signals(df)
        except Exception as e:
            st.error(f"Error generating signals: {e}")

    # Create Subplots
    rows = 1
    row_heights = [0.7]
    
    if show_rsi:
        rows += 1
        row_heights.append(0.15)
    if show_macd:
        rows += 1
        row_heights.append(0.15)
        
    specs = [[{"secondary_y": False}]]
    if show_rsi:
        specs.append([{"secondary_y": False}])
    if show_macd:
        specs.append([{"secondary_y": False}])

    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=row_heights,
                        specs=specs)

    # 1. Main Chart
    fig.add_trace(go.Candlestick(x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name="OHLC",
        increasing=dict(line=dict(color="#00FF66"), fillcolor="#00CC66"),
        decreasing=dict(line=dict(color="white"), fillcolor="white")
        ), row=1, col=1)

    # Overlays
    if show_ema:
        if 'EMA' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA'], 
                mode='lines', name=f'EMA {ema_period}', line=dict(color='teal')), row=1, col=1)
    
    if show_bb:
        if 'BB_Upper' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], 
                mode='lines', name='BB Upper', line=dict(color='gray', width=1), showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], 
                mode='lines', name='BB Lower', line=dict(color='gray', width=1), fill='tonexty', fillcolor='rgba(128,128,128,0.1)', showlegend=False), row=1, col=1)

    # Patterns Markers
    if show_doji and 'Pattern_Doji' in df.columns:
        doji_df = df[df['Pattern_Doji']]
        if not doji_df.empty:
            fig.add_trace(go.Scatter(x=doji_df.index, y=doji_df['High'], 
                mode='markers', name='Doji', marker=dict(symbol='cross', size=8, color='yellow')), row=1, col=1)

    if show_hammer and 'Pattern_Hammer' in df.columns:
        hammer_df = df[df['Pattern_Hammer']]
        if not hammer_df.empty:
            fig.add_trace(go.Scatter(x=hammer_df.index, y=hammer_df['Low'], 
                mode='markers', name='Hammer', marker=dict(symbol='triangle-up', size=10, color='lime')), row=1, col=1)

    if show_engulfing:
        if 'Pattern_Bullish_Engulfing' in df.columns:
            bull_eng = df[df['Pattern_Bullish_Engulfing']]
            if not bull_eng.empty:
                fig.add_trace(go.Scatter(x=bull_eng.index, y=bull_eng['Low'], 
                    mode='markers', name='Bull Engulf', marker=dict(symbol='triangle-up-dot', size=10, color='green')), row=1, col=1)
        
        if 'Pattern_Bearish_Engulfing' in df.columns:
            bear_eng = df[df['Pattern_Bearish_Engulfing']]
            if not bear_eng.empty:
                fig.add_trace(go.Scatter(x=bear_eng.index, y=bear_eng['High'], 
                    mode='markers', name='Bear Engulf', marker=dict(symbol='triangle-down-dot', size=10, color='red')), row=1, col=1)

    # Trade Signals
    # Trade Signals
    if show_signals:
        # 1. EMA Crossovers
        if show_ema and 'EMA' in df.columns:
            # BUY: Close crosses ABOVE EMA
            ema_buy = (df['Close'] > df['EMA']) & (df['Close'].shift(1) <= df['EMA'].shift(1))
            # SELL: Close crosses BELOW EMA
            ema_sell = (df['Close'] < df['EMA']) & (df['Close'].shift(1) >= df['EMA'].shift(1))
            
            if ema_buy.any():
                fig.add_trace(go.Scatter(x=df.index[ema_buy], y=df.loc[ema_buy, 'Low'] * 0.999,
                    mode='markers', name='EMA Buy', marker=dict(symbol='triangle-up', size=10, color='green')), row=1, col=1)
            if ema_sell.any():
                fig.add_trace(go.Scatter(x=df.index[ema_sell], y=df.loc[ema_sell, 'High'] * 1.001,
                    mode='markers', name='EMA Sell', marker=dict(symbol='triangle-down', size=10, color='red')), row=1, col=1)

        # 2. RSI Crossovers
        if show_rsi and 'RSI' in df.columns:
            # BUY: RSI crosses ABOVE 30
            rsi_buy = (df['RSI'] > 30) & (df['RSI'].shift(1) <= 30)
            # SELL: RSI crosses BELOW 70
            rsi_sell = (df['RSI'] < 70) & (df['RSI'].shift(1) >= 70)
            
            if rsi_buy.any():
                fig.add_trace(go.Scatter(x=df.index[rsi_buy], y=df.loc[rsi_buy, 'Low'] * 0.998,
                    mode='markers', name='RSI Buy', marker=dict(symbol='circle', size=8, color='blue')), row=1, col=1)
            if rsi_sell.any():
                fig.add_trace(go.Scatter(x=df.index[rsi_sell], y=df.loc[rsi_sell, 'High'] * 1.002,
                    mode='markers', name='RSI Sell', marker=dict(symbol='circle', size=8, color='yellow')), row=1, col=1)

        # 3. MACD Crossovers
        if show_macd and 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            # BUY: MACD crosses ABOVE Signal
            macd_buy = (df['MACD'] > df['MACD_Signal']) & (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1))
            # SELL: MACD crosses BELOW Signal
            macd_sell = (df['MACD'] < df['MACD_Signal']) & (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1))

            if macd_buy.any():
                fig.add_trace(go.Scatter(x=df.index[macd_buy], y=df.loc[macd_buy, 'Low'] * 0.997,
                    mode='markers', name='MACD Buy', marker=dict(symbol='star', size=10, color='cyan')), row=1, col=1)
            if macd_sell.any():
                fig.add_trace(go.Scatter(x=df.index[macd_sell], y=df.loc[macd_sell, 'High'] * 1.003,
                    mode='markers', name='MACD Sell', marker=dict(symbol='x', size=10, color='orange')), row=1, col=1)

        # 4. Bollinger Bands Touch/Cross
        if show_bb and 'BB_Lower' in df.columns and 'BB_Upper' in df.columns:
            # BUY: Close touches or crosses BELOW Lower Band (using crossover logic for plotting)
            bb_buy = (df['Close'] <= df['BB_Lower']) & (df['Close'].shift(1) > df['BB_Lower'].shift(1))
            # SELL: Close touches or crosses ABOVE Upper Band
            bb_sell = (df['Close'] >= df['BB_Upper']) & (df['Close'].shift(1) < df['BB_Upper'].shift(1))
            
            if bb_buy.any():
                fig.add_trace(go.Scatter(x=df.index[bb_buy], y=df.loc[bb_buy, 'Low'] * 0.996,
                    mode='markers', name='BB Buy', marker=dict(symbol='triangle-up', size=10, color='purple')), row=1, col=1)
            if bb_sell.any():
                fig.add_trace(go.Scatter(x=df.index[bb_sell], y=df.loc[bb_sell, 'High'] * 1.004,
                    mode='markers', name='BB Sell', marker=dict(symbol='triangle-down', size=10, color='brown')), row=1, col=1)


    current_row = 2
    
    # RSI
    if show_rsi:
        if 'RSI' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='purple')), row=current_row, col=1)
            fig.add_shape(type="line", x0=df.index[0], x1=df.index[-1], y0=70, y1=70, line=dict(color="red", width=1, dash="dash"), row=current_row, col=1)
            fig.add_shape(type="line", x0=df.index[0], x1=df.index[-1], y0=30, y1=30, line=dict(color="green", width=1, dash="dash"), row=current_row, col=1)
            fig.update_yaxes(title_text="RSI", range=[0, 100], row=current_row, col=1)
            current_row += 1

    # MACD
    if show_macd:
        if 'MACD' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name="MACD", line=dict(color='blue')), row=current_row, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name="Signal", line=dict(color='orange')), row=current_row, col=1)
            fig.add_trace(go.Bar(x=df.index, y=df['Hist'], name="Hist"), row=current_row, col=1)
            fig.update_yaxes(title_text="MACD", row=current_row, col=1)

    fig.update_layout(title=f"{current_ticker} - {interval} Intraday Analysis",
                      xaxis_title="Time",
                      height=800,
                      xaxis_rangeslider_visible=False)
    
    st.plotly_chart(fig, width="stretch")

    # 📌 Trade Signals Section
    if show_signals:
        st.markdown("### 📌 Trade Signals")
        last_row = df.iloc[-1]
        active_signals = []

        if 'Signal_EMA' in df.columns:
            sig = last_row['Signal_EMA']
            if sig == 1: active_signals.append("• **EMA**: :green[BUY] (Close > EMA)")
            elif sig == -1: active_signals.append("• **EMA**: :red[SELL] (Close < EMA)")

        if 'Signal_RSI' in df.columns:
            sig = last_row['Signal_RSI']
            if sig == 1: active_signals.append("• **RSI**: :green[BUY] (Oversold < 30)")
            elif sig == -1: active_signals.append("• **RSI**: :red[SELL] (Overbought > 70)")

        if 'Signal_MACD' in df.columns:
            sig = last_row['Signal_MACD']
            if sig == 1: active_signals.append("• **MACD**: :green[BUY] (MACD > Signal)")
            elif sig == -1: active_signals.append("• **MACD**: :red[SELL] (MACD < Signal)")

        if 'Signal_BB' in df.columns:
            sig = last_row['Signal_BB']
            if sig == 1: active_signals.append("• **Bollinger Bands**: :green[BUY] (Price < Lower Band)")
            elif sig == -1: active_signals.append("• **Bollinger Bands**: :red[SELL] (Price > Upper Band)")

        if active_signals:
            for s in active_signals:
                st.markdown(s)
        else:
            st.info("HOLD – No active signals")


    # Display Data Table with Patterns
    with st.expander("View Raw Data", expanded=False):
        # Format boolean columns to text for better readability if present
        display_df = df.copy()
        if 'Pattern_Doji' in display_df.columns:
            display_df['Doji'] = display_df['Pattern_Doji'].apply(lambda x: '✅' if x else '')
        if 'Pattern_Hammer' in display_df.columns:
            display_df['Hammer'] = display_df['Pattern_Hammer'].apply(lambda x: '✅' if x else '')
            
        # Dynamic Column Selection
        columns_to_show = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        if show_ema and 'EMA' in display_df.columns:
            columns_to_show.append('EMA')
            
        if show_rsi and 'RSI' in display_df.columns:
            columns_to_show.append('RSI')
            
        if show_macd:
            if 'MACD' in display_df.columns: columns_to_show.append('MACD')
            if 'MACD_Signal' in display_df.columns: columns_to_show.append('MACD_Signal')
            if 'Hist' in display_df.columns: columns_to_show.append('Hist')
            
        if show_bb:
            if 'BB_Upper' in display_df.columns: columns_to_show.append('BB_Upper')
            if 'BB_Lower' in display_df.columns: columns_to_show.append('BB_Lower')
            
        # Add Pattern columns if generated
        if 'Doji' in display_df.columns: columns_to_show.append('Doji')
        if 'Hammer' in display_df.columns: columns_to_show.append('Hammer')

        # Filter and Display
        # Only format numeric columns
        numeric_cols = [c for c in columns_to_show if c not in ['Doji', 'Hammer']]
        st.dataframe(display_df[columns_to_show].style.format("{:.2f}", subset=numeric_cols))


st.sidebar.markdown("---")
st.sidebar.info("Developed for Academic Review")
