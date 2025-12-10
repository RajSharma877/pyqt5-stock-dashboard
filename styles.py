LIGHT_STYLE = """
/* ======== GLOBAL STYLES ======== */
QWidget {
    background-color: #fafbfc;
    color: #1a202c;
    font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
    font-weight: 400;
    line-height: 1.5;
}

QMainWindow {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                stop: 0 #f7fafc, stop: 0.5 #edf2f7, stop: 1 #e2e8f0);
}

/* ======== SIDEBAR NAVIGATION ======== */
QWidget[objectName="sidebar"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #ffffff, stop: 1 #f8fafc);
    border-right: 2px solid #e2e8f0;
    border-radius: 0px;
    padding: 20px 10px;
    max-width: 200px;
    min-width: 180px;
}

QPushButton[objectName="nav_button"] {
    background: transparent;
    border: none;
    border-radius: 12px;
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
    font-size: 18px;
    color: #64748b;
    margin: 4px 0px;
    min-height: 20px;
}

QPushButton[objectName="nav_button"]:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #3b82f6, stop: 1 #1d4ed8);
    color: #ffffff;
    transform: translateX(4px);
}

QPushButton[objectName="nav_button"]:pressed {
    background: #1e40af;
    color: #ffffff;
}

/* ======== TOP BAR ======== */
QWidget[objectName="top_bar"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #ffffff, stop: 1 #f8fafc);
    border-radius: 16px;
    padding: 16px 24px;
    margin: 8px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

QLineEdit[objectName="ticker_input"] {
    background: #ffffff;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px 20px;
    font-size: 16px;
    font-weight: 500;
    color: #1a202c;
    min-height: 20px;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

QLineEdit[objectName="ticker_input"]:focus {
    border: 2px solid #3b82f6;
    background: #ffffff;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

QPushButton[objectName="search_button"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #3b82f6, stop: 1 #2563eb);
    border: none;
    border-radius: 12px;
    padding: 14px 32px;
    font-weight: 700;
    font-size: 14px;
    color: #ffffff;
    min-height: 20px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QPushButton[objectName="search_button"]:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #2563eb, stop: 1 #1d4ed8);
    transform: translateY(-2px);
}

QPushButton[objectName="search_button"]:pressed {
    background: #1e40af;
    transform: translateY(0px);
}

QPushButton[objectName="theme_button"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #f59e0b, stop: 1 #d97706);
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
    color: #ffffff;
    min-height: 16px;
}

QPushButton[objectName="theme_button"]:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #d97706, stop: 1 #b45309);
}

/* ======== CHART AREA ======== */
QFrame[objectName="chart_frame"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 24px;
    margin: 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* ======== CARDS & PANELS ======== */
QFrame {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 20px;
    margin: 6px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* ======== RIGHT PANEL ======== */
QWidget[objectName="right_panel"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #ffffff, stop: 1 #f8fafc);
    border-left: 2px solid #e2e8f0;
    padding: 16px;
    max-width: 350px;
    min-width: 320px;
}

/* ======== INDICATORS SECTION ======== */
QCheckBox {
    font-weight: 500;
    color: #374151;
    padding: 8px 12px;
    border-radius: 8px;
    margin: 3px 0px;
}

QCheckBox:hover {
    background-color: #f3f4f6;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #d1d5db;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                stop: 0 #10b981, stop: 1 #059669);
    border: 2px solid #059669;
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC42IDEuNEw0LjIgNy44TDEuNCA1IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4=);
}

QCheckBox::indicator:hover {
    border: 2px solid #6b7280;
}

/* ======== LABELS & HEADERS ======== */
QLabel {
    font-weight: 600;
    color: #1f2937;
    padding: 4px 0px;
}

QLabel[objectName="section_header"] {
    font-size: 16px;
    font-weight: 700;
    color: #111827;
    padding: 12px 0px 8px 0px;
    border-bottom: 2px solid #e5e7eb;
    margin-bottom: 12px;
}

QLabel[objectName="avg_price"] {
    font-size: 18px;
    font-weight: 700;
    color: #059669;
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(16, 185, 129, 0.1), stop: 1 rgba(5, 150, 105, 0.05));
    padding: 12px 16px;
    border-radius: 12px;
    border: 1px solid rgba(16, 185, 129, 0.2);
    margin: 8px;
}


/* ======== TEXT AREAS ======== */
QTextEdit {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 16px;
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 13px;
    color: #374151;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
    line-height: 1.6;
}

QTextEdit[objectName="fundamentals"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #fef3c7, stop: 1 #fde68a);
    border: 1px solid #f59e0b;
    color: #92400e;
    font-weight: 500;
}

QTextEdit[objectName="details"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #dbeafe, stop: 1 #bfdbfe);
    border: 1px solid #3b82f6;
    color: #1e40af;
    font-weight: 500;
}

/* ======== SCROLL AREAS ======== */
QScrollArea {
    border: none;
    background: transparent;
    border-radius: 12px;
}

QScrollBar:vertical {
    background: #f1f5f9;
    width: 8px;
    border-radius: 4px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ======== NEWS SECTION ======== */
QWidget[objectName="news_item"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #ffffff, stop: 1 #f8fafc);
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 16px;
    margin: 6px 0px;
}

 QTabWidget#reports_tabs::pane {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        background: white;
        padding: 10px;
    }
    
    QTabWidget#reports_tabs::tab-bar {
        alignment: center;
    }
    
    QTabWidget#reports_tabs QTabBar::tab {
        background: #f8fafc;
        color: #64748b;
        border: 1px solid #e2e8f0;
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 12px 24px;
        margin-right: 4px;
        font-weight: 600;
        font-size: 11px;
    }
    
    QTabWidget#reports_tabs QTabBar::tab:selected {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
        color: white;
        border: 1px solid #3b82f6;
    }
    
    QTabWidget#reports_tabs QTabBar::tab:hover {
        background: #f1f5f9;
        color: #334155;
    }
    
    QPushButton#generate_ai_btn {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8b5cf6, stop:1 #a855f7);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 12px;
        padding: 10px 20px;
    }
    
    QPushButton#generate_ai_btn:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c3aed, stop:1 #9333ea);
        transform: translateY(-1px);
    }
    
    QPushButton#generate_ai_btn:pressed {
        background: #6d28d9;
        transform: translateY(0px);
    }
    
    QPushButton#generate_ai_btn:disabled {
        background: #d1d5db;
        color: #9ca3af;
    }
    
    QLabel#ai_status_label {
        color: #64748b;
        font-size: 11px;
        font-style: italic;
        padding: 8px;
        background: rgba(59, 130, 246, 0.1);
        border-radius: 6px;
        border-left: 3px solid #3b82f6;
    }
    
    QTextEdit#ai_report_text {
        background: white;
        color: #1f2937;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
        font-size: 11px;
        line-height: 1.6;
    }
    
    QLabel#status_label {
        color: #64748b;
        font-size: 12px;
        padding: 10px;
        background: rgba(59, 130, 246, 0.05);
        border-radius: 8px;
        font-weight: 500;
    }
    
    QScrollArea#report_scroll {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        background: #f8fafc;
    }

QWidget[objectName="news_item"]:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #f0f9ff, stop: 1 #e0f2fe);
    border: 1px solid #3b82f6;
    transform: translateY(-2px);
}

/* ======== FINANCE COLORS ======== */
.profit { color: #059669; font-weight: 700; }
.loss { color: #dc2626; font-weight: 700; }
.neutral { color: #3b82f6; font-weight: 600; }
.volume { color: #7c3aed; font-weight: 600; }

/* ======== ANIMATIONS & EFFECTS ======== */
QPushButton, QCheckBox, QLineEdit, QFrame {
    transition: all 0.2s ease-in-out;
}
"""

