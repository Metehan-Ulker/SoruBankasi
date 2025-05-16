import sqlite3
import openpyxl
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QHBoxLayout, QRadioButton, QComboBox, QMessageBox

def veritabani_olustur():
    conn = sqlite3.connect("soru_bankasi.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Sorular (
        id INTEGER PRIMARY KEY,
        soru TEXT NOT NULL,
        sik1 TEXT NOT NULL,
        sik2 TEXT NOT NULL,
        sik3 TEXT NOT NULL,
        sik4 TEXT NOT NULL,
        dogru_cevap INTEGER NOT NULL
    )""")

    conn.commit()
    conn.close()


def sorulari_excel_aktar():
    conn = sqlite3.connect("soru_bankasi.db")
    cursor = conn.cursor()
    cursor.execute("SELECT soru, sik1, sik2, sik3, sik4, dogru_cevap FROM Sorular")
    sorular = cursor.fetchall()
    conn.close()

    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sorular"
    ws.append(["Soru", "Şık A", "Şık B", "Şık C", "Şık D", "Doğru Cevap"])

    
    for soru in sorular:
        soru_metni, sik1, sik2, sik3, sik4, dogru_cevap = soru
        ws.append([soru_metni, sik1, sik2, sik3, sik4, chr(65 + dogru_cevap)])  

    wb.save("soru_bankasi_sorular.xlsx")
    print("Sorular Excel dosyasına aktarıldı!")

class AnaPencere(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soru Bankası")
        self.setGeometry(600, 300, 700, 500)
        self.setStyleSheet("background-color: #f0f0f0;")  
        
        self.soru_ekle_btn = QPushButton("Soru Ekle", self)
        self.soru_sec_btn = QPushButton("Soruları Görüntüle", self)
        self.excel_aktar_btn = QPushButton("Excel'e Aktar", self)

        self.soru_ekle_btn.clicked.connect(self.soru_ekle)
        self.soru_sec_btn.clicked.connect(self.soru_sec)
        self.excel_aktar_btn.clicked.connect(sorulari_excel_aktar)


        self.soru_ekle_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.soru_sec_btn.setStyleSheet("background-color: #008CBA; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.excel_aktar_btn.setStyleSheet("background-color: #f44336; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")

    
        layout = QVBoxLayout()
        layout.addWidget(self.soru_ekle_btn)
        layout.addWidget(self.soru_sec_btn)
        layout.addWidget(self.excel_aktar_btn)

        self.setLayout(layout)

    def soru_ekle(self):
        self.pencere = SoruEklemePenceresi()
        self.pencere.show()

    def soru_sec(self):
        self.pencere = SoruSecmePenceresi()
        self.pencere.show()

class SoruEklemePenceresi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soru Ekle")
        self.setGeometry(600, 300, 700, 500)
        self.setStyleSheet("background-color: #f9f9f9;")  
        self.initUI()

    def initUI(self):
        self.soru_label = QLabel("Soru:")
        self.soru_girisi = QLineEdit()

        self.sik_labels = []
        self.sik_girisi = []
        self.sik_secimi = []
        for i in range(4):
            label = QLabel(f"Şık {i+1}:")
            entry = QLineEdit()
            radio = QRadioButton("Doğru Cevap")
            self.sik_labels.append(label)
            self.sik_girisi.append(entry)
            self.sik_secimi.append(radio)

        self.kaydet_btn = QPushButton("Soruyu Kaydet")
        self.kaydet_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.kaydet_btn.clicked.connect(self.soru_kaydet)

        layout = QVBoxLayout()
        layout.addWidget(self.soru_label)
        layout.addWidget(self.soru_girisi)

        for i in range(4):
            h_layout = QHBoxLayout()
            h_layout.addWidget(self.sik_labels[i])
            h_layout.addWidget(self.sik_girisi[i])
            h_layout.addWidget(self.sik_secimi[i])
            layout.addLayout(h_layout)

        layout.addWidget(self.kaydet_btn)
        self.setLayout(layout)

    def soru_kaydet(self):
        soru = self.soru_girisi.text()
        siklar = [entry.text() for entry in self.sik_girisi]
        dogru_cevap_index = next((i for i, radio in enumerate(self.sik_secimi) if radio.isChecked()), None)

        if soru and all(siklar) and dogru_cevap_index is not None:
            conn = sqlite3.connect("soru_bankasi.db")
            cursor = conn.cursor()

            cursor.execute("INSERT INTO Sorular (soru, sik1, sik2, sik3, sik4, dogru_cevap) VALUES (?, ?, ?, ?, ?, ?)",
                           (soru, siklar[0], siklar[1], siklar[2], siklar[3], dogru_cevap_index))

            conn.commit()
            conn.close()

            self.soru_girisi.clear()
            for entry in self.sik_girisi:
                entry.clear()
            for radio in self.sik_secimi:
                radio.setChecked(False)

            QMessageBox.information(self, "Başarılı", "Soru başarıyla eklendi!", QMessageBox.Ok)

        else:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun ve doğru cevabı seçin.", QMessageBox.Ok)

class SoruSecmePenceresi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soruları Görüntüle")
        self.setGeometry(600, 300, 700, 500)
        self.initUI()

    def initUI(self):
        self.soru_label = QLabel("Seçilen Soru:", self)
        self.soru_goster = QLabel("", self)
        self.soru_listesi = QComboBox(self)
        self.soru_sec_btn = QPushButton("Soruyu Yazdır", self)

        self.soru_sec_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.soru_sec_btn.clicked.connect(self.soru_sec)
        self.soru_yukle()

        layout = QVBoxLayout()
        layout.addWidget(self.soru_label)
        layout.addWidget(self.soru_listesi)
        layout.addWidget(self.soru_sec_btn)
        layout.addWidget(self.soru_goster)

        self.setLayout(layout)

    def soru_yukle(self):
        conn = sqlite3.connect("soru_bankasi.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, soru FROM Sorular")
        sorular = cursor.fetchall()
        conn.close()

        for id, soru in sorular:
            self.soru_listesi.addItem(soru, id)

    def soru_sec(self):
        soru_id = self.soru_listesi.currentData()
        conn = sqlite3.connect("soru_bankasi.db")
        cursor = conn.cursor()
        cursor.execute("SELECT soru, sik1, sik2, sik3, sik4 FROM Sorular WHERE id = ?", (soru_id,))
        soru_bilgisi = cursor.fetchone()
        conn.close()

        if soru_bilgisi:
            soru, sik1, sik2, sik3, sik4 = soru_bilgisi
            self.soru_goster.setText(f"{soru}\nA) {sik1}\nB) {sik2}\nC) {sik3}\nD) {sik4}")

if __name__ == "__main__":
    veritabani_olustur()
    app = QApplication([])
    pencere = AnaPencere()
    pencere.show()
    app.exec_()
