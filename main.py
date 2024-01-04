import os
import shutil
import cv2
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from qt_material import apply_stylesheet
import sys


# 主窗口
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口参数
        self.resize(1920, 1200)

        label1 = QLabel("prompt num: ", self)
        label1.setGeometry(20, 50, 250, 50)
        self.promptNum = QTextEdit("3", self)
        self.promptNum.setGeometry(200, 50, 80, 50)

        label2 = QLabel("gear num: ", self)
        label2.setGeometry(420, 50, 250, 50)
        self.gearNum = QTextEdit("8", self)
        self.gearNum.setGeometry(600, 50, 80, 50)

        self.promptInput = []
        for i in range(5):
            promptInputTemp = []
            for y in range(3):
                for x in range(3):
                    checkBoxTemp = QCheckBox(self)
                    checkBoxTemp.setGeometry(20 + i * 200 + x * 50, 200 + y * 50, 50, 50)
                    checkBoxTemp.setStyleSheet("QCheckBox::indicator { width: 50px; height: 50px;}")
                    promptInputTemp.append(checkBoxTemp)
            self.promptInput.append(promptInputTemp)

        self.chessInput = []
        for y in range(7):
            for x in range(6):
                checkBoxTemp = QCheckBox(self)
                checkBoxTemp.setGeometry(200 + x * 50, 400 + y * 50, 50, 50)
                checkBoxTemp.setStyleSheet("QCheckBox::indicator { width: 50px; height: 50px;}")
                checkBoxTemp.setTristate(True)
                checkBoxTemp.setChecked(True)
                self.chessInput.append(checkBoxTemp)

        self.startBtn = QPushButton("Start", self)
        self.startBtn.setStyleSheet("QPushButton {font-size:30px}")
        self.startBtn.setGeometry(220, 850, 250, 100)
        self.startBtn.clicked.connect(
            lambda: self.StartBtnClick(
                self.promptNum.toPlainText(),
                self.gearNum.toPlainText(),
                self.promptInput,
                self.chessInput,
            )
        )

        self.resetBtn = QPushButton("Reset", self)
        self.resetBtn.setStyleSheet("QPushButton {font-size:30px}")
        self.resetBtn.setGeometry(600, 850, 250, 100)
        self.resetBtn.clicked.connect(self.ResetBtnClick)

        self.calNum = QLabel("result count: ", self)
        self.calNum.setGeometry(1300, 50, 250, 50)
        self.imageShow = QLabel(None, self)
        self.imageShow.setFixedSize(600, 700)
        self.imageShow.move(1200, 150)
        self.imageShow.setPixmap(QPixmap(600, 700))
        self.imageShow.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.showMaximized()

    def PromptInputTransform(self, input: list):
        """将提示输入转换为3*3的矩阵

        Args:
            input (list): 输入的列表

        Returns:
            np.array: 3*3的矩阵
        """
        output = np.zeros((3, 3))
        for y in range(3):
            for x in range(3):
                if input[y * 3 + x].isChecked():
                    output[y, x] = 1
        return output

    def ChessInputTransform(self, input: list):
        """将棋盘输入转换为7*6的矩阵

        Args:
            input (list): 输入的列表

        Returns:
            np.array: 7*6的矩阵
        """

        output = np.zeros((7, 6))
        for y in range(7):
            for x in range(6):
                if input[y * 6 + x].checkState() == Qt.CheckState.Checked:
                    output[y, x] = 1
                elif input[y * 6 + x].checkState() == Qt.CheckState.PartiallyChecked:
                    output[y, x] = 2
        return output

    def FillPrompt(self, waitting: np.array, prompt: list, chess: np.array):
        """将提示填充入棋盘

        Args:
            waitting (np.array): 待填充的样式
            prompt (list): 提示
            chess (np.array): 棋盘

        Returns:
            np.array: 填充结果
        """
        chessResult = chess.copy()
        for y in range(5):
            for x in range(4):
                num = int(waitting[y, x])
                if num == 0:
                    continue
                for py in range(3):
                    for px in range(3):
                        if prompt[num - 1][py, px] == 1:
                            if chessResult[y + py, x + px] == 0:
                                return chess
                            else:
                                chessResult[y + py, x + px] = 5
        # 检查填充结果是否符合提示
        for y in range(5):
            for x in range(4):
                num = int(waitting[y, x])
                if num == 0:
                    continue
                for py in range(3):
                    for px in range(3):
                        if prompt[num - 1][py, px] == 1 and chessResult[y + py, x + px] != 5:
                            return chess
                        if prompt[num - 1][py, px] == 0 and chessResult[y + py, x + px] == 5:
                            return chess
        return chessResult

    def ShowChess(self, chess: np.array, sumArray: np.array, saveNum: int, isSaved: bool):
        """显示棋盘

        Args:
            chess (np.array): 棋盘
            sumArray (np.array): 统计结果
            saveNum (int): 存储的序号
            isSaved (bool): 是否存储
        """
        showImage = np.zeros((700, 600, 3), np.uint8)

        for y in range(7):
            for x in range(6):
                if chess[y, x] == 5:
                    cv2.rectangle(
                        showImage, (100 * x, 100 * y), (100 * x + 100, 100 * y + 100), (0, 0, 255), -1
                    )
                elif chess[y, x] == 1:
                    cv2.rectangle(
                        showImage, (100 * x, 100 * y), (100 * x + 100, 100 * y + 100), (255, 255, 255), -1
                    )
                else:
                    cv2.rectangle(
                        showImage, (100 * x, 100 * y), (100 * x + 100, 100 * y + 100), (100, 100, 100), -1
                    )
                sumValue = int(sumArray[y, x])
                if sumValue != 0:
                    cv2.putText(
                        showImage,
                        str(sumValue),
                        (100 * x + 30, 100 * y + 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 0, 0),
                        2,
                    )
        for y in range(7):
            cv2.line(showImage, (0, 100 * y), (600, 100 * y), (255, 0, 0), 2)
        for x in range(6):
            cv2.line(showImage, (100 * x, 0), (100 * x, 700), (255, 0, 0), 2)

        if isSaved:
            cv2.imwrite("result/" + str(saveNum) + ".jpg", showImage)
        else:
            sortArray = np.sort(np.unique(np.ravel(sumArray)))
            sortArray = sortArray[::-1]
            for num, maxValue in enumerate(sortArray):
                if num >= 3 or maxValue == 0:
                    break
                maxIndexs = np.argwhere(sumArray == maxValue)
                match num:
                    case 0:
                        color = (0, 255, 0)
                    case 1:
                        color = (200, 255, 0)
                    case 2:
                        color = (0, 220, 220)

                for maxIndex in maxIndexs:
                    y, x = maxIndex
                    cv2.rectangle(
                        showImage,
                        (100 * x, 100 * y),
                        (100 * x + 100, 100 * y + 100),
                        color,
                        5,
                    )

            imgTmp = QImage(
                showImage.data,
                showImage.shape[1],
                showImage.shape[0],
                showImage.shape[1] * 3,
                QImage.Format.Format_BGR888,
            )
            self.imageShow.setPixmap(QPixmap.fromImage(imgTmp))
            QApplication.processEvents()

    def StartBtnClick(self, prompt_num: str, gear_num: str, prompt_input: list, chess_input: list):
        self.startBtn.setText("running...")
        QApplication.processEvents()

        # 转换界面上的输入
        promptNum = int(prompt_num)
        gearNum = int(gear_num)
        promptInput = []
        for i in range(promptNum):
            promptInput.append(self.PromptInputTransform(prompt_input[i]))

        chessInput = self.ChessInputTransform(chess_input)

        # 穷举提示排列的方式
        waittingArray = []
        for a in range(20):
            if promptNum < 2:
                arrayTemp = np.zeros((5, 4))
                y, x = divmod(a, 4)
                arrayTemp[y, x] = 1
                waittingArray.append(arrayTemp.copy())
                continue
            for b in range(20):
                if b == a:
                    continue
                if promptNum < 3:
                    arrayTemp = np.zeros((5, 4))
                    y, x = divmod(a, 4)
                    arrayTemp[y, x] = 1
                    y, x = divmod(b, 4)
                    arrayTemp[y, x] = 2
                    waittingArray.append(arrayTemp.copy())
                    continue
                for c in range(20):
                    if c == a or c == b:
                        continue
                    if promptNum < 4:
                        arrayTemp = np.zeros((5, 4))
                        y, x = divmod(a, 4)
                        arrayTemp[y, x] = 1
                        y, x = divmod(b, 4)
                        arrayTemp[y, x] = 2
                        y, x = divmod(c, 4)
                        arrayTemp[y, x] = 3
                        waittingArray.append(arrayTemp.copy())
                        continue
                    for d in range(20):
                        if d == a or d == b or d == c:
                            continue
                        if promptNum < 5:
                            arrayTemp = np.zeros((5, 4))
                            y, x = divmod(a, 4)
                            arrayTemp[y, x] = 1
                            y, x = divmod(b, 4)
                            arrayTemp[y, x] = 2
                            y, x = divmod(c, 4)
                            arrayTemp[y, x] = 3
                            y, x = divmod(d, 4)
                            arrayTemp[y, x] = 4
                            waittingArray.append(arrayTemp.copy())
                            continue
                        for e in range(20):
                            if e == a or e == b or e == c or e == d:
                                continue
                            arrayTemp = np.zeros((5, 4))
                            y, x = divmod(a, 4)
                            arrayTemp[y, x] = 1
                            y, x = divmod(b, 4)
                            arrayTemp[y, x] = 2
                            y, x = divmod(c, 4)
                            arrayTemp[y, x] = 3
                            y, x = divmod(d, 4)
                            arrayTemp[y, x] = 4
                            y, x = divmod(e, 4)
                            arrayTemp[y, x] = 5
                            waittingArray.append(arrayTemp.copy())

        result = []
        if os.path.exists("./result"):
            shutil.rmtree("./result")
        os.mkdir("./result")
        # if os.path.exists("./txt"):
        #     shutil.rmtree("./txt")
        # os.mkdir("./txt")
        for waittingNum in range(len(waittingArray)):
            # np.savetxt("txt/" + str(waittingNum) + ".txt", waittingArray[waittingNum])
            fillResult = self.FillPrompt(waittingArray[waittingNum], promptInput, chessInput)
            # 剔除与输入不相符的排列
            count = np.bincount(fillResult.astype(int).flatten())
            if len(count) < 6 or count[5] != gearNum or count[2] > 0:
                continue
            self.ShowChess(fillResult, np.zeros((7, 6)), waittingNum, True)
            result.append(fillResult)
        # 统计所有结果中，每一个位置的出现次数
        resultSum = np.zeros((7, 6))
        resultClean = []
        for resultNum in range(len(result)):
            resultTemp = np.where(result[resultNum] == 1, 0, result[resultNum])
            resultTemp = resultTemp / 5
            resultSum = resultSum + resultTemp
            resultClean.append(resultTemp)
        # 计算出现概率最大的方式
        resultMul = np.zeros(len(resultClean))
        for resultNum in range(len(resultClean)):
            resultTemp = np.multiply(resultClean[resultNum], resultSum)
            sumValue = np.sum(resultTemp)
            resultMul[resultNum] = sumValue
        self.calNum.setText("result count: " + str(len(result)))
        if len(result) == 0:
            self.imageShow.setPixmap(QPixmap(600, 700))
            return
        maxIndex = int(np.argmax(resultMul))
        self.ShowChess(result[maxIndex], resultSum, 0, False)
        self.startBtn.setText("Start")
        QApplication.processEvents()

    def ResetBtnClick(self):
        self.promptNum.setText("3")
        self.gearNum.setText("8")

        for inputTemp in self.promptInput:
            for checkBoxTemp in inputTemp:
                checkBoxTemp.setChecked(False)

        for checkBoxTemp in self.chessInput:
            checkBoxTemp.setChecked(False)
            checkBoxTemp.setChecked(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    apply_stylesheet(app, theme="dark_cyan.xml")
    window.setStyleSheet(
        """
        QLabel {font-size:20px}
        QPushButton {font-size:20px}
        QRadioButton {font-size:20px}
        QTextEdit {font-size:20px;color:rgb(255,255,255)}
        QComboBox {font-size:20px;color:rgb(255,255,255)}
        """
    )
    sys.exit(app.exec())
