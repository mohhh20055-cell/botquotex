//+------------------------------------------------------------------+
//| MT4_Volcano_Bot_Connected.mq4                                      |
//| VOLCANO BOT - EA متصل مباشرة بالبوت على Render                      |
//| يرسل الإشارات عبر HTTP POST API                                    |
//+------------------------------------------------------------------+
#property copyright "Volcano Bot - Cloud Connected"
#property version   "15.0"
#property strict

//--- إعدادات البوت
input string  BotAPI_URL      = "https://botquotex-api-xxxx.onrender.com"; // رابط البوت على Render
input string  BotAPI_Key     = "";                                         // مفتاح API (اختياري)
input double  DefaultAmount   = 1.0;                                        // المبلغ الافتراضي
input int     DefaultDuration = 60;                                          // المدة الافتراضية (ثواني)
input bool    DebugMode      = true;                                        // وضع التصحيح
input bool    AutoStart      = false;                                      // بدء تلقائي عند التحميل

//--- Prefix للكائنات
#define PREFIX "VB15_"

//--- أسماء الأزرار
string btnUpName    = "btn_up";
string btnDnName    = "btn_dn";
string btnStartName = "btn_start";
string btnSendName  = "btn_send";
string btnHistUp    = "btn_hist_up";
string btnHistDn    = "btn_hist_dn";
string btnCloseName = "btn_close";
string btnMinName   = "btn_min";
string btnTestName  = "btn_test";

//--- ثوابت التصميم
#define PANEL_X        20
#define PANEL_Y        20
#define PANEL_W        500
#define PANEL_H        420

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
bool   apiConnected     = false;

