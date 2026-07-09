//+------------------------------------------------------------------+
//| UltimateSignalScanner_v14.0_MODIFIED.mq4                          |
//| VOLCANO BOT - Modified for Perfect Integration                   |
//+------------------------------------------------------------------+
#property copyright "Trading Expert - Modified for Volcano Bot"
#property version   "14.0"
#property strict

//--- إعدادات البوت
input double DefaultAmount   = 1.0;
input int    DefaultDuration = 60;      // المدة الافتراضية بالثواني
input string SignalFileName  = "SignalsLog.txt"; // نفس اسم ملف البوت
input bool   DebugMode      = true;

//--- Prefix للكائنات
#define PREFIX "VP14_"

//--- أسماء الأزرار
string btnUpName    = "btn_up";
string btnDnName    = "btn_dn";
string btnStartName = "btn_start";
string btnHistUp    = "btn_hist_up";
string btnHistDn    = "btn_hist_dn";
string btnCloseName = "btn_close";
string btnMinName   = "btn_min";

//--- ثوابت التصميم
#define PANEL_X        20
#define PANEL_Y        20
#define PANEL_W        440
#define PANEL_H        360

//--- السجل التاريخي
#define HIST_VISIBLE_ROWS 8
#define MAX_HISTORY_SIZE  500
int histScrollOffset = 0;

//--- قائمة البافر
#define MENU_VISIBLE_ROWS  7
#define MENU_TOTAL_BUFFERS 20
int  menuScrollOffset = 0;
int  menuAnchorX      = 0;
int  menuAnchorY      = 0;
bool menuIsOpen       = false;

//--- المتغيرات العامة
string detectedIndicator = "";
int    selectedUpBuffer  = -1;
int    selectedDnBuffer  = -1;
bool   isScanning        = false;
bool   indicatorClosed   = false;
bool   isPanelMinimized = false;

//--- كاش الإشارات
struct SignalRow {
   string timeStr;
   string sigType;
   int    bufNum;
   string priceStr;
   string symbolName;
   color  clr;
   bool   isNew;
};
SignalRow sigCache[];
int sigCacheCount = 0;

//--- متغيرات التتبع
datetime LastCandleTime     = 0;
int      LastPeriodSec      = 0;
bool     callSentThisBar    = false;
bool     putSentThisBar     = false;
int      flashCount         = 0;
bool     flashVisible       = true;
string   flashType          = "";
int      remainingSeconds    = 0;

//--- لوحة الألوان
color CLR_BG_DARK    = C'10,12,20';
color CLR_BG_MID     = C'16,20,32';
color CLR_BG_LIGHT   = C'24,28,45';
color CLR_ACCENT     = C'255,160,0';
color CLR_BORDER     = C'50,60,90';
color CLR_BORDER2    = C'80,90,120';
color CLR_CALL       = C'0,220,120';
color CLR_CALL_DIM   = C'0,80,50';
color CLR_PUT        = C'255,60,80';
color CLR_PUT_DIM    = C'100,15,30';
color CLR_TEXT_W     = C'220,225,240';
color CLR_TEXT_DIM   = C'120,130,160';
color CLR_TEXT_YEL   = C'255,220,80';
color CLR_ROW_A      = C'18,22,36';
color CLR_ROW_B      = C'22,28,44';
color CLR_SCAN_ON    = C'0,180,100';
color CLR_SCAN_OFF   = C'200,50,60';
color CLR_PROGRESS   = C'0,160,255';

string currentMenuFor = "";

//+------------------------------------------------------------------+
string ConvertSymbolName(string s) {
   string base = StringSubstr(s, 0, 6);
   if(StringFind(s, "OTC", 6) != -1) return base + "_otc";
   return base;
}

//+------------------------------------------------------------------+
int GetPeriodSeconds() { return PeriodSeconds(PERIOD_CURRENT); }

//+------------------------------------------------------------------+
//| تحويل اسم الأداة لـ Quotex                                        |
//+------------------------------------------------------------------+
string GetQuotexSymbol(string sym) {
   // تحويل أسماء MT4 لأسماء Quotex
   if(sym == "EURUSD") return "EUR/USD";
   if(sym == "GBPUSD") return "GBP/USD";
   if(sym == "USDJPY") return "USD/JPY";
   if(sym == "AUDUSD") return "AUD/USD";
   if(sym == "USDCAD") return "USD/CAD";
   if(sym == "USDCHF") return "USD/CHF";
   if(sym == "EURGBP") return "EUR/GBP";
   if(sym == "EURJPY") return "EUR/JPY";
   if(sym == "GBPJPY") return "GBP/JPY";
   if(sym == "AUDJPY") return "AUD/JPY";
   if(sym == "NZDUSD") return "NZD/USD";
   if(sym == "EURAUD") return "EUR/AUD";
   if(sym == "EURCAD") return "EUR/CAD";
   if(sym == "GBPAUD") return "GBP/AUD";
   if(sym == "GBPCAD") return "GBP/CAD";
   if(sym == "XAUUSD") return "XAU/USD"; // الذهب
   if(sym == "GOLD")   return "XAU/USD";
   if(sym == "BTCUSD") return "BTC/USD";
   if(sym == "ETHUSD") return "ETH/USD";
   
   // إذا لم يتم التعرف، أرجع الاسم كما هو مع استبدال الخلفية
   StringReplace(sym, "_", "/");
   return sym;
}

