import numpy as np
from typing import Dict, Any, List

class TradingStrategies:
    """استراتيجيات التداول المختلفة"""
    
    @staticmethod
    def rsi_strategy(prices: List[float], period: int = 14, oversold: int = 30, overbought: int = 70) -> Dict:
        """استراتيجية RSI"""
        if len(prices) < period:
            return {"signal": "neutral", "reason": "بيانات غير كافية"}
        
        # حساب RSI
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        # اتخاذ القرار
        if rsi <= oversold:
            return {"signal": "call", "reason": f"RSI منخفض ({rsi:.2f}) - منطقة تشبع بيعي", "rsi": rsi}
        elif rsi >= overbought:
            return {"signal": "put", "reason": f"RSI مرتفع ({rsi:.2f}) - منطقة تشبع شرائي", "rsi": rsi}
        else:
            return {"signal": "neutral", "reason": f"RSI محايد ({rsi:.2f})", "rsi": rsi}
    
    @staticmethod
    def macd_strategy(prices: List[float]) -> Dict:
        """استراتيجية MACD"""
        if len(prices) < 26:
            return {"signal": "neutral", "reason": "بيانات غير كافية"}
        
        # حساب EMA السريع والبطيء
        ema12 = TradingStrategies._calculate_ema(prices, 12)
        ema26 = TradingStrategies._calculate_ema(prices, 26)
        
        if len(ema12) < 2 or len(ema26) < 2:
            return {"signal": "neutral", "reason": "بيانات غير كافية"}
        
        macd_line = ema12[-1] - ema26[-1]
        macd_prev = ema12[-2] - ema26[-2]
        
        # حساب خط الإشارة (EMA9 للماكد)
        macd_values = []
        for i in range(9, len(prices)):
            if i >= 12 and i >= 26:
                macd_values.append(ema12[i - min(12, len(ema12)-1)] - ema26[i - min(26, len(ema26)-1)])
        
        if len(macd_values) >= 9:
            signal_line = TradingStrategies._calculate_ema(macd_values, 9)
            if len(signal_line) > 0:
                if macd_line > signal_line[-1] and macd_prev <= signal_line[-2] if len(signal_line) >= 2 else False:
                    return {"signal": "call", "reason": "تقاطع MACD للأعلى (إشارة شراء)", "macd": macd_line}
                elif macd_line < signal_line[-1] and macd_prev >= signal_line[-2] if len(signal_line) >= 2 else False:
                    return {"signal": "put", "reason": "تقاطع MACD للأسفل (إشارة بيع)", "macd": macd_line}
        
        return {"signal": "neutral", "reason": "لا توجد إشارة واضحة", "macd": macd_line}
    
    @staticmethod
    def bollinger_strategy(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict:
        """استراتيجية Bollinger Bands"""
        if len(prices) < period:
            return {"signal": "neutral", "reason": "بيانات غير كافية"}
        
        # حساب المتوسط المتحرك والانحراف المعياري
        sma = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        current_price = prices[-1]
        
        # اتخاذ القرار
        if current_price <= lower_band:
            return {"signal": "call", "reason": f"السعر عند النطاق السفلي ({current_price:.5f}) - متوقع ارتداد لأعلى", 
                    "upper": upper_band, "lower": lower_band}
        elif current_price >= upper_band:
            return {"signal": "put", "reason": f"السعر عند النطاق العلوي ({current_price:.5f}) - متوقع ارتداد لأسفل",
                    "upper": upper_band, "lower": lower_band}
        else:
            return {"signal": "neutral", "reason": f"السعر داخل النطاق ({current_price:.5f})", 
                    "upper": upper_band, "lower": lower_band}
    
    @staticmethod
    def _calculate_ema(prices: List[float], period: int) -> List[float]:
        """حساب EMA"""
        if len(prices) < period:
            return []
        
        ema = [np.mean(prices[:period])]
        multiplier = 2 / (period + 1)
        
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    @staticmethod
    def combined_strategy(prices: List[float]) -> Dict:
        """استراتيجية مدمجة من عدة مؤشرات"""
        rsi_signal = TradingStrategies.rsi_strategy(prices)
        macd_signal = TradingStrategies.macd_strategy(prices)
        bollinger_signal = TradingStrategies.bollinger_strategy(prices)
        
        # ترجيح الإشارات
        signals = []
        if rsi_signal["signal"] != "neutral":
            signals.append(rsi_signal["signal"])
        if macd_signal["signal"] != "neutral":
            signals.append(macd_signal["signal"])
        if bollinger_signal["signal"] != "neutral":
            signals.append(bollinger_signal["signal"])
        
        if not signals:
            return {"signal": "neutral", "reason": "لا توجد إشارات متوافقة", "details": {"rsi": rsi_signal, "macd": macd_signal, "bollinger": bollinger_signal}}
        
        # غالبية الإشارات
        call_count = signals.count("call")
        put_count = signals.count("put")
        
        if call_count > put_count:
            return {"signal": "call", "reason": f"إشارات متوافقة: {call_count} Call, {put_count} Put", "details": {"rsi": rsi_signal, "macd": macd_signal, "bollinger": bollinger_signal}}
        elif put_count > call_count:
            return {"signal": "put", "reason": f"إشارات متوافقة: {call_count} Call, {put_count} Put", "details": {"rsi": rsi_signal, "macd": macd_signal, "bollinger": bollinger_signal}}
        else:
            return {"signal": "neutral", "reason": "إشارات متساوية - انتظار", "details": {"rsi": rsi_signal, "macd": macd_signal, "bollinger": bollinger_signal}}