
# -*- coding: UTF-8 -*-
import json,time
import urllib, urllib2
import requests
import wave
from pyaudio import PyAudio,paInt16
import base64
import os
import Levenshtein as lst #文本相似度比较
import pygame



from audioDB import AudioDB


class Audio:
    """语音相关操作的类，基于百度语音"""
    preUrl = 'https://openapi.baidu.com/oauth/2.0/token'
    preTToAUrl = 'https://tsn.baidu.com/text2audio'
    preAToTUrl = 'https://vop.baidu.com/server_api'

    #设置wav的相关参数
    channels = 1    #通道数
    sampwidth = 2   #两个字节
    framerate = 8000    #码率
    NUM_SAMPLES = 2000  #采样点

    #录音时间控制器
    TIME = 20


    def __init__(self,appKey,appSecret):
        self.appKey = appKey
        self.appSecret = appSecret
        self.cuid = 'lukai'#不做数据统计，故写死


    #获取token
    def getToken(self):
        """拼接url，根据appKey和appSecret获取token

        grant_type：必须参数，固定为“client_credentials”；
        client_id：必须参数，应用的 API Key；
        client_secret：必须参数，应用的 Secret Key;
        """
        url = self.preUrl + '?' + 'grant_type=client_credentials' + '&' + 'client_id=' + self.appKey + '&' + 'client_secret='+ self.appSecret
        request = urllib2.Request(url)
        request.add_header('Content-Type', 'application/json; charset=UTF-8')
        response = urllib2.urlopen(request)
        #异常处理
        return json.loads(response.read())['access_token']


    #语音合成时，tex参数需要按照url参数标准使用url_encode UTF8编码
    def transToUrl(self,text):
        return urllib.quote(text)


    def transToText(self,text):
        return urllib.unquote(text)

    #将文字合成为语音
    def textToAudio(self,text,ctp='1',lan='zh',spd='5',pit='5',vol='5',per='0'):
        """此方法返回一个可以下载mp3的url

        tex	必填	合成的文本，使用UTF-8编码。小于512个中文字或者英文数字。（文本在百度服务器内转换为GBK后，长度必须小于1024字节）
        tok	必填	开放平台获取到的开发者access_token（见上面的“鉴权认证机制”段落）
        cuid必填	用户唯一标识，用来区分用户，计算UV值。建议填写能区分用户的机器 MAC 地址或 IMEI 码，长度为60字符以内
        ctp	必填	客户端类型选择，web端填写固定值1
        lan	必填	固定值zh。语言选择,目前只有中英文混合模式，填写固定值zh
        spd	选填	语速，取值0-9，默认为5中语速
        pit	选填	音调，取值0-9，默认为5中语调
        vol	选填	音量，取值0-15，默认为5中音量
        per	选填	发音人选择, 0为普通女声，1为普通男生，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女声
        """
        url = self.preTToAUrl + '?' +'tex=' + self.transToUrl(text) + '&tok=' + self.getToken() + '&lan=' + lan + '&cuid=' + self.cuid + '&ctp=' + ctp + '&spd=' + spd + '&pit=' + pit + '&vol=' + vol + '&per=' + per
        request = urllib2.Request(url)
        request.add_header('Content-Type', 'application/json; charset=UTF-8')
        response = urllib2.urlopen(request)

        return url

    #下载文件到工程目录下的questions目录下
    def downloadUrlFile(self,url,filename):
        print "downloading with requests"
        r = requests.get(url)
        filename = 'questions/' + filename
        with open(filename, "wb") as code:
            code.write(r.content)

    #生成wav文件
    def saveWaveFile(self,filename,data):
        wf = wave.open(filename,'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.sampwidth)
        wf.setframerate(self.framerate)
        wf.writeframes("".join(data))

        wf.close()

    #采集语音
    def record(self,filename):
        """

        :param filename:
        :return: 生成的wav文件名
        """
        pa = PyAudio()
        stream = pa.open(format = paInt16, channels = self.channels, rate = self.framerate,
                         input = True,frames_per_buffer = self.NUM_SAMPLES)
        #采集语音
        myBuff = []
        count = 0

        #目前不会写静音检测，故先写死录音时间
        while count < self.TIME :
            stringAudioData = stream.read(self.NUM_SAMPLES)
            myBuff.append(stringAudioData)
            count+=1
            print '采集音频中.'

        self.saveWaveFile(filename,myBuff)
        stream.close()

        return filename


    #语音识别
    def audioToText(self,filename):
        """
        format	必填	语音文件的格式，pcm 或者 wav 或者 amr。不区分大小写。推荐pcm文件
        rate	必填	采样率，16000，固定值
        channel	必填	声道数，仅支持单声道，请填写固定值 1
        cuid	必填	用户唯一标识，用来区分用户，计算UV值。建议填写能区分用户的机器 MAC 地址或 IMEI 码，长度为60字符以内。
        token	必填	开放平台获取到的开发者[access_token]获取 Access Token "access_token")
        dev_pid	选填	不填写lan参数生效，都不填写，默认1537（普通话 输入法模型），dev_pid参数见本节开头的表格
        lan	    选填，废弃参数	历史兼容参数，请使用dev_pid。如果dev_pid填写，该参数会被覆盖。语种选择,输入法模型，默认中文（zh）。 中文=zh、粤语=ct、英文=en，不区分大小写。
        url	    选填	可下载的语音下载地址，与callback连一起使用，确保百度服务器可以访问。
        callback	选填	用户服务器的识别结果回调地址，确保百度服务器可以访问
        speech	选填	本地语音文件的的二进制语音数据 ，需要进行base64 编码。与len参数连一起使用。
        len	    选填	本地语音文件的的字节数，单位字节
        :param filename:
        :return:
        """
        # 设置音频属性，根据百度的要求，采样率必须为8000，压缩格式支持pcm（不压缩）、wav、opus、speex、amr
        WAVE_TYPE = "wav"



        # 打开音频文件，并进行编码
        f = open(filename, "r")
        speech = base64.b64encode(f.read())
        size = os.path.getsize(filename)
        update = json.dumps(
            {"format": WAVE_TYPE, "rate": self.framerate, 'channel': 1, 'cuid': self.cuid, 'token': self.getToken(), 'speech': speech,
             'len': size})
        headers = {'Content-Type': 'application/json'}
        url = "http://vop.baidu.com/server_api"
        req = urllib2.Request(url, update, headers)

        r = urllib2.urlopen(req)

        t = r.read()
        result = json.loads(t)
        print result
        if result['err_msg'] == 'success.':
            word = result['result'][0].encode('utf-8')
            if word != '':
                if word[len(word) - 3:len(word)] == '，':
                    print word[0:len(word) - 3]
                else:
                    print word
            else:
                print "音频文件不存在或格式错误"
        else:
            print "错误"


        #关闭文件,并删除
        f.close()
        os.remove(filename)

        return word


    #播放音频
    def playAudio(self,filename):

        filename = 'questions/'+filename
        pygame.mixer.init()
        print("播放音乐"+filename)

        pygame.mixer.music.load(filename)
        #播放载入的音乐。该函数立即返回，音乐播放在后台进行。所以加sleep让音乐播放完毕后，再继续后续操作
        pygame.mixer.music.play()
        while True:
            #判断是否在播放音乐,返回1为正在播放
            a = pygame.mixer.music.get_busy()
            if a != 1:
                break




if __name__ == '__main__':
    appKey = 'U8yPrnfLly6Frz0Hc3TFvcyh'
    appSecret = 'qWl7mIbT6Pi5sgCcLkn3NWc8rzMTqSG3'

    row = 3
    #语音操作对西那个
    audio = Audio(appKey,appSecret)
    #问题对象
    question = AudioDB('db.csv')

    #获取问题
    qText = question.getValue(row,'question')
    print qText
    #获取问题编号
    qNo = question.getValue(row,'no')
    print qNo

    #生成录音文件
    url = audio.textToAudio(qText)
    filename = str(qNo)+'.mp3'
    audio.downloadUrlFile(url,filename)


    #播放问题语音
    audio.playAudio(filename)

    #采集音频，生成wav文件
    audio.record(str(qNo) + '.wav')

    #
    #生成录音识别后的文字
    tNo = audio.audioToText(str(qNo) + '.wav')
    #
    # #获取比对数据
    # stan = '三个日念什么'
    #
    # #计算相似度
    # print lst.ratio(stan,tNo)