//+------------------------------------------------------------------+
//| كتابة الإشارة في الملف - نسخة محسنة                                |
//+------------------------------------------------------------------+
bool WriteSignalToFile(string message) {
   // إنشاء محتوى جديد (يستبدل المحتوى السابق)
   int handle = FileOpen(SignalFileName, FILE_WRITE|FILE_TXT|FILE_ANSI);
   if(handle == INVALID_HANDLE) {
      // محاولة في مجلد مشترك
      handle = FileOpen(SignalFileName, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
      if(handle == INVALID_HANDLE) {
         Print("VP14: ❌ Failed to write signal file. Error=", GetLastError());
         return false;
      }
   }
   
   FileWrite(handle, message);
   FileClose(handle);
   
   if(DebugMode) {
      Print("VP14: ✅ SIGNAL WRITTEN: [", message, "]");
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| حفظ الإشارة فوراً                                                |
//+------------------------------------------------------------------+
bool SaveSignal(string sigType, int bufferNum, double value) {
   // منع الإرسال المتكرر في نفس الشمعة
   if(sigType == "CALL" && callSentThisBar) return true;
   if(sigType == "PUT" && putSentThisBar) return true;
   
   // تحويل اسم الأداة
   string sym = GetQuotexSymbol(Symbol());
   
   // تنسيق الإشارة: SYMBOL,SIDE,AMOUNT,DURATION
   string msg = sym + "," + sigType + "," + DoubleToString(DefaultAmount, 2) + "," + (string)DefaultDuration;
   
   if(WriteSignalToFile(msg)) {
      if(sigType == "CALL") {
         callSentThisBar = true;
         AddSignalToHistory("CALL", bufferNum, value, true);
         UpdateStatusLabel("✅ CALL SAVED - " + sym, CLR_CALL);
         TriggerFlash("CALL");
      } else if(sigType == "PUT") {
         putSentThisBar = true;
         AddSignalToHistory("PUT", bufferNum, value, true);
         UpdateStatusLabel("✅ PUT SAVED - " + sym, CLR_PUT);
         TriggerFlash("PUT");
      }
      
      if(DebugMode) {
         Print("VP14: ✅ Signal saved: ", msg);
      }
      
      return true;
   }
   
   return false;
}

//+------------------------------------------------------------------+
//| فحص البافرات وإرسال الإشارات                                      |
//+------------------------------------------------------------------+
void CheckAndSendSignals() {
   if(!isScanning) return;
   if(selectedUpBuffer == -1 && selectedDnBuffer == -1) return;
   
   datetime currentTime = TimeCurrent();
   datetime candleCloseTime = LastCandleTime + LastPeriodSec;
   int secondsToClose = (int)(candleCloseTime - currentTime);
   
   // فحص البافر قبل الإغلاق بـ 1 ثانية
   if(secondsToClose <= 1 && secondsToClose >= 0) {
      CheckBuffers(0, "BEFORE_CLOSE");
   }
   
   // فحص البافر بعد الإغلاق مباشرة
   if(secondsToClose <= 0) {
      // فحص shift 0 و 1
      for(int shift = 0; shift <= 1; shift++) {
         CheckBuffers(shift, "AT_CLOSE");
      }
   }
}

//+------------------------------------------------------------------+
//| فحص البافرات المحددة                                             |
//+------------------------------------------------------------------+
void CheckBuffers(int shift, string timing) {
   // فحص CALL buffer
   if(selectedUpBuffer != -1 && !callSentThisBar) {
      double callVal = iCustom(NULL, 0, detectedIndicator, selectedUpBuffer, shift);
      bool callOk = (callVal != EMPTY_VALUE && callVal != 0 && callVal != NULL);
      
      if(callOk && callVal > 0) {
         if(DebugMode) {
            Print("VP14: 📡 CALL detected at shift=", shift, " timing=", timing);
         }
         UpdateStatusLabel("📡 CALL @ " + timing, CLR_CALL);
         SaveSignal("CALL", selectedUpBuffer, callVal);
      }
   }
   
   // فحص PUT buffer
   if(selectedDnBuffer != -1 && !putSentThisBar) {
      double putVal = iCustom(NULL, 0, detectedIndicator, selectedDnBuffer, shift);
      bool putOk = (putVal != EMPTY_VALUE && putVal != 0 && putVal != NULL);
      
      if(putOk && putVal > 0) {
         if(DebugMode) {
            Print("VP14: 📡 PUT detected at shift=", shift, " timing=", timing);
         }
         UpdateStatusLabel("📡 PUT @ " + timing, CLR_PUT);
         SaveSignal("PUT", selectedDnBuffer, putVal);
      }
   }
}

//+------------------------------------------------------------------+
void ResetBarState() {
   callSentThisBar = false;
   putSentThisBar  = false;
   flashCount      = 0;
}

//+------------------------------------------------------------------+
int OnInit() {
   EventKillTimer();
   
   // اكتشاف المؤشر
   for(int i = 0; i < ChartIndicatorsTotal(0, 0); i++) {
      string n = ChartIndicatorName(0, 0, i);
      if(n != "" && StringFind(n, "VP14") < 0) {
         detectedIndicator = n;
         Print("VP14: ✅ Detected indicator: ", n);
         break;
      }
   }
   
   if(detectedIndicator == "") {
      Print("VP14: ⚠️ No external indicator detected!");
   }
   
   LastCandleTime = Time[0];
   LastPeriodSec  = GetPeriodSeconds();
   ResetBarState();
   
   BuildSignalCache();
   CreateMainUI();
   EventSetTimer(1);
   
   Print("==========================================");
   Print("VP14: 🚀 VOLCANO BOT MT4 SENDER v14.0");
   Print("VP14: 📁 Signal File: ", SignalFileName);
   Print("VP14: 📝 Format: SYMBOL,SIDE,AMOUNT,DURATION");
   Print("VP14: ⏱️ Timer: 1 second (continuous)");
   Print("VP14: 🔗 Bot URL: https://botquotex-api.onrender.com");
   Print("==========================================");
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
   EventKillTimer();
   ObjectsDeleteAll(0, PREFIX);
   Print("VP14: Deinitialized. Reason=", reason);
}

//+------------------------------------------------------------------+
void OnTick() {
   if(!isScanning) return;
   
   datetime curCandle = Time[0];
   datetime curTime   = TimeCurrent();
   
   // شمعة جديدة
   if(curCandle != LastCandleTime) {
      Print("VP14: 🕯️ NEW CANDLE @ ", TimeToStr(curCandle, TIME_SECONDS));
      
      LastCandleTime = curCandle;
      LastPeriodSec  = GetPeriodSeconds();
      ResetBarState();
      
      UpdateStatusLabel("⏳ Monitoring...", CLR_TEXT_YEL);
      
      datetime candleClose = LastCandleTime + LastPeriodSec;
      Print("VP14: ⏰ Candle closes at: ", TimeToStr(candleClose, TIME_SECONDS));
   }
   
   // تحديث الوقت المتبقي
   datetime candleCloseNow = LastCandleTime + LastPeriodSec;
   remainingSeconds = (int)(candleCloseNow - curTime);
   if(remainingSeconds < 0) remainingSeconds = 0;
   UpdateTimerBar();
   
   // فحص وإرسال الإشارات
   CheckAndSendSignals();
}

//+------------------------------------------------------------------+
void OnTimer() {
   if(indicatorClosed) return;
   
   // إعادة بناء الواجهة إذا اختفت
   if(ObjectFind(0, PREFIX + "bg") < 0) {
      if(isPanelMinimized) CreateMiniUI();
      else CreateMainUI();
   }
   
   // تأثير الوميض
   if(flashCount > 0) {
      flashVisible = !flashVisible;
      flashCount--;
      DrawFlashAlert(flashVisible);
      if(flashCount == 0) {
         flashVisible = true;
         DrawFlashAlert(false);
      }
   }
   
   // تحديث الساعة
   UpdateClockLabel();
}

//+------------------------------------------------------------------+
int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[],
                const double &high[], const double &low[],
                const double &close[], const long &tick_volume[],
                const long &volume[], const int &spread[]) {
   return(rates_total);
}

//+------------------------------------------------------------------+
void TriggerFlash(string type) {
   flashCount   = 8;
   flashVisible = true;
   flashType    = type;
}

//+------------------------------------------------------------------+
void AddSignalToHistory(string sigType, int bufNum, double price, bool isNew) {
   SignalRow nr;
   nr.timeStr    = TimeToStr(TimeCurrent(), TIME_MINUTES | TIME_SECONDS);
   nr.sigType    = sigType;
   nr.bufNum     = bufNum;
   nr.priceStr   = DoubleToString(price, Digits());
   nr.symbolName = GetQuotexSymbol(Symbol());
   nr.clr        = (sigType == "CALL") ? CLR_CALL : CLR_PUT;
   nr.isNew      = isNew;
   
   ArrayResize(sigCache, sigCacheCount + 1);
   for(int i = sigCacheCount; i > 0; i--) sigCache[i] = sigCache[i - 1];
   sigCache[0] = nr;
   sigCacheCount++;
   
   if(sigCacheCount > MAX_HISTORY_SIZE) {
      ArrayResize(sigCache, MAX_HISTORY_SIZE);
      sigCacheCount = MAX_HISTORY_SIZE;
   }
   histScrollOffset = 0;
   DrawHistoryRows();
}

//+------------------------------------------------------------------+
void BuildSignalCache() {
   if(detectedIndicator == "") return;
   sigCacheCount = 0;
   ArrayResize(sigCache, 0);
   string cs = GetQuotexSymbol(Symbol());
   
   for(int i = 1; i < 200 && sigCacheCount < MAX_HISTORY_SIZE; i++) {
      double v0 = iCustom(NULL, 0, detectedIndicator, 0, i);
      double v1 = iCustom(NULL, 0, detectedIndicator, 1, i);
      double v2 = iCustom(NULL, 0, detectedIndicator, 2, i);
      double v3 = iCustom(NULL, 0, detectedIndicator, 3, i);
      
      string sig = ""; color col = clrWhite; int buf = -1;
      if(v0 != 0 && v0 != EMPTY_VALUE) { sig = "CALL"; col = CLR_CALL; buf = 0; }
      else if(v2 != 0 && v2 != EMPTY_VALUE) { sig = "CALL"; col = CLR_CALL; buf = 2; }
      else if(v1 != 0 && v1 != EMPTY_VALUE) { sig = "PUT"; col = CLR_PUT; buf = 1; }
      else if(v3 != 0 && v3 != EMPTY_VALUE) { sig = "PUT"; col = CLR_PUT; buf = 3; }
      
      if(sig != "") {
         ArrayResize(sigCache, sigCacheCount + 1);
         sigCache[sigCacheCount].timeStr    = TimeToStr(Time[i], TIME_MINUTES);
         sigCache[sigCacheCount].sigType     = sig;
         sigCache[sigCacheCount].bufNum       = buf;
         sigCache[sigCacheCount].priceStr    = DoubleToString(Open[i], Digits());
         sigCache[sigCacheCount].symbolName  = cs;
         sigCache[sigCacheCount].clr         = col;
         sigCache[sigCacheCount].isNew       = false;
         sigCacheCount++;
      }
   }
}

//+------------------------------------------------------------------+
// واجهة المستخدم
//+------------------------------------------------------------------+
void CreateMainUI() {
   int bx = PANEL_X, by = PANEL_Y, w = PANEL_W, h = PANEL_H;
   
   DrawRectEx("shadow",   bx + 4, by + 4, w, h, C'5,6,10', C'5,6,10', 0);
   DrawRectEx("frame",    bx - 2, by - 2, w + 4, h + 4, CLR_BG_DARK, CLR_ACCENT, 0);
   DrawRectEx("bg",       bx, by, w, h, CLR_BG_MID, CLR_BORDER, 0);
   
   // الهيدر
   DrawRectEx("hdr",      bx, by, w, 38, CLR_BG_DARK, CLR_ACCENT, 0);
   DrawRectEx("hdr_line", bx, by + 38, w, 2, CLR_ACCENT, CLR_ACCENT, 0);
   DrawLabelEx("ico",     bx + 10, by + 9, "🔥", CLR_ACCENT, 13);
   DrawLabelEx("title",  bx + 32, by + 10, "VOLCANO BOT", CLR_ACCENT, 10);
   DrawLabelEx("ver",    bx + 160, by + 14, "v14.0 MT4", CLR_TEXT_DIM, 7);
   DrawLabelEx("clk_ico", bx + 250, by + 10, "⏱", CLR_TEXT_DIM, 8);
   DrawLabelEx("clock",  bx + 268, by + 10, TimeToStr(TimeCurrent(), TIME_MINUTES | TIME_SECONDS), CLR_TEXT_YEL, 8);
   CreateBtn(btnMinName,  bx + w - 60, by + 5, 24, 27, "—", CLR_BORDER2, 8);
   CreateBtn(btnCloseName, bx + w - 32, by + 5, 27, 27, "✕", C'180,30,40', 10);
   
   // شريط المعلومات
   int iy = by + 42;
   DrawRectEx("info_bar", bx, iy, w, 26, CLR_BG_LIGHT, CLR_BORDER, 0);
   DrawLabelEx("sym_lbl",  bx + 10, iy + 6, "SYMBOL:", CLR_TEXT_DIM, 7);
   DrawLabelEx("sym_val",  bx + 58, iy + 6, GetQuotexSymbol(Symbol()), CLR_TEXT_YEL, 8);
   DrawLabelEx("ind_lbl",  bx + 140, iy + 6, "INDICATOR:", CLR_TEXT_DIM, 7);
   string indTxt = (detectedIndicator == "") ? "NOT FOUND" : detectedIndicator;
   if(StringLen(indTxt) > 16) indTxt = StringSubstr(indTxt, 0, 14) + "..";
   color indClr = (detectedIndicator == "") ? CLR_PUT : CLR_CALL;
   DrawLabelEx("ind_val", bx + 210, iy + 6, indTxt, indClr, 7);
   DrawLabelEx("file_lbl", bx + 340, iy + 6, "📁 " + SignalFileName, C'100, 140, 255', 7);
   
   // لوحة الإعداد
   int cy = iy + 30;
   DrawRectEx("cfg_panel",    bx + 8, cy, w - 16, 80, CLR_BG_DARK, CLR_BORDER, 0);
   DrawRectEx("cfg_title_bar", bx + 8, cy, w - 16, 18, CLR_BORDER, CLR_BORDER, 0);
   DrawLabelEx("cfg_title", bx + 14, cy + 3, "⚙ BUFFER CONFIGURATION", CLR_TEXT_DIM, 7);
   
   CreateBtnStyled(btnUpName, bx + 14, cy + 24, 140, 24,
      (selectedUpBuffer == -1) ? "▲ SET CALL BUFFER" : "▲ CALL: Buf#" + (string)selectedUpBuffer,
      (selectedUpBuffer == -1) ? CLR_BG_LIGHT : CLR_CALL_DIM, CLR_CALL);
   CreateBtnStyled(btnDnName, bx + 164, cy + 24, 140, 24,
      (selectedDnBuffer == -1) ? "▼ SET PUT BUFFER" : "▼ PUT: Buf#" + (string)selectedDnBuffer,
      (selectedDnBuffer == -1) ? CLR_BG_LIGHT : CLR_PUT_DIM, CLR_PUT);
   
   string stTxt = isScanning ? "■  STOP SCAN" : "▶  START SCAN";
   color stBg = isScanning ? CLR_SCAN_OFF :
      ((selectedUpBuffer != -1 && selectedDnBuffer != -1) ? CLR_SCAN_ON : CLR_BORDER);
   CreateBtnBig(btnStartName, bx + 318, cy + 22, 118, 50, stTxt, stBg);
   
   // قسم الإشارة الحية
   int lsy = cy + 86;
   DrawRectEx("flash_bg", bx + 8, lsy, w - 16, 36, CLR_BG_MID, CLR_BORDER, 0);
   DrawLabelEx("live_lbl",   bx + 16, lsy + 11, "LIVE:", CLR_TEXT_DIM, 7);
   DrawLabelEx("live_badge", bx + 52, lsy + 8, "—", CLR_TEXT_DIM, 10);
   DrawLabelEx("timer_ico",  bx + 180, lsy + 11, "⏳", CLR_TEXT_DIM, 7);
   DrawLabelEx("timer_lbl",  bx + 198, lsy + 11, "—", CLR_TEXT_DIM, 7);
   DrawRectEx("timer_track", bx + 230, lsy + 14, w - 254, 8, CLR_BG_DARK, CLR_BORDER, 0);
   DrawRectEx("timer_bar",   bx + 230, lsy + 14, 2, 8, CLR_PROGRESS, CLR_PROGRESS, 0);
   
   // شريط الحالة
   int sty = lsy + 40;
   DrawRectEx("st_bar",  bx + 8, sty, w - 16, 24, CLR_BG_DARK, CLR_BORDER, 0);
   DrawLabelEx("st_ico", bx + 14, sty + 7, "●", CLR_TEXT_DIM, 7);
   DrawLabelEx("st_val", bx + 26, sty + 6, "READY - Bot: " + SignalFileName, CLR_TEXT_DIM, 7);
   
   // جدول الإشارات
   int hy = sty + 30;
   DrawRectEx("hist_hdr", bx + 8, hy, w - 16, 20, C'14,18,30', CLR_BORDER, 0);
   DrawLabelEx("h_icon",    bx + 14, hy + 5, "📋", CLR_TEXT_DIM, 7);
   DrawLabelEx("h_title",   bx + 30, hy + 5, "SIGNAL HISTORY", CLR_TEXT_W, 7);
   DrawLabelEx("hist_counter", bx + 200, hy + 5, "0 / 0", CLR_TEXT_DIM, 7);
   CreateScrollBtn(btnHistUp, bx + w - 50, hy + 2, 19, 16, "▲");
   CreateScrollBtn(btnHistDn, bx + w - 28, hy + 2, 19, 16, "▼");
   
   DrawRectEx("hist_body", bx + 8, hy + 20, w - 16, HIST_VISIBLE_ROWS * 20 + 18, CLR_BG_DARK, CLR_BORDER, 0);
   int hcy = hy + 22;
   DrawRectEx("col_hdr",   bx + 8, hcy, w - 16, 16, CLR_BG_LIGHT, CLR_BORDER, 0);
   DrawLabelEx("hc_time",   bx + 14, hcy + 3, "TIME", CLR_TEXT_DIM, 6);
   DrawLabelEx("hc_side",   bx + 82, hcy + 3, "SIDE", CLR_TEXT_DIM, 6);
   DrawLabelEx("hc_sym",    bx + 145, hcy + 3, "SYMBOL", CLR_TEXT_DIM, 6);
   DrawLabelEx("hc_buf",    bx + 235, hcy + 3, "BUF", CLR_TEXT_DIM, 6);
   DrawLabelEx("hc_price",  bx + 290, hcy + 3, "PRICE", CLR_TEXT_DIM, 6);
   DrawLabelEx("hc_status", bx + 375, hcy + 3, "STATUS", CLR_TEXT_DIM, 6);
   
   DrawHistoryRows();
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
void DrawHistoryRows() {
   if(isPanelMinimized) return;
   int bx = PANEL_X, by = PANEL_Y;
   int hy = by + 38 + 26 + 30 + 80 + 36 + 24 + 30;
   int rsy = hy + 22 + 16 + 2;
   
   for(int r = 0; r < HIST_VISIBLE_ROWS; r++) {
      string p = (string)r;
      ObjectDelete(0, PREFIX + "rw_bg_" + p);
      ObjectDelete(0, PREFIX + "rw_new_" + p);
      ObjectDelete(0, PREFIX + "rw_time_" + p);
      ObjectDelete(0, PREFIX + "rw_side_" + p);
      ObjectDelete(0, PREFIX + "rw_sym_" + p);
      ObjectDelete(0, PREFIX + "rw_buf_" + p);
      ObjectDelete(0, PREFIX + "rw_price_" + p);
      ObjectDelete(0, PREFIX + "rw_stat_" + p);
   }
   
   if(sigCacheCount == 0) {
      DrawLabelEx("hist_empty", bx + 155, rsy + 28, "No signals recorded yet", CLR_TEXT_DIM, 8);
      UpdateHistScrollBtns();
      ChartRedraw(0);
      return;
   }
   ObjectDelete(0, PREFIX + "hist_empty");
   
   for(int r = 0; r < HIST_VISIBLE_ROWS; r++) {
      int idx = histScrollOffset + r;
      if(idx >= sigCacheCount) break;
      string p = (string)r;
      int rowY = rsy + r * 20;
      color rowBg = (r % 2 == 0) ? CLR_ROW_A : CLR_ROW_B;
      if(sigCache[idx].isNew)
         rowBg = (sigCache[idx].sigType == "CALL") ? C'0,30,18' : C'35,8,15';
      
      string bgNm = PREFIX + "rw_bg_" + p;
      ObjectCreate(0, bgNm, OBJ_RECTANGLE_LABEL, 0, 0, 0);
      ObjectSetInteger(0, bgNm, OBJPROP_XDISTANCE, bx + 9);
      ObjectSetInteger(0, bgNm, OBJPROP_YDISTANCE, rowY);
      ObjectSetInteger(0, bgNm, OBJPROP_XSIZE, PANEL_W - 18);
      ObjectSetInteger(0, bgNm, OBJPROP_YSIZE, 19);
      ObjectSetInteger(0, bgNm, OBJPROP_BGCOLOR, rowBg);
      ObjectSetInteger(0, bgNm, OBJPROP_COLOR, CLR_BORDER);
      ObjectSetInteger(0, bgNm, OBJPROP_BORDER_TYPE, BORDER_FLAT);
      ObjectSetInteger(0, bgNm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, bgNm, OBJPROP_ZORDER, 0);
      ObjectSetInteger(0, bgNm, OBJPROP_SELECTABLE, false);
      
      if(sigCache[idx].isNew) {
         string nNm = PREFIX + "rw_new_" + p;
         ObjectCreate(0, nNm, OBJ_RECTANGLE_LABEL, 0, 0, 0);
         ObjectSetInteger(0, nNm, OBJPROP_XDISTANCE, bx + 9);
         ObjectSetInteger(0, nNm, OBJPROP_YDISTANCE, rowY);
         ObjectSetInteger(0, nNm, OBJPROP_XSIZE, 3);
         ObjectSetInteger(0, nNm, OBJPROP_YSIZE, 19);
         ObjectSetInteger(0, nNm, OBJPROP_BGCOLOR, sigCache[idx].clr);
         ObjectSetInteger(0, nNm, OBJPROP_COLOR, sigCache[idx].clr);
         ObjectSetInteger(0, nNm, OBJPROP_BORDER_TYPE, BORDER_FLAT);
         ObjectSetInteger(0, nNm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
         ObjectSetInteger(0, nNm, OBJPROP_ZORDER, 1);
         ObjectSetInteger(0, nNm, OBJPROP_SELECTABLE, false);
      }
      
      DrawLabelEx("rw_time_" + p, bx + 15, rowY + 4, sigCache[idx].timeStr, CLR_TEXT_W, 6);
      DrawLabelEx("rw_side_" + p, bx + 82, rowY + 3,
         (sigCache[idx].sigType == "CALL") ? "▲ CALL" : "▼ PUT",
         sigCache[idx].clr, 7);
      DrawLabelEx("rw_sym_" + p, bx + 145, rowY + 4, sigCache[idx].symbolName, C'180,200,255', 6);
      DrawLabelEx("rw_buf_" + p, bx + 238, rowY + 4, "#" + (string)sigCache[idx].bufNum, CLR_TEXT_DIM, 6);
      DrawLabelEx("rw_price_" + p, bx + 290, rowY + 4, sigCache[idx].priceStr, CLR_TEXT_YEL, 6);
      DrawLabelEx("rw_stat_" + p, bx + 375, rowY + 4,
         sigCache[idx].isNew ? "✅ SAVED" : "•",
         sigCache[idx].isNew ? CLR_CALL : CLR_TEXT_DIM, 6);
   }
   UpdateHistScrollBtns();
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
void UpdateHistScrollBtns() {
   bool canUp = (histScrollOffset > 0);
   bool canDn = (histScrollOffset + HIST_VISIBLE_ROWS < sigCacheCount);
   ObjectSetInteger(0, PREFIX + btnHistUp, OBJPROP_BGCOLOR, canUp ? CLR_ACCENT : CLR_BORDER);
   ObjectSetInteger(0, PREFIX + btnHistUp, OBJPROP_COLOR, canUp ? CLR_BG_DARK : CLR_TEXT_DIM);
   ObjectSetInteger(0, PREFIX + btnHistDn, OBJPROP_BGCOLOR, canDn ? CLR_ACCENT : CLR_BORDER);
   ObjectSetInteger(0, PREFIX + btnHistDn, OBJPROP_COLOR, canDn ? CLR_BG_DARK : CLR_TEXT_DIM);
   string cnt = (sigCacheCount == 0) ? "Empty" :
      (string)(histScrollOffset + 1) + "-" +
      (string)MathMin(histScrollOffset + HIST_VISIBLE_ROWS, sigCacheCount) +
      " / " + (string)sigCacheCount;
   ObjectSetString(0, PREFIX + "hist_counter", OBJPROP_TEXT, cnt);
}

//+------------------------------------------------------------------+
void UpdateTimerBar() {
   if(isPanelMinimized) return;
   int total = LastPeriodSec; if(total <= 0) total = 1;
   double ratio = (double)remainingSeconds / total;
   if(ratio > 1.0) ratio = 1.0;
   if(ratio < 0.0) ratio = 0.0;
   int barMaxW = PANEL_W - 254, barW = (int)(barMaxW * ratio);
   color barClr = CLR_PROGRESS;
   if(ratio < 0.25) barClr = CLR_PUT;
   else if(ratio < 0.5) barClr = CLR_TEXT_YEL;
   ObjectSetInteger(0, PREFIX + "timer_bar", OBJPROP_XSIZE, MathMax(barW, 2));
   ObjectSetInteger(0, PREFIX + "timer_bar", OBJPROP_BGCOLOR, barClr);
   ObjectSetInteger(0, PREFIX + "timer_bar", OBJPROP_COLOR, barClr);
   string tStr = (string)remainingSeconds + "s";
   ObjectSetString(0, PREFIX + "timer_lbl", OBJPROP_TEXT, tStr);
   ObjectSetInteger(0, PREFIX + "timer_lbl", OBJPROP_COLOR, barClr);
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
void UpdateClockLabel() {
   string t = TimeToStr(TimeCurrent(), TIME_MINUTES | TIME_SECONDS);
   if(ObjectFind(0, PREFIX + "clock") >= 0)
      ObjectSetString(0, PREFIX + "clock", OBJPROP_TEXT, t);
}

//+------------------------------------------------------------------+
void UpdateLiveSignalBadge(string sig) {
   if(sig == "CALL") {
      ObjectSetString(0, PREFIX + "live_badge", OBJPROP_TEXT, "▲ CALL");
      ObjectSetInteger(0, PREFIX + "live_badge", OBJPROP_COLOR, CLR_CALL);
   } else if(sig == "PUT") {
      ObjectSetString(0, PREFIX + "live_badge", OBJPROP_TEXT, "▼ PUT");
      ObjectSetInteger(0, PREFIX + "live_badge", OBJPROP_COLOR, CLR_PUT);
   } else {
      ObjectSetString(0, PREFIX + "live_badge", OBJPROP_TEXT, "—");
      ObjectSetInteger(0, PREFIX + "live_badge", OBJPROP_COLOR, CLR_TEXT_DIM);
   }
}

//+------------------------------------------------------------------+
void DrawFlashAlert(bool visible) {
   string nm = PREFIX + "flash_bg";
   if(!visible || flashType == "") {
      ObjectSetInteger(0, nm, OBJPROP_BGCOLOR, CLR_BG_MID);
      ObjectSetInteger(0, nm, OBJPROP_COLOR, CLR_BORDER);
   } else {
      color fc = (flashType == "CALL") ? C'0,55,28' : C'55,8,18';
      color bc = (flashType == "CALL") ? CLR_CALL : CLR_PUT;
      ObjectSetInteger(0, nm, OBJPROP_BGCOLOR, fc);
      ObjectSetInteger(0, nm, OBJPROP_COLOR, bc);
   }
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
void UpdateStatusLabel(string txt, color c) {
   if(ObjectFind(0, PREFIX + "st_val") >= 0) {
      ObjectSetString(0, PREFIX + "st_val", OBJPROP_TEXT, txt);
      ObjectSetInteger(0, PREFIX + "st_val", OBJPROP_COLOR, c);
      color dotClr = (c == CLR_CALL) ? CLR_CALL : (c == CLR_PUT) ? CLR_PUT : (c == CLR_TEXT_YEL) ? CLR_TEXT_YEL : CLR_TEXT_DIM;
      ObjectSetInteger(0, PREFIX + "st_ico", OBJPROP_COLOR, dotClr);
   }
}

//+------------------------------------------------------------------+
void ShowMenu(int ax, int ay) {
   menuAnchorX = ax; menuAnchorY = ay; menuIsOpen = true;
   const int ROW_H = 26, OPT_W = 130, SCR_W = 24, PAD = 5;
   const int TW = OPT_W + SCR_W + PAD * 3, TH = PAD + MENU_VISIBLE_ROWS * ROW_H + PAD;
   
   string bgNm = PREFIX + "m_bg";
   ObjectDelete(0, bgNm); ObjectCreate(0, bgNm, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSetInteger(0, bgNm, OBJPROP_XDISTANCE, ax - 2); ObjectSetInteger(0, bgNm, OBJPROP_YDISTANCE, ay - 2);
   ObjectSetInteger(0, bgNm, OBJPROP_XSIZE, TW + 4); ObjectSetInteger(0, bgNm, OBJPROP_YSIZE, TH + 4);
   ObjectSetInteger(0, bgNm, OBJPROP_BGCOLOR, CLR_ACCENT); ObjectSetInteger(0, bgNm, OBJPROP_COLOR, CLR_ACCENT);
   ObjectSetInteger(0, bgNm, OBJPROP_BORDER_TYPE, BORDER_FLAT);
   ObjectSetInteger(0, bgNm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, bgNm, OBJPROP_ZORDER, 3); ObjectSetInteger(0, bgNm, OBJPROP_SELECTABLE, false);
   
   string bgIn = PREFIX + "m_bg_in";
   ObjectDelete(0, bgIn); ObjectCreate(0, bgIn, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSetInteger(0, bgIn, OBJPROP_XDISTANCE, ax); ObjectSetInteger(0, bgIn, OBJPROP_YDISTANCE, ay);
   ObjectSetInteger(0, bgIn, OBJPROP_XSIZE, TW); ObjectSetInteger(0, bgIn, OBJPROP_YSIZE, TH);
   ObjectSetInteger(0, bgIn, OBJPROP_BGCOLOR, CLR_BG_DARK); ObjectSetInteger(0, bgIn, OBJPROP_COLOR, CLR_BG_DARK);
   ObjectSetInteger(0, bgIn, OBJPROP_BORDER_TYPE, BORDER_FLAT);
   ObjectSetInteger(0, bgIn, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, bgIn, OBJPROP_ZORDER, 4); ObjectSetInteger(0, bgIn, OBJPROP_SELECTABLE, false);
   
   for(int i = 0; i < MENU_VISIBLE_ROWS; i++) {
      int bufIdx = menuScrollOffset + i, rowY = ay + PAD + i * ROW_H;
      string optNm = PREFIX + "opt_" + (string)bufIdx;
      ObjectDelete(0, optNm);
      if(bufIdx >= MENU_TOTAL_BUFFERS) continue;
      bool sel = (currentMenuFor == "UP" && bufIdx == selectedUpBuffer) || (currentMenuFor == "DN" && bufIdx == selectedDnBuffer);
      string lbl = (currentMenuFor == "UP" ? "▲ " : "▼ ") + "Buffer " + (string)bufIdx;
      ObjectCreate(0, optNm, OBJ_BUTTON, 0, 0, 0);
      ObjectSetInteger(0, optNm, OBJPROP_XDISTANCE, ax + PAD); ObjectSetInteger(0, optNm, OBJPROP_YDISTANCE, rowY);
      ObjectSetInteger(0, optNm, OBJPROP_XSIZE, OPT_W); ObjectSetInteger(0, optNm, OBJPROP_YSIZE, ROW_H - 2);
      ObjectSetString(0, optNm, OBJPROP_TEXT, lbl);
      ObjectSetInteger(0, optNm, OBJPROP_BGCOLOR, sel ? CLR_ACCENT : CLR_BG_LIGHT);
      ObjectSetInteger(0, optNm, OBJPROP_COLOR, sel ? CLR_BG_DARK : CLR_TEXT_W);
      ObjectSetInteger(0, optNm, OBJPROP_FONTSIZE, 8);
      ObjectSetInteger(0, optNm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, optNm, OBJPROP_ZORDER, 5); ObjectSetInteger(0, optNm, OBJPROP_SELECTABLE, true);
   }
   int scrX = ax + PAD + OPT_W + PAD;
   bool cUp = (menuScrollOffset > 0), cDn = (menuScrollOffset + MENU_VISIBLE_ROWS < MENU_TOTAL_BUFFERS);
   
   string mU = PREFIX + "m_scroll_up"; ObjectDelete(0, mU); ObjectCreate(0, mU, OBJ_BUTTON, 0, 0, 0);
   ObjectSetInteger(0, mU, OBJPROP_XDISTANCE, scrX); ObjectSetInteger(0, mU, OBJPROP_YDISTANCE, ay + PAD);
   ObjectSetInteger(0, mU, OBJPROP_XSIZE, SCR_W); ObjectSetInteger(0, mU, OBJPROP_YSIZE, 24);
   ObjectSetString(0, mU, OBJPROP_TEXT, "▲");
   ObjectSetInteger(0, mU, OBJPROP_BGCOLOR, cUp ? CLR_ACCENT : CLR_BORDER);
   ObjectSetInteger(0, mU, OBJPROP_COLOR, cUp ? CLR_BG_DARK : CLR_TEXT_DIM);
   ObjectSetInteger(0, mU, OBJPROP_FONTSIZE, 9); ObjectSetInteger(0, mU, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, mU, OBJPROP_ZORDER, 6); ObjectSetInteger(0, mU, OBJPROP_SELECTABLE, true);
   
   string mD = PREFIX + "m_scroll_dn"; ObjectDelete(0, mD); ObjectCreate(0, mD, OBJ_BUTTON, 0, 0, 0);
   ObjectSetInteger(0, mD, OBJPROP_XDISTANCE, scrX); ObjectSetInteger(0, mD, OBJPROP_YDISTANCE, ay + TH - 26 - PAD);
   ObjectSetInteger(0, mD, OBJPROP_XSIZE, SCR_W); ObjectSetInteger(0, mD, OBJPROP_YSIZE, 24);
   ObjectSetString(0, mD, OBJPROP_TEXT, "▼");
   ObjectSetInteger(0, mD, OBJPROP_BGCOLOR, cDn ? CLR_ACCENT : CLR_BORDER);
   ObjectSetInteger(0, mD, OBJPROP_COLOR, cDn ? CLR_BG_DARK : CLR_TEXT_DIM);
   ObjectSetInteger(0, mD, OBJPROP_FONTSIZE, 9); ObjectSetInteger(0, mD, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, mD, OBJPROP_ZORDER, 6); ObjectSetInteger(0, mD, OBJPROP_SELECTABLE, true);
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
void HideMenu() {
   menuIsOpen = false;
   ObjectDelete(0, PREFIX + "m_bg"); ObjectDelete(0, PREFIX + "m_bg_in");
   ObjectDelete(0, PREFIX + "m_scroll_up"); ObjectDelete(0, PREFIX + "m_scroll_dn");
   for(int i = 0; i < MENU_TOTAL_BUFFERS; i++) ObjectDelete(0, PREFIX + "opt_" + (string)i);
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
void ToggleMinimize() {
   isPanelMinimized = !isPanelMinimized;
   ObjectsDeleteAll(0, PREFIX);
   if(isPanelMinimized) CreateMiniUI();
   else CreateMainUI();
}

//+------------------------------------------------------------------+
void CreateMiniUI() {
   int bx = PANEL_X, by = PANEL_Y, w = PANEL_W;
   DrawRectEx("frame", bx - 2, by - 2, w + 4, 44, CLR_BG_DARK, CLR_ACCENT, 0);
   DrawRectEx("bg", bx, by, w, 40, CLR_BG_DARK, CLR_ACCENT, 0);
   DrawLabelEx("ico", bx + 10, by + 12, "🔥", CLR_ACCENT, 12);
   DrawLabelEx("title", bx + 32, by + 13, "VOLCANO BOT v14.0", CLR_ACCENT, 9);
   DrawLabelEx("st_val", bx + 200, by + 13,
      isScanning ? "● SCANNING" : "● STOPPED",
      isScanning ? CLR_CALL : CLR_PUT, 8);
   CreateBtn(btnMinName, bx + w - 60, by + 7, 24, 26, "□", CLR_BORDER2, 8);
   CreateBtn(btnCloseName, bx + w - 32, by + 7, 27, 26, "✕", C'180,30,40', 10);
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
void UpdateStartBtnStyle() {
   bool ready = (selectedUpBuffer != -1 && selectedDnBuffer != -1);
   if(isScanning) {
      ObjectSetString(0, PREFIX + btnStartName, OBJPROP_TEXT, "■  STOP SCAN");
      ObjectSetInteger(0, PREFIX + btnStartName, OBJPROP_BGCOLOR, CLR_SCAN_OFF);
   } else {
      ObjectSetString(0, PREFIX + btnStartName, OBJPROP_TEXT, "▶  START SCAN");
      ObjectSetInteger(0, PREFIX + btnStartName, OBJPROP_BGCOLOR, ready ? CLR_SCAN_ON : CLR_BORDER);
   }
}

//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam) {
   if(id != CHARTEVENT_OBJECT_CLICK) return;
   
   if(sparam == PREFIX + btnCloseName) {
      indicatorClosed = true;
      ObjectsDeleteAll(0, PREFIX);
      return;
   }
   
   if(sparam == PREFIX + btnMinName) { ToggleMinimize(); return; }
   
   if(isPanelMinimized) return;
   
   if(sparam == PREFIX + btnUpName) {
      if(menuIsOpen && currentMenuFor == "UP") { HideMenu(); return; }
      if(menuIsOpen) HideMenu();
      currentMenuFor = "UP"; menuScrollOffset = 0;
      ShowMenu(PANEL_X + 14, PANEL_Y + 38 + 26 + 30 + 48);
      return;
   }
   if(sparam == PREFIX + btnDnName) {
      if(menuIsOpen && currentMenuFor == "DN") { HideMenu(); return; }
      if(menuIsOpen) HideMenu();
      currentMenuFor = "DN"; menuScrollOffset = 0;
      ShowMenu(PANEL_X + 164, PANEL_Y + 38 + 26 + 30 + 48);
      return;
   }
   
   if(sparam == PREFIX + "m_scroll_up") {
      if(menuScrollOffset > 0) { menuScrollOffset--; ShowMenu(menuAnchorX, menuAnchorY); }
      ObjectSetInteger(0, PREFIX + "m_scroll_up", OBJPROP_STATE, false);
      return;
   }
   if(sparam == PREFIX + "m_scroll_dn") {
      if(menuScrollOffset + MENU_VISIBLE_ROWS < MENU_TOTAL_BUFFERS)
         { menuScrollOffset++; ShowMenu(menuAnchorX, menuAnchorY); }
      ObjectSetInteger(0, PREFIX + "m_scroll_dn", OBJPROP_STATE, false);
      return;
   }
   
   if(StringFind(sparam, PREFIX + "opt_") == 0) {
      int b = (int)StringToInteger(StringSubstr(sparam, StringLen(PREFIX + "opt_")));
      if(currentMenuFor == "UP") {
         selectedUpBuffer = b;
         ObjectSetString(0, PREFIX + btnUpName, OBJPROP_TEXT, "▲ CALL: Buf#" + (string)b);
         ObjectSetInteger(0, PREFIX + btnUpName, OBJPROP_BGCOLOR, CLR_CALL_DIM);
      }
      if(currentMenuFor == "DN") {
         selectedDnBuffer = b;
         ObjectSetString(0, PREFIX + btnDnName, OBJPROP_TEXT, "▼ PUT: Buf#" + (string)b);
         ObjectSetInteger(0, PREFIX + btnDnName, OBJPROP_BGCOLOR, CLR_PUT_DIM);
      }
      HideMenu();
      UpdateStartBtnStyle();
      return;
   }
   
   if(sparam == PREFIX + btnHistUp) {
      if(histScrollOffset > 0) { histScrollOffset--; DrawHistoryRows(); }
      ObjectSetInteger(0, PREFIX + btnHistUp, OBJPROP_STATE, false);
      return;
   }
   if(sparam == PREFIX + btnHistDn) {
      if(histScrollOffset + HIST_VISIBLE_ROWS < sigCacheCount)
         { histScrollOffset++; DrawHistoryRows(); }
      ObjectSetInteger(0, PREFIX + btnHistDn, OBJPROP_STATE, false);
      return;
   }
   
   if(sparam == PREFIX + btnStartName) {
      if(menuIsOpen) { HideMenu(); return; }
      if(!isScanning && (selectedUpBuffer == -1 || selectedDnBuffer == -1)) {
         UpdateStatusLabel("⚠️ Set CALL and PUT buffers first!", CLR_TEXT_YEL);
         ObjectSetInteger(0, PREFIX + btnStartName, OBJPROP_STATE, false);
         return;
      }
      isScanning = !isScanning;
      UpdateStartBtnStyle();
      ObjectSetInteger(0, PREFIX + btnStartName, OBJPROP_STATE, false);
      
      if(isScanning) {
         LastCandleTime = Time[0];
         LastPeriodSec = GetPeriodSeconds();
         ResetBarState();
         Print("VP14: 🟢 SCAN STARTED - Signals will be sent to bot!");
         UpdateStatusLabel("🟢 SCANNING - Bot connected: " + SignalFileName, CLR_SCAN_ON);
      } else {
         UpdateStatusLabel("🔴 SCAN STOPPED", CLR_PUT);
         UpdateLiveSignalBadge("");
         flashCount = 0;
         Print("VP14: 🔴 SCAN STOPPED");
      }
   }
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
// دوال مساعدة للرسم
//+------------------------------------------------------------------+
void DrawRectEx(string n, int x, int y, int w, int h, color bg, color brd, int z) {
   string nm = PREFIX + n;
   if(ObjectFind(0, nm) < 0) ObjectCreate(0, nm, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSetInteger(0, nm, OBJPROP_XDISTANCE, x); ObjectSetInteger(0, nm, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, nm, OBJPROP_XSIZE, w); ObjectSetInteger(0, nm, OBJPROP_YSIZE, h);
   ObjectSetInteger(0, nm, OBJPROP_BGCOLOR, bg); ObjectSetInteger(0, nm, OBJPROP_COLOR, brd);
   ObjectSetInteger(0, nm, OBJPROP_BORDER_TYPE, BORDER_FLAT);
   ObjectSetInteger(0, nm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, nm, OBJPROP_ZORDER, z); ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
}

void DrawLabelEx(string n, int x, int y, string t, color c, int sz) {
   string nm = PREFIX + n;
   if(ObjectFind(0, nm) < 0) ObjectCreate(0, nm, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, nm, OBJPROP_XDISTANCE, x); ObjectSetInteger(0, nm, OBJPROP_YDISTANCE, y);
   ObjectSetString(0, nm, OBJPROP_TEXT, t); ObjectSetInteger(0, nm, OBJPROP_COLOR, c);
   ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, sz); ObjectSetInteger(0, nm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, nm, OBJPROP_ZORDER, 2); ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
}

void CreateBtn(string n, int x, int y, int w, int h, string t, color bg, int sz) {
   string nm = PREFIX + n;
   if(ObjectFind(0, nm) < 0) ObjectCreate(0, nm, OBJ_BUTTON, 0, 0, 0);
   ObjectSetInteger(0, nm, OBJPROP_XDISTANCE, x); ObjectSetInteger(0, nm, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, nm, OBJPROP_XSIZE, w); ObjectSetInteger(0, nm, OBJPROP_YSIZE, h);
   ObjectSetString(0, nm, OBJPROP_TEXT, t); ObjectSetInteger(0, nm, OBJPROP_BGCOLOR, bg);
   ObjectSetInteger(0, nm, OBJPROP_COLOR, CLR_TEXT_W); ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, sz);
   ObjectSetInteger(0, nm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, nm, OBJPROP_ZORDER, 3); ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, true);
}

void CreateBtnStyled(string n, int x, int y, int w, int h, string t, color bg, color txtC) {
   string nm = PREFIX + n;
   if(ObjectFind(0, nm) < 0) ObjectCreate(0, nm, OBJ_BUTTON, 0, 0, 0);
   ObjectSetInteger(0, nm, OBJPROP_XDISTANCE, x); ObjectSetInteger(0, nm, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, nm, OBJPROP_XSIZE, w); ObjectSetInteger(0, nm, OBJPROP_YSIZE, h);
   ObjectSetString(0, nm, OBJPROP_TEXT, t); ObjectSetInteger(0, nm, OBJPROP_BGCOLOR, bg);
   ObjectSetInteger(0, nm, OBJPROP_COLOR, txtC); ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, 8);
   ObjectSetInteger(0, nm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, nm, OBJPROP_ZORDER, 3); ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, true);
}

void CreateBtnBig(string n, int x, int y, int w, int h, string t, color bg) {
   string nm = PREFIX + n;
   if(ObjectFind(0, nm) < 0) ObjectCreate(0, nm, OBJ_BUTTON, 0, 0, 0);
   ObjectSetInteger(0, nm, OBJPROP_XDISTANCE, x); ObjectSetInteger(0, nm, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, nm, OBJPROP_XSIZE, w); ObjectSetInteger(0, nm, OBJPROP_YSIZE, h);
   ObjectSetString(0, nm, OBJPROP_TEXT, t); ObjectSetInteger(0, nm, OBJPROP_BGCOLOR, bg);
   ObjectSetInteger(0, nm, OBJPROP_COLOR, CLR_BG_DARK); ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, 9);
   ObjectSetInteger(0, nm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, nm, OBJPROP_ZORDER, 3); ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, true);
}

void CreateScrollBtn(string n, int x, int y, int w, int h, string t) {
   string nm = PREFIX + n;
   if(ObjectFind(0, nm) < 0) ObjectCreate(0, nm, OBJ_BUTTON, 0, 0, 0);
   ObjectSetInteger(0, nm, OBJPROP_XDISTANCE, x); ObjectSetInteger(0, nm, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, nm, OBJPROP_XSIZE, w); ObjectSetInteger(0, nm, OBJPROP_YSIZE, h);
   ObjectSetString(0, nm, OBJPROP_TEXT, t); ObjectSetInteger(0, nm, OBJPROP_BGCOLOR, CLR_ACCENT);
   ObjectSetInteger(0, nm, OBJPROP_COLOR, CLR_BG_DARK); ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, 7);
   ObjectSetInteger(0, nm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, nm, OBJPROP_ZORDER, 3); ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, true);
}
//+------------------------------------------------------------------+