//--- كاش الإشارات
struct SignalRow {
   string timeStr;
   string sigType;
   int    bufNum;
   string symbolName;
   string status;
   color  clr;
   bool   sent;
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
int      remainingSeconds   = 0;

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
color CLR_API_OK     = C'0,200,100';
color CLR_API_ERR    = C'255,80,80';

string currentMenuFor = "";

//+------------------------------------------------------------------+
//| تحويل اسم الأداة لـ Quotex                                           |
//+------------------------------------------------------------------+
string GetQuotexSymbol(string sym) {
   // StringTrim doesn't exist in MQL4, use manual trim
   while(StringGetCharacter(sym, 0) == 32) sym = StringSubstr(sym, 1);
   while(StringGetCharacter(sym, StringLen(sym)-1) == 32) sym = StringSubstr(sym, 0, StringLen(sym)-1);
   
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
   if(sym == "XAUUSD" || sym == "GOLD") return "XAU/USD";
   if(sym == "BTCUSD" || sym == "BTC") return "BTC/USD";
   if(sym == "ETHUSD" || sym == "ETH") return "ETH/USD";
   
   StringReplace(sym, "_", "/");
   return sym;
}

//+------------------------------------------------------------------+
//| إرسال الإشارة للبوت عبر HTTP POST                                    |
//+------------------------------------------------------------------+
bool SendSignalToBot(string symbol, string direction, double amount, int duration) {
   // التحقق من الاتصال
   if(!apiConnected) {
      if(DebugMode) Print("VB15: ⚠️ API not connected!");
      return false;
   }
   
   // التحقق من الرابط
   if(StringFind(BotAPI_URL, "xxxx") != -1) {
      if(DebugMode) Print("VB15: ⚠️ Please set valid BotAPI_URL!");
      return false;
   }
   
   // بناء JSON
   string json = "{";
   json += "\"asset\":\"" + symbol + "\",";
   json += "\"direction\":\"" + direction + "\",";
   json += "\"amount\":" + DoubleToString(amount, 2) + ",";
   json += "\"duration\":" + IntegerToString(duration);
   json += "}";
   
   // إعداد HTTP Request
   char postData[];
   char result[];
   string headers = "Content-Type: application/json";
   
   // تحويل JSON للبايتات
   StringToCharArray(json, postData);
   
   // إرسال الطلب
   int timeout = 5000; // 5 ثواني
   int res = WebRequest(
      "POST", 
      BotAPI_URL + "/signal",
      headers,
      timeout,
      postData,
      result
   );
   
   if(res == -1) {
      // خطأ في الشبكة
      int err = GetLastError();
      if(DebugMode) Print("VB15: ❌ Network error: ", err);
      UpdateApiStatus(false);
      return false;
   }
   
   if(res == 200 || res == 201) {
      // نجاح
      if(DebugMode) Print("VB15: ✅ Signal sent successfully! Response code: ", res);
      return true;
   } else {
      // خطأ HTTP
      if(DebugMode) Print("VB15: ❌ HTTP error: ", res);
      return false;
   }
}

//+------------------------------------------------------------------+
//| اختبار الاتصال بالبوت                                               |
//+------------------------------------------------------------------+
bool TestBotConnection() {
   if(StringFind(BotAPI_URL, "xxxx") != -1) {
      if(DebugMode) Print("VB15: ⚠️ Please set valid BotAPI_URL first!");
      return false;
   }
   
   char result[];
   string headers = "Content-Type: application/json";
   
   int timeout = 5000;
   int res = WebRequest(
      "GET", 
      BotAPI_URL + "/health",
      headers,
      timeout,
      result
   );
   
   if(res == 200) {
      apiConnected = true;
      if(DebugMode) Print("VB15: ✅ Bot connection successful!");
      return true;
   } else {
      apiConnected = false;
      if(DebugMode) Print("VB15: ❌ Bot connection failed! HTTP code: ", res);
      return false;
   }
}

//+------------------------------------------------------------------+
//| حفظ الإشارة وإرسالها للبوت                                          |
//+------------------------------------------------------------------+
bool SaveAndSendSignal(string sigType, int bufferNum) {
   // منع الإرسال المتكرر
   if(sigType == "CALL" && callSentThisBar) return true;
   if(sigType == "PUT" && putSentThisBar) return true;
   
   // تحويل اسم الأداة
   string sym = GetQuotexSymbol(Symbol());
   
   // إضافة للسجل
   AddSignalToHistory(sigType, bufferNum, "PENDING");
   
   // إرسال للبوت
   bool sent = SendSignalToBot(sym, sigType, DefaultAmount, DefaultDuration);
   
   // تحديث حالة الإشارة
   if(sent) {
      UpdateSignalStatus(0, "✅ SENT", sigType == "CALL" ? CLR_CALL : CLR_PUT);
      
      if(sigType == "CALL") {
         callSentThisBar = true;
         TriggerFlash("CALL");
         UpdateStatusLabel("✅ CALL SENT - " + sym, CLR_CALL);
      } else {
         putSentThisBar = true;
         TriggerFlash("PUT");
         UpdateStatusLabel("✅ PUT SENT - " + sym, CLR_PUT);
      }
      
      if(DebugMode) {
         Print("VB15: ✅ Signal sent: ", sym, " ", sigType, " $", DefaultAmount, " ", DefaultDuration, "s");
      }
   } else {
      UpdateSignalStatus(0, "❌ FAILED", CLR_PUT);
      UpdateStatusLabel("❌ Signal failed!", CLR_PUT);
   }
   
   return sent;
}

//+------------------------------------------------------------------+
//| تحديث حالة إشارة في السجل                                          |
//+------------------------------------------------------------------+
void UpdateSignalStatus(int idx, string status, color clr) {
   if(idx < 0 || idx >= sigCacheCount) return;
   sigCache[idx].status = status;
   sigCache[idx].clr = clr;
   sigCache[idx].sent = (StringFind(status, "SENT") != -1);
   DrawHistoryRows();
}

//+------------------------------------------------------------------+
//| فحص البافرات وإرسال الإشارات                                         |
//+------------------------------------------------------------------+
void CheckAndSendSignals() {
   if(!isScanning) return;
   if(selectedUpBuffer == -1 && selectedDnBuffer == -1) return;
   if(!apiConnected) return;
   
   datetime currentTime = TimeCurrent();
   datetime candleCloseTime = LastCandleTime + LastPeriodSec;
   int secondsToClose = (int)(candleCloseTime - currentTime);
   
   // فحص قبل الإغلاق
   if(secondsToClose <= 1 && secondsToClose >= 0) {
      CheckBuffers(0, "BEFORE");
   }
   
   // فحص عند الإغلاق
   if(secondsToClose <= 0) {
      CheckBuffers(0, "CLOSE");
      CheckBuffers(1, "AFTER");
   }
}

//+------------------------------------------------------------------+
//| فحص البافرات المحددة                                                |
//+------------------------------------------------------------------+
void CheckBuffers(int shift, string timing) {
   // فحص CALL buffer
   if(selectedUpBuffer != -1 && !callSentThisBar) {
      double callVal = iCustom(NULL, 0, detectedIndicator, selectedUpBuffer, shift);
      bool callOk = (callVal != EMPTY_VALUE && callVal != 0 && callVal != NULL);
      
      if(callOk && callVal > 0) {
         if(DebugMode) Print("VB15: 📡 CALL @ ", timing, " shift=", shift);
         UpdateStatusLabel("📡 CALL @ " + timing, CLR_CALL);
         SaveAndSendSignal("CALL", selectedUpBuffer);
      }
   }
   
   // فحص PUT buffer
   if(selectedDnBuffer != -1 && !putSentThisBar) {
      double putVal = iCustom(NULL, 0, detectedIndicator, selectedDnBuffer, shift);
      bool putOk = (putVal != EMPTY_VALUE && putVal != 0 && putVal != NULL);
      
      if(putOk && putVal > 0) {
         if(DebugMode) Print("VB15: 📡 PUT @ ", timing, " shift=", shift);
         UpdateStatusLabel("📡 PUT @ " + timing, CLR_PUT);
         SaveAndSendSignal("PUT", selectedDnBuffer);
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
void UpdateApiStatus(bool connected) {
   apiConnected = connected;
   if(ObjectFind(0, PREFIX + "api_badge") >= 0) {
      string txt = connected ? "🟢 CONNECTED" : "🔴 OFFLINE";
      color clr = connected ? CLR_API_OK : CLR_API_ERR;
      ObjectSetString(0, PREFIX + "api_badge", OBJPROP_TEXT, txt);
      ObjectSetInteger(0, PREFIX + "api_badge", OBJPROP_COLOR, clr);
   }
}

//+------------------------------------------------------------------+
int OnInit() {
   EventKillTimer();
   
   // اكتشاف المؤشر
   for(int i = 0; i < ChartIndicatorsTotal(0, 0); i++) {
      string n = ChartIndicatorName(0, 0, i);
      if(n != "" && StringFind(n, "VB15") < 0 && StringFind(n, "VP") < 0) {
         detectedIndicator = n;
         Print("VB15: ✅ Detected indicator: ", n);
         break;
      }
   }
   
   if(detectedIndicator == "") {
      Print("VB15: ⚠️ No external indicator detected!");
   }
   
   // اختبار الاتصال بالبوت
   if(BotAPI_URL != "" && StringFind(BotAPI_URL, "xxxx") == -1) {
      TestBotConnection();
   }
   
   LastCandleTime = Time[0];
   LastPeriodSec  = Period() * 60;
   ResetBarState();
   
   BuildSignalCache();
   CreateMainUI();
   EventSetTimer(1);
   
   if(AutoStart && detectedIndicator != "" && apiConnected) {
      isScanning = true;
      UpdateStartBtnStyle();
   }
   
   Print("==========================================");
   Print("VB15: 🚀 VOLCANO BOT CONNECTED v15.0");
   Print("VB15: 🔗 Bot URL: ", BotAPI_URL);
   Print("VB15: 📡 Symbol: ", GetQuotexSymbol(Symbol()));
   Print("VB15: 💰 Amount: $", DefaultAmount);
   Print("VB15: ⏱️ Duration: ", DefaultDuration, "s");
   Print("==========================================");
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
   EventKillTimer();
   ObjectsDeleteAll(0, PREFIX);
   Print("VB15: Deinitialized. Reason=", reason);
}

//+------------------------------------------------------------------+
void OnTick() {
   if(!isScanning) return;
   
   datetime curCandle = Time[0];
   datetime curTime  = TimeCurrent();
   
   // شمعة جديدة
   if(curCandle != LastCandleTime) {
      Print("VB15: 🕯️ NEW CANDLE @ ", TimeToStr(curCandle, TIME_SECONDS));
      
      LastCandleTime = curCandle;
      LastPeriodSec  = Period() * 60;
      ResetBarState();
      
      UpdateStatusLabel("⏳ Monitoring...", CLR_TEXT_YEL);
      
      datetime candleClose = LastCandleTime + LastPeriodSec;
      Print("VB15: ⏰ Candle closes at: ", TimeToStr(candleClose, TIME_SECONDS));
   }
   
   // تحديث الوقت
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
   
   // إعادة بناء الواجهة
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
void AddSignalToHistory(string sigType, int bufNum, string status) {
   SignalRow nr;
   nr.timeStr    = TimeToStr(TimeCurrent(), TIME_MINUTES | TIME_SECONDS);
   nr.sigType    = sigType;
   nr.bufNum     = bufNum;
   nr.symbolName = GetQuotexSymbol(Symbol());
   nr.status     = status;
   nr.clr        = (sigType == "CALL") ? CLR_CALL : CLR_PUT;
   nr.sent       = false;
   
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
         sigCache[sigCacheCount].sigType   = sig;
         sigCache[sigCacheCount].bufNum    = buf;
         sigCache[sigCacheCount].symbolName = cs;
         sigCache[sigCacheCount].status     = "HIST";
         sigCache[sigCacheCount].clr       = col;
         sigCache[sigCacheCount].sent       = false;
         sigCacheCount++;
      }
   }
}

//+------------------------------------------------------------------+
// واجهة المستخدم
//+------------------------------------------------------------------+
void CreateMainUI() {
   int bx = PANEL_X, by = PANEL_Y, w = PANEL_W, h = PANEL_H;
   
   DrawRectEx("shadow",  bx + 4, by + 4, w, h, C'5,6,10', C'5,6,10', 0);
   DrawRectEx("frame",   bx - 2, by - 2, w + 4, h + 4, CLR_BG_DARK, CLR_ACCENT, 0);
   DrawRectEx("bg",      bx, by, w, h, CLR_BG_MID, CLR_BORDER, 0);
   
   // الهيدر
   DrawRectEx("hdr",      bx, by, w, 40, CLR_BG_DARK, CLR_ACCENT, 0);
   DrawRectEx("hdr_line", bx, by + 40, w, 2, CLR_ACCENT, CLR_ACCENT, 0);
   DrawLabelEx("ico",     bx + 10, by + 11, "🌐", CLR_ACCENT, 13);
   DrawLabelEx("title",  bx + 34, by + 12, "VOLCANO BOT CLOUD", CLR_ACCENT, 10);
   DrawLabelEx("ver",    bx + 220, by + 16, "v15.0", CLR_TEXT_DIM, 7);
   DrawLabelEx("clk_ico",bx + 270, by + 12, "⏱", CLR_TEXT_DIM, 8);
   DrawLabelEx("clock",  bx + 288, by + 12, TimeToStr(TimeCurrent(), TIME_MINUTES | TIME_SECONDS), CLR_TEXT_YEL, 8);
   CreateBtn(btnMinName,   bx + w - 85, by + 7, 24, 27, "—", CLR_BORDER2, 8);
   CreateBtn(btnTestName,  bx + w - 57, by + 7, 28, 27, "🔄", CLR_BORDER2, 8);
   CreateBtn(btnCloseName, bx + w - 25, by + 7, 27, 27, "✕", C'180,30,40', 10);
   
   // شريط المعلومات
   int iy = by + 45;
   DrawRectEx("info_bar", bx, iy, w, 30, CLR_BG_LIGHT, CLR_BORDER, 0);
   DrawLabelEx("sym_lbl", bx + 10, iy + 8, "SYMBOL:", CLR_TEXT_DIM, 7);
   DrawLabelEx("sym_val", bx + 58, iy + 8, GetQuotexSymbol(Symbol()), CLR_TEXT_YEL, 8);
   DrawLabelEx("ind_lbl", bx + 150, iy + 8, "INDICATOR:", CLR_TEXT_DIM, 7);
   string indTxt = (detectedIndicator == "") ? "NOT FOUND" : detectedIndicator;
   if(StringLen(indTxt) > 14) indTxt = StringSubstr(indTxt, 0, 12) + "..";
   DrawLabelEx("ind_val", bx + 220, iy + 8, indTxt, (detectedIndicator == "") ? CLR_PUT : CLR_CALL, 7);
   
   // حالة API
   string apiTxt = apiConnected ? "🟢 CONNECTED" : "🔴 OFFLINE";
   color apiClr = apiConnected ? CLR_API_OK : CLR_API_ERR;
   DrawRectEx("api_box", bx + 340, iy + 3, 150, 24, CLR_BG_MID, apiClr, 0);
   DrawLabelEx("api_badge", bx + 350, iy + 8, apiTxt, apiClr, 8);
   
   // لوحة الإعداد
   int cy = iy + 34;
   DrawRectEx("cfg_panel",    bx + 8, cy, w - 16, 85, CLR_BG_DARK, CLR_BORDER, 0);
   DrawRectEx("cfg_title_bar", bx + 8, cy, w - 16, 18, CLR_BORDER, CLR_BORDER, 0);
   DrawLabelEx("cfg_title", bx + 14, cy + 3, "⚙ BUFFER CONFIGURATION", CLR_TEXT_DIM, 7);
   
   CreateBtnStyled(btnUpName, bx + 14, cy + 24, 150, 26,
      (selectedUpBuffer == -1) ? "▲ SET CALL" : "▲ CALL: Buf#" + (string)selectedUpBuffer,
      (selectedUpBuffer == -1) ? CLR_BG_LIGHT : CLR_CALL_DIM, CLR_CALL);
   CreateBtnStyled(btnDnName, bx + 174, cy + 24, 150, 26,
      (selectedDnBuffer == -1) ? "▼ SET PUT" : "▼ PUT: Buf#" + (string)selectedDnBuffer,
      (selectedDnBuffer == -1) ? CLR_BG_LIGHT : CLR_PUT_DIM, CLR_PUT);
   
   // إعدادات التداول
   DrawRectEx("trade_cfg", bx + 14, cy + 55, 130, 24, CLR_BG_MID, CLR_BORDER, 0);
   DrawLabelEx("amount_lbl", bx + 18, cy + 61, "AMOUNT: $" + DoubleToString(DefaultAmount, 2), CLR_TEXT_W, 7);
   DrawRectEx("dur_cfg", bx + 154, cy + 55, 170, 24, CLR_BG_MID, CLR_BORDER, 0);
   DrawLabelEx("dur_lbl", bx + 158, cy + 61, "DURATION: " + IntegerToString(DefaultDuration) + "s", CLR_TEXT_W, 7);
   
   // زر البدء
   string stTxt = isScanning ? "■  STOP SCAN" : "▶  START SCAN";
   color stBg = isScanning ? CLR_SCAN_OFF :
      ((selectedUpBuffer != -1 && selectedDnBuffer != -1 && apiConnected) ? CLR_SCAN_ON : CLR_BORDER);
   CreateBtnBig(btnStartName, bx + 340, cy + 22, 150, 55, stTxt, stBg);
   
   // قسم الإشارة الحية
   int lsy = cy + 90;
   DrawRectEx("flash_bg", bx + 8, lsy, w - 16, 38, CLR_BG_MID, CLR_BORDER, 0);
   DrawLabelEx("live_lbl",   bx + 16, lsy + 13, "LIVE:", CLR_TEXT_DIM, 7);
   DrawLabelEx("live_badge", bx + 55, lsy + 10, "—", CLR_TEXT_DIM, 10);
   DrawLabelEx("timer_ico",   bx + 200, lsy + 13, "⏳", CLR_TEXT_DIM, 7);
   DrawLabelEx("timer_lbl",   bx + 218, lsy + 13, "—", CLR_TEXT_DIM, 7);
   DrawRectEx("timer_track", bx + 260, lsy + 16, w - 290, 8, CLR_BG_DARK, CLR_BORDER, 0);
   DrawRectEx("timer_bar",   bx + 260, lsy + 16, 2, 8, CLR_PROGRESS, CLR_PROGRESS, 0);
   
   // شريط الحالة
   int sty = lsy + 42;
   DrawRectEx("st_bar",  bx + 8, sty, w - 16, 24, CLR_BG_DARK, CLR_BORDER, 0);
   DrawLabelEx("st_ico", bx + 14, sty + 7, "●", CLR_TEXT_DIM, 7);
   DrawLabelEx("st_val", bx + 26, sty + 6, "READY - Bot: " + BotAPI_URL, CLR_TEXT_DIM, 7);
   
   // جدول الإشارات
   int hy = sty + 30;
   DrawRectEx("hist_hdr", bx + 8, hy, w - 16, 20, C'14,18,30', CLR_BORDER, 0);
   DrawLabelEx("h_icon",    bx + 14, hy + 5, "📋", CLR_TEXT_DIM, 7);
   DrawLabelEx("h_title",   bx + 30, hy + 5, "SIGNAL HISTORY", CLR_TEXT_W, 7);
   DrawLabelEx("hist_counter", bx + 220, hy + 5, "0 / 0", CLR_TEXT_DIM, 7);
   CreateScrollBtn(btnHistUp, bx + w - 50, hy + 2, 19, 16, "▲");
   CreateScrollBtn(btnHistDn, bx + w - 28, hy + 2, 19, 16, "▼");
   
   DrawRectEx("hist_body", bx + 8, hy + 20, w - 16, HIST_VISIBLE_ROWS * 20 + 18, CLR_BG_DARK, CLR_BORDER, 0);
   int hcy = hy + 22;
   DrawRectEx("col_hdr", bx + 8, hcy, w - 16, 16, CLR_BG_LIGHT, CLR_BORDER, 0);
   DrawLabelEx("hc_time",   bx + 14, hcy + 3, "TIME", CLR_TEXT_DIM, 6);
   DrawLabelEx("hc_side",   bx + 95, hcy + 3, "SIDE", CLR_TEXT_DIM, 6);
   DrawLabelEx("hc_sym",    bx + 165, hcy + 3, "SYMBOL", CLR_TEXT_DIM, 6);
   DrawLabelEx("hc_buf",    bx + 270, hcy + 3, "BUF", CLR_TEXT_DIM, 6);
   DrawLabelEx("hc_status", bx + 340, hcy + 3, "STATUS", CLR_TEXT_DIM, 6);
   
   DrawHistoryRows();
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
void DrawHistoryRows() {
   if(isPanelMinimized) return;
   int bx = PANEL_X, by = PANEL_Y;
   int hy = by + 45 + 30 + 34 + 85 + 90 + 42 + 30;
   int rsy = hy + 22 + 16 + 2;
   
   for(int r = 0; r < HIST_VISIBLE_ROWS; r++) {
      string p = (string)r;
      ObjectDelete(0, PREFIX + "rw_bg_" + p);
      ObjectDelete(0, PREFIX + "rw_new_" + p);
      ObjectDelete(0, PREFIX + "rw_time_" + p);
      ObjectDelete(0, PREFIX + "rw_side_" + p);
      ObjectDelete(0, PREFIX + "rw_sym_" + p);
      ObjectDelete(0, PREFIX + "rw_buf_" + p);
      ObjectDelete(0, PREFIX + "rw_stat_" + p);
   }
   
   if(sigCacheCount == 0) {
      DrawLabelEx("hist_empty", bx + 180, rsy + 28, "No signals recorded", CLR_TEXT_DIM, 8);
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
      if(sigCache[idx].sent)
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
      
      if(sigCache[idx].sent) {
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
      DrawLabelEx("rw_side_" + p, bx + 95, rowY + 3,
         (sigCache[idx].sigType == "CALL") ? "▲ CALL" : "▼ PUT",
         sigCache[idx].clr, 7);
      DrawLabelEx("rw_sym_" + p, bx + 165, rowY + 4, sigCache[idx].symbolName, C'180,200,255', 6);
      DrawLabelEx("rw_buf_" + p, bx + 273, rowY + 4, "#" + (string)sigCache[idx].bufNum, CLR_TEXT_DIM, 6);
      DrawLabelEx("rw_stat_" + p, bx + 340, rowY + 4, sigCache[idx].status, sigCache[idx].clr, 6);
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
   int barMaxW = PANEL_W - 290, barW = (int)(barMaxW * ratio);
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
   DrawLabelEx("ico", bx + 10, by + 12, "🌐", CLR_ACCENT, 12);
   DrawLabelEx("title", bx + 34, by + 13, "VOLCANO BOT v15.0", CLR_ACCENT, 9);
   string statusTxt = isScanning ? "● SCANNING" : "● STOPPED";
   color statusClr = isScanning ? CLR_CALL : CLR_PUT;
   DrawLabelEx("st_val", bx + 200, by + 13, statusTxt, statusClr, 8);
   CreateBtn(btnMinName, bx + w - 60, by + 7, 24, 26, "□", CLR_BORDER2, 8);
   CreateBtn(btnCloseName, bx + w - 32, by + 7, 27, 26, "✕", C'180,30,40', 10);
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
void UpdateStartBtnStyle() {
   bool ready = (selectedUpBuffer != -1 && selectedDnBuffer != -1 && apiConnected);
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
   
   // زر اختبار الاتصال
   if(sparam == PREFIX + btnTestName) {
      if(TestBotConnection()) {
         UpdateStatusLabel("✅ Bot Connected!", CLR_CALL);
         UpdateApiStatus(true);
      } else {
         UpdateStatusLabel("❌ Connection Failed!", CLR_PUT);
         UpdateApiStatus(false);
      }
      CreateMainUI();
      return;
   }
   
   if(isPanelMinimized) return;
   
   if(sparam == PREFIX + btnUpName) {
      if(menuIsOpen && currentMenuFor == "UP") { HideMenu(); return; }
      if(menuIsOpen) HideMenu();
      currentMenuFor = "UP"; menuScrollOffset = 0;
      ShowMenu(PANEL_X + 14, PANEL_Y + 45 + 30 + 34 + 50);
      return;
   }
   if(sparam == PREFIX + btnDnName) {
      if(menuIsOpen && currentMenuFor == "DN") { HideMenu(); return; }
      if(menuIsOpen) HideMenu();
      currentMenuFor = "DN"; menuScrollOffset = 0;
      ShowMenu(PANEL_X + 174, PANEL_Y + 45 + 30 + 34 + 50);
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
      if(!isScanning && !apiConnected) {
         UpdateStatusLabel("⚠️ Test bot connection first!", CLR_TEXT_YEL);
         ObjectSetInteger(0, PREFIX + btnStartName, OBJPROP_STATE, false);
         return;
      }
      isScanning = !isScanning;
      UpdateStartBtnStyle();
      ObjectSetInteger(0, PREFIX + btnStartName, OBJPROP_STATE, false);
      
      if(isScanning) {
         LastCandleTime = Time[0];
         LastPeriodSec = Period() * 60;
         ResetBarState();
         Print("VB15: 🟢 SCAN STARTED - Signals will be sent to bot!");
         UpdateStatusLabel("🟢 SCANNING - Bot: " + BotAPI_URL, CLR_SCAN_ON);
      } else {
         UpdateStatusLabel("🔴 SCAN STOPPED", CLR_PUT);
         UpdateLiveSignalBadge("");
         flashCount = 0;
         Print("VB15: 🔴 SCAN STOPPED");
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
