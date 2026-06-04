import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from quotexapi import Quotex
from strategies import TradingStrategies

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuotexBot:
    """بوت التداول الآلي لـ Quotex"""
    
    def __init__(self, email: str, password: str, demo_mode: bool = True):
        self.email = email
        self.password = password
        self.demo_mode = demo_mode
        self.client = None
        self.is_running = False
        self.current_strategy = "combined"
        self.trade_history = []
        self.statistics = {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "profit": 0.0,
            "current_balance": 0.0
        }
        
    async def connect(self) -> bool:
        """الاتصال بـ Quotex"""
        try:
            self.client = Quotex(
                email=self.email,
                password=self.password,
                lang="en"
            )
            
            # تعيين وضع الحساب (حقيقي أو تجريبي)
            mode = "PRACTICE" if self.demo_mode else "REAL"
            self.client.set_account_mode(mode)
            
            check, reason = await self.client.connect()
            
            if check:
                logger.info(f"✅ تم الاتصال بنجاح - وضع {'تجريبي' if self.demo_mode else 'حقيقي'}")
                # جلب الرصيد
                self.statistics["current_balance"] = await self.client.get_balance()
                return True
            else:
                logger.error(f"❌ فشل الاتصال: {reason}")
                return False
                
        except Exception as e:
            logger.error(f"❌ خطأ في الاتصال: {str(e)}")
            return False
    
    async def get_market_data(self, asset: str, duration: int = 60) -> Optional[list]:
        """جلب بيانات السوق"""
        try:
            candles = await self.client.get_candles(asset, None, duration * 50, duration)
            if candles:
                prices = [float(candle["close"]) for candle in candles]
                return prices
            return None
        except Exception as e:
            logger.error(f"خطأ في جلب البيانات: {str(e)}")
            return None
    
    async def analyze_market(self, asset: str) -> Dict:
        """تحليل السوق واتخاذ القرار"""
        try:
            # جلب بيانات 100 شمعة للتحليل
            prices = await self.get_market_data(asset, 60)
            
            if not prices or len(prices) < 50:
                return {"signal": "neutral", "reason": "بيانات غير كافية للتحليل"}
            
            # تطبيق الاستراتيجية المختارة
            if self.current_strategy == "rsi":
                signal = TradingStrategies.rsi_strategy(prices)
            elif self.current_strategy == "macd":
                signal = TradingStrategies.macd_strategy(prices)
            elif self.current_strategy == "bollinger":
                signal = TradingStrategies.bollinger_strategy(prices)
            else:  # combined
                signal = TradingStrategies.combined_strategy(prices)
            
            return signal
            
        except Exception as e:
            logger.error(f"خطأ في التحليل: {str(e)}")
            return {"signal": "neutral", "reason": f"خطأ: {str(e)}"}
    
    async def execute_trade(self, asset: str, amount: float, duration: int = 60) -> Dict:
        """تنفيذ صفقة تداول"""
        try:
            # تحليل السوق أولاً
            analysis = await self.analyze_market(asset)
            
            if analysis["signal"] == "neutral":
                return {
                    "success": False,
                    "reason": analysis["reason"],
                    "signal": "neutral"
                }
            
            # تنفيذ الصفقة
            direction = "call" if analysis["signal"] == "call" else "put"
            logger.info(f"🔄 تنفيذ صفقة {direction} على {asset} بمبلغ ${amount}")
            
            success, result = await self.client.buy(amount, asset, direction, duration)
            
            if success:
                trade_info = {
                    "id": result,
                    "asset": asset,
                    "direction": direction,
                    "amount": amount,
                    "duration": duration,
                    "timestamp": datetime.now().isoformat(),
                    "signal_reason": analysis["reason"]
                }
                self.trade_history.append(trade_info)
                self.statistics["total_trades"] += 1
                
                # انتظار نتيجة الصفقة
                win = await self.client.check_win(result)
                
                if win:
                    self.statistics["wins"] += 1
                    profit = amount * 0.8  # profit تقريبي 80%
                    self.statistics["profit"] += profit
                    self.statistics["current_balance"] += profit
                    return {
                        "success": True,
                        "result": "win",
                        "profit": profit,
                        "analysis": analysis
                    }
                else:
                    self.statistics["losses"] += 1
                    self.statistics["profit"] -= amount
                    self.statistics["current_balance"] -= amount
                    return {
                        "success": True,
                        "result": "loss",
                        "loss": amount,
                        "analysis": analysis
                    }
            else:
                return {
                    "success": False,
                    "reason": result,
                    "signal": analysis["signal"]
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ الصفقة: {str(e)}")
            return {"success": False, "reason": str(e)}
    
    async def start_bot(self, asset: str = "EURUSD", amount: float = 10, 
                       duration: int = 60, max_trades: int = 10):
        """تشغيل البوت"""
        self.is_running = True
        trades_count = 0
        
        logger.info(f"🚀 بدء تشغيل البوت - Asset: {asset}, Amount: ${amount}")
        
        while self.is_running and (max_trades == 0 or trades_count < max_trades):
            try:
                result = await self.execute_trade(asset, amount, duration)
                
                if result.get("success"):
                    trades_count += 1
                    logger.info(f"✅ الصفقة #{trades_count}: {result.get('result', 'unknown')}")
                else:
                    logger.warning(f"⚠️ فشل التنفيذ: {result.get('reason', 'Unknown error')}")
                
                # انتظار بين الصفقات (دقيقتين)
                await asyncio.sleep(120)
                
            except Exception as e:
                logger.error(f"خطأ في حلقة التداول: {str(e)}")
                await asyncio.sleep(60)
        
        self.is_running = False
        logger.info("🛑 توقف البوت")
    
    def stop_bot(self):
        """إيقاف البوت"""
        self.is_running = False
        logger.info("🛑 جاري إيقاف البوت...")
    
    async def get_balance(self) -> float:
        """الحصول على الرصيد الحالي"""
        if self.client:
            return await self.client.get_balance()
        return 0.0
    
    def get_statistics(self) -> Dict:
        """الحصول على إحصائيات التداول"""
        win_rate = 0
        if self.statistics["total_trades"] > 0:
            win_rate = (self.statistics["wins"] / self.statistics["total_trades"]) * 100
        
        return {
            **self.statistics,
            "win_rate": win_rate,
            "running": self.is_running,
            "strategy": self.current_strategy
        }
    
    async def close(self):
        """إغلاق الاتصال"""
        if self.client:
            self.client.close()
            logger.info("🔌 تم إغلاق الاتصال")