DARK_STYLE = """
/* ======== GLOBAL STYLES ======== */
QWidget {
    background-color: #0f172a;
    color: #e2e8f0;
    font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
    font-weight: 400;
    line-height: 1.5;
}

QMainWindow {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                stop: 0 #020617, stop: 0.5 #0f172a, stop: 1 #1e293b);
}

/* ======== SIDEBAR NAVIGATION ======== */
QWidget[objectName="sidebar"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #1e293b, stop: 1 #334155);
    border-right: 2px solid #334155;
    border-radius: 0px;
    padding: 20px 10px;
    max-width: 200px;
    min-width: 180px;
}

QPushButton[objectName="nav_button"] {
    background: transparent;
    border: none;
    border-radius: 12px;
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
    font-size: 18px;
    color: #94a3b8;
    margin: 4px 0px;
    min-height: 20px;
}

QPushButton[objectName="nav_button"]:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #3b82f6, stop: 1 #1d4ed8);
    color: #ffffff;
    transform: translateX(4px);
}

QPushButton[objectName="nav_button"]:pressed {
    background: #1e40af;
    color: #ffffff;
}

/* ======== TOP BAR ======== */
QWidget[objectName="top_bar"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #1e293b, stop: 1 #0f172a);
    border-radius: 16px;
    padding: 16px 24px;
    margin: 8px;
    border: 1px solid #334155;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}

QLineEdit[objectName="ticker_input"] {
    background: #0f172a;
    border: 2px solid #334155;
    border-radius: 12px;
    padding: 14px 20px;
    font-size: 16px;
    font-weight: 500;
    color: #f1f5f9;
    min-height: 20px;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

QLineEdit[objectName="ticker_input"]:focus {
    border: 2px solid #3b82f6;
    background: #1e293b;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

QPushButton[objectName="search_button"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #3b82f6, stop: 1 #2563eb);
    border: none;
    border-radius: 12px;
    padding: 14px 32px;
    font-weight: 700;
    font-size: 14px;
    color: #ffffff;
    min-height: 20px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QPushButton[objectName="search_button"]:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #2563eb, stop: 1 #1d4ed8);
    transform: translateY(-2px);
}

QPushButton[objectName="search_button"]:pressed {
    background: #1e40af;
    transform: translateY(0px);
}

QPushButton[objectName="theme_button"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #f59e0b, stop: 1 #d97706);
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
    color: #ffffff;
    min-height: 16px;
}

QPushButton[objectName="theme_button"]:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #d97706, stop: 1 #b45309);
}

/* ======== CHART AREA ======== */
QFrame[objectName="chart_frame"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 20px;
    padding: 24px;
    margin: 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}

/* ======== CARDS & PANELS ======== */
QFrame {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 20px;
    margin: 6px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
}

/* ======== RIGHT PANEL ======== */
QWidget[objectName="right_panel"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #1e293b, stop: 1 #0f172a);
    border-left: 2px solid #334155;
    padding: 16px;
    max-width: 350px;
    min-width: 320px;
}

/* ======== INDICATORS SECTION ======== */
QCheckBox {
    font-weight: 500;
    color: #cbd5e1;
    padding: 8px 12px;
    border-radius: 8px;
    margin: 3px 0px;
}

QCheckBox:hover {
    background-color: #334155;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #475569;
    background-color: #0f172a;
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                stop: 0 #10b981, stop: 1 #059669);
    border: 2px solid #059669;
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC42IDEuNEw0LjIgNy44TDEuNCA1IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4=);
}

QCheckBox::indicator:hover {
    border: 2px solid #64748b;
}

  QTabWidget#reports_tabs::pane {
        border: 1px solid #334155;
        border-radius: 12px;
        background: #1e293b;
        padding: 10px;
    }
    
    QTabWidget#reports_tabs::tab-bar {
        alignment: center;
    }
    
    QTabWidget#reports_tabs QTabBar::tab {
        background: #334155;
        color: #94a3b8;
        border: 1px solid #475569;
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 12px 24px;
        margin-right: 4px;
        font-weight: 600;
        font-size: 11px;
    }
    
    QTabWidget#reports_tabs QTabBar::tab:selected {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
        color: white;
        border: 1px solid #3b82f6;
    }
    
    QTabWidget#reports_tabs QTabBar::tab:hover {
        background: #475569;
        color: #e2e8f0;
    }
    
    QPushButton#generate_ai_btn {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8b5cf6, stop:1 #a855f7);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 12px;
        padding: 10px 20px;
    }
    
    QPushButton#generate_ai_btn:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c3aed, stop:1 #9333ea);
        transform: translateY(-1px);
    }
    
    QPushButton#generate_ai_btn:pressed {
        background: #6d28d9;
        transform: translateY(0px);
    }
    
    QPushButton#generate_ai_btn:disabled {
        background: #4b5563;
        color: #9ca3af;
    }
    
    QLabel#ai_status_label {
        color: #94a3b8;
        font-size: 11px;
        font-style: italic;
        padding: 8px;
        background: rgba(59, 130, 246, 0.1);
        border-radius: 6px;
        border-left: 3px solid #3b82f6;
    }
    
    QTextEdit#ai_report_text {
        background: #1e293b;
        color: #e2e8f0;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
        font-size: 11px;
        line-height: 1.6;
    }
    
    QLabel#status_label {
        color: #94a3b8;
        font-size: 12px;
        padding: 10px;
        background: rgba(59, 130, 246, 0.1);
        border-radius: 8px;
        font-weight: 500;
    }
    
    QScrollArea#report_scroll {
        border: 1px solid #334155;
        border-radius: 12px;
        background: #0f172a;
    }

/* ======== LABELS & HEADERS ======== */
QLabel {
    font-weight: 600;
    color: #f1f5f9;
    padding: 4px 0px;
}

QLabel[objectName="section_header"] {
    font-size: 16px;
    font-weight: 700;
    color: #f8fafc;
    padding: 12px 0px 8px 0px;
    border-bottom: 2px solid #475569;
    margin-bottom: 12px;
}

QLabel[objectName="avg_price"] {
    font-size: 18px;
    font-weight: 700;
    color: #10b981;
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(16, 185, 129, 0.2), stop: 1 rgba(5, 150, 105, 0.1));
    padding: 12px 16px;
    border-radius: 12px;
    border: 1px solid rgba(16, 185, 129, 0.3);
    margin: 8px;
}



/* ======== TEXT AREAS ======== */
QTextEdit {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px;
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 13px;
    color: #cbd5e1;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
    line-height: 1.6;
}

QTextEdit[objectName="fundamentals"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 rgba(245, 158, 11, 0.2), stop: 1 rgba(217, 119, 6, 0.1));
    border: 1px solid #f59e0b;
    color: #fbbf24;
    font-weight: 500;
}

QTextEdit[objectName="details"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 rgba(59, 130, 246, 0.2), stop: 1 rgba(29, 78, 216, 0.1));
    border: 1px solid #3b82f6;
    color: #60a5fa;
    font-weight: 500;
}

/* ======== SCROLL AREAS ======== */
QScrollArea {
    border: none;
    background: transparent;
    border-radius: 12px;
}

QScrollBar:vertical {
    background: #1e293b;
    width: 8px;
    border-radius: 4px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #475569;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #64748b;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ======== NEWS SECTION ======== */
QWidget[objectName="news_item"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #1e293b, stop: 1 #0f172a);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px;
    margin: 6px 0px;
}

QWidget[objectName="news_item"]:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 rgba(59, 130, 246, 0.1), stop: 1 rgba(29, 78, 216, 0.05));
    border: 1px solid #3b82f6;
    transform: translateY(-2px);
}

/* ======== FINANCE COLORS ======== */
.profit { color: #22c55e; font-weight: 700; }
.loss { color: #ef4444; font-weight: 700; }
.neutral { color: #60a5fa; font-weight: 600; }
.volume { color: #a78bfa; font-weight: 600; }

/* ======== ANIMATIONS & EFFECTS ======== */
QPushButton, QCheckBox, QLineEdit, QFrame {
    transition: all 0.2s ease-in-out;
}
"""


def get_theme(is_dark):
    return DARK_STYLE if is_dark else LIGHT_STYLE
