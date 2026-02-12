import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from decision_engine import generate_signals

class TestDecisionEngine(unittest.TestCase):
    def setUp(self):
        # Create a base dataframe with neutral values
        self.base_df = pd.DataFrame({
            'Close': [100.0] * 5,
            'RSI': [50.0] * 5,
            'MACD': [0.0] * 5,
            'MACD_Signal': [0.0] * 5,
            'BB_Upper': [110.0] * 5,
            'BB_Lower': [90.0] * 5
        })

    def test_rsi_buy(self):
        df = self.base_df.copy()
        df.loc[4, 'RSI'] = 25.0
        result = generate_signals(df)
        self.assertEqual(result.iloc[4]['Signal'], 1)
        self.assertIn("RSI Oversold", result.iloc[4]['Signal_Reason'])

    def test_rsi_sell(self):
        df = self.base_df.copy()
        df.loc[4, 'RSI'] = 75.0
        result = generate_signals(df)
        self.assertEqual(result.iloc[4]['Signal'], -1)
        self.assertIn("RSI Overbought", result.iloc[4]['Signal_Reason'])

    def test_macd_buy_crossover(self):
        df = self.base_df.copy()
        # Row 3: MACD <= Signal (0 <= 0) - Neutral/Bearish setup
        # Row 4: MACD > Signal (1 > 0) - Bullish Crossover
        df.loc[3, 'MACD'] = 0.0
        df.loc[3, 'MACD_Signal'] = 0.0
        df.loc[4, 'MACD'] = 1.0
        df.loc[4, 'MACD_Signal'] = 0.0
        
        result = generate_signals(df)
        self.assertEqual(result.iloc[4]['Signal'], 1)
        self.assertIn("MACD Bullish Crossover", result.iloc[4]['Signal_Reason'])

    def test_macd_no_crossover_just_continuation(self):
        df = self.base_df.copy()
        # Row 3: MACD > Signal already (1 > 0)
        # Row 4: MACD > Signal still (2 > 0)
        # Should NOT trigger crossover signal if logic is strict about crossover
        df.loc[3, 'MACD'] = 1.0
        df.loc[3, 'MACD_Signal'] = 0.0
        df.loc[4, 'MACD'] = 2.0
        df.loc[4, 'MACD_Signal'] = 0.0
        
        result = generate_signals(df)
        self.assertEqual(result.iloc[4]['Signal'], 0) # Expect Hold
        # Because prev_macd (1) > prev_signal (0), so (prev_macd <= prev_signal) is calc as False

    def test_bollinger_buy(self):
        df = self.base_df.copy()
        df.loc[4, 'Close'] = 89.0 # Below BB_Lower (90)
        result = generate_signals(df)
        self.assertEqual(result.iloc[4]['Signal'], 1)
        self.assertIn("Price below BB Lower", result.iloc[4]['Signal_Reason'])

if __name__ == '__main__':
    unittest.main()
