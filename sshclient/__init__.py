from mcdreforged.api.all import *
from typing import Optional
import paramiko

ssh_client = None

class SSHClient:
    def __init__(self):
        self.client = None

    # 连接到远程服务器
    def connect(self, src: CommandSource, hostname, username, password, port):
        if self.client is not None and self.client.get_transport() is not None:
            src.reply("[SSH]已经连接到了SSH服务器")
        else: 
            try:
                # debug
                src.reply(f"[SSH]使用端口：{port}")
                if port == 22:
                    src.reply(f"[SSH]正在连接到 {hostname}...")
                else:
                    src.reply(f"[SSH]正在连接到 {hostname}:{port}...")
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.client.connect(hostname, port=port, username=username, password=password, timeout=5)
                src.reply("[SSH]成功连接到SSH服务器")
                src.reply("[SSH]SSH会话为全局共享，所有人都可以使用，且同时只能运行一个ssh会话")
                src.reply("[SSH]若要连接到新的ssh会话，请先断开连接")
            except Exception as e:
                src.reply(f"[SSH/错误]连接失败: {e}")

    # 执行命令
    def execute(self, command, src: CommandSource):
        if self.client is None or self.client.get_transport() is None:
            src.reply("[SSH]请先使用!!ssh connect <地址> <用户名> <密码> <可选：端口>进行连接")
            src.reply("[SSH]使用!!ssh help查看帮助")
        else:
            try:
                src.reply("[SSH]正在执行命令（返回结果不带“[SSH]“前缀）")
                stdin, stdout, stderr = self.client.exec_command(command)
                output = stdout.read().decode().strip()
                error = stderr.read().decode().strip()
                if output:
                    src.reply(output)
                if error:
                    src.reply(error)
            except Exception as e:
                src.reply(f"[SSH/错误]执行命令失败: {e}")

    # 断开连接
    def disconnect(self, src: Optional[CommandSource] = None):
        if self.client is None or self.client.get_transport() is None:
            if src is not None:
                src.reply("[SSH/错误]尚未连接到任何SSH服务器")

        else:
            if self.client.get_transport().is_active():
                if src is not None:
                    src.reply("[SSH/警告]若有命令正在运行，强制断开会中断它们")
            self.client.close()
            self.client = None
            if src is not None:
                src.reply("[SSH]已断开SSH连接")

def on_load(server: PluginServerInterface, old_module):
    global ssh_client
    ssh_client = SSHClient()    
    server.register_command(
        Literal("!!ssh")
        .runs(lambda src: src.reply("[SSH]使用!!ssh help查看帮助"))
        .then(Literal("connect")
              .then(Text("hostname")
                    .then(Text("username")
                        .then(Text("password")
                            .then(Integer("port").suggests(lambda: ["22"])
                            .runs(lambda src, ctx: ssh_client.connect(src, ctx["hostname"], ctx["username"], ctx["password"], ctx["port"])))
                            .runs(lambda src, ctx: ssh_client.connect(src, ctx["hostname"], ctx["username"], ctx["password"], ctx.get("port", 22)))))))
        .then(Literal("disconnect")
              .runs(lambda src: ssh_client.disconnect(src)))
        .then(Literal("help")
            .runs(lambda src: help(src)))
        .then(QuotableText("command")
              .runs(lambda src, ctx: ssh_client.execute(ctx["command"], src)))
    )

    server.logger.info("SSH客户端插件加载完成")

def help(src: CommandSource):
    src.reply("[SSH]使用!!ssh connect <地址> <用户名> <密码> <端口>进行连接")
    src.reply("[SSH]使用!!ssh disconnect断开连接，包括失败的连接")
    src.reply("[SSH]使用!!ssh \"<命令>\"向远程服务器执行命令，并获取命令执行结果")

def on_unload(server: PluginServerInterface):
    global ssh_client
    ssh_client.disconnect()
    server.logger.info("[SSH]插件将卸载，现有的ssh会话将被强制断开")