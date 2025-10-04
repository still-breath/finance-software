from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QLabel, QPushButton)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

from utils.logger import log_app_event

class ReportsPage(QWidget):
    """Standalone Reports Page extracted from DashboardWindow.
    Provides financial analytics cards and the simplified Monthly Trends (chart + recent 6 months table only).
    """
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.setStyleSheet("background-color: transparent;")
        self._build_ui()
    
    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 20, 0, 0)
        main_layout.setSpacing(20)
        title = QLabel("📊 Financial Reports & Analytics")
        title.setFont(QFont('Segoe UI', 24, QFont.Bold))
        title.setStyleSheet("color: #1a202c; margin-bottom: 10px;")
        main_layout.addWidget(title)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(20)
        # Summary / distribution row
        row1 = QHBoxLayout(); row1.setSpacing(20)
        self.monthly_overview_card = self._create_monthly_overview_card(); row1.addWidget(self.monthly_overview_card)
        self.category_distribution_card = self._create_category_distribution_card(); row1.addWidget(self.category_distribution_card)
        self.content_layout.addLayout(row1)
        # Trends + AI stats row
        row2 = QHBoxLayout(); row2.setSpacing(20)
        self.monthly_trend_card = self._create_monthly_trend_card(); row2.addWidget(self.monthly_trend_card)
        self.ai_stats_card = self._create_ai_stats_card(); row2.addWidget(self.ai_stats_card)
        self.content_layout.addLayout(row2)
        # Top categories + recent activity row
        row3 = QHBoxLayout(); row3.setSpacing(20)
        self.top_categories_card = self._create_top_categories_card(); row3.addWidget(self.top_categories_card)
        self.recent_activity_card = self._create_recent_summary_card(); row3.addWidget(self.recent_activity_card)
        self.content_layout.addLayout(row3)
        self.content_layout.addStretch()
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    # Card factories
    def _card_frame(self):
        card = QFrame(); card.setFrameStyle(QFrame.NoFrame)
        card.setStyleSheet("QFrame{background:white;border-radius:12px;}")
        shadow = QGraphicsDropShadowEffect(); shadow.setBlurRadius(15); shadow.setXOffset(0); shadow.setYOffset(3); shadow.setColor(QColor(0,0,0,30))
        card.setGraphicsEffect(shadow)
        return card
    
    def _create_monthly_overview_card(self):
        card = self._card_frame(); layout = QVBoxLayout(card); layout.setContentsMargins(20,20,20,20)
        title = QLabel("📅 This Month Overview"); title.setFont(QFont('Segoe UI',16,QFont.Bold)); title.setStyleSheet("color:#1f2937;margin-bottom:15px;"); layout.addWidget(title)
        self.monthly_income_label = QLabel("Income: Loading...")
        self.monthly_expense_label = QLabel("Expenses: Loading...")
        self.monthly_balance_label = QLabel("Balance: Loading...")
        self.monthly_transactions_label = QLabel("Transactions: Loading...")
        for lbl in [self.monthly_income_label,self.monthly_expense_label,self.monthly_balance_label,self.monthly_transactions_label]:
            lbl.setFont(QFont('Segoe UI',12)); lbl.setStyleSheet("color:#4b5563;margin:3px 0;"); layout.addWidget(lbl)
        layout.addStretch(); return card
    
    def _create_category_distribution_card(self):
        card = self._card_frame(); layout = QVBoxLayout(card); layout.setContentsMargins(20,20,20,20)
        title = QLabel("🎯 Category Distribution"); title.setFont(QFont('Segoe UI',16,QFont.Bold)); title.setStyleSheet("color:#1f2937;margin-bottom:15px;"); layout.addWidget(title)
        self.category_stats_layout = QVBoxLayout(); layout.addLayout(self.category_stats_layout)
        loading = QLabel("Loading category data..."); loading.setFont(QFont('Segoe UI',11)); loading.setStyleSheet("color:#6b7280;"); self.category_stats_layout.addWidget(loading)
        layout.addStretch(); return card
    
    def _create_monthly_trend_card(self):
        card = self._card_frame(); layout = QVBoxLayout(card); layout.setContentsMargins(20,20,20,20)
        title = QLabel("📈 Monthly Trends"); title.setFont(QFont('Segoe UI',16,QFont.Bold)); title.setStyleSheet("color:#1f2937;margin-bottom:15px;"); layout.addWidget(title)
        self.trend_info_layout = QVBoxLayout(); layout.addLayout(self.trend_info_layout)
        loading = QLabel("Loading trend data..."); loading.setFont(QFont('Segoe UI',11)); loading.setStyleSheet("color:#6b7280;"); self.trend_info_layout.addWidget(loading)
        layout.addStretch(); return card
    
    def _create_ai_stats_card(self):
        card = self._card_frame(); layout = QVBoxLayout(card); layout.setContentsMargins(20,20,20,20)
        title = QLabel("🤖 AI Categorization Stats"); title.setFont(QFont('Segoe UI',16,QFont.Bold)); title.setStyleSheet("color:#1f2937;margin-bottom:15px;"); layout.addWidget(title)
        self.ai_stats_layout = QVBoxLayout(); layout.addLayout(self.ai_stats_layout)
        loading = QLabel("Loading AI statistics..."); loading.setFont(QFont('Segoe UI',11)); loading.setStyleSheet("color:#6b7280;"); self.ai_stats_layout.addWidget(loading)
        layout.addStretch(); return card
    
    def _create_top_categories_card(self):
        card = self._card_frame(); layout = QVBoxLayout(card); layout.setContentsMargins(20,20,20,20)
        title = QLabel("🏆 Top Spending Categories"); title.setFont(QFont('Segoe UI',16,QFont.Bold)); title.setStyleSheet("color:#1f2937;margin-bottom:15px;"); layout.addWidget(title)
        self.top_categories_layout = QVBoxLayout(); layout.addLayout(self.top_categories_layout)
        loading = QLabel("Loading top categories..."); loading.setFont(QFont('Segoe UI',11)); loading.setStyleSheet("color:#6b7280;"); self.top_categories_layout.addWidget(loading)
        layout.addStretch(); return card
    
    def _create_recent_summary_card(self):
        card = self._card_frame(); layout = QVBoxLayout(card); layout.setContentsMargins(20,20,20,20)
        title = QLabel("⏰ Recent Activity"); title.setFont(QFont('Segoe UI',16,QFont.Bold)); title.setStyleSheet("color:#1f2937;margin-bottom:15px;"); layout.addWidget(title)
        self.recent_summary_layout = QVBoxLayout(); layout.addLayout(self.recent_summary_layout)
        loading = QLabel("Loading recent activity..."); loading.setFont(QFont('Segoe UI',11)); loading.setStyleSheet("color:#6b7280;"); self.recent_summary_layout.addWidget(loading)
        layout.addStretch(); return card
    
    # Data loading
    def load_all(self):
        try:
            monthly_data = self.api_client.get_monthly_stats(); self.update_monthly_overview(monthly_data); self.update_monthly_trends(monthly_data)
            category_data = self.api_client.get_category_stats(); self.update_category_distribution(category_data); self.update_ai_stats(category_data); self.update_top_categories(category_data)
            tx_data = self.api_client.get_transactions(); self.update_recent_summary(tx_data)
        except Exception as e:
            log_app_event("reports_load_error", "ReportsPage", {"error": str(e)})
    
    # Update helpers
    def update_monthly_overview(self, data):
        try:
            stats = data.get('monthly_stats', [])
            if stats:
                cur = stats[0]
                income = cur.get('income', 0); expense = cur.get('expense', 0); balance = cur.get('balance', 0)
                summary = self.api_client.get_transaction_summary(); txn_count = summary.get('summary', {}).get('transaction_count', 0)
                self.monthly_income_label.setText(f"💰 Income: Rp {income:,.0f}"); self.monthly_income_label.setStyleSheet("color:#059669;font-weight:600;margin:3px 0;")
                self.monthly_expense_label.setText(f"💸 Expenses: Rp {expense:,.0f}"); self.monthly_expense_label.setStyleSheet("color:#dc2626;font-weight:600;margin:3px 0;")
                bal_color = '#059669' if balance >=0 else '#dc2626'
                self.monthly_balance_label.setText(f"📊 Balance: Rp {balance:,.0f}"); self.monthly_balance_label.setStyleSheet(f"color:{bal_color};font-weight:600;margin:3px 0;")
                self.monthly_transactions_label.setText(f"🧾 Transactions: {txn_count}"); self.monthly_transactions_label.setStyleSheet("color:#4b5563;font-weight:600;margin:3px 0;")
            else:
                self.monthly_income_label.setText("💰 Income: Rp 0"); self.monthly_expense_label.setText("💸 Expenses: Rp 0"); self.monthly_balance_label.setText("📊 Balance: Rp 0"); self.monthly_transactions_label.setText("🧾 Transactions: 0")
        except Exception as e:
            log_app_event("reports_update_monthly_overview_error", "ReportsPage", {"error": str(e)})
    
    def update_category_distribution(self, data):
        try:
            while self.category_stats_layout.count():
                child = self.category_stats_layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()
            categories = data.get('category_distribution', [])
            if categories:
                for category in categories[:5]:
                    name = category.get('category_name', 'Unknown'); amount = abs(category.get('total_amount', 0)); count = category.get('transaction_count', 0)
                    item = QLabel(f"{name} — Rp {amount:,.0f} ({count} txn)"); item.setFont(QFont('Segoe UI',11)); item.setStyleSheet("color:#374151;margin:2px 0;"); self.category_stats_layout.addWidget(item)
            else:
                nd = QLabel("No category data available"); nd.setFont(QFont('Segoe UI',11)); nd.setStyleSheet("color:#9ca3af;"); self.category_stats_layout.addWidget(nd)
        except Exception as e:
            log_app_event("reports_update_category_distribution_error", "ReportsPage", {"error": str(e)})
    
    def update_ai_stats(self, data):
        try:
            while self.ai_stats_layout.count():
                child = self.ai_stats_layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()
            methods = data.get('prediction_methods', [])
            total = sum(m.get('count',0) for m in methods)
            if methods and total>0:
                display = {'ai_prediction': '🤖 AI Prediction','manual':'👤 Manual','default':'⚡ Default'}
                for m in methods:
                    name = display.get(m.get('method','unknown'), m.get('method','unknown').title()); count = m.get('count',0); pct = (count/total)*100 if total else 0
                    lbl = QLabel(f"{name}: {pct:.1f}% ({count})"); lbl.setFont(QFont('Segoe UI',11)); lbl.setStyleSheet("color:#6366f1;margin:2px 0;"); self.ai_stats_layout.addWidget(lbl)
            else:
                nd = QLabel("No prediction data available"); nd.setFont(QFont('Segoe UI',11)); nd.setStyleSheet("color:#9ca3af;"); self.ai_stats_layout.addWidget(nd)
        except Exception as e:
            log_app_event("reports_update_ai_stats_error", "ReportsPage", {"error": str(e)})
    
    def update_top_categories(self, data):
        try:
            while self.top_categories_layout.count():
                child = self.top_categories_layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()
            categories = data.get('category_distribution', [])
            if categories:
                sorted_cats = sorted(categories, key=lambda x: abs(x.get('total_amount',0)), reverse=True)
                medals = ['🥇','🥈','🥉']
                for i, cat in enumerate(sorted_cats[:3]):
                    name = cat.get('category_name','Unknown'); amount = abs(cat.get('total_amount',0)); avg = abs(cat.get('avg_amount',0))
                    lbl = QLabel(f"{medals[i] if i<3 else '🏅'} {name}: Rp {amount:,.0f} (Avg Rp {avg:,.0f})"); lbl.setFont(QFont('Segoe UI',11)); lbl.setStyleSheet("color:#1f2937;margin:3px 0;"); self.top_categories_layout.addWidget(lbl)
            else:
                nd = QLabel("No spending data available"); nd.setFont(QFont('Segoe UI',11)); nd.setStyleSheet("color:#9ca3af;"); self.top_categories_layout.addWidget(nd)
        except Exception as e:
            log_app_event("reports_update_top_categories_error", "ReportsPage", {"error": str(e)})
    
    def update_recent_summary(self, data):
        try:
            while self.recent_summary_layout.count():
                child = self.recent_summary_layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()
            txs = data.get('transactions', [])
            if txs:
                for tx in txs[:5]:
                    desc = tx.get('description','Unknown'); amount = tx.get('amount',0); cat = tx.get('category_name','No Category'); date = tx.get('transaction_date','')[:10]
                    color = '#059669' if amount>0 else '#dc2626'; sign = '+' if amount>0 else ''
                    lbl = QLabel(f"{date} • {cat} • {desc[:28] + '...' if len(desc)>28 else desc} — <span style='color:{color};font-weight:600'>{sign}Rp {abs(amount):,.0f}</span>")
                    lbl.setFont(QFont('Segoe UI',10)); lbl.setTextFormat(Qt.RichText); lbl.setStyleSheet("color:#374151;margin:2px 0;")
                    self.recent_summary_layout.addWidget(lbl)
            else:
                nd = QLabel("No recent transactions"); nd.setFont(QFont('Segoe UI',11)); nd.setStyleSheet("color:#9ca3af;"); self.recent_summary_layout.addWidget(nd)
        except Exception as e:
            log_app_event("reports_update_recent_summary_error", "ReportsPage", {"error": str(e)})
    
    def update_monthly_trends(self, monthly_data):
        try:
            raw = []
            if not monthly_data: return
            if 'monthly_stats' in monthly_data: raw = monthly_data.get('monthly_stats', [])
            elif 'months' in monthly_data: raw = monthly_data.get('months', [])
            elif isinstance(monthly_data, list): raw = monthly_data
            cleaned = []
            for item in raw:
                mkey = item.get('month') or item.get('period') or item.get('date')
                if not mkey: continue
                mid = mkey[:7]
                inc = item.get('income') or item.get('total_income') or 0
                exp = item.get('expense') or item.get('total_expense') or 0
                bal = item.get('balance') or (inc - abs(exp))
                cleaned.append({'month': mid,'income': float(inc),'expense': float(exp),'balance': float(bal)})
            cleaned.sort(key=lambda x: x['month'])
            # Clear layout
            while self.trend_info_layout.count():
                child = self.trend_info_layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()
            if not cleaned:
                self.trend_info_layout.addWidget(QLabel("No data")); return
            def fmt_month(m):
                try:
                    y, mo = m.split('-'); names=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']; return f"{names[int(mo)-1]} {y}"
                except Exception: return m
            # Chart
            try:
                from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
                from matplotlib.figure import Figure
                fig = Figure(figsize=(4,2.2)); ax = fig.add_subplot(111)
                labels=[fmt_month(r['month']) for r in cleaned]; balances=[r['balance'] for r in cleaned]
                ax.plot(labels, balances, marker='o', linewidth=2, color='#6366f1'); ax.fill_between(range(len(balances)), balances, color='#6366f1', alpha=0.08)
                ax.set_ylabel('Balance (IDR)')
                ax.set_xticklabels(labels, rotation=0, ha='center', fontsize=9)
                ax.grid(axis='y', linestyle='--', alpha=0.3)
                fig.tight_layout()
                canvas=FigureCanvas(fig); self.trend_info_layout.addWidget(canvas)
            except Exception as chart_err:
                err=QLabel(f"Chart error: {chart_err}"); err.setStyleSheet('color:#dc2626;'); self.trend_info_layout.addWidget(err)
            # Table
            html_rows=[]
            for r in cleaned[-6:]:
                idx = cleaned.index(r); prev_bal = cleaned[idx-1]['balance'] if idx>0 else 0; delta = r['balance']-prev_bal if idx>0 else 0
                html_rows.append(f"<tr><td style='padding:2px 8px'>{fmt_month(r['month'])}</td><td style='padding:2px 8px;text-align:right'>{r['income']:,.0f}</td><td style='padding:2px 8px;text-align:right'>{r['expense']:,.0f}</td><td style='padding:2px 8px;text-align:right'>{r['balance']:,.0f}</td><td style='padding:2px 8px;text-align:right'>{'+' if delta>0 else ''}{delta:,.0f}</td></tr>")
            table=QLabel("<div style='margin-top:8px'><b>Recent 6 Months</b><br><table style='border-collapse:collapse;font-size:11px;color:#374151'><tr style='background:#f1f5f9'><th style='padding:2px 8px;text-align:left'>Month</th><th style='padding:2px 8px'>Income</th><th style='padding:2px 8px'>Expense</th><th style='padding:2px 8px'>Balance</th><th style='padding:2px 8px'>Δ Bal</th></tr>" + "".join(html_rows) + "</table></div>")
            table.setTextFormat(Qt.RichText); self.trend_info_layout.addWidget(table)
            log_app_event("reports_trends_loaded", "ReportsPage", {"months": len(cleaned)})
        except Exception as e:
            log_app_event("reports_update_monthly_trends_error", "ReportsPage", {"error": str(e)})
