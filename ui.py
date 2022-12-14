import json
import os
import random
import re
import webbrowser

import requests
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import dialog
import ini_operation as ini


class Ui_MainWindow(object):
    def set_token(self):
        if self.token.toPlainText() == "":
            self.show_dialog = dialog.ShowInfoDialog("Token不能为空!")
            self.show_dialog.show_dialog()
            return
        ini.setToken(self.token.toPlainText())
        self.show_dialog = dialog.ShowInfoDialog("设置成功! 请重启软件!")
        self.show_dialog.show_dialog()

    def randomTunnelName(self):
        self.chars = []
        for i in range(65, 91):
            self.chars.append(chr(i))
        for i in range(97, 123):
            self.chars.append(chr(i))
        self.gen_tunnel_name_list = []
        for i in range(10):
            self.gen_tunnel_name_list.append(random.choice(self.chars))
        self.gen_tunnel_name = ""
        for i in range(10):
            self.gen_tunnel_name = self.gen_tunnel_name + self.gen_tunnel_name_list[i]
        return self.gen_tunnel_name

    def clear_cache(self):
        try:
            self.allIniFile = os.listdir("temp")
        except FileNotFoundError:
            self.show_dialog = dialog.ShowInfoDialog("无缓存配置可清理!")
            self.show_dialog.show_dialog()
            return
        os.chdir("temp")
        for i in range(len(self.allIniFile)):
            os.remove(self.allIniFile[i])
        os.chdir("..")
        os.rmdir("temp")
        self.show_dialog = dialog.ShowInfoDialog("清理成功!")
        self.show_dialog.show_dialog()

    def getPersonalInfo(self):
        if not os.path.exists("config.ini"):
            self.show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
            self.show_dialog.show_dialog()
            # 特殊需求return false
            return False
        self.headers = {
            'authorization': f'Bearer {ini.readToken()}',
        }
        self.response = requests.get("https://api.laecloud.com/api/users", headers=self.headers)
        self.response.encoding = self.response.apparent_encoding
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog(
                f"向后端接口发送请求时发生错误:\n\n{self.response.status_code}: {self.tunnels}")
            self.show_dialog.show_dialog()
            return
        try:
            self.personal_info = json.loads(self.response.text)
        except json.decoder.JSONDecodeError:
            self.show_dialog = dialog.ShowInfoDialog(
                f"对后端接口返回JSON数据解码时发生错误:\n\n{self.response.status_code}: {self.response.text}")
            self.show_dialog.show_dialog()
            return
        self.return_data = []
        self.return_data.append(self.personal_info["name"])
        self.return_data.append(str(self.personal_info["id"]))
        self.return_data.append(str(self.personal_info["balance"]))
        self.return_data.append(self.personal_info["email"])
        return self.return_data

    def listOfTunnel(self):
        if not os.path.exists("config.ini"):
            self.show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
            self.show_dialog.show_dialog()
            return
        self.headers = {
            'authorization': f'Bearer {ini.readToken()}',
        }

        self.response = requests.get('https://api.laecloud.com/api/modules/frp/hosts', headers=self.headers)
        self.response.encoding = self.response.apparent_encoding
        try:
            self.tunnels = json.loads(self.response.text)
        except json.decoder.JSONDecodeError:
            self.show_dialog = dialog.ShowInfoDialog(
                f"对后端接口返回JSON数据解码时发生错误:\n\n{self.response.status_code}: {self.response.text}")
            self.show_dialog.show_dialog()
            return
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog(
                f"向后端接口发送请求时发生错误:\n\n{self.response.status_code}: {self.tunnels}")
            self.show_dialog.show_dialog()
            return
        self.chooseTunnel.clear()
        for i in range(len(self.tunnels)):
            self.chooseTunnel.addItem(self.tunnels[i]["name"])

    def start_tunnel(self):
        if not os.path.exists("config.ini"):
            self.show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
            self.show_dialog.show_dialog()
            return
        if self.chooseTunnel.currentText() == "":
            self.show_dialog = dialog.ShowInfoDialog("您尚未选择隧道!")
            self.show_dialog.show_dialog()
            return
        if not os.path.exists("frpc.exe"):
            self.show_dialog = dialog.ShowInfoDialog("frpc.exe文件缺失, 请重新下载启动器!")
            self.show_dialog.show_dialog()
            return
        self.headers = {
            'authorization': f'Bearer {ini.readToken()}',
        }

        self.response = requests.get('https://api.laecloud.com/api/modules/frp/hosts', headers=self.headers)
        self.response.encoding = self.response.apparent_encoding
        try:
            self.tunnels = json.loads(self.response.text)
        except json.decoder.JSONDecodeError:
            self.show_dialog = dialog.ShowInfoDialog(
                f"对后端接口返回JSON数据解码时发生错误:\n\n{self.response.status_code}: {self.response.text}")
            self.show_dialog.show_dialog()
            return
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog(
                f"向后端接口发送请求时发生错误:\n\n{self.response.status_code}: {self.tunnels}")
            self.show_dialog.show_dialog()
            return
        self.regular = re.compile(r'.*?"id":(\d+),"name":"{}".*?'.format(self.chooseTunnel.currentText()))
        self.tunnelId = re.findall(self.regular, self.response.text)[0]
        self.headers_more = {
            'authorization': f'Bearer {ini.readToken()}',
        }
        self.response = requests.get(f'https://api.laecloud.com/api/modules/frp/hosts/{self.tunnelId}',
                                     headers=self.headers_more)
        self.response.encoding = self.response.apparent_encoding
        try:
            self.more_info_json = json.loads(self.response.text)
        except json.decoder.JSONDecodeError:
            self.show_dialog = dialog.ShowInfoDialog(
                f"对后端接口返回JSON数据解码时发生错误:\n\n{self.response.status_code}: {self.response.text}")
            self.show_dialog.show_dialog()
            return
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog(
                f"向后端接口发送请求时发生错误:\n\n{self.response.status_code}: {self.more_info_json}")
            self.show_dialog.show_dialog()
            return
        self.ini_config = self.more_info_json["config"]["server"] + "\n\n" + \
                          self.more_info_json["config"]["client"]
        try:
            with open(f"temp/{self.more_info_json['name']}.ini", 'w', encoding="utf-8") as f:
                f.write(self.ini_config)
        except FileNotFoundError:
            os.mkdir("temp")
            with open(f"temp/{self.more_info_json['name']}.ini", 'w', encoding="utf-8") as f:
                f.write(self.ini_config)
        self.baseLog = r"""   __  __ ___   ___         
  /  \/  / __/ / __/ _ ___ 
 / /\// / _/  / _/ '_/ '_\
/_/  /_/___/ /_//_/ / .__/
                   /_/   
                   
ME Frp 服务即将启动
弹出框出现 start proxy success 即为隧道启动成功，否则隧道尚未启动。


"""
        self.outputLog.setText(self.baseLog)
        self.stopTunnelBtn.setDisabled(False)
        os.system(f"start run.bat {self.more_info_json['name']}")

    def stop_tunnel(self):
        self.stopTunnelBtn.setDisabled(True)
        os.system("taskkill /f /IM frpc.exe")
        self.outputLog.clear()

    def openTokenWebsite(self):
        webbrowser.open("https://api.laecloud.com/")

    def openStatusWebsite(self):
        webbrowser.open("https://dash.laecloud.com/servers")

    def openGitHub(self):
        webbrowser.open("https://github.com/kingc2022/mefrp-gui")

    def updateCreateTunnelPage(self):
        if self.protocol.currentText() == "HTTP":
            self.chooseServer.clear()
            for i in range(len(self.servers)):
                if self.servers[i]["allow_http"] == 1 and self.servers[i]["status"] == "up":
                    self.chooseServer.addItem(self.servers[i]["name"])
        elif self.protocol.currentText() == "HTTPS":
            self.chooseServer.clear()
            for i in range(len(self.servers)):
                if self.servers[i]["allow_https"] == 1 and self.servers[i]["status"] == "up":
                    self.chooseServer.addItem(self.servers[i]["name"])
        elif self.protocol.currentText() == "TCP":
            self.chooseServer.clear()
            for i in range(len(self.servers)):
                if self.servers[i]["allow_tcp"] == 1 and self.servers[i]["status"] == "up":
                    self.chooseServer.addItem(self.servers[i]["name"])
        elif self.protocol.currentText() == "UDP":
            self.chooseServer.clear()
            for i in range(len(self.servers)):
                if self.servers[i]["allow_udp"] == 1 and self.servers[i]["status"] == "up":
                    self.chooseServer.addItem(self.servers[i]["name"])
        self.label_12.setText(re.sub("[A-Z]+", self.protocol.currentText(), self.label_12.text()))
        if self.protocol.currentText() == "HTTP" or self.protocol.currentText() == "HTTPS":
            self.specialArgument.setPlaceholderText("绑定域名")
        else:
            self.specialArgument.setPlaceholderText("远程端口")

    def create_tunnel(self):
        if not os.path.exists("config.ini"):
            self.show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
            self.show_dialog.show_dialog()
            return
        self.headers = {
            'authorization': f'Bearer {ini.readToken()}',
        }
        if self.protocol.currentText() == "TCP" or self.protocol.currentText() == "UDP":
            self.json_data = {
                'name': self.tunnelName.text(),
                'protocol': 'tcp',
                'local_address': self.localIP.text(),
                'remote_port': self.specialArgument.text(),
                'custom_domain': None,
                'create_https': False,
                'create_cdn': False,
            }
            if self.protocol.currentText() == "UDP":
                self.json_data["protocol"] = "udp"
            for i in range(0, len(self.servers)):
                if self.servers[i]["name"] == self.chooseServer.currentText():
                    self.json_data["server_id"] = self.servers[i]["id"]
            self.response = requests.post('https://api.laecloud.com/api/modules/frp/hosts', headers=self.headers, json=self.json_data)
            self.response.encoding = self.response.apparent_encoding
            try:
                self.create_tunnel_json = json.loads(self.response.text)
            except json.decoder.JSONDecodeError:
                self.show_dialog = dialog.ShowInfoDialog(
                    f"对后端接口返回JSON数据解码时发生错误:\n\n{self.response.status_code}: {self.response.text}")
                self.show_dialog.show_dialog()
                return
            if self.response.status_code != 200:
                self.show_dialog = dialog.ShowInfoDialog(
                    f"向后端接口发送请求时发生错误:\n\n{self.response.status_code}: {self.create_tunnel_json}")
                self.show_dialog.show_dialog()
                return
            else:
                self.show_dialog = dialog.ShowInfoDialog("创建成功！")
                self.show_dialog.show_dialog()
                return
        else:
            self.json_data = {
                'name': self.tunnelName.text(),
                'protocol': 'http',
                'local_address': self.localIP.text(),
                'remote_port': None,
                'custom_domain': self.specialArgument.text(),
                'create_https': False,
                'create_cdn': False,
            }
            if self.protocol.currentText() == "HTTPS":
                self.json_data["protocol"] = "https"
            for i in range(0, len(self.servers)):
                if self.servers[i]["name"] == self.chooseServer.currentText():
                    self.json_data["server_id"] = self.servers[i]["id"]
            self.response = requests.post('https://api.laecloud.com/api/modules/frp/hosts', headers=self.headers,
                                          json=self.json_data)
            self.response.encoding = self.response.apparent_encoding
            try:
                self.create_tunnel_json = json.loads(self.response.text)
            except json.decoder.JSONDecodeError:
                self.show_dialog = dialog.ShowInfoDialog(
                    f"对后端接口返回JSON数据解码时发生错误:\n\n{self.response.status_code}: {self.response.text}")
                self.show_dialog.show_dialog()
                return
            if self.response.status_code != 200:
                self.show_dialog = dialog.ShowInfoDialog(
                    f"向后端接口发送请求时发生错误:\n\n{self.response.status_code}: {self.create_tunnel_json}")
                self.show_dialog.show_dialog()
                return
            else:
                self.show_dialog = dialog.ShowInfoDialog("创建成功！")
                self.show_dialog.show_dialog()
                return

    def emptyWorkingSets(self):
        if not os.path.exists("config.ini"):
            self.show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
            self.show_dialog.show_dialog()
            return
        if not os.path.exists("RAMMap.exe"):
            self.show_dialog = dialog.ShowInfoDialog("RAMMap.exe文件缺失, 请重新下载启动器!")
            self.show_dialog.show_dialog()
            return
        os.system("RAMMap.exe -Ew")
        self.show_dialog = dialog.ShowInfoDialog("清理内存完毕!")
        self.show_dialog.show_dialog()

    def emptySystemWorkingSets(self):
        if not os.path.exists("config.ini"):
            self.show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
            self.show_dialog.show_dialog()
            return
        if not os.path.exists("RAMMap.exe"):
            self.show_dialog = dialog.ShowInfoDialog("RAMMap.exe文件缺失, 请重新下载启动器!")
            self.show_dialog.show_dialog()
            return
        os.system("RAMMap.exe -Es")
        self.show_dialog = dialog.ShowInfoDialog("清理内存完毕!")
        self.show_dialog.show_dialog()

    def emptyModifiedPageList(self):
        if not os.path.exists("config.ini"):
            self.show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
            self.show_dialog.show_dialog()
            return
        if not os.path.exists("RAMMap.exe"):
            self.show_dialog = dialog.ShowInfoDialog("RAMMap.exe文件缺失, 请重新下载启动器!")
            self.show_dialog.show_dialog()
            return
        os.system("RAMMap.exe -Em")
        self.show_dialog = dialog.ShowInfoDialog("清理内存完毕!")
        self.show_dialog.show_dialog()

    def emptyStandbyList(self):
        if not os.path.exists("config.ini"):
            self.show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
            self.show_dialog.show_dialog()
            return
        if not os.path.exists("RAMMap.exe"):
            self.show_dialog = dialog.ShowInfoDialog("RAMMap.exe文件缺失, 请重新下载启动器!")
            self.show_dialog.show_dialog()
            return
        os.system("RAMMap.exe -Et")
        self.show_dialog = dialog.ShowInfoDialog("清理内存完毕!")
        self.show_dialog.show_dialog()

    def emptyPriority0StandByList(self):
        if not os.path.exists("config.ini"):
            self.show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
            self.show_dialog.show_dialog()
            return
        if not os.path.exists("RAMMap.exe"):
            self.show_dialog = dialog.ShowInfoDialog("RAMMap.exe文件缺失, 请重新下载启动器!")
            self.show_dialog.show_dialog()
            return
        os.system("RAMMap.exe -E0")
        self.show_dialog = dialog.ShowInfoDialog("清理内存完毕!")
        self.show_dialog.show_dialog()

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(620, 440)
        MainWindow.setWindowTitle(u"Mirror Edge Frp \u5ba2\u6237\u7aef - V1.7 Released")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(10, 10, 601, 421))
        font = QFont()
        font.setFamily(u"\u5b8b\u4f53")
        self.tabWidget.setFont(font)
        self.tokenSettings = QWidget()
        self.tokenSettings.setObjectName(u"tokenSettings")
        self.setTokenBtn = QPushButton(self.tokenSettings)
        self.setTokenBtn.setObjectName(u"setTokenBtn")
        self.setTokenBtn.setGeometry(QRect(150, 250, 281, 31))
        self.setTokenBtn.setFont(font)
        self.setTokenBtn.setText(u"\u8bbe\u7f6eToken")
        self.token = QTextEdit(self.tokenSettings)
        self.token.setObjectName(u"token")
        self.token.setGeometry(QRect(150, 120, 281, 121))
        self.token.setFont(font)
        self.token.setPlaceholderText(
            u"\u7b2c\u4e00\u6b21\u4f7f\u7528\u8bf7\u5230api.laecloud.com, \u70b9\u51fb\"\u83b7\u53d6\u65b0\u7684Token\"\u6309\u94ae, \u5c06Token\u590d\u5236\u5230\u8fd9\u91cc, \u7136\u540e\u70b9\u51fb\"\u8bbe\u7f6eToken\"\u6309\u94ae")
        self.label = QLabel(self.tokenSettings)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(150, 50, 291, 21))
        font1 = QFont()
        font1.setFamily(u"\u5b8b\u4f53")
        font1.setPointSize(12)
        self.label.setFont(font1)
        self.label.setText(u"Token (\u53ea\u6709\u914d\u7f6e\u5b8cToken\u624d\u80fd\u6b63\u5e38\u4f7f\u7528)")
        self.openWebsite = QPushButton(self.tokenSettings)
        self.openWebsite.setObjectName(u"openWebsite")
        self.openWebsite.setGeometry(QRect(204, 80, 151, 23))
        self.openWebsite.setFont(font)
        self.openWebsite.setCursor(QCursor(Qt.PointingHandCursor))
        self.openWebsite.setFocusPolicy(Qt.NoFocus)
        self.openWebsite.setStyleSheet(u"")
        self.openWebsite.setText(u"\u6253\u5f00api.laecloud.com")
        self.tabWidget.addTab(self.tokenSettings, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tokenSettings), u"Token\u8bbe\u7f6e")
        self.personalInfo = QWidget()
        self.personalInfo.setObjectName(u"personalInfo")
        self.infoTable = QTableWidget(self.personalInfo)
        if (self.infoTable.columnCount() < 2):
            self.infoTable.setColumnCount(2)
        if (self.infoTable.rowCount() < 5):
            self.infoTable.setRowCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setText(u"\u540d\u79f0");
        __qtablewidgetitem.setTextAlignment(Qt.AlignCenter);
        self.infoTable.setItem(0, 0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setText(u"\u503c");
        __qtablewidgetitem1.setTextAlignment(Qt.AlignCenter);
        self.infoTable.setItem(0, 1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setText(u"\u7528\u6237\u540d");
        __qtablewidgetitem2.setTextAlignment(Qt.AlignCenter);
        self.infoTable.setItem(1, 0, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setTextAlignment(Qt.AlignCenter);
        self.infoTable.setItem(1, 1, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setText(u"\u7528\u6237ID");
        __qtablewidgetitem4.setTextAlignment(Qt.AlignCenter);
        self.infoTable.setItem(2, 0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setTextAlignment(Qt.AlignCenter);
        self.infoTable.setItem(2, 1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setText(u"\u4f59\u989d");
        __qtablewidgetitem6.setTextAlignment(Qt.AlignCenter);
        self.infoTable.setItem(3, 0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        __qtablewidgetitem7.setTextAlignment(Qt.AlignCenter);
        self.infoTable.setItem(3, 1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        __qtablewidgetitem8.setText(u"\u90ae\u7bb1");
        __qtablewidgetitem8.setTextAlignment(Qt.AlignCenter);
        self.infoTable.setItem(4, 0, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        __qtablewidgetitem9.setTextAlignment(Qt.AlignCenter);
        self.infoTable.setItem(4, 1, __qtablewidgetitem9)
        self.infoTable.setObjectName(u"infoTable")
        self.infoTable.setGeometry(QRect(10, 10, 571, 371))
        self.infoTable.setFont(font)
        self.infoTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.infoTable.setRowCount(5)
        self.infoTable.setColumnCount(2)
        self.infoTable.horizontalHeader().setVisible(False)
        self.infoTable.horizontalHeader().setDefaultSectionSize(290)
        self.infoTable.verticalHeader().setVisible(False)
        self.infoTable.verticalHeader().setDefaultSectionSize(40)
        self.tabWidget.addTab(self.personalInfo, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.personalInfo), u"\u4e2a\u4eba\u4fe1\u606f")
        self.startTunnel = QWidget()
        self.startTunnel.setObjectName(u"startTunnel")
        self.chooseTunnel = QComboBox(self.startTunnel)
        self.chooseTunnel.setObjectName(u"chooseTunnel")
        self.chooseTunnel.setGeometry(QRect(100, 20, 291, 22))
        font2 = QFont()
        font2.setFamily(u"\u5fae\u8f6f\u96c5\u9ed1")
        self.chooseTunnel.setFont(font2)
        self.chooseTunnel.setCurrentText(u"")
        self.chooseTunnel.setPlaceholderText(u"--\u8bf7\u9009\u62e9--")
        self.startTunnelBtn = QPushButton(self.startTunnel)
        self.startTunnelBtn.setObjectName(u"startTunnelBtn")
        self.startTunnelBtn.setGeometry(QRect(10, 90, 91, 31))
        self.startTunnelBtn.setFont(font2)
        self.startTunnelBtn.setText(u"\u542f\u52a8\u96a7\u9053")
        self.stopTunnelBtn = QPushButton(self.startTunnel)
        self.stopTunnelBtn.setObjectName(u"stopTunnelBtn")
        self.stopTunnelBtn.setGeometry(QRect(110, 90, 111, 31))
        self.stopTunnelBtn.setFont(font2)
        self.stopTunnelBtn.setText(u"\u505c\u6b62\u6240\u6709\u96a7\u9053")
        self.label_2 = QLabel(self.startTunnel)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 20, 81, 21))
        self.label_2.setFont(font2)
        self.label_2.setText(u"\u9009\u62e9\u96a7\u9053")
        self.outputLog = QTextEdit(self.startTunnel)
        self.outputLog.setObjectName(u"outputLog")
        self.outputLog.setGeometry(QRect(10, 170, 571, 211))
        self.outputLog.setFont(font2)
        self.outputLog.setFocusPolicy(Qt.NoFocus)
        self.outputLog.setReadOnly(True)
        self.label_3 = QLabel(self.startTunnel)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 140, 41, 21))
        self.label_3.setFont(font2)
        self.label_3.setText(u"\u65e5\u5fd7")
        self.label_8 = QLabel(self.startTunnel)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(10, 60, 61, 21))
        self.label_8.setFont(font2)
        self.label_8.setText(u"\u64cd\u4f5c\u533a")
        self.refreshTunnelBtn = QPushButton(self.startTunnel)
        self.refreshTunnelBtn.setObjectName(u"refreshTunnelBtn")
        self.refreshTunnelBtn.setGeometry(QRect(490, 90, 91, 31))
        self.refreshTunnelBtn.setFont(font2)
        self.refreshTunnelBtn.setText(u"\u5237\u65b0\u96a7\u9053")
        self.clearCacheBtn = QPushButton(self.startTunnel)
        self.clearCacheBtn.setObjectName(u"clearCacheBtn")
        self.clearCacheBtn.setGeometry(QRect(370, 90, 111, 31))
        self.clearCacheBtn.setFont(font2)
        self.clearCacheBtn.setText(u"\u6e05\u9664\u914d\u7f6e\u6587\u4ef6\u7f13\u5b58")
        self.tabWidget.addTab(self.startTunnel, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.startTunnel), u"\u542f\u52a8\u96a7\u9053")
        self.createTunnel = QWidget()
        self.createTunnel.setObjectName(u"createTunnel")
        self.label_9 = QLabel(self.createTunnel)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(20, 80, 71, 31))
        self.label_9.setFont(font2)
        self.label_9.setText(u"\u96a7\u9053\u540d\u79f0")
        self.tunnelName = QLineEdit(self.createTunnel)
        self.tunnelName.setObjectName(u"tunnelName")
        self.tunnelName.setGeometry(QRect(20, 110, 201, 21))
        self.tunnelName.setFont(font2)
        self.label_10 = QLabel(self.createTunnel)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(20, 150, 91, 31))
        self.label_10.setFont(font2)
        self.label_10.setText(u"\u672c\u5730\u5730\u5740\u548c\u7aef\u53e3")
        self.localIP = QLineEdit(self.createTunnel)
        self.localIP.setObjectName(u"localIP")
        self.localIP.setGeometry(QRect(20, 180, 201, 21))
        self.localIP.setFont(font2)
        self.localIP.setText(u"127.0.0.1:80")
        self.label_11 = QLabel(self.createTunnel)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(20, 220, 51, 31))
        self.label_11.setFont(font2)
        self.label_11.setText(u"\u534f\u8bae")
        self.protocol = QComboBox(self.createTunnel)
        self.protocol.addItem(u"HTTP")
        self.protocol.addItem(u"HTTPS")
        self.protocol.addItem(u"TCP")
        self.protocol.addItem(u"UDP")
        self.protocol.setObjectName(u"protocol")
        self.protocol.setGeometry(QRect(20, 250, 121, 22))
        self.protocol.setFont(font2)
        self.openStatusPage = QPushButton(self.createTunnel)
        self.openStatusPage.setObjectName(u"openStatusPage")
        self.openStatusPage.setGeometry(QRect(20, 30, 201, 31))
        self.openStatusPage.setFont(font2)
        self.openStatusPage.setCursor(QCursor(Qt.PointingHandCursor))
        self.openStatusPage.setText(u"\u6253\u5f00\u670d\u52a1\u5668\u72b6\u6001\u9875\u9762")
        self.label_12 = QLabel(self.createTunnel)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(280, 80, 171, 31))
        self.label_12.setFont(font2)
        self.label_12.setText(u"\u9009\u62e9\u652f\u6301HTTP\u534f\u8bae\u7684\u8282\u70b9")
        self.protocolBtn = QPushButton(self.createTunnel)
        self.protocolBtn.setObjectName(u"protocolBtn")
        self.protocolBtn.setGeometry(QRect(150, 250, 71, 23))
        self.protocolBtn.setFont(font2)
        self.protocolBtn.setText(u"\u786e\u5b9a")
        self.chooseServer = QComboBox(self.createTunnel)
        self.chooseServer.setObjectName(u"chooseServer")
        self.chooseServer.setGeometry(QRect(280, 110, 221, 22))
        self.chooseServer.setFont(font2)
        self.label_13 = QLabel(self.createTunnel)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(280, 150, 61, 31))
        self.label_13.setFont(font2)
        self.label_13.setText(u"\u7279\u6b8a\u53c2\u6570")
        self.specialArgument = QLineEdit(self.createTunnel)
        self.specialArgument.setObjectName(u"specialArgument")
        self.specialArgument.setGeometry(QRect(280, 180, 221, 21))
        self.specialArgument.setFont(font2)
        self.specialArgument.setPlaceholderText(u"\u7ed1\u5b9a\u57df\u540d")
        self.createTunnelBtn = QPushButton(self.createTunnel)
        self.createTunnelBtn.setObjectName(u"createTunnelBtn")
        self.createTunnelBtn.setGeometry(QRect(280, 240, 221, 31))
        self.createTunnelBtn.setFont(font2)
        self.createTunnelBtn.setText(u"\u786e\u5b9a")
        self.tabWidget.addTab(self.createTunnel, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.createTunnel), u"\u65b0\u5efa\u96a7\u9053")
        self.cleanMemory = QWidget()
        self.cleanMemory.setObjectName(u"cleanMemory")
        self.label_4 = QLabel(self.cleanMemory)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 20, 581, 31))
        font3 = QFont()
        font3.setFamily(u"\u5fae\u8f6f\u96c5\u9ed1")
        font3.setPointSize(16)
        font3.setBold(True)
        font3.setWeight(75)
        self.label_4.setFont(font3)
        self.label_4.setStyleSheet(u"color: rgb(220, 53, 69)")
        self.label_4.setText(
            u"\u6e05\u7406\u5185\u5b58\u6709\u65f6\u53ef\u80fd\u5e26\u6765\u4e0d\u53ef\u9006\u7684\u540e\u679c\uff01")
        self.label_4.setAlignment(Qt.AlignCenter)
        self.label_5 = QLabel(self.cleanMemory)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 60, 581, 31))
        self.label_5.setFont(font3)
        self.label_5.setStyleSheet(u"color: rgb(220, 53, 69)")
        self.label_5.setText(
            u"\u82e5\u9700\u8981\u6e05\u7406\u5185\u5b58\uff0c\u8bf7\u4e00\u6b21\u4e00\u6b21\u70b9\u51fb\u4e0b\u5217\u6309\u94ae\uff01\u5207\u52ff\u5fc3\u6025\uff01")
        self.label_5.setAlignment(Qt.AlignCenter)
        self.workingSetsBtn = QPushButton(self.cleanMemory)
        self.workingSetsBtn.setObjectName(u"workingSetsBtn")
        self.workingSetsBtn.setGeometry(QRect(80, 130, 201, 31))
        self.workingSetsBtn.setText(u"Empty Working Sets")
        self.systemWorkingSetsBtn = QPushButton(self.cleanMemory)
        self.systemWorkingSetsBtn.setObjectName(u"systemWorkingSetsBtn")
        self.systemWorkingSetsBtn.setGeometry(QRect(290, 130, 201, 31))
        self.systemWorkingSetsBtn.setText(u"Empty System Working Sets")
        self.modifiedPageListBtn = QPushButton(self.cleanMemory)
        self.modifiedPageListBtn.setObjectName(u"modifiedPageListBtn")
        self.modifiedPageListBtn.setGeometry(QRect(80, 180, 411, 31))
        self.modifiedPageListBtn.setText(
            u"Empty Modified Page List\uff08\u6b64\u9009\u9879\u4f1a\u5361\u4f4f1-2\u5206\u949f\uff09")
        self.standbyListBtn = QPushButton(self.cleanMemory)
        self.standbyListBtn.setObjectName(u"standbyListBtn")
        self.standbyListBtn.setGeometry(QRect(80, 230, 201, 31))
        self.standbyListBtn.setText(u"Empty Standby List")
        self.priority0StandbyBtn = QPushButton(self.cleanMemory)
        self.priority0StandbyBtn.setObjectName(u"priority0StandbyBtn")
        self.priority0StandbyBtn.setGeometry(QRect(290, 230, 201, 31))
        self.priority0StandbyBtn.setText(u"Empty Priority 0 standby List")
        self.tabWidget.addTab(self.cleanMemory, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.cleanMemory), u"\u6e05\u7406\u5185\u5b58")
        self.about = QWidget()
        self.about.setObjectName(u"about")
        self.label_15 = QLabel(self.about)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setGeometry(QRect(0, 40, 601, 221))
        font4 = QFont()
        font4.setFamily(u"Courier")
        font4.setPointSize(16)
        self.label_15.setFont(font4)
        self.label_15.setText(u"Copyright \u00a9 kingc, All rights reserved.\n"
                              "\n"
                              "Copyright \u00a9 ME Frp 2022.\n"
                              "\n"
                              "Aehxy \u7b56\u5212 / \u8fd0\u8425\n"
                              "\n"
                              "\u83b1\u4e91 \u6240\u6709")
        self.label_15.setAlignment(Qt.AlignCenter)
        self.gotoGitHub = QPushButton(self.about)
        self.gotoGitHub.setObjectName(u"gotoGitHub")
        self.gotoGitHub.setGeometry(QRect(184, 292, 231, 41))
        self.gotoGitHub.setFont(font1)
        self.gotoGitHub.setCursor(QCursor(Qt.PointingHandCursor))
        self.gotoGitHub.setText(u"\u524d\u5f80\u672c\u9879\u76ee\u7684GitHub\u4ed3\u5e93")
        self.tabWidget.addTab(self.about, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.about), u"\u5173\u4e8e")
        MainWindow.setCentralWidget(self.centralwidget)

        self.tabWidget.setCurrentIndex(0)

        # StyleSheet部分
        self.openWebsite.setStyleSheet("""
        border: none;
        color: #0d6efd;
        text-decoration: underline;
        """)
        self.openStatusPage.setStyleSheet("""
        border: none;
        color: #0d6efd;
        text-decoration: underline;
        """)
        self.gotoGitHub.setStyleSheet("""
        border: none;
        color: #0d6efd;
        text-decoration: underline;
        """)

        QMetaObject.connectSlotsByName(MainWindow)
        # 自定义代码部分 / 逻辑代码部分

        # 初始化自定义ini模块
        ini.init()
        # 获取用户所有隧道
        self.listOfTunnel()
        # 按钮点击事件绑定
        self.setTokenBtn.clicked.connect(self.set_token)
        self.startTunnelBtn.clicked.connect(self.start_tunnel)
        self.stopTunnelBtn.clicked.connect(self.stop_tunnel)
        self.openWebsite.clicked.connect(self.openTokenWebsite)
        self.refreshTunnelBtn.clicked.connect(self.listOfTunnel)
        self.openStatusPage.clicked.connect(self.openStatusWebsite)
        self.protocolBtn.clicked.connect(self.updateCreateTunnelPage)
        self.createTunnelBtn.clicked.connect(self.create_tunnel)
        self.clearCacheBtn.clicked.connect(self.clear_cache)
        self.workingSetsBtn.clicked.connect(self.emptyWorkingSets)
        self.systemWorkingSetsBtn.clicked.connect(self.emptySystemWorkingSets)
        self.modifiedPageListBtn.clicked.connect(self.emptyModifiedPageList)
        self.standbyListBtn.clicked.connect(self.emptyStandbyList)
        self.priority0StandbyBtn.clicked.connect(self.emptyPriority0StandByList)
        self.gotoGitHub.clicked.connect(self.openGitHub)
        # 设置禁用停止所有隧道按钮
        self.stopTunnelBtn.setDisabled(True)
        # 设置新建隧道 隧道名称
        self.tunnelName.setText(self.randomTunnelName())
        # 获取用户信息并填入表中
        self.info = self.getPersonalInfo()
        if self.info:
            __qtablewidgetitem = QTableWidgetItem()
            __qtablewidgetitem.setText(self.info[0])
            __qtablewidgetitem.setTextAlignment(Qt.AlignCenter)
            self.infoTable.setItem(1, 1, __qtablewidgetitem)
            __qtablewidgetitem2 = QTableWidgetItem()
            __qtablewidgetitem2.setText(self.info[1])
            __qtablewidgetitem2.setTextAlignment(Qt.AlignCenter)
            self.infoTable.setItem(2, 1, __qtablewidgetitem2)
            __qtablewidgetitem3 = QTableWidgetItem()
            __qtablewidgetitem3.setText(self.info[2])
            __qtablewidgetitem3.setTextAlignment(Qt.AlignCenter)
            self.infoTable.setItem(3, 1, __qtablewidgetitem3)
            __qtablewidgetitem4 = QTableWidgetItem()
            __qtablewidgetitem4.setText(self.info[3])
            __qtablewidgetitem4.setTextAlignment(Qt.AlignCenter)
            self.infoTable.setItem(4, 1, __qtablewidgetitem4)
        # 获取服务器列表 供新建隧道板块使用
        if not os.path.exists("config.ini"):
            self.show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
            self.show_dialog.show_dialog()
            return
        self.headers = {
            'authorization': f'Bearer {ini.readToken()}',
        }
        self.response = requests.get('https://api.laecloud.com/api/modules/frp/servers', headers=self.headers)
        self.response.encoding = self.response.apparent_encoding
        try:
            self.servers = json.loads(self.response.text)
        except json.decoder.JSONDecodeError:
            self.show_dialog = dialog.ShowInfoDialog(
                f"对后端接口返回JSON数据解码时发生错误:\n\n{self.response.status_code}: {self.response.text}")
            self.show_dialog.show_dialog()
            return
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog(
                f"向后端接口发送请求时发生错误:\n\n{self.response.status_code}: {self.servers}")
            self.show_dialog.show_dialog()
            return
        # 如果有config.ini文件直接切换到隧道板块
        if os.path.exists("config.ini"):
            self.tabWidget.setCurrentIndex(2)
