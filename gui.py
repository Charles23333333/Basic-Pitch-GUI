import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QCheckBox, QPushButton,
    QFileDialog, QMessageBox, QProgressBar, QGroupBox, QFormLayout, QDoubleSpinBox, QComboBox, QLabel
)
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QIcon
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH

class Converter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("icon.ico"))
        layout = QVBoxLayout()
        self.settings = QSettings(os.path.join(os.getcwd(), "settings.ini"), QSettings.Format.IniFormat)

        self.lang_box = QComboBox()
        self.lang_box.addItems(["English", "中文"])
        saved_lang = self.settings.value("language", "English")
        if saved_lang in ["English", "中文"]:
            self.lang_box.setCurrentText(saved_lang)
        self.lang_box.currentTextChanged.connect(self.update_language)
        layout.addWidget(self.lang_box)

        self.sonify_cb = QCheckBox()
        self.save_midi_cb = QCheckBox()
        self.save_notes_cb = QCheckBox()
        self.save_outputs_cb = QCheckBox()
        self.overwrite_cb = QCheckBox()
        layout.addWidget(self.sonify_cb)
        layout.addWidget(self.save_midi_cb)
        layout.addWidget(self.save_notes_cb)
        layout.addWidget(self.save_outputs_cb)
        layout.addWidget(self.overwrite_cb)

        self.sonify_cb.setChecked(self.settings.value("sonify", False, type=bool))
        self.save_midi_cb.setChecked(self.settings.value("save_midi", True, type=bool))
        self.save_notes_cb.setChecked(self.settings.value("save_notes", False, type=bool))
        self.save_outputs_cb.setChecked(self.settings.value("save_outputs", False, type=bool))
        self.overwrite_cb.setChecked(self.settings.value("overwrite", False, type=bool))

        self.adv_group = QGroupBox()
        self.adv_layout = QFormLayout()
        self.onset_threshold = QDoubleSpinBox()
        self.frame_threshold = QDoubleSpinBox()
        self.min_note_length = QDoubleSpinBox()
        self.min_freq = QDoubleSpinBox()
        self.max_freq = QDoubleSpinBox()
        self.onset_label = QLabel()
        self.frame_label = QLabel()
        self.min_note_label = QLabel()
        self.min_freq_label = QLabel()
        self.max_freq_label = QLabel()
        self.onset_threshold.setRange(0.0, 1.0)
        self.onset_threshold.setSingleStep(0.05)
        self.onset_threshold.setValue(self.settings.value("onset_threshold", 0.5, type=float))
        self.frame_threshold.setRange(0.0, 1.0)
        self.frame_threshold.setSingleStep(0.05)
        self.frame_threshold.setValue(self.settings.value("frame_threshold", 0.3, type=float))
        self.min_note_length.setRange(0.0, 1000.0)
        self.min_note_length.setSingleStep(10.0)
        self.min_note_length.setValue(self.settings.value("min_note_length", 127.7, type=float))
        self.min_freq.setRange(20.0, 20000.0)
        self.min_freq.setSingleStep(10.0)
        self.min_freq.setValue(self.settings.value("min_freq", 50.0, type=float))
        self.max_freq.setRange(20.0, 20000.0)
        self.max_freq.setSingleStep(10.0)
        self.max_freq.setValue(self.settings.value("max_freq", 5000.0, type=float))
        self.adv_layout.addRow(self.onset_label, self.onset_threshold)
        self.adv_layout.addRow(self.frame_label, self.frame_threshold)
        self.adv_layout.addRow(self.min_note_label, self.min_note_length)
        self.adv_layout.addRow(self.min_freq_label, self.min_freq)
        self.adv_layout.addRow(self.max_freq_label, self.max_freq)
        self.adv_group.setLayout(self.adv_layout)
        layout.addWidget(self.adv_group)

        self.button = QPushButton()
        self.button.clicked.connect(self.run_conversion)
        layout.addWidget(self.button)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress)

        self.setLayout(layout)
        self.update_language(self.lang_box.currentText())

    def update_language(self, lang):
        if lang == "中文":
            self.setWindowTitle("Basic Pitch 图形界面转换器")
            self.sonify_cb.setText("生成音频预览 (sonify_midi)")
            self.save_midi_cb.setText("保存 MIDI 文件 (save_midi)")
            self.save_notes_cb.setText("保存音符 JSON (save_notes)")
            self.save_outputs_cb.setText("保存模型输出 (save_model_outputs)")
            self.overwrite_cb.setText("覆盖已有文件")
            self.button.setText("选择文件并转换")
            self.adv_group.setTitle("高级参数")
            self.onset_label.setText("起始阈值")
            self.frame_label.setText("帧阈值")
            self.min_note_label.setText("最小音符长度 (毫秒)")
            self.min_freq_label.setText("最小频率 (Hz)")
            self.max_freq_label.setText("最大频率 (Hz)")
        else:
            self.setWindowTitle("Basic Pitch GUI Converter")
            self.sonify_cb.setText("Generate audio preview (sonify_midi)")
            self.save_midi_cb.setText("Save MIDI file (save_midi)")
            self.save_notes_cb.setText("Save notes JSON (save_notes)")
            self.save_outputs_cb.setText("Save model outputs (save_model_outputs)")
            self.overwrite_cb.setText("Overwrite existing files")
            self.button.setText("Select files and convert")
            self.adv_group.setTitle("Advanced")
            self.onset_label.setText("Onset threshold")
            self.frame_label.setText("Frame threshold")
            self.min_note_label.setText("Minimum note length (ms)")
            self.min_freq_label.setText("Minimum frequency (Hz)")
            self.max_freq_label.setText("Maximum frequency (Hz)")

    def run_conversion(self):
        audio_files, _ = QFileDialog.getOpenFileNames(
            self,
            "Choose input audio file",
            "",
            "Audio files (*.wav *.mp3 *.ogg *.flac *.m4a)"
        )

        if not audio_files:
            return
        output_dir = QFileDialog.getExistingDirectory(self, "Choose output directory")
        if not output_dir:
            return
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        try:
            self.progress.setValue(10)
            self.progress.setFormat("Loading model...")
            self.progress.repaint()
            self.progress.setValue(40)
            self.progress.setFormat("Processing audio...")
            self.progress.repaint()
            if self.overwrite_cb.isChecked():
                for f in audio_files:
                    stem = Path(f).stem
                    if self.save_midi_cb.isChecked():
                        (output_path / f"{stem}_basic_pitch.mid").unlink(missing_ok=True)
                    if self.save_outputs_cb.isChecked():
                        (output_path / f"{stem}_basic_pitch.npz").unlink(missing_ok=True)
                    if self.sonify_cb.isChecked():
                        (output_path / f"{stem}_basic_pitch.wav").unlink(missing_ok=True)
                    if self.save_notes_cb.isChecked():
                        (output_path / f"{stem}_basic_pitch.csv").unlink(missing_ok=True)
            predict_and_save(
                [Path(f) for f in audio_files],
                output_path,
                sonify_midi=self.sonify_cb.isChecked(),
                model_or_model_path=ICASSP_2022_MODEL_PATH,
                save_midi=self.save_midi_cb.isChecked(),
                save_model_outputs=self.save_outputs_cb.isChecked(),
                save_notes=self.save_notes_cb.isChecked(),
                onset_threshold=self.onset_threshold.value(),
                frame_threshold=self.frame_threshold.value(),
                minimum_note_length=self.min_note_length.value(),
                minimum_frequency=self.min_freq.value(),
                maximum_frequency=self.max_freq.value()
            )
            self.progress.setValue(80)
            self.progress.setFormat("Saving results...")
            self.progress.repaint()
            self.progress.setValue(100)
            self.progress.setFormat("Done")
            QMessageBox.information(self, "Success", f"MIDI saved to {output_path}")
        except Exception as e:
            self.progress.setValue(0)
            self.progress.setFormat("Error")
            QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        self.settings.setValue("language", self.lang_box.currentText())
        self.settings.setValue("sonify", self.sonify_cb.isChecked())
        self.settings.setValue("save_midi", self.save_midi_cb.isChecked())
        self.settings.setValue("save_notes", self.save_notes_cb.isChecked())
        self.settings.setValue("save_outputs", self.save_outputs_cb.isChecked())
        self.settings.setValue("overwrite", self.overwrite_cb.isChecked())
        self.settings.setValue("onset_threshold", self.onset_threshold.value())
        self.settings.setValue("frame_threshold", self.frame_threshold.value())
        self.settings.setValue("min_note_length", self.min_note_length.value())
        self.settings.setValue("min_freq", self.min_freq.value())
        self.settings.setValue("max_freq", self.max_freq.value())
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Converter()
    window.show()
    sys.exit(app.exec())
