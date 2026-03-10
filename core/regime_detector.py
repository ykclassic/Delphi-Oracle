import numpy as np
from sklearn.mixture import GaussianMixture
import logging

class RegimeDetector:
    def __init__(self, n_regimes=3):
        self.model = GaussianMixture(n_components=n_regimes, random_state=42, n_init=5)

    def classify(self, df):
        """Classifies market regime with safety checks for empty slices."""
        try:
            # 1. Feature Engineering
            close = df['Close'].tail(100)
            returns = np.log(close / close.shift(1)).fillna(0)
            volatility = returns.rolling(window=10).std().fillna(0)
            
            features = np.column_stack([returns, volatility])
            
            # 2. Fit ML Model
            self.model.fit(features)
            labels = self.model.predict(features)
            current_label = labels[-1]
            
            # 3. Handle Potential Empty Clusters (Fixes the RuntimeWarning)
            cluster_vols = []
            for i in range(3):
                subset = features[labels == i, 1]
                if len(subset) > 0:
                    cluster_vols.append(subset.mean())
                else:
                    cluster_vols.append(float('inf')) # Push empty clusters to 'Chaos'
            
            # 4. Rank by Volatility: 0=Low, 1=Medium, 2=High
            rank = np.argsort(cluster_vols)
            
            if current_label == rank[0]: return 0   # Range
            if current_label == rank[1]: return 1   # Trend
            return 2                               # Chaos
            
        except Exception as e:
            logging.error(f"Regime Detection Error: {e}")
            return 0 # Default to Range (conservative)
